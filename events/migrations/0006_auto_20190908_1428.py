# Generated by Django 2.2.2 on 2019-09-08 11:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20190908_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
