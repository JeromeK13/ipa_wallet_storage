import logging
import os
from datetime import datetime
from typing import Optional

# Logger instance
_LOGGER: Optional[logging.Logger] = None
_LOG_LEVELS: dict = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


# Set logger configurations and return logger
def get_logger() -> logging.Logger:
    """ Gets or creates a global Logger

    :return: logging.Logger - Logger instance
    """
    global _LOGGER, _LOG_LEVELS

    if not _LOGGER:
        datetime_value = datetime.now().strftime('%d_%m_%Y')
        format_value = '[%(asctime)s] [%(levelname)s] %(name)s | %(message)s'
        logging.basicConfig(filename=f'./logs/{datetime_value}.log',
                            filemode='a',
                            format=format_value,
                            level=_LOG_LEVELS.get(os.environ.get("LOG_LEVEL")))
        _LOGGER = logging.getLogger(name=os.environ.get("APP_NAME"))
    return _LOGGER
