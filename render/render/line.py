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

# const lineStyleSimple = (config: LineStyleConfigSimple) => {

#     const stroke = new style.Stroke({
#         color: config.strokeColor,
#         width: config.strokeWidth,
#         lineDash: config.dash,
#     });
#     const styles = [new style.Style({ stroke })];

#     return (/* feature, resolution */) => styles;
# };


def line_style_simple(config):
    return make_style([make_symbolizer(config)])


# const lineStyleDiscrete = (config: LineStyleConfigDiscrete) => {
#     const groups = config.groups;
#     const groupStyles = groups.reduce<style.Style[]>((acc, group) => {
#         acc.push(new style.Style({
#             stroke: new style.Stroke({
#                 color: group.strokeColor,
#                 width: group.strokeWidth,
#                 lineDash: group.dash,
#             }),
#         }));
#         return acc;
#     }, []);

#     const findIndex = (v: string) => {
#         for (let i = 0; i < groups.length; i += 1) {
#             const group = groups[i];
#             const idx = group.values.indexOf(v);
#             if (idx >= 0) {
#                 return i;
#             }
#         }
#         return -1;
#     };

#     return (feature: Feature, _resolution: number) => {
#         const styles: style.Style[] = [];

#         const props = feature.getProperties();
#         const value = props[config.propName];
#         if (typeof value === 'string') {
#             const idx = findIndex(value);
#             if (idx >= 0) {
#                 styles.push(groupStyles[idx]);
#             }
#         }

#         return styles;
#     };
# };


def make_discrete_rule(propname, values):
    r = mapnik.Rule()
    r.filter = mapnik.Expression(
        ' or '.join(
            map(lambda v: '[{}] = \'{}\''.format(propname, v),
                values)))

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


# const lineStyleContinuous = (config: LineStyleConfigContinuous) => {
#     const intervals = config.intervals;
#     const styles = intervals.reduce<StyleReg>((acc, itv) => {
#         acc[itv.low] = new style.Style({
#             stroke: new style.Stroke({
#                 color: itv.strokeColor,
#                 width: itv.strokeWidth,
#             }),
#         });
#         return acc;
#     }, {});

#     const findLow = (n: number) => {
#         for (let i = 0; i < intervals.length; i += 1) {
#             if (n >= intervals[i].low
#                 && n < intervals[i].high) {
#                 return intervals[i].low;
#             }
#         }
#         return null;
#     };

#     return (feature: Feature) => {
#         const props = feature.getProperties();
#         const value = props[config.propName];
#         if (typeof value === 'number') {
#             const low = findLow(value);
#             if (low !== null) {
#                 return [styles[low]];
#             }
#         }
#         return [];
#     };
# };

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
