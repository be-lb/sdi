import mapnik
from django.contrib.gis.db.models import Extent

# model, g = get_layer('tev', 'ibge3_greenfield_area')
# qa = model.objects.all()
# q = qa.aggregate(Extent(g))
# k = '{}__extent'.format(g)
# print('extent: {}'.format(q[k]))


def pluck(keys, any):
    o = dict()
    for k in keys:
        o[k] = getattr(any, k)
    return o


EXTENT_KEYS = (
    'minx',
    'miny',
    'maxx',
    'maxy', )


def bbox2d_to_geometry(srid, bbox):
    args = pluck(EXTENT_KEYS, bbox)
    args.update(dict(srid=srid))
    return """SRID={srid};POLYGON (( {minx} {miny}, {minx} {maxy}, {maxx} {maxy}, {maxx} {miny}, {minx} {miny} ))""".format(
        **args)


def get_extent(model, geometry_column):
    qs = model.objects.all().aggregate(Extent(geometry_column))
    k = '{}__extent'.format(geometry_column)
    extent = qs[k]
    return mapnik.Box2d(*extent)


GEOMETRY_TYPE_MAP = dict(
    PointField=mapnik.GeometryType.Point,
    MultiPointField=mapnik.GeometryType.MultiPoint,
    LineStringField=mapnik.GeometryType.LineString,
    MultiLineStringField=mapnik.GeometryType.MultiLineString,
    PolygonField=mapnik.GeometryType.Polygon,
    MultiPolygonField=mapnik.GeometryType.MultiPolygon)


def get_geometry_type(field_type):
    return GEOMETRY_TYPE_MAP[field_type]


def get_fields(model):
    try:
        i = model.objects.first()
        fs = i._meta.get_fields()
        return [f.name for f in fs]
    except Exception:
        return []


def get_srid(model, geometry_column, default_srid):
    try:
        i = model.objects.first()
        geom = getattr(i, geometry_column)
        return geom.srid
    except Exception:
        return default_srid


class GeoDjangoDatasource:
    def __init__(self, model, geometry_column, geometry_type):
        self.model = model
        self.geometry_column = geometry_column
        self.envelope = get_extent(model, geometry_column)
        self.geometry_type = get_geometry_type(geometry_type)
        self.data_type = mapnik.DataType.Vector

    def features(self, query):
        geometry_column = self.geometry_column
        model = self.model
        qs = model.objects
        fields = get_fields(model)
        srid = get_srid(model, geometry_column,
                        31370)  # FIXME should come from settings
        filter = dict()
        filter_key = '{}__intersects'.format(geometry_column)
        filter[filter_key] = bbox2d_to_geometry(srid, query.bbox)
        instances = qs.filter(**filter)
        context = mapnik.Context()
        for f in fields:
            if f != geometry_column:
                context.push(f)

        def get_feature_from_instance(instance):
            feature = mapnik.Feature(context, instance.pk)
            geom = getattr(instance, geometry_column)
            feature.geometry.from_wkb(geom.wkb.tobytes())
            for k in fields:
                if k != geometry_column:
                    feature[k] = getattr(instance, k)
            return feature

        return map(get_feature_from_instance, instances)

    def features_at_point(self, point):
        geometry_column = self.geometry_column
        model = self.model
        qs = model.objects
        fields = get_fields(model)
        srid = get_srid(model, geometry_column,
                        31370)  # FIXME should come from settings
        filter = dict()
        filter_key = '{}__intersects'.format(geometry_column)
        filter[filter_key] = 'SRID={};{}'.format(srid, point.to_wkt())
        instances = qs.filter(**filter)
        context = mapnik.Context()
        for f in fields:
            if f != geometry_column:
                context.push(f)

        def get_feature_from_instance(instance):
            feature = mapnik.Feature(context, instance.pk)
            geom = getattr(instance, geometry_column)
            feature.geometry.from_wkb(geom.wkb.tobytes())
            for k in fields:
                if k != geometry_column:
                    feature[k] = getattr(instance, k)
            return feature

        return map(get_feature_from_instance, instances)
