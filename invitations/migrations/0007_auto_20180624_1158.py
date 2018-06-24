# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-24 11:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0006_remove_eventinvitation_language'),
    ]

    operations = [
        migrations.RenameField(
            model_name='eventinvitation',
            old_name='subject',
            new_name='subject_en',
        ),
        migrations.AddField(
            model_name='eventinvitation',
            name='subject_ro',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
