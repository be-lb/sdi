# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-09 16:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webservice', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wmslayer',
            old_name='name',
            new_name='display_name',
        ),
    ]