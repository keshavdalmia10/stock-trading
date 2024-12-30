import logging
from logging.config import dictConfig

# Define an enumeration for logging levels
class LogLevel:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

# Define the logging configuration dictionary
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'normal': {
            'format': '%(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'normal',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'detailed',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': logging.DEBUG,  # Initial logging level set to DEBUG
    },
}

# Configure logging using the configuration dictionary
dictConfig(LOGGING_CONFIG)

# Function to set logging level across all loggers
def set_logging_level(level):
    logging.getLogger().setLevel(level)
    for handler in logging.getLogger().handlers:
        handler.setLevel(level)

#CRITICAL > ERROR > WARNING > INFO > DEBUG