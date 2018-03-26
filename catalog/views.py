import os

from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from django.core.checks import Warning, register
from django.views.decorators.csrf import csrf_exempt
from pycsw.server import Csw
from lxml import etree

try:
    csw_config_main = settings.CSW_CONFIG_MAIN
except AttributeError:
    csw_config_main = None

try:
    csw_config_inspire = settings.CSW_CONFIG_INSPIRE
except AttributeError:
    csw_config_inspire = None


@register()
def check_csw_config_main(app_configs, **kwargs):
    errors = []
    if not csw_config_main:
        errors.append(
            Warning(
                'Missing Config For Catalog [CSW_CONFIG_MAIN]',
                hint='Set CSW_CONFIG_MAIN in your settings',
                obj=settings,
                id='sdi.catalog.W001',
            ))
    return errors


@register()
def check_csw_config_inspire(app_configs, **kwargs):
    errors = []
    if not csw_config_inspire:
        errors.append(
            Warning(
                'Missing Config For Catalog [CSW_CONFIG_INSPIRE]',
                hint='Set CSW_CONFIG_INSPIRE in your settings',
                obj=settings,
                id='sdi.catalog.W002',
            ))
    return errors


def get_csw_config(request):
    config = {
        'server': {
            'home':
            '.',
            'url':
            '{}://{}{}'.format(request.scheme, request.get_host(),
                               reverse('catalog')),
            'encoding':
            'UTF-8',
            'language':
            'en',
            'maxrecords':
            '10',
            'loglevel':
            'DEBUG',
            'logfile':
            '/tmp/pycsw.log',
            #  'federatedcatalogues': 'http://geo.data.gov/geoportal/csw/discovery',
            #  'pretty_print': 'true',
            #  'domainquerytype': 'range',
            'domaincounts':
            'true',
            'profiles':
            'apiso',
        },
        'repository': {
            'source': 'catalog.repo.Repository',
            'mappings': os.path.join(
                os.path.dirname(__file__), 'repo/mappings.py')
        },
    }

    if csw_config_main:
        config.update({'metadata:main': csw_config_main})
    if csw_config_inspire:
        config.update({'metadata:inspire': csw_config_inspire})

    return config


def get_csw_env(request):
    return request.META


class DirectCsw(Csw):
    def __init__(self, request):
        super().__init__(
            get_csw_config(request), get_csw_env(request), version='2.0.2')

    def direct_dispatch_get_all(self, request):
        self.requesttype = 'GET'
        self.kvp = {
            'service': 'CSW',
            'version': '2.0.2',
            'request': 'GetRecords',
            'elementsetname': 'full',
            'typenames': 'gmd:MD_Metadata',
            'resulttype': 'results',
            # 'constraintlanguage': 'CQL_TEXT',
            # 'constraint': None,
            'outputschema': 'http://www.isotc211.org/2005/gmd',
            'startposition': 1,
            'maxrecords': 10
        }
        # return self.getrecords()
        return self.dispatch()[1]

    def direct_dispatch_get_id(self, request, id):
        self.requesttype = 'GET'
        self.kvp = {
            'service': 'CSW',
            'version': '2.0.2',
            'request': 'GetRecordById',
            'id': id,
            'outputschema': 'http://www.isotc211.org/2005/gmd',
        }
        # return self.getrecordbyid()
        return self.dispatch()[1]


def get_records(request):
    node = DirectCsw(request).direct_dispatch_get_all(request)
    return HttpResponse(node)


def get_record_by_id(request, id):
    node = DirectCsw(request).direct_dispatch_get_id(request, id)
    # return HttpResponse(etree.tostring(node, pretty_print=True))
    return HttpResponse(node)


@csrf_exempt
def get_csw(request):
    csw = Csw(get_csw_config(request), request.environ, version='2.0.2')
    http_status_code, response = csw.dispatch_wsgi()
    # print(response)
    return HttpResponse(response, content_type=csw.contenttype)