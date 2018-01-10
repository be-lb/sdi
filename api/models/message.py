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

from django.db import models
from django.contrib.postgres.fields import JSONField


class MessageRecord(models.Model):
    fr = models.TextField(blank=True)
    nl = models.TextField(blank=True)
    parameters = JSONField(null=True, blank=True)

    def __str__(self):
        # return 'fr: {}\nnl: {}'.format(self.fr[:32], self.nl[:32])
        return self.fr[:64]

    def update_record(self, fr='', nl='', parameters=None):
        self.fr = fr
        self.nl = nl
        self.parameters = parameters
        self.save()

    def to_dict(self):
        return dict(fr=self.fr, nl=self.nl)


def message_field(name):
    return models.ForeignKey(
        MessageRecord,
        on_delete=models.PROTECT,
        related_name=name,
    )


def message(fr=None, nl=None):
    return MessageRecord.objects.create(fr=fr, nl=nl)


def simple_message(msg):
    return message(fr=msg, nl=msg)
