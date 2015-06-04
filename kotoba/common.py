import logging
import sys
from . import misc

DEFAULT_LOG_LEVEL = logging.DEBUG

class LoggerRepository(object):
    _cache = {}

    @staticmethod
    def get(name, level=logging.DEBUG, show_time=True):
        if name in LoggerRepository._cache:
            return LoggerRepository._cache[name]

        logging_handler = logging.StreamHandler()
        logging_handler.setLevel(level)
        logging_handler.setFormatter(
            logging.Formatter(
                '%(levelname)s %(asctime)s %(name)s: %(message)s'
                if show_time
                else '%(levelname)s %(name)s: %(message)s',
                datefmt='%Y.%m.%d %H:%M:%S %Z'
            )
        )

        logger = logging.getLogger(name)
        logger.addHandler(logging_handler)
        logger.setLevel(level)

        LoggerRepository._cache[name] = logger

        return logger

def node_debug_message(node, message, ignore_indentation=False):
    if not misc.debug_mode:
        return

    LoggerRepository.get('Node', DEFAULT_LOG_LEVEL).debug(
        message if ignore_indentation else '%s%s' % (' ' * node.level() * 2, message)
    )

def is_string(ref):
    try:
        return type(ref) in [unicode, str]
    except NameError:
        return type(ref) is str