import logging
import pathlib as pl
from data_validation.exceptions import CastException
import data_validation.init_loggers as log_util
from datetime import datetime
from copy import deepcopy
from functools import partial
from collections.abc import Callable
from typing import Any
from enum import Enum
from typing import Dict, Tuple, List

from data_validation.data_casting_func import _cast_to_bool_from_int,\
                                              _cast_to_datetime_from_int,\
                                              _cast_to_int_from_float,\
                                              _cast_to_bool_from_str


class ValidationMeta(type):
    def __new__(cls: type, name: str, bases: tuple, dct: dict):
        
        
        if "__slots__" not in dct:
            dct["__slots__"] = (f"_{name}" for name in dct["__annotations__"])
        #     all_slots = [f"_{name}" for name in dct["__slots__"]]
            # all_slots.extend([name for name in dct["__slots__"]])
            # dct["__slots__"] = tuple(all_slots)
        # if "__annotations__" in dct:
        #     dct["__annotations__"] = {f"_{k}": v for k, v in dct["__annotations__"].items()}
        if "__dataclass_fields__" in dct.keys() and "__slots__" in dct:
            pass
            # dct.__init__(first_name="HANS")
            # for k in dct["__dataclass_fields__"].keys():
            #     if k not in dct.keys():
            #         dct[k] = False
        

        x = super().__new__(cls, name, bases, dct)
        x.__test_attr__ = "test"
        return x


class TypeHandler():
    DATEFORMAT: str = None
    TYPE_MAPPING: Dict[Tuple[type], Callable[[Any], Any]] = {
        (int, bool): _cast_to_bool_from_int,
        (int, float): lambda x: float(x),
        (str, pl.Path): lambda x: pl.Path(x),
        (str, int): lambda x: int(x) if x else None,
        (str, float): lambda x: float(x) if x else None,
        (float, int): _cast_to_int_from_float,
        (int, datetime): _cast_to_datetime_from_int,
        (str, bool): _cast_to_bool_from_str,
    }

    @classmethod
    def add_type_mapping(cls, *, incoming_type: type, casted_type: type, func: callable, **kwargs) -> None:
        derived_func = partial(
            func, **kwargs)
        cls.TYPE_MAPPING[(incoming_type, casted_type)] = derived_func


class Function_Mapper():
    args: list
    kwargs: dict

    def __init__(self,
                 func: Callable,
                 value_kw: str,
                 *args,
                 **kwargs
                 ) -> None:
        self.value_kw = value_kw
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def invoke(self, value):
        self.kwargs = {k: self.resolve_ref_by_function(v) for k, v in self.kwargs.items()}
        self.kwargs[self.value_kw] = value
        return self.func(*self.args, **self.kwargs)

    def resolve_ref_by_function(self, item):
        if not isinstance(item, self.__class__):
            return item
        return item.invoke()


class Static_Function_Mapper(Function_Mapper):
    def __init__(self,
                 func: Callable,
                 *args,
                 **kwargs) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def invoke(self):
        return self.func(*self.args, **self.kwargs)            


