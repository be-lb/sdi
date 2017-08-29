from ..models import MessageRecord

from rest_framework import serializers

class MessageRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageRecord
        fields = ['fr', 'nl']
