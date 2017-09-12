
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
from rest_framework import serializers

from ..models import MessageRecord


class UserSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    maps = serializers.PrimaryKeyRelatedField(
        required=False, many=True, read_only=True
    )
    layers = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'maps', 'layers', 'roles')

    def get_id(self, instance):
        return str(instance.id)

    def get_name(self, instance):
        return instance.get_full_name()

    def get_layers(self, instance):
        return []

    def get_roles(self, instance):
        roles = []
        for g in instance.groups.all():
            roles.append(dict(
                id=str(g.id),
                label=dict(fr=g.name, nl=g.name)
            ))
        return roles
