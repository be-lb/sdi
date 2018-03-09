from django.contrib.admin import ModelAdmin


def replace_fr(o):
    return o.replace.fr


def replace_nl(o):
    return o.replace.nl


class AliasAdmin(ModelAdmin):
    list_display = ('select', replace_fr, replace_nl)
