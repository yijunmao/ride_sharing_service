# Generated by Django 2.2.10 on 2020-03-16 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ride_app', '0012_auto_20200207_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='arr_date_time',
            field=models.DateTimeField(default='2020-03-16 01:51', verbose_name='Arrival Time'),
        ),
        migrations.AlterField(
            model_name='sharer',
            name='earliest_time',
            field=models.DateTimeField(default='2020-03-16 01:51', verbose_name='Earliest Time'),
        ),
        migrations.AlterField(
            model_name='sharer',
            name='latest_time',
            field=models.DateTimeField(default='2020-03-16 01:51', verbose_name='Latest Time'),
        ),
    ]
