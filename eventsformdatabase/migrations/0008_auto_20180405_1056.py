# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-04-05 10:56
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events_form_database', '0007_auto_20180405_0904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savedeventformdataentry',
            name='dragos_saved_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='Dragos Plugin data'),
        ),
        migrations.AlterField(
            model_name='savedeventformwizarddataentry',
            name='dragos_saved_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='Dragos Plugin data'),
        ),
    ]
