from django.conf import settings
from django.core.checks import Warning, register


@register()
def check_csw_config_main(app_configs, **kwargs):
    errors = []
    if getattr(settings, 'CSW_CONFIG_MAIN', None) is None:
        errors.append(
            Warning(
                'Missing Config For Catalog [CSW_CONFIG_MAIN]',
                hint='Set CSW_CONFIG_MAIN in your settings',
                obj=settings,
                id='sdi.catalog.W001',
            ))
    return errors


@register()
def check_csw_config_inspire(app_configs, **kwargs):
    errors = []
    if getattr(settings, 'CSW_CONFIG_INSPIRE', None) is None:
        errors.append(
            Warning(
                'Missing Config For Catalog [CSW_CONFIG_INSPIRE]',
                hint='Set CSW_CONFIG_INSPIRE in your settings',
                obj=settings,
                id='sdi.catalog.W002',
            ))
    return errors