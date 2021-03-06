#
#  Copyright (C) 2017 Atelier Cartographique <contact@atelier-cartographique.be>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import io
import codecs
from json import loads, dump
from django.core.serializers import serialize
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import authenticate, login, logout
from django.core.cache import caches, InvalidCacheBackendError
from rest_framework.decorators import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed, AuthenticationFailed

from .models import (Category, Keyword, LayerInfo, MessageRecord, MetaData,
                     Topic, UserMap, Attachment, Alias, PointOfContact,
                     Organisation, ResponsibleOrganisation, Organisation)
from .serializers import (
    CategorySerializer, KeywordSerializer, LayerInfoSerializer,
    MessageRecordSerializer, MetaDataSerializer, TopicSerializer,
    UserMapSerializer, UserSerializer, AttachmentSerializer, AliasSerializer,
    PointOfContactSerializer, ResponsibleOrgSerializer)

from .serializers.layer import get_serializer, get_model, get_geojson
from .permissions import ViewSetWithPermissions, ViewSetWithPermissionsAndFilter
from .rules import LAYER_VIEW_PERMISSION, SERVICE_VIEW_PERMISSION

from webservice.models import Service

renderer = JSONRenderer()


def render_json(data):
    return renderer.render(data)


def login_view(request):
    if request.method == "POST":
        data = loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        # next = data.get('next', None)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            json_data = UserSerializer(user).data
            return JsonResponse(json_data)
        else:
            raise AuthenticationFailed()

    raise MethodNotAllowed(request.method)


def logout_view(request):
    if request.method == "POST":
        u = request.user
        id = u.id
        logout(request)
        return JsonResponse({
            'logout': 'OK',
            'id': id,
        })
    raise MethodNotAllowed(request.method)


def make_wms_config(service, layer):
    data = dict(
        url=reverse('webservice.wms_proxy', args=[service.id]),
        name=layer.display_name.to_dict(),
        srs=layer.crs,
        params=dict(
            LAYERS=layer.layers.to_dict(),
            STYLES=layer.styles,
            VERSION=service.version,
        ))

    # if service.version == '1.1.1':
    #     data.update(srs=layer.crs)
    # else:
    #     data.update(crs=layer.crs)

    return data


def get_wms_config(request, id, name):
    user = request.user
    service = Service.objects.get(service='wms', id=id)
    if not user.has_perm(SERVICE_VIEW_PERMISSION, service):
        raise PermissionDenied()

    layer = service.wms_layers.get(name=name)
    return JsonResponse(make_wms_config(service, layer))


def get_wms_layers(request):
    user = request.user
    services = Service.objects.filter(service='wms')
    results = dict()

    for service in filter(lambda s: user.has_perm(SERVICE_VIEW_PERMISSION, s),
                          services):
        for layer in service.wms_layers.all():
            key = '{}/{}'.format(service.id, layer.name)
            results[key] = make_wms_config(service, layer)

    return JsonResponse(results)


class UserViewSet(ViewSetWithPermissionsAndFilter):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserMapViewSet(ViewSetWithPermissionsAndFilter):
    """
    API endpoint that allows user maps to be viewed or edited.
    """
    serializer_class = UserMapSerializer

    def get_queryset(self):
        if 'list' == self.action:
            return (UserMap.objects.filter(
                status='published').order_by('-last_modified'))

        return UserMap.objects.all()


class MessageViewSet(ViewSetWithPermissions):
    """
    API endpoint that allows messages to be viewed or edited.
    """
    queryset = MessageRecord.objects.all()
    serializer_class = MessageRecordSerializer


class CategoryViewSet(ViewSetWithPermissions):
    """
    API endpoint that allows user maps to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class LayerInfoViewSet(ViewSetWithPermissions):
    """
    API endpoint that allows user maps to be viewed or edited.
    """
    queryset = LayerInfo.objects.all()
    serializer_class = LayerInfoSerializer


class Pagination(PageNumberPagination):
    page_size = 256 / 4


class MetaDataViewSet(ViewSetWithPermissions):
    """
    API endpoint that allows MetaData to be viewed or edited.
    """

    queryset = MetaData.objects.fetch_bulk().order_by('resource_identifier')
    serializer_class = MetaDataSerializer
    pagination_class = Pagination


class TopicViewSet(ViewSetWithPermissions):

    queryset = Topic.objects.prefetch_related('name', 'thesaurus',
                                              'thesaurus__name')
    serializer_class = TopicSerializer


class KeywordViewSet(ViewSetWithPermissions):

    queryset = Keyword.objects.prefetch_related(
        'name', 'thesaurus', 'thesaurus__name').order_by('thesaurus')
    serializer_class = KeywordSerializer


class AttachmentViewSet(ViewSetWithPermissions):

    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


class LayerViewList(APIView):
    """get a geojson from a table"""

    def get(self, request, schema, table):
        user = request.user
        if not user.has_perm(LAYER_VIEW_PERMISSION, (schema, table)):
            raise PermissionDenied()

        try:
            cache = caches['layers']
            ckey = '{}.{}'.format(schema, table)
            try:
                reader = cache.read(ckey)
                reader_type = type(reader)
                print('ReaderType {} {}'.format(ckey, reader_type))
                if reader_type is io.BufferedReader:
                    return FileResponse(
                        reader, content_type='application/json')
                elif reader_type is dict:
                    return Response(reader)

                response = HttpResponse(
                    reader, content_type='application/json')
                return response

            except KeyError:
                # there's been of juggling to force diskcache
                # to return a BufferedReader from cache.read
                stream = io.BytesIO()
                writer = codecs.getwriter("utf-8")(stream)
                data = get_geojson(schema, table)
                dump(data, writer)
                stream.seek(0)
                cache.set(ckey, stream, read=True)
                return Response(data)

        except InvalidCacheBackendError:
            print('InvalidCacheBackendError')
            return Response(get_geojson(schema, table))


class AliasViewSet(ViewSetWithPermissions):
    """
    API endpoint that allows alias to be viewed or edited.
    """
    queryset = Alias.objects.prefetch_related('replace')
    serializer_class = AliasSerializer
    # pagination_class = Pagination


class PointOfContactViewSet(ViewSetWithPermissions):
    """
    API endpoint that allows point of contact to be viewed.
    """
    queryset = PointOfContact.objects.select_related('organisation')
    serializer_class = PointOfContactSerializer


class ResponsibleOrganisationViewSet(ViewSetWithPermissions):
    """
    API endpoint that allows organisation to be viewed.
    """
    queryset = ResponsibleOrganisation.objects
    serializer_class = ResponsibleOrgSerializer