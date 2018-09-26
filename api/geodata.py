from importlib import import_module
import logging

from django.apps import apps
from django.conf.urls import url, include

from . import rules

logger = logging.getLogger(__name__)


def load_loaders():
    urlpatterns = []
    try:
        for label in apps.app_configs:
            app = apps.app_configs[label]
            geodata = getattr(app, 'geodata', None)
            if geodata is not None:
                logger.info('Installing geodata loader "{}"'.format(label))
                urlpatterns.append(
                    url(r'^geodata/', include('{}.urls'.format(app.name))))

                try:
                    module_rules = import_module('.rules', app.name)
                    module_rules.hook(rules)
                except:
                    logger.warning(
                        'Geodata loader "{}" does not hook into the permissions system'.
                        format(label))

                logger.info('Installed geodata loader "{}"'.format(label))

    except Exception as ex:
        logger.warning('Failed with geodata loader "{}"'.format(ex))

    return urlpatterns
