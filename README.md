A Spatial Data Infrastructure platform for BE/LB
================================================


# install

The installation process involves several steps.
- sdi server (this repository)
- sdi clients

Here we'll go through the installation of the server. 
The server is a Django project running on Python 3. It comes with a ```requirements.txt``` to help manage dependencies. The system is made to connect with a Postgis backend for layers storage, so you'll have to install one or have details to connect to such database server. On the other hand, the project itself does not make use of a spatial database for its own storage, so any of Django supported database backend will do.
The reference deployment target is Debian 9, and following commands assume a similar system.

Install system dependencies with
```sh
sudo apt install \
    build-essential \
    python3-dev \
    libgeos-dev \
    libxml2-dev \
    libxslt1-dev\
    libz-dev\
    python-virtualenv\
    git-core
```

For Python dependencies, it is advised to first create a virtual environment
```sh
virtualenv -p python3 venv && source venv/bin/activate
```

From within this directory, install dependencies with Pip
```sh
pip install -r requirements.txt
```



For deployment at IBGE, we'll also need
```sh
pip install django_python3_ldap
```


The project is distributed with a very generic settings file that you want to adjust to your configuration. Here's an example based on actual deployment. We create a file ```prod_settings.py``` at the root of sdi's directory, and further manage commands are called with ```--settings prod_settings```

```python
# call base settings
from main.settings import *

# a secret key
SECRET_KEY = 'a-secret-key'

# actual allowed hosts
ALLOWED_HOSTS = ['10.0.0.1']

# in case you want more applications loaded
INSTALLED_APPS.append('django_python3_ldap')

# an actual database setting
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': '127.0.0.1',
        'PORT': 5432,
        'NAME': 'name',
        'PASSWORD': 'password',
        'USER': 'user',
    },
}

# specific config for layers database
LAYERS_DB = {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'HOST': 'x.x.x.x',
    'NAME': 'dbname',
    'PASSWORD': 'password',
    'USER': 'username',
}

# here's a little loop to point to your postgis schemas 
LAYERS_SCHEMAS = [
    'shema_name_0',
    'shema_name_1',
    'shema_name_2',
    'shema_name_3',
    'shema_name_4',
]

for schema in LAYERS_SCHEMAS:
    db_config = LAYERS_DB.copy()
    db_config.update({
        'OPTIONS': {
            'options': '-c search_path={},public'.format(schema),
        },
    })
    DATABASES[schema] = db_config


# clients are declared here in the form
# name : path/to/distribution
CLIENTS_ROOT = '/home/pierre/System/src/ibge/sdi-clients


MAX_DECIMAL_DIGITS = 2

DEFAULT_GROUP = 'sdi:geodata'
PUBLIC_GROUP = 'sdi:public'


# Sorry, but we really need cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/home/pierre/System/var/cache/sdi',
        'OPTIONS': {
            'MAX_ENTRIES': 200000
        }
    },
    'layers': {
        'BACKEND': 'diskcache.DjangoCache',
        'LOCATION': '/home/pierre/System/var/cache/sdi/layers',
        'TIMEOUT': 60 * 60 * 24,
        'SHARDS': 4,
        'DATABASE_TIMEOUT': 1.0,
        'OPTIONS': {
            'size_limit': 2**32  # 4 gigabytes
        }
    }
}

# a django setting
MEDIA_ROOT = '/var/www/sdi/'

```

## logging

Here we'll use ELK (elasticsearch, logstash & kibana). A simple setup is to run a ELK container such as http://elk-docker.readthedocs.io/
and python-logstash package.



```python
LOGGING = {
  
    'handlers': {
        'logstash': {
            'level': 'ERROR',
            'class': 'logstash.TCPLogstashHandler',
            'host': 'localhost',
            'port': 5959, # Default value: 5959
            'version': 1, # Version of logstash event schema. Default value: 0 (for backward compatibility of the library)
            'message_type': 'django',  # 'type' field in logstash message. Default value: 'logstash'.
            'fqdn': False, # Fully qualified domain name. Default value: false.
            'tags': ['django.request'], # list of tags. Default: None.
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['logstash'],
            'level': 'ERROR',
            'propagate': True,
    },
}
```