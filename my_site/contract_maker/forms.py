# Форма для ввода данных заказчика и параметров договора/акта
from datetime import date

from django import forms

from .models import Contract, Customer, WorkType


class CustomerForm(forms.Form):
    """Форма добавления/редактирования клиента в базу."""

    CLIENT_TYPE_INDIVIDUAL = "individual"
    CLIENT_TYPE_LEGAL = "legal"
    CLIENT_TYPE_CHOICES = [
        (CLIENT_TYPE_INDIVIDUAL, "Физическое лицо"),
        (CLIENT_TYPE_LEGAL, "Юридическое лицо или ИП"),
    ]

    client_type = forms.ChoiceField(
        label="Статус клиента",
        choices=CLIENT_TYPE_CHOICES,
        initial=CLIENT_TYPE_LEGAL,
        widget=forms.RadioSelect,
    )
    org_name = forms.CharField(
        label="Наименование организации / ФИО",
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "ООО «Пример» или Иванов Иван Иванович"}),
    )
    rep_position = forms.CharField(
        label="Должность представителя",
        max_length=100,
        required=False,
        initial="директора",
        widget=forms.TextInput(attrs={"placeholder": "директора"}),
    )
    rep_name = forms.CharField(
        label="ФИО представителя",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Иванов Иван Иванович"}),
    )
    basis = forms.CharField(
        label="Действует на основании",
        max_length=255,
        required=False,
        initial="Устава",
        widget=forms.TextInput(attrs={"placeholder": "Устава"}),
    )
    short_name = forms.CharField(
        label="Краткая подпись (в реквизитах)",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "И.И. Иванов"}),
    )
    address = forms.CharField(
        label="Адрес заказчика",
        max_length=500,
        required=False,
        initial="г. Минск",
        widget=forms.TextInput(attrs={"placeholder": "г. Минск"}),
    )
    unp = forms.CharField(label="УНП", max_length=20, required=False, widget=forms.TextInput(attrs={"placeholder": "УНП"}))
    okpo = forms.CharField(label="ОКПО", max_length=20, required=False, widget=forms.TextInput(attrs={"placeholder": "ОКПО"}))
    iban = forms.CharField(label="IBAN", max_length=50, required=False, widget=forms.TextInput(attrs={"placeholder": "IBAN"}))


