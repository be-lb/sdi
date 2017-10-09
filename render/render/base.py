# This module is based on previous work in
# sdi-clients/compose/src/ports/map/map-styles

from uuid import uuid4

import mapnik
from pyproj import Proj
from layer.models import get_layer

from .line import line_style
from .datasource import GeoDjangoDatasource

point_kind = ('point-simple', 'point-discrete', 'point-continuous')
line_kind = ('line-simple', 'line-discrete', 'line-continuous')
polygon_kind = ('polygon-simple', 'polygon-discrete', 'polygon-continuous')


def get_layer_style(layer):
    """Given a LayerInfo instance, returns mapnik symbolizers
    """
    config = line.style
    kind = config['kind']
    if kind in point_kind:
        return point_style(config)
    elif kind in line_kind:
        return line_style(config)
    elif kind in polygon_kind:
        return polygon_style(config)


def make_layer_components(layer):
    md = layer.metadata
    rid = md.resource_identifier
    schema, table_name = rid.split('.')[:2]
    model, geometry_column, geometry_type = get_layer(schema, table_name)
    ds = GeoDjangoDatasource(model, geometry_column, geometry_type)
    style = get_layer_style(layer)
    py_ds = mapnik.create_python_datasource(ds)

    return py_ds, style


def extent_to_bbox(extent):
    """Expect an array of 4 values
    [minx, miny, maxx, maxy]
    """
    return mapnik.Box2d(*extent)


def render_image(map_info, size, extent):
    """Given a UserMap model, a size and a bounding box, returns an image of the map.
    """
    proj = Proj(init='epsg:31370')
    m = mapnik.Map(size[0], size[1], proj.srs)
    for ds, style in map(make_layer_components, map_info.layers):
        sid = uuid4()
        m.append_style(sid, style)
        lyr = mapnik.Layer(sid)
        lyr.styles.append(sid)
        lyr.datasource = ds

    m.zoom_to_box(extent_to_bbox(extent))
    im = mapnik.Image(*size)
    mapnik.render(m, im)
