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
from json import loads
from django.core.serializers import serialize
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from rest_framework.decorators import APIView
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination

from .models import (Category, Keyword, LayerInfo, MessageRecord, MetaData,
                     Topic, UserMap, Attachment, Alias)
from .serializers import (
    CategorySerializer, KeywordSerializer, LayerInfoSerializer,
    MessageRecordSerializer, MetaDataSerializer, TopicSerializer,
    UserMapSerializer, UserSerializer, AttachmentSerializer, AliasSerializer)

from .serializers.layer import get_serializer, get_model, get_geojson


def login_view(request):
    if request.method == "POST":
        data = loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        # next = data.get('next', None)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            json_data = JSONRenderer().render(UserSerializer(user).data)
            # if next:
            #     next_comps = next.split('/')
            #     next_app = next_comps[0]
            #     next_path = '/'.join(next_comps[1:])
            #     next_url = reverse('clients.root', args=(next_app, next_path))
            #     return HttpResponseRedirect(next_url)
            return HttpResponse(json_data)
        else:
            return HttpResponseBadRequest('Authentication Failed')

    return HttpResponseBadRequest('Wrong Verb')


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return HttpResponse(JSONRenderer().render('logout'))
    return HttpResponseBadRequest('Wrong Verb')


class UserViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserMapViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows user maps to be viewed or edited.
    """

    serializer_class = UserMapSerializer

    def get_queryset(self):
        if 'list' == self.action:
            return (
                UserMap.objects.filter(
                    status='published'
                    ).order_by(
                    '-last_modified'
                    )
                )

        return UserMap.objects.all()


class MessageViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows user maps to be viewed or edited.
    """
    queryset = MessageRecord.objects.all()
    serializer_class = MessageRecordSerializer


class CategoryViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows user maps to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class LayerInfoViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows user maps to be viewed or edited.
    """
    queryset = LayerInfo.objects.all()
    serializer_class = LayerInfoSerializer


class Pagination(PageNumberPagination):
    page_size = 120


class MetaDataViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows MetaData to be viewed or edited.
    """

    queryset = MetaData.objects.select_related(
        'title', 'abstract', 'bounding_box').prefetch_related(
        'topics', 'keywords', 'responsible_organisation',
        'point_of_contact', 'point_of_contact__user',
        'responsible_organisation__name', 'point_of_contact__organisation',
        'point_of_contact__organisation__name')
    serializer_class = MetaDataSerializer
    pagination_class = Pagination

    # def list(self, request, *args, **kwargs):
    #     def get_data():
    #         queryset = self.filter_queryset(self.get_queryset())

    #         page = self.paginate_queryset(queryset)
    #         if page is not None:
    #             serializer = self.get_serializer(page, many=True)
    #             return serializer.data

    #         serializer = self.get_serializer(queryset, many=True)
    #         serializer.data

    #     data = cache.get_or_set( request.path, get_data, 3600 * 24)
    #     return Response(data)


class TopicViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Topic.objects.prefetch_related('name', 'thesaurus',
                                              'thesaurus__name')
    serializer_class = TopicSerializer


class KeywordViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Keyword.objects.prefetch_related(
        'name', 'thesaurus', 'thesaurus__name').order_by('thesaurus')
    serializer_class = KeywordSerializer


class AttachmentViewSet(viewsets.ModelViewSet):

    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


class LayerViewList(APIView):
    """get a geojson from a table"""
    def get(self, request, schema, table):
        ckey = '{}.{}'.format(schema, table)
        data = cache.get(ckey)
        if data is None:
            data = cache.get_or_set(ckey , get_geojson(schema, table) , 3600)
        
        return Response(data)




# layer_qs_cache = dict()


# class LayerViewList(generics.ListAPIView):

#     def get_queryset(self):
#         schema = self.kwargs.get('schema')
#         table = self.kwargs.get('table')
#         key = '{}/{}'.format(schema, table)
#         if key not in layer_qs_cache:
#             model = get_model(schema, table)
#             layer_qs_cache[key] = model.objects.all()

#         return layer_qs_cache[key]

    # def get_serializer_class(self):
    #     schema = self.kwargs.get('schema')
    #     table = self.kwargs.get('table')

    #     return get_serializer(schema, table)

# LC = dict()

# class LayerViewList(generics.ListAPIView):

#     def list(self, request, *args, **kwargs):
#         schema = self.kwargs.get('schema')
#         table = self.kwargs.get('table')
#         key = '{}/{}'.format(schema, table)
#         if key not in LC:
#             model = get_model(schema, table)
#             ser = get_serializer(schema, table)()
#             features = []
#             for row in model.objects.all().iterator():
#                 features.append(ser.to_representation(row))
#             LC[key] = dict(
#                 type='FeatureCollection',
#                 features=features
#             )

#         return JsonResponse(LC[key])

#     def get_serializer_class(self):
#         schema = self.kwargs.get('schema')
#         table = self.kwargs.get('table')

#         return get_serializer(schema, table)


class AliasViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows alias to be viewed or edited.
    """
    queryset = Alias.objects.prefetch_related('replace')
    serializer_class = AliasSerializer
    # pagination_class = Pagination
