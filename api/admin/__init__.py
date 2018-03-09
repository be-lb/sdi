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

from django.contrib.admin import site, ModelAdmin, SimpleListFilter

from ..models import *

from .layer_info import LayerInfoAdmin
from .permission_group import PermissionGroupAdmin
from .metadata import MetadataAdmin
from .user_map import UserMapAdmin
from .alias import AliasAdmin
from .attachment import AttachmentAdmin

site.register(Alias, AliasAdmin)
site.register(Attachment, AttachmentAdmin)
site.register(LayerGroup)
site.register(LayerInfo, LayerInfoAdmin)
site.register(MetaData, MetadataAdmin)
site.register(Organisation)
site.register(PermissionGroup, PermissionGroupAdmin)
# site.register(PointOfContact)
# site.register(ResponsibleOrganisation)
# site.register(Role)
# site.register(Thesaurus)
# site.register(Topic)
site.register(UserMap, UserMapAdmin)

# site.register(BaseLayer)
# site.register(BoundingBox)
# site.register(Category)
# site.register(Keyword)
# site.register(MessageRecord)