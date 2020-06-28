import contextlib
import logging
import threading
import time

from django.core.cache import caches

_logger = threading.local()


class CacheLogHandler(logging.StreamHandler):  # pragma: no cover
    """Log handler that goes to the django cache"""

    def __init__(self, key, clear=False, cache_name='pgclone'):
        super().__init__()
        self._key = key
        self._cache = caches[cache_name]
        if clear:
            self._cache.delete(self._key)

    def emit(self, record):
        msg = self._cache.get(self._key) or ''
        msg += f'{record.msg}\n'
        self._cache.set(self._key, msg, 24 * 60 * 60)


def new_stdout_logger(level=logging.INFO):
    """Make a temporary pgclone logger to go to stdout"""
    logger = logging.Logger(f'pgclone-logger-{int(time.time())}')
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    logger.addHandler(handler)

    return logger


def new_cache_logger(
    key, clear=False, level=logging.INFO, cache_name='pgclone'
):  # pragma: no cover
    """Make a temporary cache logger"""
    logger = logging.Logger(key)
    logger.setLevel(level)
    handler = CacheLogHandler(key, clear=clear, cache_name=cache_name)
    handler.setLevel(level)
    logger.addHandler(handler)

    return logger


def get_default_logger():
    """Returns the default global logger"""
    return logging.getLogger('pgclone')


def get_logger():
    """
    Gets the current logger. Either returns
    the one set with set_logger or the default logger
    """
    return getattr(_logger, 'value', get_default_logger())


@contextlib.contextmanager
def set_logger(logger):
    global _logger

    if hasattr(_logger, 'value'):  # pragma: no cover
        raise RuntimeError('Global logger has already been set')

    _logger.value = logger
    try:
        yield
    finally:
        delattr(_logger, 'value')
