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
from django import forms

from .models import (Document, Image,)


def upload_document(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    f = forms.FileField()
    file = request.FILES['file']
    f.run_validators(file)
    instance = Document(
        user=request.user,
        document=file,
    )
    instance.save()
    url = reverse('document-get', args=[instance.id])
    return JsonResponse({'url': url, 'id': instance.id})


def upload_image(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    f = forms.ImageField()
    file = request.FILES['file']
    f.run_validators(file)
    instance = Image(
        user=request.user,
        image=file,
    )
    instance.save()
    url = reverse('image-get', args=[instance.id])
    return JsonResponse({'url': url, 'id': instance.id})


def get_document(request, id):
    document = Document.objects.get(id=id)
    return FileResponse(streaming_content=document.document)


def get_image(request, id):
    image = Image.objects.get(id=id)
    return FileResponse(streaming_content=image.image)
