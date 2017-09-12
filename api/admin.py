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

from django.contrib import admin

from .models import *

admin.site.register(Attachment)
admin.site.register(BaseLayer)
admin.site.register(BoundingBox)
admin.site.register(Category)
admin.site.register(Keyword)
admin.site.register(LayerInfo)
admin.site.register(MessageRecord)
admin.site.register(MetaData)
admin.site.register(Organisation)
admin.site.register(PointOfContact)
admin.site.register(ResponsibleOrganisation)
admin.site.register(Role)
admin.site.register(Thesaurus)
admin.site.register(Topic)
admin.site.register(UserMap)
