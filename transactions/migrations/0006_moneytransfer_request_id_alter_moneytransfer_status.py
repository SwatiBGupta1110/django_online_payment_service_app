# Generated by Django 4.2 on 2023-04-20 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0005_alter_amount_email_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="moneytransfer",
            name="request_id",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="moneytransfer",
            name="status",
            field=models.CharField(
                choices=[
                    ("sent", "Sent"),
                    ("received", "Received"),
                    ("pending", "Pending"),
                    ("accepted", "Accepted"),
                    ("rejected", "Rejected"),
                    ("canceled", "Canceled"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]