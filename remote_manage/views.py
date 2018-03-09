from django.shortcuts import render, redirect
from api.models import MetaData
from django.db import connections
from django.conf import settings
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.


## << REFRESH - copied from draftmetadata.py
def dictfetchall(cursor):
    # from django docs
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


GEOMETRY = dict(
    POINT='Point',
    POLYGON='Polygon',
    LINESTRING='LineString',
    MULTIPOINT='MultiPoint',
    MULTIPOLYGON='MultiPolygon',
    MULTILINESTRING='MultiLineString',
)


def refresh_shema(schema, user):
    conn = connections[schema]
    with conn.cursor() as cursor:
        cursor.execute('''
        SELECT f_table_name, type
        FROM "public"."geometry_columns"
        WHERE f_table_schema = %s
        ''', [schema])
        for r in cursor.fetchall():
            try:
                table_name = '{}/{}'.format(schema, r[0])
                geometry_type = GEOMETRY[r[1]]
                try:
                    md = MetaData.objects.get(resource_identifier=table_name)
                except MetaData.DoesNotExist:
                    try:
                        md = MetaData.objects.create_draft(
                            table_name, geometry_type, user)
                    except Exception as e:
                        pass

            except Exception as e:
                pass


def sync_metadata(user):
    for schema in settings.LAYERS_SCHEMAS:
        refresh_shema(schema, user)


@staff_member_required
def api_metadata_sync(request):
    sync_metadata(request.user)
    return redirect(reverse('admin:api_metadata_changelist'))


## >> REFRESH
