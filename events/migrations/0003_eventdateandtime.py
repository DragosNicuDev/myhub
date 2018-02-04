# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-04 11:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_event_event_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventDateAndTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_dateandtime', models.DateTimeField(verbose_name='Date and Time')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='date_event', to='events.Event')),
            ],
        ),
    ]
