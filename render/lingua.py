# Copyright (C) 2016  Atelier Cartographique <contact@atelier-carographique.be>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from enum import Enum
from collections import namedtuple


Size = namedtuple('Size', ['width', 'height'])
Point = namedtuple('Point', ['x', 'y'])
BoundingBox = namedtuple('BoundingBox', ['minx', 'miny', 'maxx', 'maxy'])


RequestFormat = namedtuple('RequestFormat', ['name', 'format'])

def format_list_str (val):
    return val.split(',')

def format_list_float (val):
    return [float(v) for v in val.split(',')]

def format_parse_bool (val):
    truth = ('TRUE', 'True', 'true', '1')
    return val in truth


def format_token (val):
    try:
        return LinguaWMS.Token(val)
    except ValueError:
        return None

def format_parse_color (val):
    # TODO
    return val

class LinguaWMS:

    class MissingParameter(KeyError):
        pass

    class Token(Enum):
        GetCapabilities = 'GetCapabilities'
        GetMap = 'GetMap'


    class Request:
        version = RequestFormat('VERSION', str)
        service = RequestFormat('SERVICE', str)
        request = RequestFormat('REQUEST', format_token)
        format = RequestFormat('FORMAT', str)
        updatesequence = RequestFormat('UPDATESEQUENCE', str)
        layers = RequestFormat('LAYERS', format_list_str)
        styles = RequestFormat('STYLES', format_list_str)
        crs = RequestFormat('CRS', str)
        bbox = RequestFormat('BBOX', format_list_float)
        width = RequestFormat('WIDTH', int)
        height = RequestFormat('HEIGHT', int)
        transparent = RequestFormat('TRANSPARENT', format_parse_bool)
        bgcolor = RequestFormat('BGCOLOR', format_parse_color)
        exceptions = RequestFormat('EXCEPTIONS', str)
        time = RequestFormat('TIME', str)
        elevation = RequestFormat('ELEVATION', str)


        @staticmethod
        def get (query, param, default=None):
            keys = dict()
            for k in query.keys():
                keys[k.upper()] = k
            actual_key = keys.get(param.name, None)
            if None == actual_key:
                return default
            val = query.get(actual_key, default)
            return param.format(val)


        @staticmethod
        def gets (query, params, mandatory=True):
            results = dict()
            for param in params:
                val = LinguaWMS.Request.get(query, param, None)
                if mandatory and (None == val):
                    raise LinguaWMS.MissingParameter(param)
                results[param.name] = val
            return results
