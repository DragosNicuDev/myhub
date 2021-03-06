# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-06 11:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20180205_1704'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_description', models.TextField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_description', to='events.Event')),
            ],
        ),
    ]
