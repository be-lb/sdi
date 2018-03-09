from functools import partial
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.core.checks import Error, register
from rules import (add_perm, predicate, always_allow, is_superuser)

from .models import (
    Alias,
    Attachment,
    Attachment,
    BaseLayer,
    BoundingBox,
    Category,
    Keyword,
    LayerGroup,
    LayerInfo,
    LayerLink,
    MessageRecord,
    MetaData,
    Organisation,
    PointOfContact,
    ResponsibleOrganisation,
    Role,
    Thesaurus,
    Topic,
    UserMap,
)

LAYER_VIEW_PERMISSION = 'api.view_layer_data'

try:
    PUBLIC_GROUP = settings.PUBLIC_GROUP
    public_group_queryset = Group.objects.filter(name=PUBLIC_GROUP)
except AttributeError:
    PUBLIC_GROUP = None

try:
    DEFAULT_GROUP = settings.DEFAULT_GROUP
    default_group_queryset = Group.objects.filter(name=DEFAULT_GROUP)
except AttributeError:
    DEFAULT_GROUP = None


@register()
def check_public_group(app_configs, **kwargs):
    errors = []
    if not PUBLIC_GROUP:
        errors.append(
            Error(
                'No Public Group Configured',
                hint='Set PUBLIC_GROUP in your settings',
                obj=settings,
                id='sdi.api.W001',
            ))
    return errors


@register()
def check_default_group(app_configs, **kwargs):
    errors = []
    if not DEFAULT_GROUP:
        errors.append(
            Error(
                'No Default Group Configured',
                hint='Set DEFAULT_GROUP in your settings',
                obj=settings,
                id='sdi.api.E001',
            ))
    return errors


def ensure_group(name):
    try:
        Group.objects.get(name=name)
    except Group.DoesNotExist:
        Group.objects.create(name=name)


ensure_group(DEFAULT_GROUP)
ensure_group(PUBLIC_GROUP)

##############
# HELPERS    #
##############


def permission(perm_type, model):
    meta = model._meta
    return '{}.{}_{}'.format(meta.app_label, perm_type, meta.model_name)


view = partial(permission, 'view')
change = partial(permission, 'change')
add = partial(permission, 'add')
delete = partial(permission, 'delete')


def get_map_user(user_map):
    return user_map.user


def get_map_groups(user_map):
    """
    If a specific set of groups is attached to this map, return it, otherwise returns the default set
    """
    pg = user_map.permission_group_user_map.all()
    gids = list(pg.values_list('group', flat=True))
    if len(gids) > 0:
        return Group.objects.filter(id__in=gids)

    return default_group_queryset


def get_layer_user(layer_info):
    get_map_user(layer_info.usermap_set.first())


def get_attachment_user(attachment):
    get_map_user(attachment.user_map)


def group_intersects(gs1, gs2):
    if gs1 and gs2:
        for g1 in gs1:
            for g2 in gs2:
                if g1.id == g2.id:
                    return True
    return False


def layer_uri(schema, table_name):
    return '{}/{}'.format(schema, table_name)


def get_maps_for_layer(uri):
    md = MetaData.objects.get(resource_identifier=uri)
    return UserMap.objects.filter(layers__metadata=md.id)


##############
# PREDICATES #
##############


@predicate
def is_user(req_user, user_obj):
    print('is_user {} {} {}'.format(req_user, user_obj, req_user == user_obj))
    return req_user == user_obj


@predicate
def is_public_map(user, user_map):
    if PUBLIC_GROUP and user_map:
        pgs = get_map_groups(user_map).filter(name=PUBLIC_GROUP)
        return pgs.count() > 0
    return False


@predicate
def is_map_author(user, user_map):
    return user_map and user == get_map_user(user_map)


@predicate
def is_layerinfo_author(user, layer_info):
    return layer_info and user == get_layer_user(layer_info)


@predicate
def is_attachment_author(user, attachment):
    return attachment and user == get_attachment_user(attachment)


@predicate
def map_group_intersects(user, user_map):
    if user_map:
        return group_intersects(user.groups.all(), get_map_groups(user_map))
    return False


@predicate
def is_published(user, user_map):
    return user_map and user_map.status == UserMap.PUBLISHED


@predicate
def is_layer_author(user, layer):
    maps = get_maps_for_layer(layer_uri(*layer))
    for m in maps:
        if is_map_author(user, m):
            return True
    return False


@predicate
def layer_group_intersects(user, layer):
    maps = get_maps_for_layer(layer_uri(*layer))
    for m in maps:
        if map_group_intersects(user, m):
            return True
    return False


@predicate
def is_public_layer(user, layer):
    maps = get_maps_for_layer(layer_uri(*layer))
    for m in maps:
        if is_public_map(user, m):
            return True
    return False


@predicate
def user_is_default_group(user):
    try:
        user.groups.get(name=DEFAULT_GROUP)
        return True
    except Group.DoesNotExist:
        return False
    return False


##############
# RULES      #
##############

add_perm(change(UserMap), is_map_author)
add_perm(delete(UserMap), is_map_author)
add_perm(view(UserMap), is_map_author | map_group_intersects | is_public_map)

add_perm(LAYER_VIEW_PERMISSION,
         is_layer_author | layer_group_intersects | is_public_layer)

add_perm(change(LayerInfo), is_layerinfo_author)
add_perm(delete(LayerInfo), is_layerinfo_author)

add_perm(change(Attachment), is_attachment_author)
add_perm(delete(Attachment), is_attachment_author)
add_perm(view(Attachment), always_allow)

add_perm(view(User), is_user)

add_perm(view(MetaData), always_allow)
add_perm(change(MetaData), user_is_default_group)

add_perm(view(Alias), always_allow)
add_perm(change(Alias), user_is_default_group)

print('api.rules loaded')