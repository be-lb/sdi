
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

import uuid
import json
from datetime import datetime

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User

from .message import MessageRecord, message
from .metadata import MetaData


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.ForeignKey(
        MessageRecord,
        on_delete=models.PROTECT,
        related_name='category_name',
    )

    def __str__(self):
        return str(self.name)


class LayerInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metadata = models.ForeignKey(
        MetaData,
        on_delete=models.PROTECT,
        related_name='layer_info_md',
    )
    visible = models.BooleanField()
    style = JSONField()
    feature_view_options = JSONField()

    def update(self, data):
        self.metadata = data.pop('metadata')
                                 # DRF gives us a plain MetaData Model, weird
        self.visible = data.pop('visible')
        self.style = data.pop('style')
        self.feature_view_options = data.pop('feature_view_options')
        self.save()

    def __str__(self):
        return str(self.metadata.title)


class BaseLayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.ForeignKey(
        MessageRecord,
        on_delete=models.PROTECT,
        related_name='base_layer_name',
    )
    srs = models.TextField()
    params = JSONField()
    url = models.ForeignKey(
        MessageRecord,
        on_delete=models.PROTECT,
        related_name='base_layer_url',
    )

    def __str__(self):
        return str(self.name)


def get_default_base_layer():
    base = BaseLayer.objects.first()
    if not base:
        default_base_dict = settings.DEFAULT_BASE_LAYER
        name = message(**default_base_dict['name'])
        url = message(**default_base_dict['url'])
        return BaseLayer.objects.create(
            name=name,
            srs=default_base_dict['srs'],
            params=default_base_dict['params'],
            url=url,
        )
    return base


class UserMapManager(models.Manager):

    def create_map(self, user, title_data, description_data, image_url=None):
        instance = UserMap(
            user=user,
            title=message(**title_data),
            description=message(**description_data),
            image_url=image_url,
            base_layer=get_default_base_layer(),
        )
        instance.save()
        return instance


class UserMap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_modified = models.DateTimeField(default=datetime.now, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='maps',
        default=0,
        editable=False,
    )
    title = models.ForeignKey(
        MessageRecord,
        on_delete=models.PROTECT,
        related_name='map_title',
        null=True,
        blank=True,
    )
    description = models.ForeignKey(
        MessageRecord,
        on_delete=models.PROTECT,
        related_name='map_description',
    )
    image_url = models.URLField(
        null=True,
        blank=True,
    )
    categories = models.ManyToManyField(
        Category,
        through='CategoryLink'
    )
    layers = models.ManyToManyField(
        LayerInfo,
        through='LayerLink'
    )
    base_layer = models.ForeignKey(
        BaseLayer,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    objects = UserMapManager()

    def update_title(self, data):
        self.title.update_record(**data)

    def update_description(self, data):
        self.description.update_record(**data)

    def update_image(self, image_url=None):
        self.image_url = image_url
        self.save()

    def update_categories(self, data=[]):
        self.categories.clear()
        for cat in data:
            # cat = Category.objects.get(id=cat_id)
            CategoryLink.objects.create(
                category=cat,
                user_map=self,
            )

    def update_layers(self, layers=[]):
        self.layers.clear()
        for idx, layer_data in enumerate(layers):
            try:
                lid = layer_data.pop('id')
                layer = LayerInfo.objects.get(id=lid)
                layer.update(layer_data)
                LayerLink.objects.create(
                    layer=layer,
                    user_map=self,
                    sort_index=idx,
                )
            except Exception as e:
                print('Failed to Link Layer {}'.format(e))
                print('{}'.format(layer_data))

    def __str__(self):
        return str(self.title)


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.ForeignKey(
        MessageRecord,
        on_delete=models.PROTECT,
        related_name='attachment_name',
    )
    url = models.ForeignKey(
        MessageRecord,
        on_delete=models.PROTECT,
        related_name='attachment_url',
    )
    user_map = models.ForeignKey(
        UserMap,
        on_delete=models.CASCADE,
        related_name='attachment_user_map',
    )

    def __str__(self):
        return str(self.name)


class LayerLink(models.Model):
    layer = models.ForeignKey(
        LayerInfo,
        on_delete=models.CASCADE,
        related_name='user_map_layer',
    )
    user_map = models.ForeignKey(
        UserMap,
        on_delete=models.CASCADE,
        related_name='layer_user_map',
    )
    sort_index = models.IntegerField()


class CategoryLink(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='user_map_category',
    )
    user_map = models.ForeignKey(
        UserMap,
        on_delete=models.CASCADE,
        related_name='category_user_map',
    )
