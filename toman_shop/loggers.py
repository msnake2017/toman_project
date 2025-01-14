from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / 'logs'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'django_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'filename': LOG_DIR / 'django.log'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['django_file'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}
