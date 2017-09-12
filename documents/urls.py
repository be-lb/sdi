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

from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^documents/$',
        views.upload_document,
        name='document-upload',
    ),
    url(
        r'^images/$',
        views.upload_image,
        name='image-upload'
    ),
    url(
        r'^documents/(.+)$',
        views.get_document,
        name='document-get',
    ),
    url(
        r'^images/(.+)$',
        views.get_image,
        name='image-get'
    ),
]
