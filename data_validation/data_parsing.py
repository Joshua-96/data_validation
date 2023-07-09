import logging
import pathlib as pl
from typing import Sequence
from data_validation.init_loggers import init_console_logger, init_file_logger
from abc import ABC, abstractmethod
from collections import ChainMap

from data_validation.validation import ValidationMeta


class DataParingError(Exception):
    def __init__(self, message: str = None) -> None:
        super().__init__(message)


class Container(metaclass=ValidationMeta):
    """Abstract Base Class serving as Component Class that implements the Composite 
       pattern
       :param META_PARAMS: list - carry arguments from composite classes to leaf classes but are
        not directly part of a leaf class e.g. a relative path is given in a nested field
        the full path can only the constructed if the base path is propagated down from it's parent nodes """

    META_PARAMS = ["base_path", "log_level"]

    def __post_init__(self, **kwargs):
        """general post init method that performs type checking and propagates the 
           error upwards
           :**kwargs Keyword arguments to pass for initiating a leaf class instance

           :raises DataParsingError, being re-raised if the Validator class raises an Error
           """
        # set the META_PARAMS module-wide if they are set in the class i.E.
        # the top Level Classes

        self.init_logger()

    def __new__(cls, *args, **kwargs):
        cls.__annotations__ = ChainMap(*(c.__annotations__ for c in cls.__mro__ if '__annotations__' in c.__dict__) )
        obj = super().__new__(cls)
        return obj

    def __init__(self) -> None:
        super().__init__()

    def __iter__(self):
        return iter(self.as_dict())

    def __getitem__(self, item):
        return list(self)[item]

    def init_logger(self):
        """initialize the class logger with the name of the class,
           if a base_path is given, the logs will be written there as well"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger = init_console_logger(self.logger)
        if hasattr(self, "base_path") and self.base_path is not None:
            self.logger = init_file_logger(self.logger, self.base_path)

    def check_passed_args(self, kwargs: dict):
        """check the arguments upon instantiation of a child class,
           gives a warning, if no value is provided"""
        for key in self.__dict__.keys():
            if key == "logger":
                continue
            if key not in kwargs.keys():
                self.logger.warn(
                    f"Fallback for key {key} as it is not specified in params," +
                    f"refer to default params.json for use, using default value {getattr(self, key)}")

    def as_dict(self) -> dict:
        """Converts the a composite class into a flattened dict where key values 
           for Leaf classes are prefixed with it's name e.g. 
            Params{ModelParams{name, structure}, DataParams{image_shape,mask_shape}} -> 
            {Model_Params_name:..., Model_Params_structure:..., DataParams_image_shape:...}"""
        output_dict = {}
        for key, value in self.__dict__.items():
            if type(value) in [int, float, str, bool] or value is None:
                output_dict[key] = value
            elif isinstance(value, pl.Path):
                output_dict[key] = str(value)
            elif type(value) == dict:
                sub_dict = {f"{key}_{value}": sub_value
                            for value, sub_value in value.items()}
                output_dict.update(sub_dict)
            elif issubclass(type(value), Container):
                append_dict = {f"{value.__class__.__name__}_{k}": v
                               for k, v in value.__dict__.items()}
                append_dict.pop(f"{value.__class__.__name__}_logger")
                output_dict.update(append_dict)
            elif isinstance(value, logging.Logger):
                pass
            elif isinstance(value, Sequence):
                output_dict[key] = ",".join([str(v) for v in value])
            else:
                output_dict[key] = str(value)
                self.logger.warn(
                    f"Unsupported datastructure, for dict unpacking: {value}")

        return output_dict

    def as_nested_dict(self) -> dict:
        """get nested dict representation of a composite class"""
        output_dict = {}
        for key, value in self.__dict__.items():
            if key in self.META_PARAMS + ["distribution"]:
                continue
            if type(value) in [int, float, str, list] or value is None:
                output_dict[key] = value
            elif type(value) == dict:
                output_dict.update({key: value})
            elif issubclass(type(value), Container):
                output_dict.update({key: value.as_nested_dict()})
            elif isinstance(value, pl.Path):
                output_dict[key] = str(value)
        return output_dict


class Iterable_Baseclass(Container):
    """Baseclass that implements subscription magic methods"""

    def __init__(self) -> None:
        super().__init__()

    def __iter__(self):
        return iter(self.as_dict().values())

    def __getitem__(self, item):
        return list(self)[item]
