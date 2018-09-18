# -*- coding: utf-8 -*-
# from https://github.com/yvandermeer/django-http-proxy
#
# License found in setup.py https://github.com/yvandermeer/django-http-proxy/blob/develop/setup.py
# 'License :: OSI Approved :: MIT License'
#
# Authors in https://github.com/yvandermeer/django-http-proxy/blob/develop/AUTHORS
# The Django HTTP Proxy is developed and maintained by Yuri van der Meer.
# Many thanks to Will Larson for providing the inspiration and original source
# code for this app:
# http://lethain.com/entry/2008/sep/30/suffer-less-by-using-django-dev-server-as-a-proxy/
#

import logging
import re

from django.http import HttpResponse
from django.utils.six.moves import urllib
from django.views.generic import View

logger = logging.getLogger(__name__)

REWRITE_REGEX = re.compile(r'((?:src|action|href)=["\'])/(?!\/)')


class HttpProxy(View):
    """
    Class-based view to configure Django HTTP Proxy for a URL pattern.

    In its most basic usage::

            from httpproxy.views import HttpProxy

            urlpatterns += patterns('',
                (r'^my-proxy/(?P<url>.*)$',
                    HttpProxy.as_view(base_url='http://python.org/')),
            )

    Using the above configuration (and assuming your Django project is server by
    the Django development server on port 8000), a request to
    ``http://localhost:8000/my-proxy/index.html`` is proxied to
    ``http://python.org/index.html``.
    """

    base_url = None
    """
    The base URL that the proxy should forward requests to.
    """

    rewrite = False
    """
    If you configure the HttpProxy view on any non-root URL, the proxied
    responses may still contain references to resources as if they were served
    at the root. By setting this attribute to ``True``, the response will be
    :meth:`rewritten <httpproxy.views.HttpProxy.rewrite_response>` to try to
    fix the paths.
    """

    _msg = 'Response body: \n%s'

    def dispatch(self, request, url, *args, **kwargs):
        # print('URL0: {}'.format(url))
        self.url = url
        self.original_request_path = request.path
        request = self.normalize_request(request)

        response = super(HttpProxy, self).dispatch(request, *args, **kwargs)

        if self.rewrite:
            response = self.rewrite_response(request, response)
        return response

    def normalize_request(self, request):
        """
        Updates all path-related info in the original request object with the
        url given to the proxy.

        This way, any further processing of the proxy'd request can just ignore
        the url given to the proxy and use request.path safely instead.
        """
        # if not self.url.startswith('/'):
        #     self.url = '/' + self.url
        request.path = self.url
        request.path_info = self.url
        request.META['PATH_INFO'] = self.url
        return request

    def rewrite_response(self, request, response):
        """
        Rewrites the response to fix references to resources loaded from HTML
        files (images, etc.).

        .. note::
            The rewrite logic uses a fairly simple regular expression to look for
            "src", "href" and "action" attributes with a value starting with "/"
            – your results may vary.
        """
        proxy_root = self.original_request_path.rsplit(request.path, 1)[0]
        response.content = REWRITE_REGEX.sub(r'\1{}/'.format(proxy_root),
                                             response.content)
        return response

    def get(self, *args, **kwargs):
        return self.get_response()

    def post(self, request, *args, **kwargs):
        headers = {}
        if request.META.get('CONTENT_TYPE'):
            headers['Content-type'] = request.META.get('CONTENT_TYPE')
        return self.get_response(body=request.body, headers=headers)

    def get_full_url(self, url):
        """
        Constructs the full URL to be requested.
        """
        param_str = self.request.GET.urlencode()
        request_url = u'%s%s' % (self.base_url, url)
        request_url += '?%s' % param_str if param_str else ''
        return request_url

    def create_request(self, url, body=None, headers={}):
        request = urllib.request.Request(url, body, headers)
        logger.info('%s %s' % (request.get_method(), request.get_full_url()))
        return request

    def get_response(self, body=None, headers={}):
        request_url = self.get_full_url(self.url)
        request = self.create_request(request_url, body=body, headers=headers)
        response = urllib.request.urlopen(request, timeout=12)
        try:
            response_body = response.read()
            status = response.getcode()
            logger.debug(self._msg % response_body)
        except urllib.error.HTTPError as e:
            response_body = e.read()
            logger.error(self._msg % response_body)
            status = e.code
        return HttpResponse(
            response_body,
            status=status,
            content_type=response.headers['content-type'])


class HttpProxyBasicAuth(HttpProxy):
    username = None
    password = None

    def get_response(self, body=None, headers={}):
        # print('URL: {}'.format(self.url))
        request_url = self.get_full_url(self.url)
        request = self.create_request(request_url, body=body, headers=headers)

        passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, request_url, self.username, self.password)
        authhandler = urllib.request.HTTPBasicAuthHandler(passman)
        opener = urllib.request.build_opener(authhandler)

        response = opener.open(request)
        try:
            response_body = response.read()
            status = response.getcode()
            logger.debug(self._msg % response_body)
        except urllib.error.HTTPError as e:
            response_body = e.read()
            logger.error(self._msg % response_body)
            status = e.code
        return HttpResponse(
            response_body,
            status=status,
            content_type=response.headers['content-type'])
