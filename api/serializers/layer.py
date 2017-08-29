
# from rest_framework import serializers
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
    model, geometry_field = get_layer(schema, table)
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
    model, geometry_field = get_layer(schema, table)

    return model
