# Generated by Django 4.2 on 2023-04-15 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("convert_currency_api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rate",
            name="rate",
            field=models.DecimalField(decimal_places=4, default=1, max_digits=10),
        ),
    ]