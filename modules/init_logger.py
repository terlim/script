import logging
import logging.handlers
from pathlib import Path


def init_logger(logDir: Path, name: str, mode=0) -> logging:
    fileName = logDir.joinpath(name + '.log')

    logger = logging.getLogger(name)
    FORMAT = '%(asctime)s - %(name)s:%(lineno)s - %(levelname)s - %(message)s'
    logger.setLevel(logging.DEBUG)
    if mode == 0:
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter(FORMAT))
        sh.setLevel(logging.DEBUG)
        fh = logging.handlers.RotatingFileHandler(filename=fileName,
                                                  mode='w',
                                                  backupCount=1,
                                                  encoding='UTF-8')
        fh.setFormatter(logging.Formatter(FORMAT))
        fh.setLevel(logging.DEBUG)
        logger.addHandler(sh)
        logger.addHandler(fh)
    if mode == 1:
        fh = logging.handlers.RotatingFileHandler(filename=fileName,
                                                  mode='a',
                                                  maxBytes=10485760,
                                                  backupCount=100,
                                                  encoding='UTF-8')
        fh.setFormatter(logging.Formatter(FORMAT))
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    return logger
