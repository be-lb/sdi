
from .mapnik_xml import Style, Rule, Filter,MarkersSymbolizer, TextSymbolizer, stroke, fill


# if (config.label) {
#     const label = config.label;
#     propName = label.propName;
#     resLimit = label.resLimit;
#     labelStyle = new style.Text({
#         font: labelFont(label.size),
#         textAlign: label.align,
#         textBaseline: label.baseline,
#         offsetX: label.xOffset,
#         offsetY: label.yOffset,
#         fill: new style.Fill({
#             color: label.color,
#         }),
#         stroke: new style.Stroke({
#             width: 1,
#             color: 'white',
#         }),
#     });
# }

def label(rule, config):
    s = TextSymbolizer(rule, config['propName'])
    s.set('face_name', 'open_sans') # FIXME
    s.set('size', config['size'])
    s.set('dx', config['offsetX'])
    s.set('dy', config['offsetY'])
    s.set('justify_alignment', config['textAlign'])
    s.set('vertical_alignment', config['textBaseline'])
    s.set('fill', config['color'])
    s.set('halo_fill', '#ffffff')
    s.set('halo_radius', 1)
    

def marker(rule, config):
    s = MarkersSymbolizer(rule)
    s.set('width', config['size'])
    s.set('heigh', config['size'])
    s.set('fill', config['color'])




def style_simple(style, config):
    if 'label' in config:
        label(style, config['label'])
    if 'marker' in config:
        marker(style, config['marker'])






def style_discrete(style, config):
    pass



def style_continuous(style, config):
    pass



styles = {
    'point-simple': style_simple,
    'point-discrete': style_discrete,
    'point-continuous': style_continuous,
}


def point_style(map_root, layer_info):
    kind = layer_info.style['kind']
    s = Style(map_root, str(layer_info.id))
    if kind in styles:
        styles[kind](s, layer_info.style)

