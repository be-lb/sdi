
#
#  Copyright (C) 2017 Atelier Cartographique <contact@atelier-cartographique.be>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from django.db import connections
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from layers.models import get_layer


# def layer(request, schema, table):
#     model, ser = get_layer(schema, table)
#     items = model.objects.using(schema).all()
#     print(len(items))
#     json = ser(items)
#     return HttpResponse(json)
#   if is_geometry:
#                 def json_ser_for_model(geom_f, items):
#                     return serialize('geojson',
#                                      items,
#                                      geometry_field=geom_f)
#                 json_ser = partial(json_ser_for_model, att_name)


GEOJSON_QUERY = """
SELECT row_to_json(fc)
  FROM (
    SELECT 
      'FeatureCollection' AS type, 
      array_to_json(array_agg(f)) AS features
    FROM (
        SELECT 
          'Feature' AS type, 
          ST_AsGeoJSON(sd.{geometry_column})::json AS geometry, 
          row_to_json((
            SELECT prop FROM (SELECT {field_names}) AS prop
           )) AS properties
        FROM "{schema}"."{table}" AS sd 
    ) AS f 
  ) AS fc;
"""

def get_query(schema, table):
    model, geometry_field, geometry_field_type = get_layer(schema, table)
    fields = []
    for field in model._meta.get_fields():
        if field.get_attname() != geometry_field:
            fields.append(field.column)
    
    return GEOJSON_QUERY.format(
            schema=schema,
            table=table,
            geometry_column=geometry_field,
            field_names=', '.join(fields))

def get_geojson(schema, table):
    query = get_query(schema, table)
    with connections[schema].cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()

    return row[0]


def get_serializer(schema, table):
    model, geometry_field, geometry_field_type = get_layer(schema, table)
    meta = type('Meta', (), dict(
        model=model,
        fields='__all__',
        geo_field=geometry_field,))
    serializer_name = 'serializer_{}_{}'.format(schema, table)
    serializer = type(
        serializer_name,
        (GeoFeatureModelSerializer,),
        dict(Meta=meta),
    )

    return serializer


def get_model(schema, table):
    model, geometry_field, geometry_field_type = get_layer(schema, table)

    return model
