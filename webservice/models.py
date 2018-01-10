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

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField

from api.models.message import message_field



class Service(models.Model):
    WMS = 'wms'
    TMS = 'tms'
    SERVICE_CHOICES = (
        (WMS, 'Web Map Service'),
        (TMS, 'Tile Map Service'),
    )

    id = models.CharField(max_length=126, primary_key=True)
    provider = models.URLField()
    version = models.CharField(max_length=6)
    service = models.CharField(
        max_length=6,
        choices=SERVICE_CHOICES)

    def __str__(self):
        return '{} <{}> ({})'.format(self.id, self.provider, self.service)


class WmsLayer(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=126)
    display_name = message_field('wms_layer_name')
    layers = message_field('wms_layer_layers')
    crs = models.CharField(max_length=64)
    styles = models.CharField(max_length=1024)

    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE,
        related_name='wms_layers',
        )


    def __str__(self):
        return '{} [{}]'.format(self.name, self.layers)
