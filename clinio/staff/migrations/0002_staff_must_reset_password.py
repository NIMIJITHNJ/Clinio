# Generated by Django 5.2.1 on 2025-05-25 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='must_reset_password',
            field=models.BooleanField(default=True),
        ),
    ]
