"""
Django settings for tests.
"""

SECRET_KEY = "test-secret-key-for-testing-only"

DEBUG = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "rest_framework",
    "rest_framework_api_key",
    "drf_scoped_permissions",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = "tests.urls"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "drf_scoped_permissions.authentication.APIKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "drf_scoped_permissions.permissions.HasAPIKeyOrGroupScope",
    ],
}

USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
