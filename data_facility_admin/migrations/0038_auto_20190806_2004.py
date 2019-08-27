# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-07 00:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_facility_admin', '0037_auto_20190805_1429'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datasetaccess',
            old_name='expire_at',
            new_name='end_at',
        ),
        migrations.RenameField(
            model_name='datasetaccess',
            old_name='granted_at',
            new_name='start_at',
        ),
        migrations.RenameField(
            model_name='historicaldatasetaccess',
            old_name='expire_at',
            new_name='end_at',
        ),
        migrations.RenameField(
            model_name='historicaldatasetaccess',
            old_name='granted_at',
            new_name='start_at',
        ),
        migrations.RemoveField(
            model_name='datasetaccess',
            name='requested_at',
        ),
        migrations.RemoveField(
            model_name='datasetaccess',
            name='reviewed_at',
        ),
        migrations.RemoveField(
            model_name='historicaldatasetaccess',
            name='requested_at',
        ),
        migrations.RemoveField(
            model_name='historicaldatasetaccess',
            name='reviewed_at',
        ),
    ]
