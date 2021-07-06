"""
Django settings for simple_booking project.

Generated by 'django-admin startproject' using Django 3.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-x9-5w5rix&5(-o$lgplwo!kvxl(a3p9o=0l6!c%$5fm4n#32-!')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool( os.environ.get('DJANGO_DEBUG', True) )

ALLOWED_HOSTS = os.environ.get('SERVERNAMES', '').split()

if not DEBUG:
    SECURE_HSTS_SECONDS = int( os.environ.get('SERVER_HSTS_SECONDS', 3600) )

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

UNDER_CONSTRUCTION = bool( os.environ.get('DJANGO_UNDER_CONSTRUCTION', False) )

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_underconstruction',
    'captcha',
    'bootstrap',
    'fontawesome',
    'crispy_forms',
    'extra_settings',
    'verify_email.apps.VerifyEmailConfig',
    'tinymce',
    'booking.apps.BookingConfig',
    'blog.apps.BlogConfig',
    'base.apps.BaseConfig',
    'contact.apps.ContactConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_underconstruction.middleware.UnderConstructionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'simple_booking.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.menu', 
                'blog.context_processors.share', 
                'contact.context_processors.contact_short', 
            ],
        },
    },
]

WSGI_APPLICATION = 'simple_booking.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }

    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRESQL_NAME','django_db'),
        'USER' : os.environ.get('POSTGRESQL_USER','user_name'),
        'PASSWORD' : os.environ.get('POSTGRESQL_PW','password'),
        'HOST' : os.environ.get('POSTGRESQL_HOST','127.0.0.1'),
        'PORT' : os.environ.get('POSTGRESQL_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'uk-UA'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'

VERIFICATION_SUCCESS_TEMPLATE = None

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('DJANGO_EMAIL_HOST', 'localhost')
    EMAIL_USE_TLS = bool( os.environ.get('DJANGO_EMAIL_USE_TLS', False) )
    EMAIL_USE_SSL = bool( os.environ.get('DJANGO_EMAIL_USE_SSL', False) )
    EMAIL_PORT = int( os.environ.get('DJANGO_EMAIL_PORT', 587) )
    EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_HOST_USER','email')
    EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_HOST_PASSWORD','password')

CRISPY_TEMPLATE_PACK = 'bootstrap4'

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
        messages.DEBUG: 'alert-info',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }

SERVICE_SECRETS = os.path.join(BASE_DIR, 'service_secret.json')

TINYMCE_DEFAULT_CONFIG = {
    'height': '40em',
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'browser_spellcheck': False,
    'theme': 'silver',
    'branding': False,
    'plugins': '''
            textcolor save link media preview codesample contextmenu
            table code lists fullscreen  insertdatetime  nonbreaking
            contextmenu directionality searchreplace wordcount visualblocks
            visualchars code fullscreen autolink lists  charmap print  hr
            anchor pagebreak paste
            ''',
    'toolbar1': '''
            fullscreen preview | bold italic underline | fontselect,
            fontsizeselect  | forecolor backcolor | alignleft alignright |
            aligncenter alignjustify | indent outdent 
            ''',
    'toolbar2': '''
            visualblocks visualchars |
            charmap hr pagebreak nonbreaking anchor |  code |
            bullist numlist table |
            link media paste| codesample
            ''',
    'contextmenu': 'formats | link',
    'menubar': True,
    'statusbar': True,
    'paste_data_images': True,
    'block_unsupported_drop ': True,
    }

RECAPTCHA_ACTIVE = bool( os.environ.get('DJANGO_RECAPTCHA_ACTIVE', False) )
RECAPTCHA_PUBLIC_KEY = os.environ.get('DJANGO_RECAPTCHA_PUBLIC_KEY', 'recaptchapublickeymustbehere')
RECAPTCHA_PRIVATE_KEY = os.environ.get('DJANGO_RECAPTCHA_PRIVATE_KEY', 'recaptchaprivatekeymustbehere')
