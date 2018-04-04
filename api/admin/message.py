from django.contrib.admin import ModelAdmin


class MessageRecordAdmin(ModelAdmin):
    list_display = ('id', 'fr', 'nl')
