# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-28 21:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_facility_admin', '0014_auto_20181120_2125'),
        ('data_facility_metadata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataStore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('host', models.CharField(blank=True, help_text='Host or endpoint to access this Data Store physical location.', max_length=1024, null=True)),
                ('port', models.CharField(blank=True, max_length=1024, null=True)),
                ('database', models.CharField(blank=True, max_length=1024, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DataTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('rows', models.IntegerField(blank=True, null=True)),
                ('columns', models.IntegerField(blank=True, null=True)),
                ('values', models.IntegerField(blank=True, null=True)),
                ('gps_latitude_min', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True)),
                ('gps_latitude_max', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True)),
                ('gps_longitude_min', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True)),
                ('gps_longitude_max', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True)),
                ('size', models.CharField(blank=True, max_length=256)),
                ('temporal_coverage_start', models.DateTimeField(blank=True, null=True)),
                ('temporal_coverage_end', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_facility_admin.Dataset')),
            ],
            options={
                'ordering': ['name', 'file'],
            },
        ),
        migrations.CreateModel(
            name='DataType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('category', models.CharField(choices=[('String', 'String'), ('Numeric', 'Numeric'), ('Date/Time', 'Date/Time'), ('Misc', 'Misc')], default='String', max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FileFormat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('mimetype', models.CharField(max_length=256, unique=True)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalDataStore',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=256)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('host', models.CharField(blank=True, help_text='Host or endpoint to access this Data Store physical location.', max_length=1024, null=True)),
                ('port', models.CharField(blank=True, max_length=1024, null=True)),
                ('database', models.CharField(blank=True, max_length=1024, null=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical data store',
            },
        ),
        migrations.CreateModel(
            name='HistoricalDataTable',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('rows', models.IntegerField(blank=True, null=True)),
                ('columns', models.IntegerField(blank=True, null=True)),
                ('values', models.IntegerField(blank=True, null=True)),
                ('gps_latitude_min', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True)),
                ('gps_latitude_max', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True)),
                ('gps_longitude_min', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True)),
                ('gps_longitude_max', models.DecimalField(blank=True, decimal_places=5, max_digits=8, null=True)),
                ('size', models.CharField(blank=True, max_length=256)),
                ('temporal_coverage_start', models.DateTimeField(blank=True, null=True)),
                ('temporal_coverage_end', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('dataset', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_admin.Dataset')),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical data table',
            },
        ),
        migrations.CreateModel(
            name='HistoricalDataType',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=256)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('category', models.CharField(choices=[('String', 'String'), ('Numeric', 'Numeric'), ('Date/Time', 'Date/Time'), ('Misc', 'Misc')], default='String', max_length=256)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical data type',
            },
        ),
        migrations.CreateModel(
            name='HistoricalFile',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=256)),
                ('type', models.CharField(blank=True, db_index=True, max_length=256, null=True)),
                ('location', models.CharField(blank=True, db_index=True, max_length=256, null=True)),
                ('size', models.CharField(blank=True, max_length=256, null=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('dataset', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_admin.Dataset')),
                ('format', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_metadata.FileFormat')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical file',
            },
        ),
        migrations.CreateModel(
            name='HistoricalFileFormat',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('mimetype', models.CharField(db_index=True, max_length=256)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical file format',
            },
        ),
        migrations.CreateModel(
            name='HistoricalPhysicalDataTable',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('path', models.CharField(help_text='Indicates the path of this resource inside the given storage location', max_length=256)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('data_store', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_metadata.DataStore')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('logical_data_table', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_metadata.DataTable')),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical physical data table',
            },
        ),
        migrations.CreateModel(
            name='HistoricalStorageType',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='This field represent the storage type to be used (e.g. S3 or PG)', max_length=256)),
                ('description', models.TextField(blank=True, help_text='This field represent the storage type to be used (e.g. S3 or PG)', max_length=1024, null=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical storage type',
            },
        ),
        migrations.CreateModel(
            name='HistoricalVariable',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('unique_values', models.IntegerField(blank=True, null=True)),
                ('missing_values', models.IntegerField(blank=True, null=True)),
                ('top_k', models.CharField(blank=True, max_length=256, null=True)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('data_table', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_metadata.DataTable')),
                ('detected_type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_metadata.DataType')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('provided_type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_metadata.DataType')),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical variable',
            },
        ),
        migrations.CreateModel(
            name='PhysicalDataTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(help_text='Indicates the path of this resource inside the given storage location', max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data_store', models.ForeignKey(help_text='Address of the physical location of this table.', on_delete=django.db.models.deletion.CASCADE, to='data_facility_metadata.DataStore')),
                ('logical_data_table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_facility_metadata.DataTable')),
            ],
            options={
                'ordering': ['logical_data_table', 'path'],
            },
        ),
        migrations.CreateModel(
            name='StorageType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='This field represent the storage type to be used (e.g. S3 or PG)', max_length=256, unique=True)),
                ('description', models.TextField(blank=True, help_text='This field represent the storage type to be used (e.g. S3 or PG)', max_length=1024, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True, max_length=1024, null=True)),
                ('unique_values', models.IntegerField(blank=True, null=True)),
                ('missing_values', models.IntegerField(blank=True, null=True)),
                ('top_k', models.CharField(blank=True, max_length=256, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data_table', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_facility_metadata.DataTable')),
                ('detected_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='detected_type', to='data_facility_metadata.DataType')),
                ('provided_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='provided_type', to='data_facility_metadata.DataType')),
            ],
            options={
                'ordering': ['data_table', 'name'],
            },
        ),
        migrations.AddField(
            model_name='file',
            name='dataset',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='data_facility_admin.Dataset'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='file',
            name='location',
            field=models.CharField(blank=True, max_length=256, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='size',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='type',
            field=models.CharField(blank=True, max_length=256, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='file',
            name='format',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data_facility_metadata.FileFormat'),
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('dataset', 'name')]),
        ),
        migrations.AddField(
            model_name='historicaldatatype',
            name='data_store',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_metadata.StorageType'),
        ),
        migrations.AddField(
            model_name='historicaldatatype',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicaldatatable',
            name='file',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_metadata.File'),
        ),
        migrations.AddField(
            model_name='historicaldatatable',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicaldatastore',
            name='type',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='data_facility_metadata.StorageType'),
        ),
        migrations.AddField(
            model_name='datatype',
            name='data_store',
            field=models.ForeignKey(help_text='Which data store this data type is related to, such as Hive or Postgres.', on_delete=django.db.models.deletion.CASCADE, to='data_facility_metadata.StorageType'),
        ),
        migrations.AddField(
            model_name='datatable',
            name='file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data_facility_metadata.File'),
        ),
        migrations.AddField(
            model_name='datastore',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_facility_metadata.StorageType'),
        ),
        migrations.AlterUniqueTogether(
            name='variable',
            unique_together=set([('data_table', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='datatable',
            unique_together=set([('dataset', 'name')]),
        ),
    ]