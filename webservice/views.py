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

from django.http import HttpResponseBadRequest, JsonResponse, FileResponse
from django.urls import reverse

from .proxy import HttpProxy
from .models import Service




# def get_wms_config(request, id, name):
#     service = Service.objects.get(service='wms', id=id)
#     layer = service.wms_layers.get(name=name)
    
#     data = dict(
#         url=reverse('webservice.wms_proxy', args=[service.id]),
#         name=layer.display_name.to_dict(),
#         params=dict(
#             layers=layer.layers.to_dict(),
#             styles=layer.styles,
#             version=service.version,
#         )
#     )

#     return JsonResponse(data)

def proxy_wms_request(request, id):
    service = Service.objects.get(id=id)
    proxy = HttpProxy.as_view(base_url=service.provider)

    return proxy(request, '')

