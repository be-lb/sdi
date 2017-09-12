
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

import mimetypes
import os
import posixpath
import stat
from collections import namedtuple

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


Bundle = namedtuple('Bundle', ['mtime', 'data'])
BUNDLE_CACHE = dict()


def update_bundle(fullpath, mtime):
    with open(fullpath, 'rb') as f:
        data = f.read()
        BUNDLE_CACHE[fullpath] = Bundle(mtime, data)
        print('******************************\nBundle update [{}] [{}] '.format(
            fullpath,
            mtime,
        ))


def get_bundle(fullpath):
    statobj = os.stat(fullpath)
    mtime = statobj.st_mtime
    if fullpath in BUNDLE_CACHE:
        if mtime != BUNDLE_CACHE[fullpath]:
            update_bundle(fullpath, mtime)
    else:
        update_bundle(fullpath, mtime)

    return BUNDLE_CACHE[fullpath].data


def render_index(request, app_name, path):
    user_id = ''
    if request.user.is_authenticated():
        user_id = request.user.id

    return render(request, 'clients/app_index.html', context=dict(
        app_name=app_name,
        bundle_url=reverse('clients.bundle', args=(app_name, path)),
        style_url=reverse('clients.assets', args=(app_name, 'style.css')),
    ))


def render_bundle(request, path, fullpath):
    user_id = ''
    if request.user.is_authenticated():
        user_id = request.user.id

    return render(request, 'clients/bundle.js', context=dict(
        path=path,
        bundle=get_bundle(fullpath),
        user_id=request.user.id,
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
    return render_index(request, app_name, normalized_path)


def app(request, app_name, path):
    if app_name not in settings.CLIENTS:
        raise Http404('{} not configured'.format(app_name))
    client_root = settings.CLIENTS[app_name]
    fullpath = safe_join(client_root, 'bundle.js')

    return render_bundle(request, path, fullpath)


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
