import uuid
import math
from django.db import models


def get_manager(schema):
    m = models.Manager().db_manager(schema)
    return m


class TimeserieRecord(models.Model):
    NO_QUALITY = '__none__'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    schema = models.CharField(max_length=256)
    table = models.CharField(max_length=256)

    time_field = models.CharField(max_length=256)
    value_field = models.CharField(max_length=256)
    quality_field = models.CharField(max_length=256, default=NO_QUALITY)

    def create_model(self):

        model_fields = dict()

        def make_record(instance):
            date = getattr(instance, self.time_field)
            ts = math.floor(date.timestamp())
            value = getattr(instance, self.value_field)
            quality = getattr(instance, self.quality_field)
            return [ts, value, quality]

        def make_record_csv(instance):
            date = getattr(instance, self.time_field)
            value = getattr(instance, self.value_field)
            return [date.isoformat(), value]

        model_fields['Meta'] = type('Meta', (),
                                    dict(
                                        managed=False,
                                        db_table=self.table,
                                        app_label='timeserie'))
        model_fields['__module__'] = 'timeserie.models'
        model_fields['objects'] = get_manager(self.schema)
        model_fields['make_record'] = make_record
        model_fields['make_record_csv'] = make_record_csv

        model_fields[self.time_field] = models.DateTimeField(primary_key=True)
        model_fields[self.value_field] = models.FloatField()
        if self.quality_field != TimeserieRecord.NO_QUALITY:
            model_fields[self.quality_field] = models.FloatField()
        else:
            model_fields[self.quality_field] = 1.0

        return type('Timeserie', (models.Model, ), model_fields)

    def __str__(self):
        return str(self.name)
