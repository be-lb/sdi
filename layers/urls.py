from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(.+)/(.+)/$', views.layer),
    url(r'^(.+)/$', views.list_layers),
]
