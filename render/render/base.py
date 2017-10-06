
# This module is based on previous work in
# sdi-clients/compose/src/ports/map/map-styles

import mapnik

from .line import line_style

from layer.models import get_layer


def get_layer_style(layer):
    """Given a LayerInfo instance, returns mapnik symbolizers
    """


def make_layer(layer):
    md = layer.metadata
    rid = md.resource_identifier


def render_image(model, size, bbox):
    """Given a UserMap model, a size and a bounding box, returns an image of the map.
    """

    layers = map(get_layer_style, model.layers)
