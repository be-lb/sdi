from functools import partial
from rest_framework import viewsets
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.filters import BaseFilterBackend
import rules


class ObjectPermissions(DjangoObjectPermissions):
    """
    Similar to `DjangoObjectPermissions`, but adding 'view' permissions.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        """
        Viewset calls it whatever, so we need to neutralized otherwise
        we nevr reach object level
        """
        return True


class RulesPermissionsFilter(BaseFilterBackend):
    """
    A filter backend that limits results to those where the requesting user
    has read object level permissions.
    """

    perm_format = '%(app_label)s.view_%(model_name)s'

    def filter_queryset(self, request, queryset, view):
        user = request.user
        model_cls = queryset.model
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }
        permission = self.perm_format % kwargs

        def perm_checker(o):
            t = user.has_perm(permission, o)
            print('perm_checker[{}][{}][{}] => {}'.format(
                user, permission, o, t))
            return t

        ids = [o.pk for o in filter(perm_checker, queryset)]
        # print('IDS[{}] {}'.format(permission, ids))

        return queryset.filter(pk__in=ids)


class ViewSetWithPermissions(viewsets.ModelViewSet):
    permission_classes = (ObjectPermissions, )
    filter_backends = (RulesPermissionsFilter, )
