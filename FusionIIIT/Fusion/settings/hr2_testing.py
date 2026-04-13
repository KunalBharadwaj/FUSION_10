import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = "hr2-testing-only"
DEBUG = False
USE_TZ = False
USE_I18N = True
USE_L10N = False
TIME_ZONE = "Asia/Kolkata"
LANGUAGE_CODE = "en-us"
SITE_ID = 1
ROOT_URLCONF = "Fusion.hr2_testing_urls"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
STATIC_URL = "/static/"
MEDIA_ROOT = os.path.join(BASE_DIR, "..", "media")
MEDIA_URL = "/media/"
ALLOWED_HOSTS = ["*"]
MIDDLEWARE = []

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework.authtoken",
    "applications.globals",
    "applications.hr2",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("DB_NAME", "fusionlab"),
        "USER": os.environ.get("DB_USER", "fusion_admin"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "hello123"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", ""),
        "TEST": {
            "NAME": os.environ.get("DB_TEST_NAME", "test_hr2_fusionlab"),
        },
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}
