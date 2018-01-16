# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-16 14:27
from __future__ import unicode_literals

from django.db import migrations


from api.models import UserMap
from api.models import LayerInfo




def is_p(s):
    return s['kind'].split('-')[0] == 'polygon'

def is_simple(s):
    return  is_p(s) and  s['kind'].split('-')[1] == 'simple'

def is_cont(s):
    return  is_p(s) and  s['kind'].split('-')[1] == 'continuous'

def is_disc(s):
    return  is_p(s) and  s['kind'].split('-')[1] == 'discrete'

def patch_style(s):
    s['pattern'] = False
    s['patternAngle'] = 0

def un_patch_style(s):
    s.pop('pattern', None)
    s.pop('patternAngle', None)


def forwards_func(apps, schema_editor):
    LayerInfo = apps.get_model("api", "LayerInfo")
    db_alias = schema_editor.connection.alias
    for li in LayerInfo.objects.using(db_alias).all():
        s = li.style
        if is_simple(s):
            patch_style(s)
        elif is_cont(s):
            for si in s['intervals']:
                patch_style(si)
        elif is_disc(s):
            for si in s['groups']:
                patch_style(si)
        li.style = s
        li.save()

def reverse_func(apps, schema_editor):
    LayerInfo = apps.get_model("api", "LayerInfo")
    db_alias = schema_editor.connection.alias
    for li in LayerInfo.objects.using(db_alias).all():
        s = li.style
        if is_simple(s):
            un_patch_style(s)
        elif is_cont(s):
            for si in s['intervals']:
                un_patch_style(si)
        elif is_disc(s):
            for si in s['groups']:
                un_patch_style(si)
        li.style = s
        li.save()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20180111_1433'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
