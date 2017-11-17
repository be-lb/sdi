import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import connections

from .models import TimeserieRecord


def timeserie(request, id):

    record = get_object_or_404(TimeserieRecord, name=id)
    model = record.create_model()

    data = []
    for t in model.objects.all():
        data.append(t.make_record())

    return JsonResponse(data, safe=False)