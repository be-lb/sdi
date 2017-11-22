
import xml.etree.ElementTree as ET
from uuid import uuid4




def Map():
    e = ET.Element('Map')
    return ET.ElementTree(e)

def Layer(m, name):
    return ET.SubElement(m, 'Layer', dict(name=name))

def Datasource(layer):
    return ET.SubElement(layer, 'Datasource')

def Style(m, name):
    return ET.SubElement(m, 'Style', dict(name=name))

def StyleName(layer, name):
    e = ET.SubElement(layer, 'StyleName')
    e.text = name
    return e

def Rule(style):
    return ET.SubElement(style, 'Rule')

def Filter(rule, expression):
    e = ET.SubElement(rule, 'Filter')
    e.text = expression
    return e

def TextSymbolizer(rule, field_name):
    e = ET.SubElement(rule, 'TextSymbolizer')
    e.text = '[{}]'.format(field_name)
    return e

def LineSymbolizer(rule):
    return ET.SubElement(rule, 'LineSymbolizer')

def PolygonSymbolizer(rule):
    return ET.SubElement(rule, 'PolygonSymbolizer')

def MarkersSymbolizer(rule):
    return ET.SubElement(rule, 'MarkersSymbolizer')



def stroke(e, width, color):
    e.set('stroke', color)
    e.set('stroke-width', str(width))
    return e


def fill(e,  color):
    e.set('fill', color)
    return e

def ds_attributes(ds, **kwargs):
    for k in kwargs:
        p = ET.SubElement(ds, 'Parameter', dict(name=k))
        p.text = kwargs[k]
    
    return ds
