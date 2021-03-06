
from .mapnik_xml import Style, Rule, Filter, LineSymbolizer, stroke



def style_simple(style, config):
    stroke(LineSymbolizer(Rule(style)), 
        config['strokeWidth'], config['strokeColor'])



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




def make_continuous_rule(style, propname, low, high):
    r = Rule()
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




styles = {
    'line-simple': style_simple,
    'line-discrete': style_discrete,
    'line-continuous': style_continuous,
}


def line_style(map_root, layer_info):
    kind = layer_info.style['kind']
    s = Style(map_root, str(layer_info.id))
    if kind in styles:
        styles[kind](s, layer_info.style)

