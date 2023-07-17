import logging
import pathlib as pl
from typing import Union


class LoggingConfig():
    _LOG_DIRECTORY: pl.Path = None
    _DATEFORMAT = '%Y/%m/%d %I:%M:%S %p'
    _LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s : %(message)s'
    _FILE_NAME = "log_file"
    _FILE_SUFFIX = ".txt"

    def __init__(self) -> None:
        raise RuntimeError("This Class is not meant to be instantiated use rather it is to be "
                           "seen as a Singleton")

    @classmethod
    def set_log_directory(cls, path: Union[pl.Path, str]):
        path = pl.Path(path)
        path.mkdir(parents=True, exist_ok=True)
        cls._LOG_DIRECTORY = path

    @classmethod
    def set_dateformat(cls, format: str):
        cls._DATEFORMAT = format

    @classmethod
    def set_filename(cls, filename: str):
        cls._FILE_NAME = filename

    @classmethod
    def set_logformat(cls, format: str):
        cls._LOG_FORMAT = format

    
    @classmethod
    @property
    def LOG_DIRECTORY(cls) -> pl.Path:
        return cls._LOG_DIRECTORY

    @classmethod
    @property
    def FILE_NAME(cls) -> str:
        return cls._FILE_NAME

    @classmethod
    @property
    def FILE_PATH(cls) -> pl.Path:
        return cls._LOG_DIRECTORY.joinpath(cls.FILE_NAME).with_suffix(cls._FILE_SUFFIX)


def init_file_logger(logger: logging.Logger, logLevel=logging.DEBUG
                     ) -> logging.Logger:

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return logger
    if LoggingConfig.LOG_DIRECTORY is None:
        return logger
    log_file_handler = logging.FileHandler(LoggingConfig.FILE_PATH)
    formatter = logging.Formatter(LoggingConfig._LOG_FORMAT, datefmt=LoggingConfig._DATEFORMAT)
    log_file_handler.setFormatter(formatter)
    log_file_handler.setLevel(logLevel)
    logger.addHandler(log_file_handler)
    return logger


def init_console_logger(logger: logging.Logger, logLevel=logging.DEBUG) -> logging.Logger:
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s : %(message)s',
        datefmt='%Y/%m/%d %I:%M:%S %p')
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            return logger
    log_console_handler = logging.StreamHandler()
    log_console_handler.setLevel(logLevel)
    log_console_handler.setFormatter(formatter)
    logger.addHandler(log_console_handler)
    return logger
