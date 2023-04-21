# Generated by Django 4.2 on 2023-04-17 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "transactions",
            "0004_rename_enter_amount_to_transfer_moneytransfer_amount_to_transfer_to_payee_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="amount", name="email", field=models.EmailField(max_length=100),
        ),
        migrations.AlterField(
            model_name="moneytransfer",
            name="payee_email_address",
            field=models.EmailField(max_length=100),
        ),
        migrations.AlterField(
            model_name="moneytransfer",
            name="payer_email_address",
            field=models.EmailField(max_length=100),
        ),
    ]
