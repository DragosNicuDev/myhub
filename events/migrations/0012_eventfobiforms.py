# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-03 15:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fobi', '0014_auto_20170516_1413'),
        ('events', '0011_auto_20180302_1111'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventFobiForms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
                ('fobi', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='fobi.FormEntry')),
            ],
        ),
    ]