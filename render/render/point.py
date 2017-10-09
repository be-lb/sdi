import mapnik


def make_style(symbolizers):
    style = mapnik.Style()
    rule = mapnik.Rule()
    for sym in symbolizers:
        rule.symbols.append(sym)
    style.rules.append(rule)

    return style


def make_symbolizer(config):
    s = mapnik.LineSymbolizer()
    s.stroke = mapnik.Color(config['strokeColor'])
    s.stroke_width = config['strokeWidth']
    if 'dash' in config:
        s.stroke_dasharray = config['dash']

    return s


def line_style_simple(config):
    return make_style([make_symbolizer(config)])


def make_discrete_rule(propname, values):
    r = mapnik.Rule()
    r.filter = mapnik.Expression(' or '.join(
        map(lambda v: '[{}] = \'{}\''.format(propname, v), values)))

    return r


def line_style_discrete(config):
    style = mapnik.Style()
    propname = config['propName']
    groups = config['groups']

    for group in groups:
        rule = make_discrete_rule(propname, group['values'])
        rule.symbols.append(make_symbolizer(group))
        style.rules.append(rule)

    return style


def make_continuous_rule(propname, low, high):
    r = mapnik.Rule()
    r.filter = mapnik.Expression(
        '[{0}] >= {1} and [{0}] < {2}'.format(propname, low, high))

    return r


def line_style_continuous(config):
    style = mapnik.Style()
    propname = config['propName']
    intervals = config['intervals']

    for group in groups:
        rule = make_continuous_rule(propname, group['low'], group['high'])
        rule.symbols.append(make_symbolizer(group))
        style.rules.append(rule)

    return style


# const lineStyle = (config: LineStyleConfig): StyleFn => {
#     switch (config.kind) {
#         case 'line-simple':
#             return lineStyleSimple(config);
#         case 'line-discrete':
#             return lineStyleDiscrete(config);
#         case 'line-continuous':
#             return lineStyleContinuous(config);
#     }
# };

styles = {
    'line-simple': line_style_simple,
    'line-discrete': line_style_discrete,
    'line-continuous': line_style_continuous,
}


def line_style(config):
    kind = config['kind']
    if kind in styles:
        return style[kind](config)

    return mapnik.Style()
