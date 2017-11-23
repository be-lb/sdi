import os

from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from pycsw.server import Csw
from lxml import etree


def get_csw_config(request):
    return {
        'server': {
            'home': '.',
            'url': '{}://{}{}'.format(request.scheme, request.get_host(),reverse('catalog')),
            'encoding': 'UTF-8',
            'language': 'en',
            'maxrecords': '10',
            'loglevel': 'DEBUG',
            'logfile': '/tmp/pycsw.log',
            #  'federatedcatalogues': 'http://geo.data.gov/geoportal/csw/discovery',
            #  'pretty_print': 'true',
            #  'domainquerytype': 'range',
            'domaincounts': 'true',
            'profiles': 'apiso',
        },
        'repository': {
            'source': 'catalog.repo.Repository',
            'mappings': os.path.join(os.path.dirname(__file__), 'repo/mappings.py')
        },
        'metadata:main': {
            'identification_title': 'GeoNode Catalogue',
            'identification_abstract': 'GeoNode is an open source platform'
            ' that facilitates the creation, sharing, and collaborative use'
            ' of geospatial data',
            'identification_keywords': 'sdi, catalogue, discovery, metadata,'
            ' GeoNode',
            'identification_keywords_type': 'theme',
            'identification_fees': 'None',
            'identification_accessconstraints': 'None',
            'provider_name': 'Organization Name',
            'provider_url': 'http://example.com',
            'contact_name': 'Lastname, Firstname',
            'contact_position': 'Position Title',
            'contact_address': 'Mailing Address',
            'contact_city': 'City',
            'contact_stateorprovince': 'Administrative Area',
            'contact_postalcode': 'Zip or Postal Code',
            'contact_country': 'Country',
            'contact_phone': '+xx-xxx-xxx-xxxx',
            'contact_fax': '+xx-xxx-xxx-xxxx',
            'contact_email': 'Email Address',
            'contact_url': 'Contact URL',
            'contact_hours': 'Hours of Service',
            'contact_instructions': 'During hours of service. Off on '
            'weekends.',
            'contact_role': 'pointOfContact',
        },
        'metadata:inspire': {
            'enabled': 'true',
            'languages_supported': 'eng,gre',
            'default_language': 'eng',
            'date': 'YYYY-MM-DD',
            'gemet_keywords': 'Utility and governmental services',
            'conformity_service': 'notEvaluated',
            'contact_name': 'Organization Name',
            'contact_email': 'Email Address',
            'temp_extent': 'YYYY-MM-DD/YYYY-MM-DD',
        }
    }


def get_csw_env(request):
    return request.META


class DirectCsw(Csw):

    def __init__(self, request):
        super().__init__(get_csw_config(request),
                         get_csw_env(request), version='2.0.2')

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
    print(response)
    return HttpResponse(response, content_type=csw.contenttype)