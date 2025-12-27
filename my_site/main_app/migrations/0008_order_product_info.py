# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0007_businesssoftware_demo_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='product_name',
            field=models.CharField(blank=True, help_text='Название продукта, на который оформлен заказ', max_length=200, null=True, verbose_name='Название продукта'),
        ),
        migrations.AddField(
            model_name='order',
            name='product_version',
            field=models.CharField(blank=True, help_text='Версия продукта (например: Standard, Custom, Demo)', max_length=50, null=True, verbose_name='Версия продукта'),
        ),
        migrations.AddField(
            model_name='order',
            name='product_price',
            field=models.CharField(blank=True, help_text='Цена продукта (например: 10000 BYN)', max_length=100, null=True, verbose_name='Цена продукта'),
        ),
    ]

