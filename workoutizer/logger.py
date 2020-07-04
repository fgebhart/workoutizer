format_console = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
# format_console = "%(name)s - %(message)s"  # optionally add time: "%(asctime)s -"

logging_dict = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'colored': {'()': 'coloredlogs.ColoredFormatter', 'format': format_console, 'datefmt': '%m-%d %H:%M:%S'}
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'loggers': {},
}


def get_logging_config(django_log_level: str, wkz_log_level: str):
    logging_dict['loggers'] = {
        'django': {
            'handlers': ['console'],
            'level': django_log_level,
        },
        'wizer': {
            'handlers': ['console'],
            'level': wkz_log_level,
        },
    }

    return logging_dict


def get_logging_for_wkz():
    logging_dict['loggers'] = {
        'wkz': {
            'handlers': ['console'],
            'level': "DEBUG",
        }
    }

    return logging_dict
