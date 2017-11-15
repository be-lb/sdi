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

from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'maps', views.UserMapViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'layerinfos', views.LayerInfoViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'keywords', views.KeywordViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'metadatas', views.MetaDataViewSet)
router.register(r'attachments', views.AttachmentViewSet)
router.register(r'alias', views.AliasViewSet)

# for u in router.urls:
#     print(u)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^layers/(?P<schema>.+)/(?P<table>.+)/$',
        views.LayerViewList.as_view(),
        name='layers_list'),
    url(r'^auth/login', views.login_view, name='api.login'),
    url(r'^auth/logout', views.logout_view, name='api.logout'),
    # url(r'^auth/', include('rest_framework.urls',
    #                        namespace='rest_framework'))
]
