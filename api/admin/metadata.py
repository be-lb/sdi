from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.conf import settings


class SchemaListFilter(SimpleListFilter):
    title = 'Schema'
    parameter_name = 'schema'

    def lookups(self, request, model_admin):
        return [(s, s) for s in settings.LAYERS_SCHEMAS]

    def queryset(self, request, queryset):
        value = self.value()
        if value in settings.LAYERS_SCHEMAS:
            prefix = '{}/'.format(value)
            return queryset.filter(resource_identifier__startswith=prefix)


class MetadataAdmin(ModelAdmin):
    list_display = (
        'title',
        'resource_identifier',
        'published',
        'creation',
        'revision',
    )
    ordering = ('revision', )
    list_filter = (
        SchemaListFilter,
        'published',
    )
