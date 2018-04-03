import json
import csv

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import connections

from .models import TimeserieRecord


def timeserie_csv(request, name):
    record = get_object_or_404(TimeserieRecord, name=name)
    model = record.create_model()
    content_disposition = 'attachment; filename="{}.csv"'.format(record.name)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition

    writer = csv.writer(response)
    writer.writerow(['Time', 'Value'])
    for t in model.objects.all():
        writer.writerow(t.make_record_csv())

    return response


def timeserie(request, name):
    record = get_object_or_404(TimeserieRecord, name=name)
    model = record.create_model()
    data = [t.make_record() for t in model.objects.all()]

    return JsonResponse(data, safe=False)