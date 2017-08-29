
from django.urls import reverse
from rest_framework import serializers

from .models import (Document, Image,)


class DocumentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, instance):
        return reverse('documents-detail', args=[instance.id])

    class Meta:
        fields = (
            'id',
            'document',
            'url'
        )
