from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^api/metadata/sync/$',
        views.api_metadata_sync,
        name='manage.api_metadata_sync'),
]