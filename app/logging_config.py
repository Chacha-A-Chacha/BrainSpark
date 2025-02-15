# app/logging_config.py
import logging
import logging.config


def configure_logging():
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'ERROR',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': 'app_errors.log',
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': True
            },
            'app': {
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(logging_config)


# Call this in your app startup
configure_logging()
