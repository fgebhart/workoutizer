import os

console_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
minimal_format = "%(message)s"


def _get_formatter_and_handler(path_to_log_dir: str, use_minimal_format: bool = False):
    if not os.path.isdir(path_to_log_dir):
        os.mkdir(path_to_log_dir)
    logging_dict = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "colored": {
                "()": "coloredlogs.ColoredFormatter",
                "format": minimal_format if use_minimal_format else console_format,
                "datefmt": "%m-%d %H:%M:%S",
            },
            "format_for_file": {
                "format": "%(asctime)s :: %(levelname)s :: %(funcName)s in %(filename)s (l:%(lineno)d) :: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colored",
            },
            "file": {
                "level": "WARNING",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "format_for_file",
                "filename": os.path.join(path_to_log_dir, "wkz.log"),
                "maxBytes": 5_000_000,
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {
                "level": "DEBUG",
                "handlers": ["console", "file"],
            },
        },
    }
    return logging_dict


def get_logging_config(django_log_level: str, wkz_log_level: str, path_to_log_dir: str):
    logging_dict = _get_formatter_and_handler(path_to_log_dir=path_to_log_dir)
    logging_dict["loggers"] = {
        "django": {
            "handlers": ["console", "file"],
            "level": django_log_level,
        },
        "wkz": {
            "handlers": ["console", "file"],
            "level": wkz_log_level,
        },
    }

    return logging_dict
