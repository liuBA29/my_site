from django.db import models
from django.conf import settings


class Customer(models.Model):
    """Клиент (заказчик) для подстановки в договоры и акты."""

    CLIENT_TYPE_INDIVIDUAL = "individual"
    CLIENT_TYPE_LEGAL = "legal"
    CLIENT_TYPE_CHOICES = [
        (CLIENT_TYPE_INDIVIDUAL, "Физическое лицо"),
        (CLIENT_TYPE_LEGAL, "Юридическое лицо или ИП"),
    ]

    client_type = models.CharField(
        "Статус клиента",
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        default=CLIENT_TYPE_LEGAL,
    )
    org_name = models.CharField("Наименование организации / ФИО", max_length=255)
    rep_position = models.CharField("Должность представителя", max_length=100, blank=True, default="")
    rep_name = models.CharField("ФИО представителя", max_length=255, blank=True, default="")
    basis = models.CharField("Действует на основании", max_length=255, blank=True, default="Устава")
    short_name = models.CharField("Краткая подпись (в реквизитах)", max_length=100, blank=True, default="")
    address = models.CharField("Адрес", max_length=500, blank=True, default="")
    unp = models.CharField("УНП", max_length=20, blank=True, default="")
    okpo = models.CharField("ОКПО", max_length=20, blank=True, default="")
    iban = models.CharField("IBAN", max_length=50, blank=True, default="")

    created_at = models.DateTimeField("Добавлен", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contract_customers",
        verbose_name="Кто добавил",
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["org_name"]

    def __str__(self):
        return self.org_name or "—"

    def to_customer_dict(self):
        """Словарь для document_generator (как get_customer_dict формы)."""
        short = (self.short_name or "").strip() or (self.rep_name or "Заказчик")
        return {
            "client_type": self.client_type,
            "org_name": self.org_name or "Заказчик",
            "rep_position": self.rep_position or "",
            "rep_name": self.rep_name or "",
            "basis": self.basis or "Устава",
            "short_name": short,
            "table_name": self.org_name or "Заказчик",
            "address": self.address or "",
            "unp": self.unp or "",
            "okpo": self.okpo or "",
            "iban": self.iban or "",
        }


class WorkType(models.Model):
    """Справочник видов работ для выбора при создании договора."""

    name = models.CharField("Наименование вида работ", max_length=255)
    order = models.PositiveIntegerField("Порядок", default=0, blank=True)

    class Meta:
        verbose_name = "Вид работ"
        verbose_name_plural = "Виды работ"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Contract(models.Model):
    """Сохранённые данные сгенерированного договора и акта."""

    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts",
        verbose_name="Клиент (заказчик)",
    )
    contract_number = models.CharField("Номер договора", max_length=50)
    doc_date = models.CharField("Дата договора", max_length=20)
    act_date = models.CharField("Дата акта", max_length=20)
    location = models.CharField("Место проведения работ", max_length=255)
    total_cost = models.DecimalField("Стоимость (руб.)", max_digits=12, decimal_places=2)

    work_list = models.JSONField("Перечень работ", default=list)  # список строк
    customer_data = models.JSONField("Реквизиты заказчика", default=dict)  # снимок на момент создания

    contract_filename = models.CharField("Файл договора", max_length=255, blank=True)
    act_filename = models.CharField("Файл акта", max_length=255, blank=True)

    payment_percent = models.PositiveSmallIntegerField("Процент предоплаты", null=True, blank=True, default=100)
    is_prepay = models.BooleanField("Предоплата", default=True)

    created_at = models.DateTimeField("Создан", auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_contracts",
        verbose_name="Кто создал",
    )

    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"
        ordering = ["-created_at"]

    def __str__(self):
        customer_name = (self.customer_data or {}).get("org_name", "") or (self.customer.org_name if self.customer_id else "Заказчик")
        return f"№ {self.contract_number} от {self.doc_date} — {customer_name}"

    def get_customer_dict(self):
        """Реквизиты заказчика для генерации документа (из связи или из снимка)."""
        if self.customer_id:
            return self.customer.to_customer_dict()
        return self.customer_data or {}
