# Generated by Django 5.2.1 on 2025-06-08 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0007_appointment_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='invoice_number',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
