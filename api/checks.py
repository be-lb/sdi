from django.conf import settings
from django.core.checks import Error, register


@register()
def check_rules_object_backend(app_configs, **kwargs):
    errors = []
    try:
        auth_backends = settings.AUTHENTICATION_BACKENDS
        if 'rules.permissions.ObjectPermissionBackend' not in auth_backends:
            raise Exception(
                'Missing rules.permissions.ObjectPermissionBackend')
    except Exception:
        errors.append(
            Error(
                'Missing rules.permissions.ObjectPermissionBackend',
                hint=
                'Add \'rules.permissions.ObjectPermissionBackend\' to your AUTHENTICATION_BACKENDS setting',
                obj=settings,
                id='sdi.api.E001',
            ))
    return errors


@register()
def check_public_group(app_configs, **kwargs):
    errors = []
    if getattr(settings, 'PUBLIC_GROUP', None) is None:
        errors.append(
            Error(
                'No Public Group Configured',
                hint='Set PUBLIC_GROUP in your settings',
                obj=settings,
                id='sdi.api.E002',
            ))
    return errors


@register()
def check_default_group(app_configs, **kwargs):
    errors = []
    if getattr(settings, 'DEFAULT_GROUP', None) is None:
        errors.append(
            Error(
                'No Default Group Configured',
                hint='Set DEFAULT_GROUP in your settings',
                obj=settings,
                id='sdi.api.E003',
            ))
    return errors