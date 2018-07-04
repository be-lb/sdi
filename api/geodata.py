from importlib import import_module
import logging

from django.conf import settings
from django.conf.urls import url, include

from . import rules

logger = logging.getLogger(__name__)


def load_loaders():
    urlpatterns = []
    try:
        for loader in settings.GEODATA_LOADERS:
            urlpatterns.append(
                url(r'^geodata/', include('{}.urls'.format(loader))))

            try:
                module_rules = import_module('.rules', loader)
                module_rules.hook(rules)
            except:
                logger.warning(
                    'Geodata loader "{}" does not hook into the permissions system'.
                    format(loader))

            logger.info('Installed geodata loader "{}"'.format(loader))

    except Exception as ex:
        logger.warning('Failed with geodata loader "{}"'.format(loader), ex)

    return urlpatterns