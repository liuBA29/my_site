# Тестовые клиенты: 2 физлица, 2 юрлица/ИП

from django.db import migrations


def add_test_customers(apps, schema_editor):
    Customer = apps.get_model("contract_maker", "Customer")
    # 2 физических лица
    Customer.objects.get_or_create(
        org_name="Петров Пётр Петрович",
        defaults={
            "client_type": "individual",
            "address": "г. Минск, ул. Примерная, д. 1, кв. 1",
            "short_name": "П.П. Петров",
            "rep_position": "",
            "rep_name": "",
            "basis": "",
            "unp": "",
            "okpo": "",
            "iban": "",
        },
    )
    Customer.objects.get_or_create(
        org_name="Сидорова Анна Ивановна",
        defaults={
            "client_type": "individual",
            "address": "г. Гомель, пр. Победы, д. 10, кв. 5",
            "short_name": "А.И. Сидорова",
            "rep_position": "",
            "rep_name": "",
            "basis": "",
            "unp": "",
            "okpo": "",
            "iban": "",
        },
    )
    # 2 юридических лица / ИП
    Customer.objects.get_or_create(
        org_name='ООО "Тестовая компания"',
        defaults={
            "client_type": "legal",
            "rep_position": "директора",
            "rep_name": "Иванов Иван Иванович",
            "basis": "Устава",
            "short_name": "И.И. Иванов",
            "address": "г. Минск, ул. Бизнесовая, д. 5",
            "unp": "123456789",
            "okpo": "12345678",
            "iban": "BY00XXXX00000000000000000000",
        },
    )
    Customer.objects.get_or_create(
        org_name="ИП Козлов Сергей Николаевич",
        defaults={
            "client_type": "legal",
            "rep_position": "",
            "rep_name": "Козлов Сергей Николаевич",
            "basis": "свидетельства о гос. регистрации",
            "short_name": "С.Н. Козлов",
            "address": "г. Минск, ул. Торговая, д. 3",
            "unp": "987654321",
            "okpo": "87654321",
            "iban": "BY11YYYY00000000000000000000",
        },
    )


def remove_test_customers(apps, schema_editor):
    Customer = apps.get_model("contract_maker", "Customer")
    Customer.objects.filter(
        org_name__in=[
            "Петров Пётр Петрович",
            "Сидорова Анна Ивановна",
            'ООО "Тестовая компания"',
            "ИП Козлов Сергей Николаевич",
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("contract_maker", "0004_alter_customer_org_name"),
    ]

    operations = [
        migrations.RunPython(add_test_customers, remove_test_customers),
    ]
