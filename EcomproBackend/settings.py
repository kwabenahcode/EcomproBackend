"""
Django settings for EcomproBackend project.

Copy/paste version (CORS + JWT + Paystack + PythonAnywhere friendly)
"""

from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

# ------------------------------------------------------------
# Base / Env
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-change-me")
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "yes"]

# IMPORTANT: don't use ["*"] for ALLOWED_HOSTS in production
ALLOWED_HOSTS = [
    "ecompro.pythonanywhere.com",
    "localhost",
    "127.0.0.1",
]

# ------------------------------------------------------------
# Installed Apps
# ------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "corsheaders",
    "rest_framework",

    # Your apps
    "User",
    "Product",
    "Cart",
    "payment",
    "Orders",
]

# ------------------------------------------------------------
# Middleware
# ------------------------------------------------------------
# CORS middleware MUST be at the top (before CommonMiddleware)
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------------------------
# URLs / Templates / WSGI
# ------------------------------------------------------------
ROOT_URLCONF = "EcomproBackend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "EcomproBackend.wsgi.application"

# ------------------------------------------------------------
# Database
# ------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Custom User
AUTH_USER_MODEL = "User.User"

# ------------------------------------------------------------
# REST Framework + JWT
# ------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# ------------------------------------------------------------
# CORS (Fix CORB / CORS preflight issues)
# ------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://ecompro-frontend.vercel.app",
    "https://ecompro-online.vercel.app",
]

# If you are using Authorization header (JWT) from browser, you MUST allow it.
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# You can keep this True if you use cookies; for JWT header-only, it can be False.
# Leaving True won't break as long as you DON'T use wildcard origins.
CORS_ALLOW_CREDENTIALS = True

# Expose headers if you ever want to read them in JS (optional but harmless)
CORS_EXPOSE_HEADERS = ["Content-Type", "Authorization"]

# ------------------------------------------------------------
# Internationalization
# ------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------
# Static / Media (PythonAnywhere friendly)
# ------------------------------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------
# Paystack / App URLs
# ------------------------------------------------------------
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

# Backend base (no /api here)
BASE_URL = os.getenv("BASE_URL", "https://ecompro.pythonanywhere.com")

# Frontend base (Vercel)
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://ecompro-online.vercel.app")