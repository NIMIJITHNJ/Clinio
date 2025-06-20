# Generated by Django 5.0 on 2025-05-23 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='department',
            field=models.CharField(default='General', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctor',
            name='name',
            field=models.CharField(default='Unnamed Doctor', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctor',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='doctor_profiles/'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='qualifications',
            field=models.CharField(default='Not specified', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='doctor',
            name='phone',
            field=models.CharField(max_length=20),
        ),
    ]
