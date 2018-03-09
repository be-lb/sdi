from django.contrib.admin import ModelAdmin


def name_fr(o):
    return o.name.fr


def name_nl(o):
    return o.name.nl


def url_fr(o):
    return o.url.fr


def url_nl(o):
    return o.url.nl


class AttachmentAdmin(ModelAdmin):
    list_display = (
        'user_map',
        name_fr,
        name_nl,
        url_fr,
        url_nl,
    )
