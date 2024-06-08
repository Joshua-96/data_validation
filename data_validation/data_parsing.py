import dataclasses
from enum import Enum
import logging
import pathlib as pl
from typing import Sequence
from data_validation.exceptions import CastException
from data_validation.init_loggers import init_console_logger
from collections import ChainMap

from data_validation.meta import ValidationMeta


class DataParingError(Exception):
    def __init__(self, message: str = None) -> None:
        super().__init__(message)


class Container(metaclass=ValidationMeta):
    """Abstract Base Class serving as Component Class that implements the Composite
    pattern
    :param META_PARAMS: list - carry arguments from composite classes to leaf classes but are
     not directly part of a leaf class e.g. a relative path is given in a nested field
     the full path can only the constructed if the base path is propagated down from it's
     parent nodes"""

    META_PARAMS = ["base_path", "log_level", "logger"]

    def __new__(cls, *args, **kwargs):
        cls.__annotations__ = ChainMap(
            *(c.__annotations__ for c in cls.__mro__ if "__annotations__" in c.__dict__)
        )
        obj = super().__new__(cls)
        return obj

    @classmethod
    def static_validation(cls, verbose=True, *args, **kwargs) -> str:
        """tests if class can be initialized given the arguments without actually instantiating it
        returns Error Text if it fails and 'Success' if no errors are raised"""
        try:
            _ = cls(*args, **kwargs)
            return "Success"
        except (ValueError, TypeError, CastException) as e:
            return f"Failed with Error: {e}"

    # to ensure the compatibility with dataclasses as subclasses
    def __post_init__(self) -> None:
        logger = logging.getLogger(self.__class__.__name__)
        self.logger = init_console_logger(logger=logger)

    def __init__(self) -> None:
        self.__post_init__()
        super().__init__()

    def __iter__(self):
        return iter(self.as_flattened_dict())

    def __getitem__(self, item):
        return list(self)[item]

    def as_flattened_dict(self) -> dict:
        """Converts the a composite class into a flattened dict where key values
        for Leaf classes are prefixed with it's name."""
        output_dict = {}
        for key, value in self.__dict__.items():
            if type(value) in [int, float, str, bool] or value is None:
                output_dict[key] = value
            elif isinstance(value, pl.Path):
                output_dict[key] = str(value)
            elif isinstance(value, dict):
                sub_dict = {
                    f"{key}_{value}": sub_value for value, sub_value in value.items()
                }
                output_dict.update(sub_dict)
            elif issubclass(type(value), Container):
                append_dict = {
                    f"{value.__class__.__name__}_{k}": v
                    for k, v in value.__dict__.items()
                }
                append_dict.pop(f"{value.__class__.__name__}_logger")
                output_dict.update(append_dict)
            elif isinstance(value, logging.Logger):
                pass
            elif isinstance(value, Sequence):
                output_dict[key] = ",".join([str(v) for v in value])
            else:
                output_dict[key] = str(value)
                self.logger.warn(
                    f"Unsupported datastructure, for dict unpacking: {value}"
                )

        return output_dict

    def as_dict(self) -> dict:
        """get nested dict representation of a composite class resolving Enum types to their
        respective Str representation"""
        output_dict = {}
        for key, value in self.__dict__.items():
            if key in self.META_PARAMS:
                continue
            if type(value) in [int, float, str, list] or value is None:
                output_dict[key] = value
            elif isinstance(value, dict):
                output_dict.update({key: value})
            elif issubclass(type(value), Container):
                output_dict.update({key: value.as_dict()})
            elif isinstance(value, Enum):
                output_dict[key] = value.value
            else:
                output_dict[key] = str(value)

        return output_dict

    def dataclass_dict_repr(self) -> dict:
        # detach, and reattach logger to exclude it from the dict representation
        temp_logger = self.logger
        del self.logger
        dict_repr = dataclasses.asdict(self)
        self.logger = temp_logger
        return dict_repr
