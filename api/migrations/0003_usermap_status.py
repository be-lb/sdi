# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-28 13:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20171114_0756'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermap',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='draft', max_length=32),
        ),
    ]
