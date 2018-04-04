from django.contrib.auth.models import User, Group
from django.conf import settings

default_group = Group.objects.get(name=settings.DEFAULT_GROUP)


def sync_user_relations(user, ldap_attributes):
    user.groups.add(default_group)