class Validator:
    annotated_type: type
    value_type: type
    sub_value_type: type
    sub_annotated_type: type = type(None)
    """class for validation of arguments Dataclass Args:\n
       Args:
        func (function): callback function which will either run successfully \
            or raise a Value Error
        value_list (list): reference list for checking for inclusion of the \
            value
        value_range (list): list of form [minValue, maxValue] for checking \
            if value is in between, if None is set for maxValue or minValue, \
            performs one sided check
        default (any): default value which is dependent on the type annotation\
             the class is instantiated with
        allow_none (bool): accept None as set Value, if False and default is None\
            raises TypeError when no argument is passed
        **kwargs: additional arguments for the callback function for special\
             cases
       Raises:
        ValueError: if the Validation fails
        TypeError: if the type in value_list or value_range don't match

       Returns:
        either the default value or the value passed by the owner class \
        defaults itself to none   
    """

    def __init__(self,
                 validator_func: Function_Mapper = None,
                 cleaning_func: Function_Mapper = None,
                 default: Any = False,
                 allow_none: bool = False,
                 omit_logging: bool = False):

        self.cleaning_func = cleaning_func
        self.validator_func = validator_func
        self.allow_none = allow_none
        self.default = default
        self.omit_logging = omit_logging
        self.init_logger()

    def init_logger(self):

        self.logger = logging.getLogger()
        self.logger = log_util.init_console_logger(self.logger)
        self.logger = log_util.init_file_logger(self.logger)

    def __repr__(self) -> str:
        return str(self.default)

    def __set_name__(self, owner, name: str):
        if name.startswith("_"):
            self.name = name[1:]
        else:
            self.name = name

    def __get__(self, instance, owner):
        if not instance:
            return self
        # return instance.__dict__[self.name]
        return instance.__dict__.get(self.name, self.default)

    def __delete__(self, instance):
        del instance.__dict__[self.name]

    def _set_attr(self, instance, value):
        instance.__dict__[self.name] = value

    def _handle_None(self):
        if not self.allow_none:
            raise ValueError(
                f"field <{self.name}> is not allowed to be None, if this is undesired, " +
                "consider changing this behavior by setting <allow_none=True> in Validator-" +
                "Constructor")
        return None
    
    def _handle_default_case(self, instance, value):

        if self.default is False:
            raise TypeError(
                f"{instance.__class__.__name__}() missing 1 required " +
                f"positional argument: '{self.name}' with no default value defined")

        if not self.omit_logging and value is None:
            self.logger.warn(f"field '{self.name}' in Parentfield " +
                                f"'{instance.__class__.__name__}' was not passed defaulting to {self.default}")
        # handle case where a field is equal to another field,
        # e.g. output_dir = input_dir
        if isinstance(self.default, str)\
                and hasattr(instance, self.default):
            value = getattr(instance, self.default)
        else:
            value = self.default
        return value 

    def _handle_enum(self, instance: type, value: Any, annotated_type: type):
        try:
            value = annotated_type(value)
        except ValueError:
            self.logger.error(
                f"value {value} is not a valid option of {annotated_type}")
            if not self.allow_none:
                raise CastException(input_type=self.value_type,
                                    output_type=annotated_type,
                                    message=f"value <{value}> is not a valid option")
            value = None
        finally:
            self._set_attr(instance, value)
        return

    def _handle_Sequences(self, instance, value):
        self.sub_annotated_type = self.annotated_type.__args__[0]
        self.annotated_type = getattr(self.annotated_type, "__origin__")
        # return if list is empty
        if not value:
            return
        self.sub_value_type = type(value[0])

    def __set__(self, instance: object, value):
        if self.name.startswith("_"):
            self.name = self.name[1:]

        self.annotated_type = instance.__annotations__[self.name]
        self.value_type = type(value)
        # handle trivial case where types match
        if isinstance(value, self.annotated_type) and self.validator_func is None:
            self._set_attr(instance, value)
            return
        if value is None:
            self._handle_None()
            return

        if value is self:
            value = self._handle_default_case(instance, value)
            return
        # apply function to clean the possible values

        if isinstance(value, Validator):
            value = value.__repr__()

        # cast to annotated values if applicable
        if issubclass(self.annotated_type, Enum):
            self._handle_enum(instance, value, self.annotated_type)
            return

        if hasattr(self.annotated_type, "__origin__"):
            self._handle_Sequences(instance, value)
        else:
            self.sub_annotated_type = None
            self.sub_value_type = None

        if self.cleaning_func is not None:
            value = self.cleaning_func.invoke(value)

        if not isinstance(value, dict)\
                and self.validator_func is None:
            # pass test if int is compared to float
    
            type_tuple = (self.value_type, self.annotated_type) 
            if type_tuple in TypeHandler.TYPE_MAPPING.keys():
                fct_to_call = TypeHandler.TYPE_MAPPING[type_tuple]
                value = fct_to_call(value)
                return

            type_tuple = (self.sub_value_type, self.sub_annotated_type)
            if type_tuple in TypeHandler.TYPE_MAPPING.keys():
                fct_to_call = TypeHandler.TYPE_MAPPING[type_tuple]
                value = map(fct_to_call, value)
                return

            # treat primitive type mismatch as "real" typeError
            if self.annotated_type in [str, int, float, bool]:
                raise TypeError(f"expected type {self.annotated_type}, received {self.value_type}")
            # assume a type_mapping to a complex type is missing
            else:
                raise NotImplementedError(
                    f"value of type {self.value_type} could not be automatically casted to {self.annotated_type}")

        
        temp_bounds = deepcopy(self.validator_func.kwargs)
        # for getting proxy reference e.g. outputpath = "inputpath" with "inputpath" being a reference to the
        # field inputpath of the class itself same with the reference nested inside a list
        for key, val in temp_bounds.items():
            if isinstance(val, list):
                for i, v in enumerate(val):
                    if not isinstance(v, str):
                        continue
                    elif hasattr(instance, v):
                        val[i] = getattr(instance, v)
            else:
                if hasattr(instance, str(val)):
                    temp_bounds[key] = getattr(instance, val)
        self.validator_func.kwargs = temp_bounds
        try:
            msg = self.validator_func.invoke(value)
            if msg is not None:
                self.logger.error(msg)
        except ValueError as e:
            raise ValueError(
                f"ValidationTest failed for field '{self.name}': {e}")
        self._set_attr(instance, value)


class Validator_Slotted(Validator):
    # annotated_type: type
    # value_type: type
    # sub_value_type: type
    # sub_annotated_type: type = type(None)
    __slots__ = ('name', 'annotated_type', 'value_type', 'sub_value_type', 'sub_annotated_type',
                 'cleaning_func', 'validator_func', 'default', 'allow_none', 'omit_logging', 'logger')
    """class for validation of arguments Dataclass Args:\n
       Args:
        func (function): callback function which will either run successfully \
            or raise a Value Error
        value_list (list): reference list for checking for inclusion of the \
            value
        value_range (list): list of form [minValue, maxValue] for checking \
            if value is in between, if None is set for maxValue or minValue, \
            performs one sided check
        default (any): default value which is dependent on the type annotation\
             the class is instantiated with
        allow_none (bool): accept None as set Value, if False and default is None\
            raises TypeError when no argument is passed
        **kwargs: additional arguments for the callback function for special\
             cases
       Raises:
        ValueError: if the Validation fails
        TypeError: if the type in value_list or value_range don't match

       Returns:
        either the default value or the value passed by the owner class \
        defaults itself to none   
    """

    def __init__(self,
                 validator_func: Function_Mapper = None,
                 cleaning_func: Function_Mapper = None,
                 default: Any = False,
                 allow_none: bool = False,
                 omit_logging: bool = False):

        self.cleaning_func = cleaning_func
        self.validator_func = validator_func
        self.allow_none = allow_none
        self.default = default
        self.omit_logging = omit_logging
        self.init_logger()

    def init_logger(self):

        self.logger = logging.getLogger()
        self.logger = log_util.init_console_logger(self.logger)
        self.logger = log_util.init_file_logger(self.logger)

    def __repr__(self) -> str:
        return str(self.default)

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        if not instance:
            return self
        return getattr(instance, "_" + self.name)

    def __delete__(self, instance):
        delattr(instance, "_" + self.name)

    def _set_attr(self, instance, value):
        setattr(instance, "_" + self.name, value)