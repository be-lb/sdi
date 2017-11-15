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

from rest_framework import serializers

from ..models import Alias
from ..models.message import message
from .message import MessageRecordSerializer


class AliasSerializer(serializers.ModelSerializer):

    replace = MessageRecordSerializer()

    class Meta:
        model = Alias
        fields = ('id', 'select', 'replace')


    def create(self, validated_data):
        select_data = validated_data.pop('select')
        replace_data = validated_data.pop('replace')

        replace = message(**replace_data)
        
        return Alias.objects.create(
            select=select_data,
            replace=replace
        )

    def update(self, i, validated_data):
        select_data = validated_data.pop('select')
        replace_data = validated_data.pop('replace')
        print('alias update {}'.format(type(replace_data)))
        i.replace.update_record(**replace_data)
        i.select = select_data

        return i

