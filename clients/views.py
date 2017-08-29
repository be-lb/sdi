
import mimetypes
import os
import posixpath
import stat

from django.shortcuts import render
from django.conf import settings
from django.http import (
    FileResponse, Http404, HttpResponse,
)
from django.urls import reverse
from django.middleware.csrf import get_token

from django.utils.six.moves.urllib.parse import unquote
from django.views import static
from django.utils._os import safe_join


def render_index(request, app_name, path):
    user_id = ''
    if request.user.is_authenticated():
        user_id = request.user.id

    return render(request, 'clients/app_index.html', context=dict(
        app_name=app_name,
        path=path,
        user_id=request.user.id,
        bundle_url=reverse('clients.bundle', args=(app_name,)),
        assets_root=reverse('clients.assets', args=(app_name, path,)),
        api=reverse('api-root'),
        csrf_token=get_token(request),
    ))


def serve_static(fullpath):
    print('serve_static({})'.format(fullpath))
    if os.path.isdir(fullpath):
        raise Http404(
            "Directory indexes are not allowed here. [{}]".format(fullpath))
    if not os.path.exists(fullpath):
        raise Http404('"%(path)s" does not exist' % {'path': fullpath})

    statobj = os.stat(fullpath)
    content_type, encoding = mimetypes.guess_type(fullpath)
    content_type = content_type or 'application/octet-stream'
    response = FileResponse(open(fullpath, 'rb'), content_type=content_type)

    if stat.S_ISREG(statobj.st_mode):
        response["Content-Length"] = statobj.st_size
    if encoding:
        response["Content-Encoding"] = encoding
    return response


def app_index(request, app_name, path):
    if app_name not in settings.CLIENTS:
        raise Http404('{} not configured'.format(app_name))
    normalized_path = unquote(path).lstrip('/')
    if not normalized_path:
        return render_index(request, app_name, path)


def app(request, app_name):
    if app_name not in settings.CLIENTS:
        raise Http404('{} not configured'.format(app_name))
    client_root = settings.CLIENTS[app_name]
    fullpath = safe_join(client_root, 'bundle.js')

    return serve_static(fullpath)


def style(request, app_name, path):
    if app_name not in settings.CLIENTS:
        raise Http404('{} not configured'.format(app_name))
    client_root = settings.CLIENTS[app_name]
    normalized_path = unquote(path).lstrip('/')
    fullpath = safe_join(client_root, normalized_path)

    return serve_static(fullpath)


def index(request):
    return render(request, 'clients/index.html', context=dict(
                  clients=settings.CLIENTS
                  ))
