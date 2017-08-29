from django.db import models
from django.contrib.postgres.fields import JSONField


class MessageRecord(models.Model):
    fr = models.TextField()
    nl = models.TextField()
    parameters = JSONField(null=True, blank=True)

    def __str__(self):
        return 'fr: {}\nnl: {}'.format(self.fr[:32], self.nl[:32])

    def update_record(self, fr='', nl='', parameters=None):
        self.fr = fr
        self.nl = nl
        self.parameters = parameters
        self.save()


def message_field(name):
    return models.ForeignKey(
        MessageRecord,
        on_delete=models.PROTECT,
        related_name=name,
    )


def message(fr=None, nl=None):
    return MessageRecord.objects.create(fr=fr, nl=nl)


def simple_message(msg):
    return message(fr=msg, nl=msg)
