# This module is based on previous work in
# sdi-clients/compose/src/ports/map/map-styles

from io import StringIO
from uuid import uuid4

import mapnik
from pyproj import Proj
from layers.models import get_layer

from .point import point_style
from .line import line_style
from .polygon import polygon_style
from .datasource import set_data_source

from .mapnik_xml import Map, Layer, StyleName

point_kind = ('point-simple', 'point-discrete', 'point-continuous')
line_kind = ('line-simple', 'line-discrete', 'line-continuous')
polygon_kind = ('polygon-simple', 'polygon-discrete', 'polygon-continuous')


def set_layer_style(map_root, layer_info):
    """Given a LayerInfo instance, returns mapnik symbolizers
    """
    # config = layer_info.style
    kind = layer_info.style['kind']
    if kind in point_kind:
        return point_style(map_root, layer_info)
    elif kind in line_kind:
        return line_style(map_root, layer_info)
    elif kind in polygon_kind:
        return polygon_style(map_root, layer_info)


def make_layer_components(map_root):
    def inner(layer_info):
        md = layer_info.metadata
        rid = md.resource_identifier
        schema, table_name = rid.split('/')
        layer_name= str(layer_info.id)
        layer = Layer(map_root, layer_name)
        
        StyleName(layer, layer_name)
        set_data_source(layer, schema, table_name)
        set_layer_style(map_root, layer_info)

    return inner


def extent_to_bbox(extent):
    """Expect an array of 4 values
    [minx, miny, maxx, maxy]
    """
    return mapnik.Box2d(*extent)


def render_image(map_info, size, extent):
    """Given a UserMap model, a size and a bounding box, returns an image of the map.
    """
    proj = Proj(init='epsg:31370')

    map_tree = Map()

    for layer_info in map_info.layers.all():
        make_layer_components(map_tree.getroot())(layer_info)

    xml_file = StringIO()
    map_tree.write(xml_file, encoding='unicode', xml_declaration=True)
    xml = xml_file.getvalue()

    print('=============================================')
    print(xml)
    print('=============================================')

    m = mapnik.Map(size[0], size[1], proj.srs)
    mapnik.load_map_from_string(m, xml)
    m.zoom_to_box(extent_to_bbox(extent))
    im = mapnik.Image(*size)
    mapnik.render(m, im)
    return im
