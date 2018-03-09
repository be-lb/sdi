from django.db.models import Count
from django.contrib.admin import ModelAdmin


def title_fr(o):
    return o.title.fr


def title_nl(o):
    return o.title.nl


class UserMapAdmin(ModelAdmin):
    list_display = (
        title_fr,
        title_nl,
        'user',
        'status',
        'last_modified',
    )
    list_display_links = (
        title_fr,
        title_nl,
    )
    # list_editable = ('status', )
