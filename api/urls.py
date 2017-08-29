from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'maps', views.UserMapViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'layerinfos', views.LayerInfoViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'metadatas', views.MetaDataViewSet)

# for u in router.urls:
#     print(u)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^layers/(?P<schema>.+)/(?P<table>.+)/$',
        views.LayerViewList.as_view(), name='layers_list'),
    # url(r'^auth/', include('rest_framework.urls',
    # namespace='rest_framework'))
]
