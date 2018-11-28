import sys

from mesolex.settings.base import *  # noqa

DEBUG = True

SECRET_KEY = os.environ.get('SECRET_KEY', 'hlm&v%v5685+3@5kz359#3dla==vccyz$8fs!tvy8s$1#3hr-*')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'log/error.log',
        },
    },
    'loggers': {
        'lexicon.management.commands.import_data': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
