
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
