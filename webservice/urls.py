from django.conf.urls import url, include

from . import views

def name(n):
    return 'webservice.{}'.format(n)

urlpatterns = [
    # url(r'^wmsconfig/(?P<id>.+)/(?P<name>.+)$', 
    #     views.get_wms_config, 
    #     name=name('wms_config')),
    
    url(r'^wmsproxy/(?P<id>.+)$', 
        views.proxy_wms_request, 
        name=name('wms_proxy')),
]