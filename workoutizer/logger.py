format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
minimal_format = "%(message)s"


def _get_formatter_and_handler(use_minimal_format: bool = False):
    logging_dict = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'colored': {'()': 'coloredlogs.ColoredFormatter',
                        'format': minimal_format if use_minimal_format else format, 'datefmt': '%m-%d %H:%M:%S'}
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'colored',
            },
        },
        'loggers': {},
    }
    return logging_dict


def get_logging_config(django_log_level: str, wkz_log_level: str):
    logging_dict = _get_formatter_and_handler()
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
