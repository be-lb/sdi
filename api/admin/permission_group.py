from django.contrib.admin import ModelAdmin


class PermissionGroupAdmin(ModelAdmin):
    list_display = ('group', 'user_map')
    ordering = ('group_id', )
