import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me-use-a-longer-local-key")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

allowed_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")
if os.getenv("VERCEL_URL"):
    allowed_hosts = f"{allowed_hosts},{os.environ['VERCEL_URL'].strip()}"
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(",") if host.strip()]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

is_vercel = bool(os.getenv("VERCEL_URL"))
SECURE_SSL_REDIRECT = is_vercel or os.getenv("DJANGO_SECURE_SSL_REDIRECT", "false").lower() == "true"
SESSION_COOKIE_SECURE = is_vercel or os.getenv("DJANGO_SESSION_COOKIE_SECURE", "false").lower() == "true"
CSRF_COOKIE_SECURE = is_vercel or os.getenv("DJANGO_CSRF_COOKIE_SECURE", "false").lower() == "true"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "accounts",
    "healthcare",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "config.middleware.ApiCsrfExemptMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    },
]
WSGI_APPLICATION = "config.wsgi.application"

database_url = os.getenv("DATABASE_URL")
if not database_url and not DEBUG:
    raise ImproperlyConfigured("DATABASE_URL must be set to the Supabase Postgres connection string in production.")
if not database_url:
    database_url = "sqlite:///db.sqlite3"

DATABASES = {
    "default": dj_database_url.config(
        default=database_url,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=(database_url.startswith("postgres") or database_url.startswith("postgresql")),
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [BASE_DIR / "dashboard" / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

trusted_origins = os.getenv(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://localhost:8000,https://localhost:8000,http://127.0.0.1:8000,https://127.0.0.1:8000",
)
if os.getenv("VERCEL_URL"):
    vercel_host = os.environ["VERCEL_URL"].strip()
    trusted_origins = f"{trusted_origins},https://{vercel_host},http://{vercel_host}"
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in trusted_origins.split(",")
    if origin.strip()
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}
