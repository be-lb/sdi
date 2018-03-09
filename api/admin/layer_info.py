from django.db.models import Count
from django.contrib.admin import ModelAdmin, SimpleListFilter

from django.utils.translation import ugettext_lazy as _


class AttachedLayerInfoListFilter(SimpleListFilter):
    title = _('attached to map')
    parameter_name = 'attached'

    def lookups(self, request, model_admin):
        return (
            ('attached', _('attached')),
            ('detached', _('detached')),
        )

    def queryset(self, request, queryset):
        annotated = queryset.annotate(Count('usermap'))
        if self.value() == 'attached':
            return annotated.filter(usermap__count__gte=0)
        if self.value() == 'detached':
            return annotated.filter(usermap__count__exact=0)


def title(o):
    return o.metadata.title


def map_(o):
    return o.usermap_set.first()


def user(o):
    m = o.usermap_set.first()
    if m:
        return m.user
    return None


class LayerInfoAdmin(ModelAdmin):
    list_display = (user, title, map_, 'visible', 'group', 'legend')
    list_filter = (AttachedLayerInfoListFilter, )