class ContractMakerForm(forms.Form):
    """Параметры договора подряда и акта. Заказчик выбирается из базы."""

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.none(),
        label="Клиент (заказчик)",
        empty_label="— выберите клиента —",
        required=True,
    )

    # Договор / общее
    contract_number = forms.CharField(
        label="Номер договора",
        max_length=50,
        initial="1",
        widget=forms.TextInput(attrs={
            "placeholder": "например 1 или 2025-01",
            "title": "Уникальный номер договора. Будет указан в документе и в названии файла.",
        }),
    )
    doc_date = forms.CharField(
        label="Дата договора",
        max_length=20,
        widget=forms.TextInput(attrs={
            "placeholder": "ДД.ММ.ГГГГ",
            "title": "Дата заключения договора в формате день.месяц.год.",
        }),
    )
    act_date = forms.CharField(
        label="Дата акта",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "ДД.ММ.ГГГГ (если пусто — как дата договора)",
            "title": "Дата подписания акта. Если не указать, подставится дата договора.",
        }),
    )
    location = forms.CharField(
        label="Место проведения работ",
        max_length=255,
        initial="г. Минск",
        widget=forms.TextInput(attrs={
            "placeholder": "г. Минск",
            "title": "Город или адрес, где выполняются работы. Указывается в договоре.",
        }),
    )
    total_cost = forms.DecimalField(
        label="Стоимость работ (руб.)",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        initial=500,
        widget=forms.NumberInput(attrs={
            "step": "0.01",
            "placeholder": "500",
            "title": "Общая стоимость работ в белорусских рублях. Можно с копейками (например, 1500.50).",
        }),
    )
    work_types = forms.ModelMultipleChoiceField(
        queryset=WorkType.objects.all(),
        label="Виды работ из справочника",
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Отметьте нужные. Новые можно добавить в поле ниже — они сохранятся в справочник.",
    )
    work_list_extra = forms.CharField(
        label="Добавить новый вид работ (каждая с новой строки)",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Разработка сайта\nВёрстка страниц\n… или оставьте пустым",
            "title": "Новые виды работ. Каждая строка будет добавлена в перечень и в справочник.",
        }),
    )

    # Оплата (опционально)
    payment_percent = forms.IntegerField(
        label="Процент предоплаты",
        min_value=0,
        max_value=100,
        initial=100,
        required=False,
        widget=forms.NumberInput(attrs={
            "min": 0,
            "max": 100,
            "placeholder": "100",
            "title": "Процент предоплаты (0–100). Учитывается только при включённой галочке «Предоплата». 100 — полная предоплата.",
        }),
    )
    is_prepay = forms.BooleanField(
        label="Предоплата",
        initial=True,
        required=False,
        help_text="Снимите галочку для постоплаты (оплата после подписания акта).",
    )

    def __init__(self, customers_queryset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if customers_queryset is not None:
            self.fields["customer"].queryset = customers_queryset
        # Дата договора по умолчанию — сегодня
        if not self.initial.get("doc_date"):
            self.fields["doc_date"].initial = date.today().strftime("%d.%m.%Y")
        # Справочник видов работ (актуальный при каждом открытии формы)
        self.fields["work_types"].queryset = WorkType.objects.all()

    def get_work_list(self):
        """После is_valid(): объединённый список работ — из выбранных видов + новые строки."""
        selected = list(self.cleaned_data.get("work_types", []) or [])
        data = self.cleaned_data.get("work_list_extra", "") or ""
        extra = [line.strip() for line in data.replace(";", "\n").split("\n") if line.strip()]
        names = [wt.name for wt in selected] + extra
        return names if names else ["Услуги по договору"]

    def get_work_list_extra_parsed(self):
        """После is_valid(): список строк из поля «добавить новый вид работ» (для сохранения в справочник)."""
        data = self.cleaned_data.get("work_list_extra", "") or ""
        return [line.strip() for line in data.replace(";", "\n").split("\n") if line.strip()]


def _contracts_without_act_queryset():
    """Договоры, у которых есть файл договора, но ещё нет акта."""
    return (
        Contract.objects.exclude(contract_filename="")
        .filter(act_filename="")
        .select_related("customer")
        .order_by("-created_at")
    )


class ActForContractForm(forms.Form):
    """Форма создания акта к уже существующему договору."""

    contract = forms.ModelChoiceField(
        queryset=Contract.objects.none(),
        label="Договор",
        empty_label="— выберите договор —",
        required=True,
    )
    act_date = forms.CharField(
        label="Дата акта",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "ДД.ММ.ГГГГ (если пусто — дата договора)"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contract"].queryset = _contracts_without_act_queryset()


class ContractEditForm(forms.Form):
    """Редактирование сохранённого договора (и даты акта)."""

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.none(),
        label="Клиент (заказчик)",
        empty_label="— выберите клиента —",
        required=True,
    )
    contract_number = forms.CharField(label="Номер договора", max_length=50)
    doc_date = forms.CharField(label="Дата договора", max_length=20)
    act_date = forms.CharField(label="Дата акта", max_length=20, required=False)
    location = forms.CharField(label="Место проведения работ", max_length=255)
    total_cost = forms.DecimalField(label="Стоимость (руб.)", min_value=0, max_digits=12, decimal_places=2)
    work_list = forms.CharField(
        label="Перечень работ (каждая с новой строки)",
        widget=forms.Textarea(attrs={"rows": 5}),
        required=False,
    )
    payment_percent = forms.IntegerField(label="Процент предоплаты", min_value=0, max_value=100, required=False)
    is_prepay = forms.BooleanField(label="Предоплата", required=False)
    contract_file = forms.FileField(label="Заменить договор (PDF)", required=False)
    act_file = forms.FileField(label="Заменить акт (PDF)", required=False)

    def __init__(self, customers_queryset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if customers_queryset is not None:
            self.fields["customer"].queryset = customers_queryset

    def clean_contract_file(self):
        f = self.cleaned_data.get("contract_file")
        if f and not (getattr(f, "name", "") or "").lower().endswith(".pdf"):
            raise forms.ValidationError("Допускаются только PDF.")
        return f

    def clean_act_file(self):
        f = self.cleaned_data.get("act_file")
        if f and not (getattr(f, "name", "") or "").lower().endswith(".pdf"):
            raise forms.ValidationError("Допускаются только PDF.")
        return f

    def clean_work_list(self):
        data = self.cleaned_data.get("work_list", "") or ""
        lines = [line.strip() for line in data.replace(";", "\n").split("\n") if line.strip()]
        return lines if lines else ["Услуги по договору"]


def _validate_pdf(file_obj):
    if not file_obj:
        return
    name = getattr(file_obj, "name", "") or ""
    if not name.lower().endswith(".pdf"):
        raise forms.ValidationError("Допускаются только файлы PDF.")


class ContractManualForm(forms.Form):
    """Добавление договора/акта вручную: загрузка PDF и данные записи."""

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.none(),
        label="Клиент (заказчик)",
        empty_label="— выберите клиента —",
        required=True,
    )
    contract_number = forms.CharField(label="Номер договора", max_length=50)
    doc_date = forms.CharField(label="Дата договора", max_length=20)
    act_date = forms.CharField(label="Дата акта", max_length=20, required=False)
    location = forms.CharField(label="Место проведения работ", max_length=255, required=False)
    total_cost = forms.DecimalField(label="Стоимость (руб.)", min_value=0, max_digits=12, decimal_places=2, required=False)
    work_list = forms.CharField(
        label="Перечень работ (каждая с новой строки)",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
    )
    contract_file = forms.FileField(
        label="Файл договора (PDF)",
        help_text="Загрузите PDF договора.",
        required=True,
    )
    act_file = forms.FileField(
        label="Файл акта (PDF)",
        help_text="Необязательно. Загрузите PDF акта, если есть.",
        required=False,
    )

    def __init__(self, customers_queryset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if customers_queryset is not None:
            self.fields["customer"].queryset = customers_queryset

    def clean_contract_file(self):
        f = self.cleaned_data.get("contract_file")
        _validate_pdf(f)
        return f

    def clean_act_file(self):
        f = self.cleaned_data.get("act_file")
        _validate_pdf(f)
        return f

    def clean_work_list(self):
        data = self.cleaned_data.get("work_list", "") or ""
        lines = [line.strip() for line in data.replace(";", "\n").split("\n") if line.strip()]
        return lines if lines else ["Услуги по договору"]
