import os
from pathlib import Path

from huey import SqliteHuey

from workoutizer.logger import get_logging_config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
INITIAL_TRACE_DATA_DIR = os.path.join(BASE_DIR, "setup", "initial_trace_data")

if os.getenv("WKZ_ENV", None) == "devel":
    WORKOUTIZER_DIR = BASE_DIR
else:
    USER_HOME = Path.home()
    WORKOUTIZER_DIR = os.path.join(str(USER_HOME), ".wkz")
SQLITE_FILE = "db.sqlite3"
WORKOUTIZER_DB_PATH = os.path.join(WORKOUTIZER_DIR, SQLITE_FILE)
TRACKS_DIR = os.path.join(WORKOUTIZER_DIR, "tracks")

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

# SECURITY WARNING: keep the secret key used in production secret!
# however, as long as workoutizer is only used locally this is not an issue
SECRET_KEY = "h#ppx^(%ya18qrm+hgzf-vxr^t=r57k_65_hr73f^-n)@qc9as"

DEBUG = False

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "wkz",
    "colorfield",
    "rest_framework",
    "channels",
    "django_eventstream",
    "huey.contrib.djhuey",
]

MIDDLEWARE = [
    "django_grip.GripMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "workoutizer.urls"
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

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

WSGI_APPLICATION = "workoutizer.wsgi.application"
ASGI_APPLICATION = "workoutizer.asgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": WORKOUTIZER_DB_PATH,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_L10N = True
USE_TZ = True

PLOT_WIDTH = 1110
PLOT_HEIGHT = 300

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# set auto primary key to BigAutoField explicitly to suppress warning
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# plotting
trace_line_width = 3.5
trace_line_opacity = 0.9

LOGGING = get_logging_config(
    django_log_level=os.getenv("DJANGO_LOG_LEVEL", "WARNING"),
    wkz_log_level=os.getenv("WKZ_LOG_LEVEL", "INFO"),
    huey_log_level=os.getenv("HUEY_LOG_LEVEL", "WARNING"),
    path_to_log_dir=WORKOUTIZER_DIR,
)

HUEY = SqliteHuey(filename="/tmp/demo.db")
