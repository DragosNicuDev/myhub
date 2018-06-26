# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-21 15:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_auto_20180418_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventinvitee',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('ro', 'Română')], default='ro', max_length=2),
        ),
    ]