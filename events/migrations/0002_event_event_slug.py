# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-03 21:36
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_slug',
            field=autoslug.fields.AutoSlugField(default='', editable=False, populate_from='event_title'),
        ),
    ]
