import json

from django.shortcuts import render
from layers.models import get_layer
from django.core.serializers import serialize
from django.http import HttpResponse

from django.db import connections


def layer(request, schema, table):
    model, ser = get_layer(schema, table)
    items = model.objects.using(schema).all()
    print(len(items))
    json = ser(items)
    return HttpResponse(json)


def dictfetchall(cursor):
# from django docs
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def list_layers(request, schema):
    conn = connections[schema]
    tables = []
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM "public"."geometry_columns";')
        for r in dictfetchall(cursor):
            r_schema = r['f_table_schema']
            r_table = r['f_table_name']
            if r_schema == schema:
                tables.append(r_table)

    return HttpResponse(json.dumps(tables))
