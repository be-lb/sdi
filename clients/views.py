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

import mimetypes
import os
import posixpath
import stat
from collections import namedtuple
import json

from django.shortcuts import render
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.http import (
    FileResponse,
    Http404,
    HttpResponse, )
from django.urls import reverse
from django.middleware.csrf import get_token

from django.utils.six.moves.urllib.parse import unquote
from django.views import static
from django.utils._os import safe_join

Resource = namedtuple('Resource', ['mtime', 'data'])
Client = namedtuple('Client', ['name', 'icon'])
BUNDLE_CACHE = dict()
ICON_CACHE = dict()

configured_clients = dict()
for url, client_root in settings.CLIENTS.items():
    manifest_path = safe_join(client_root, 'manifest.json')
    with open(manifest_path) as f:
        manifest = json.load(f)
        configured_clients[url] = {
            'name': manifest['name'],
            'root': safe_join(client_root, manifest['root'])
        }


def export_manifest():
    result = []
    for codename, manifest in configured_clients.items():
        url = reverse('clients.root', args=(codename, ''))
        name = manifest['name']
        result.append(dict(url=url, name=name))

    return result


def update_resource(fullpath, mtime, cache):
    with open(fullpath, 'rb') as f:
        data = f.read()
        cache[fullpath] = Resource(mtime, data)
        print('******************************\nResource Update [{}] [{}] '.
              format(
                  fullpath,
                  mtime, ))


def get_resource(fullpath, cache):
    statobj = os.stat(fullpath)
    mtime = statobj.st_mtime
    if fullpath in cache:
        if mtime != cache[fullpath]:
            update_resource(fullpath, mtime, cache)
    else:
        update_resource(fullpath, mtime, cache)

    return cache[fullpath].data


def render_index(request, app_name, path):
    user_id = ''
    if request.user.is_authenticated():
        user_id = request.user.id

    return render(
        request,
        'clients/app_index.html',
        context=dict(
            app_name=app_name,
            bundle_url=reverse(
                'clients.bundle', args=(app_name, path)),
            style_url=reverse(
                'clients.assets', args=(app_name, 'style.css')), ))


def render_bundle(request, path, fullpath):
    user_id = ''
    if request.user.is_authenticated():
        user_id = request.user.id

    return render(
        request,
        'clients/bundle.js',
        context=dict(
            root=reverse('clients.index'),
            path=path,
            apps=export_manifest(),
            bundle=get_resource(fullpath, BUNDLE_CACHE),
            user_id=user_id,
            api=reverse('api-root'),
            csrf_token=get_token(request), ))


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
    if app_name not in configured_clients:
        raise Http404('{} not configured'.format(app_name))
    normalized_path = unquote(path).lstrip('/')
    if not normalized_path:
        return render_index(request, app_name, path)
    return render_index(request, app_name, normalized_path)


def app(request, app_name, path):
    if app_name not in configured_clients:
        raise Http404('{} not configured'.format(app_name))
    client_root = configured_clients[app_name]['root']
    fullpath = safe_join(client_root, 'bundle.js')

    return render_bundle(request, path, fullpath)


def style(request, app_name, path):
    if app_name not in configured_clients:
        raise Http404('{} not configured'.format(app_name))
    client_root = configured_clients[app_name]['root']
    normalized_path = unquote(path).lstrip('/')
    fullpath = safe_join(client_root, normalized_path)

    return serve_static(fullpath)


def index(request):
    if 'default' in configured_clients:
        return app_index(request, 'default', '')

    clients = []
    for name, client_root in settings.CLIENTS.items():
        icon_path = safe_join(client_root, 'icon.svg')
        icon = None
        try:
            icon = get_resource(icon_path, ICON_CACHE)
        except Exception:
            icon = render_to_string('clients/icon.svg', {'name': name},
                                    request)

        clients.append(Client(name, icon))

    return render(request, 'clients/index.html', context=dict(clients=clients))
