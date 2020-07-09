# -*- coding:utf-8 -*-


# ***Builtin***
import logging
import sys

# ***Custum***
from . import LOG_LEVEL

def simple_debug(namae: str = "Null",
                 level: int = 0) -> logging.Logger:
    """
    debug用

    :param namae: 名前，区分
    :param level: 打印的log等级，默认0， 为logging.DEBUG
    :return: logger
    """
    levels = (logging.DEBUG,
              logging.INFO,
              logging.WARNING,
              logging.ERROR,
              logging.CRITICAL)

    logger = logging.getLoggerClass()(namae)
    logger.setLevel(levels[level])

    console_handler = logging.StreamHandler(sys.stdout)

    if level:
        formatter = logging.Formatter('%(message)s')

    else:
        formatter = logging.Formatter('%(asctime)s - %(name)s[line:%(lineno)-03d] - %(levelname)-8s: %(message)s')

    console_handler.formatter = formatter

    logger.addHandler(console_handler)

    return logger

def justdoit(msg="ERROR"):
    def deco_func(func):

        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except:
                logger = simple_debug(level=LOG_LEVEL,
                                      namae=func.__globals__['__file__'] + ":" + func.__qualname__)
                logger.error(msg)

        return wrapper

    return deco_func


if __name__ == '__main__':
    @justdoit(msg="CNM")
    def tst():
        print("FUCKOFF", sdfd="")
    tst()

