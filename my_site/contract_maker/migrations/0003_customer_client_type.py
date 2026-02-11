# Add client_type (status) to Customer

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contract_maker", "0002_add_customer"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="client_type",
            field=models.CharField(
                choices=[("individual", "Физическое лицо"), ("legal", "Юридическое лицо или ИП")],
                default="legal",
                max_length=20,
                verbose_name="Статус клиента",
            ),
        ),
    ]
