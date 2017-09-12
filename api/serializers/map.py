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

import math
import json
from django.urls import reverse
from rest_framework import serializers

from ..models import (
    BaseLayer,
    Category,
    LayerInfo,
    MessageRecord,
    MetaData,
    UserMap,
)
from .message import MessageRecordSerializer
from collections import OrderedDict


class NonNullModelSerializer(serializers.Serializer):

    def to_representation(self, instance):
        result = super(
            NonNullModelSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class CategorySerializer(serializers.ModelSerializer):
    # name = MessageRecordSerializer()

    class Meta:
        model = Category
        fields = ('id', 'name')


class BaseLayerSerializer(serializers.ModelSerializer):
    name = MessageRecordSerializer()
    url = MessageRecordSerializer()

    class Meta:
        model = BaseLayer
        fields = ('id', 'name', 'srs', 'params', 'url')


class LayerInfoSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    metadataId = serializers.PrimaryKeyRelatedField(
        source='metadata',
        queryset=MetaData.objects,
        pk_field=serializers.UUIDField(format='hex_verbose'),
    )
    visible = serializers.BooleanField()
    style = serializers.JSONField()
    featureViewOptions = serializers.JSONField(source='feature_view_options')

    class Meta:
        model = LayerInfo
        fields = ('id', 'metadataId', 'visible', 'style', 'featureViewOptions')


class AttachmentSerializer(serializers.Serializer):
    name = MessageRecordSerializer()
    url = MessageRecordSerializer()


class UserMapSerializer(NonNullModelSerializer):
    id = serializers.UUIDField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    lastModified = serializers.SerializerMethodField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    title = MessageRecordSerializer()
    description = MessageRecordSerializer()
    baseLayer = BaseLayerSerializer(source='base_layer')
    imageUrl = serializers.CharField(
        source='image_url',
        required=False,
        max_length=1024,
    )
    # imageUrl = serializers.SerializerMethodField(
    #     method_name='get_image_url',
    #     required=False,
    # )

    categories = serializers.PrimaryKeyRelatedField(
        required=False, many=True,
        pk_field=serializers.UUIDField(format='hex_verbose'),
        queryset=Category.objects
    )

    attachments = AttachmentSerializer(many=True, default=[])
    layers = LayerInfoSerializer(many=True, default=[])

    def get_lastModified(self, instance):
        d = instance.last_modified
        return math.floor(d.timestamp() * 1000)

    def get_url(self, instance):
        return reverse('usermap-detail', args=[instance.id])

    # def get_image_url(sel, instance):
    #     url = instance.image_url
    #     print('get_image_url {}'.format(url))
    #     if url:
    #         return url
    #     return None

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        title_data = validated_data.pop('title')
        description_data = validated_data.pop('description')
        image_url = validated_data.get('image_url')
        return UserMap.objects.create_map(
            user,
            title_data,
            description_data,
            image_url,
        )

    def update(self, instance, validated_data):
        # raise Exception('WTF {}'.format(validated_data))
        title_data = validated_data.get('title')
        description_data = validated_data.get('description')
        image_url = validated_data.get('image_url')
        categories = validated_data.get('categories', [])
        layers = validated_data.get('layers', [])

        instance.update_title(title_data)
        instance.update_description(description_data)
        instance.update_image(image_url)
        instance.update_categories(categories)
        instance.update_layers(layers)

        return instance
