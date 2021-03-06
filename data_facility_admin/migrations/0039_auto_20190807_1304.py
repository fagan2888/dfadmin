# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-07 17:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('data_facility_admin', '0038_auto_20190806_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalprojectmember',
            name='end_date',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='historicalprojectmember',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='projectmember',
            name='end_date',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='projectmember',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
    ]
