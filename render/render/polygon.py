
from .mapnik_xml import (
    Style, Rule, Filter, 
    PolygonSymbolizer,LineSymbolizer, 
    stroke, fill, )



def style_simple(style, config):
    rule = Rule(style)
    stroke(LineSymbolizer(rule),
        config['strokeWidth'], config['strokeColor'])
    fill(PolygonSymbolizer(rule),
        config['fillColor'])



def make_discrete_rule(style, propname, values):
    r = Rule(style)
    Filter(r,
        ' or '.join(
            map(lambda v: '[{}] = \'{}\''.format(propname, v),
                values)))

    return r


def style_discrete(style, config):
    propname = config['propName']
    groups = config['groups']

    for group in groups:
        rule = make_discrete_rule(style, 
            propname, group['values'])
        stroke(LineSymbolizer(rule), 
            group['strokeWidth'], group['strokeColor'] )
        fill(PolygonSymbolizer(rule),
            group['fillColor'])




def make_continuous_rule(style, propname, low, high):
    r = Rule(style)
    Filter(r,
        '[{0}] >= {1} and [{0}] < {2}'.format(propname, low, high))

    return r


def style_continuous(style, config):
    propname = config['propName']
    intervals = config['intervals']

    for group in intervals:
        rule = make_continuous_rule(style, 
            propname, group['low'], group['high'])
        stroke(LineSymbolizer(rule), 
            group['strokeWidth'], group['strokeColor'] )
        fill(PolygonSymbolizer(rule),
            group['fillColor'])




styles = {
    'polygon-simple': style_simple,
    'polygon-discrete': style_discrete,
    'polygon-continuous': style_continuous,
}


def polygon_style(map_root, layer_info):
    kind = layer_info.style['kind']
    s = Style(map_root, str(layer_info.id))
    if kind in styles:
        styles[kind](s, layer_info.style)

