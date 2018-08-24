from django.db.models import Count
from django.contrib.admin import ModelAdmin
from ..models.map import UserMap


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
    list_filter = ('status', 'user__username')

    # list_editable = ('status', )

    search_fields = ['title__fr', 'title__nl']

    def clone_map(self, request, queryset):
        dones = []
        fails = []
        for obj in queryset:
            try:
                obj.clone()
                dones.append(str(obj.title))
            except Exception as ex:
                fails.append('{} because of: {}'.format(obj.title, ex))

        self.message_user(request,
                          'Successfully cloned {}.'.format(', '.join(dones)))

    clone_map.short_description = "Clone selected map"

    actions = ('clone_map', )
