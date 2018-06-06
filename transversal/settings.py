# Transversal

import os
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
#

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.abspath( os.path.dirname(__file__) )
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(ENV_PATH, '..', 'static')
PROJECT_STATIC_FOLDER = 'transversal'
STATICFILES_DIRS = [
    ( PROJECT_STATIC_FOLDER, STATIC_ROOT + '/' + PROJECT_STATIC_FOLDER + '/' ),
]
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
)
BOWER_COMPONENTS_ROOT =  STATIC_ROOT

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(ENV_PATH, '..', 'media')

LOGIN_URL = '/login'
LOGOUT_URL = '/logout'

# Name of site in the document title
DOCUMENT_TITLE = 'transversal texts'
# Title in the header of admin section
ADMIN_SITE_HEADER = DOCUMENT_TITLE
admin.site.site_header = ADMIN_SITE_HEADER

# Apps
CONTRIB_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'adminsortable',
    'ckeditor',
    'ckeditor_uploader',
    'gm2m',
    'djangobower'
)

PROJECT_APPS = (
    'apps.models',
    'apps.utils',
    'apps.views',
)

INSTALLED_APPS = CONTRIB_APPS + PROJECT_APPS

BOWER_INSTALLED_APPS = (
    'jquery',
    'jquery-highlight',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'transversal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.utils.context_processors.debug_processor',
                'apps.utils.context_processors.site_info_processor',
                'apps.models.context_processors.slideshow_header_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'transversal.wsgi.application'

#
# Internationalization
#
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', _('English')),
)
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ   = True
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)
DECIMAL_SEPARATOR = '.'

# CKEDITOR

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'width'  : '100%',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Image' ],
            ['RemoveFormat', 'Source']
        ]
    },
}

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_JQUERY_URL  = "/static/admin/js/vendor/jquery/jquery.min.js"


#
# Import private settings
#
from .private_settings import *
