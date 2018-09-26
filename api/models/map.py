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

import uuid
from datetime import datetime

from django.conf import settings
from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import User, Group

from .message import MessageRecord, message, message_field
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


class LayerGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = message_field('layergroup_name')

    def update(self, data):
        self.name.update_record(**data)

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
    group = models.ForeignKey(
        LayerGroup,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    legend = models.ForeignKey(
        MessageRecord,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    min_zoom = models.PositiveIntegerField(default=0, null=True, blank=True)
    max_zoom = models.PositiveIntegerField(default=30, null=True, blank=True)

    def update(self, data):
        self.metadata = data.pop('metadata')
        # DRF gives us a plain MetaData Model, weird
        self.visible = data.pop('visible')
        self.style = data.pop('style')
        self.feature_view_options = data.pop('feature_view_options')
        self.min_zoom = data.pop('min_zoom', 0)
        self.max_zoom = data.pop('max_zoom', 30)
        legend = data.pop('legend', None)
        if legend is not None:
            if self.legend is not None:
                self.legend.update_record(**legend)
            else:
                self.legend = message(**legend)

        self.save()

    def __str__(self):
        m = self.usermap_set.first()
        if m is not None:
            return '{} # {}'.format(str(m.title), str(self.metadata.title))
        return 'None # {}'.format(str(self.metadata.title))


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
        srs = default_base_dict['srs']
        params = default_base_dict['params']
        return BaseLayer.objects.create(
            name=name,
            srs=srs,
            params=params,
            url=url,
        )
    return base


class UserMapManager(models.Manager):
    def create_map(self,
                   user,
                   title_data,
                   description_data,
                   base_layer,
                   image_url=None):
        instance = UserMap(
            user=user,
            title=message(**title_data),
            description=message(**description_data),
            image_url=image_url,
            base_layer=base_layer,
        )
        instance.save()
        return instance


class UserMap(models.Model):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    STATUS_CHOICES = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False)
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default=DRAFT,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='maps',
        default=0,
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
    image_url = models.CharField(
        max_length=512,
        null=True,
        blank=True,
    )
    categories = models.ManyToManyField(Category, through='CategoryLink')
    layers = models.ManyToManyField(LayerInfo, through='LayerLink')
    base_layer = models.CharField(max_length=256)

    objects = UserMapManager()

    class Meta:
        ordering = ['-last_modified']

    def update_status(self, status):
        self.status = status  # could be a nice to send notifications

    def update_title(self, data):
        self.title.update_record(**data)

    def update_description(self, data):
        self.description.update_record(**data)

    def update_image(self, image_url=None):
        self.image_url = image_url

    def update_categories(self, data=[]):
        self.categories.clear()
        self.save()
        for cat in data:
            # cat = Category.objects.get(id=cat_id)
            CategoryLink.objects.create(category=cat, user_map=self)

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
                print('Attached Layer {} at index {}'.format(layer, idx))
            except Exception as e:
                print('Failed to Link Layer {}'.format(e))
                print('{}'.format(layer_data))

    def update_base_layer(self, data):
        self.base_layer = data

    def __str__(self):
        return str(self.title)


class AttachmentManager(models.Manager):
    def create_attachment(self, name_data, url_data, user_map):
        instance = Attachment(
            name=message(**name_data),
            url=message(**url_data),
            user_map=user_map)
        instance.save()
        return instance


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

    objects = AttachmentManager()

    def update(self, data):
        self.name.update_record(**data.pop('name'))
        self.url.update_record(**data.pop('url'))

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


class PermissionGroup(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='user_map_permission_group',
    )

    user_map = models.ForeignKey(
        UserMap,
        on_delete=models.CASCADE,
        related_name='permission_group_user_map',
    )

    def __str__(self):
        return str(self.group.name)