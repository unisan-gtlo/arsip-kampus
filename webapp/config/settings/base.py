from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me-in-production")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "arsip",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="arsip"),
        "USER": env("DB_USER", default="arsip"),
        "PASSWORD": env("DB_PASSWORD", default="arsip"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Makassar"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "arsip:home"
LOGOUT_REDIRECT_URL = "accounts:login"

# Google Drive / Sheets service account (built from individual env vars, never a
# committed service_account.json). GCP_PRIVATE_KEY is stored with literal \n in
# the env value and unescaped here.
GCP_SERVICE_ACCOUNT = {
    "type": env("GCP_TYPE", default="service_account"),
    "project_id": env("GCP_PROJECT_ID", default=""),
    "private_key_id": env("GCP_PRIVATE_KEY_ID", default=""),
    "private_key": env("GCP_PRIVATE_KEY", default="").replace("\\n", "\n"),
    "client_email": env("GCP_CLIENT_EMAIL", default=""),
    "client_id": env("GCP_CLIENT_ID", default=""),
    "auth_uri": env("GCP_AUTH_URI", default="https://accounts.google.com/o/oauth2/auth"),
    "token_uri": env("GCP_TOKEN_URI", default="https://oauth2.googleapis.com/token"),
}
DRIVE_FOLDER_ID = env("DRIVE_FOLDER_ID", default="")
SPREADSHEET_ID = env("SPREADSHEET_ID", default="")

MAX_UPLOAD_SIZE_MB = env.int("MAX_UPLOAD_SIZE_MB", default=20)
