from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^bundle/(?P<app_name>.+)$',
        views.app, name='clients.bundle'),
    url(r'^assets/(?P<app_name>.+)/(?P<path>.*)$',
        views.style, name='clients.assets'),
    url(r'^(?P<app_name>.+)/(?P<path>.*)$',
        views.app_index, name='clients.root'),
    url(r'^$', views.index, name='clients.index'),
]
