#########################################################################
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
#########################################################################

from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import generics

from .models import UserMap, MessageRecord, Category, LayerInfo, MetaData
from .serializers import (
    UserMapSerializer, MessageRecordSerializer, CategorySerializer,
    LayerInfoSerializer, UserSerializer, MetaDataSerializer
)

from .serializers.layer import get_serializer, get_model


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
    queryset = UserMap.objects.all().order_by('-last_modified')
    serializer_class = UserMapSerializer


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


class MetaDataViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows MetaData to be viewed or edited.
    """
    queryset = MetaData.objects.all()
    serializer_class = MetaDataSerializer


class LayerViewList(generics.ListCreateAPIView):

    def get_queryset(self):
        schema = self.kwargs.get('schema')
        table = self.kwargs.get('table')
        model = get_model(schema, table)

        return model.objects.using(schema).all()

    def get_serializer_class(self):
        schema = self.kwargs.get('schema')
        table = self.kwargs.get('table')

        return get_serializer(schema, table)
