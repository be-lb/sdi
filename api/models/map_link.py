#  Copyright (C) 2019 Atelier Cartographique <contact@atelier-cartographique.be>
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

from django.db import models


class MapLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    source = models.ForeignKey(
        'api.UserMap', on_delete=models.CASCADE, related_name='link_source')
    target = models.ForeignKey(
        'api.UserMap', on_delete=models.CASCADE, related_name='link_target')

    def __str__(self):
        return '{} -> {}'.format(self.source, self.target)

    @classmethod
    def siblings(cls, map_id):
        source = cls.objects.filter(source=map_id)
        target = cls.objects.filter(target=map_id)

        return dict(
            source=[s.id for s in source],
            target=[t.id for t in target],
        )
