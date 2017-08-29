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
