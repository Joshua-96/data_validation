import logging
import pathlib as pl
from types import MappingProxyType
from data_validation.exceptions import CastException
import data_validation.init_loggers as log_util
from datetime import datetime
from copy import deepcopy
from functools import partial
from collections.abc import Callable
from typing import Any, Sequence
from enum import Enum, auto
from typing import Dict, Tuple, List

from data_validation.data_casting_func import _cast_to_bool_from_int,\
                                              _cast_to_datetime_from_int,\
                                              _cast_to_int_from_float,\
                                              _cast_to_bool_from_str


class ValidationMeta(type):
    def __new__(cls: type, name: str, bases: tuple, dct: dict):
        
        # if "__annotations__" in dct:
        #     parent_annotations = [b.__annotations__ for b in bases if '__annotations__' in b.__dict__]
        #     dct["__annotations__"] = parent_annotations

        if "__slots__" not in dct and "__annotations__" in dct:
            dct["__slots__"] = (f"_{name}" for name in dct["__annotations__"])

        return super().__new__(cls, name, bases, dct)


class ValidatedClassSlotted(metaclass=ValidationMeta):
    __metaType__: str = "slotted"


class Scope(Enum):
    ITEM = auto()
    COLLECTION = auto()


class FunctionWrapper():
    """
    Enclosing class for calling a specified functions at a later stage with specified *args and **kwargs

    class for validation of arguments Dataclass Args:\n
       Args:
        func (function): callback function which will either run successfully \
            or raise a Value Error
        *args: any additional positional arguments
        **kwargs: any additional keyword arguments
    
       Note:
        Any Arguments Stored can be of type Function_Mapper as well and will be invoked at \
        Invocation of Master Function Mapper

       Returns:
        any value passed from the wrapped function
    """
    value_kw: str
    args: list
    kwargs: dict

    def __init__(self,
                 func: Callable,
                 *args,
                 **kwargs
                 ) -> None:
        self.func = func
        self.init_args = args
        self.args = ()
        self.kwargs = kwargs

    def __call__(self) -> Any:
        """
        invokes the enclosed functions with *args and **kwargs, \n 
        resolves any Callables of each kind of Argument 
        """
        self.kwargs = {k: self._resolve_ref_by_function(v) for k, v in self.kwargs.items()}
        self.args = [self._resolve_ref_by_function(item) for item in self.args]
        return_value = self.func(*self.args, **self.kwargs)
        self.args = ()
        return return_value

    def _resolve_ref_by_function(self, item):
        """
        checks if passed item is of self class and if so calls it's invoke Method
        """
        if not isinstance(item, self.__class__.__base__):
            return item
        return item()


class ArgFunctionWrapper(FunctionWrapper):
    """
    Child Class of Function_Mapper which calls the enclosing function with an argument passed to it

    class for validation of arguments Dataclass Args:\n
       Args:
        func (function): callback function which will either run successfully \
            or raise a Value Error
        value_kw (str): Optional keyword of the value in the enclosing function
        *args: any additional positional arguments
        **kwargs: any additional keyword arguments
    
       Note:
        Any Arguments Stored can be of type Function_Mapper as well and will be invoked at \
        Invocation of Master Function Mapper

       Returns:
        any value passed from the wrapped function
    """
    def __init__(self,
                 func: Callable[..., Any],
                 value_kw: str = None,
                 *args,
                 **kwargs) -> None:
        self.value_kw = value_kw
        super().__init__(func, *args, **kwargs)

    def __call__(self, value) -> Any:
        """invokes the enclosing function with the value provided at runtime, \n
            the value is incorporated into *arg or **kwargs before the\n
            super-implementation is called"""
        if self.value_kw is None:
            self.args = (value,) + tuple(self.init_args)
        else:
            self.kwargs[self.value_kw] = value
        return super().__call__()


DEFAULT_TYPE_MAPPING = {
        (int, bool): ArgFunctionWrapper(_cast_to_bool_from_int),
        (float, int): ArgFunctionWrapper(_cast_to_int_from_float),
        (int, datetime): ArgFunctionWrapper(_cast_to_datetime_from_int),
        (str, bool): ArgFunctionWrapper(_cast_to_bool_from_str),
    }


class DefaultTypeHandler():
    """
    provides a standardized way to handle type casting the default implementation is meant as a 
    fallback instantiate the class to overwrite default behavior

    Attributes:
        TYPE_MAPPING: Dict[Tuple[type], ArgFunctionWrapper]: 
            Provides a Mapping composed of original and destination type and cast-function, this attribute can and should be expanded 
    """

    TYPE_MAPPING: MappingProxyType[Tuple[type], ArgFunctionWrapper]
    

    def __init__(self,
                 source_type: type = None,
                 dest_type: type = None,
                 casting_fct: ArgFunctionWrapper = None,
                 empty: bool = False) -> None:
        """Constructs a Instance with or without default types and the custom casting added.

        Args:
            source_type (type, optional): type of the source. Defaults to None.
            dest_type (type, optional): type of the destination. Defaults to None.
            casting_fct (ArgFunctionWrapper, optional): ArgsFunctionWrapper instance. Defaults to None.
            empty (bool, optional): if type_mapping should be pre-initialized or empty. Defaults to False.
        """        
        if not empty:
            self.TYPE_MAPPING = DEFAULT_TYPE_MAPPING.copy()

        if source_type and dest_type and casting_fct:
            assert source_type != dest_type, "source_type and destination type can not be the same!"
            self.TYPE_MAPPING[(source_type, dest_type)] = casting_fct
        else:
            assert (source_type is None and dest_type is None and casting_fct is None), "either no args or all args need be passed"


class Validator:    
    """
    This Descriptor class manages the general UseCase of Type Checking and Data validation

    class for validation of arguments Dataclass Args:\n

       Attributes:
        ----------\n
        annotated_type: type
            type hint from assigned field
        value_type: type
            type of the passed value
        sub_value_type: type
            type of the items of a Sequence type (e.g. list, tuple, set)
        sub_annotated_type: type = type(None)
            type of the type hints of the items of a Sequence e.g. List[str]
       Raises:
        ValueError: if the Validation fails
        TypeError: if the type in value_list or value_range don't match

       Returns:
        either the default value or the value passed by the owner class \
        defaults itself to none   
    """
    annotated_type: type
    value_type: type
    sub_value_type: type
    sub_annotated_type: type = type(None)

    def __init__(self,
                 type_handler: DefaultTypeHandler = DefaultTypeHandler(), 
                 validator_func: ArgFunctionWrapper = None,
                 cleaning_func: ArgFunctionWrapper = None,
                 default: Any = False,
                 allow_none: bool = False,
                 validation_scope: Scope = Scope.ITEM,
                 logger: logging.Logger = None,
                 omit_logging: bool = False):
        """_summary_

        Args:
            type_handler (DefaultTypeHandler, optional):\n 
                Custom TypeHandler to include. Defaults to DefaultTypeHandler().\n
            validator_func (FunctionWrapper, optional):\n 
                custom Validation Functionality. Defaults to None.\n
            cleaning_func (FunctionWrapper, optional):\n 
                custom preprocessing before value is passed to type_handler instance and validation func. Defaults to None.\n
            default (Any, optional):\n
                Default for value the Descriptor is assigned to. Defaults to False.\n
            allow_none (bool, optional):\n
                if None is a valid Value. Defaults to False.\n
            validation_scope (Scope, optional): if the assigned field is of type Sequence \n
                (e.g. list, tuple, sets), determined whether the validation is applied to the elements or the collection itself. Defaults to Scope.ITEM.\n
            omit_logging (bool, optional):\n
                option to suppress all logging caused by the field. Defaults to False.
        """
        self.type_handler = type_handler
        self.cleaning_func = cleaning_func
        self.validator_func = validator_func
        self.allow_none = allow_none
        self.default = default
        self.validation_scope = validation_scope
        self.omit_logging = omit_logging
        if logger:
            self.logger = logger
        else:
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

        if self.default is False and self.annotated_type != bool:
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

    def _handle_Sequences(self, instance, value):
        self.sub_annotated_type = self.annotated_type.__args__[0]
        self.annotated_type = getattr(self.annotated_type, "__origin__")
        # return if list is empty
        if not value:
            self.sub_value_type = None
            return
        self.sub_value_type = type(value[0])

    def _handle_callables(self, value, type_tuple):
        if type_tuple[0] == dict:
            return type_tuple[1](**value)
        if isinstance(type_tuple[0], Sequence) and not type_tuple[1] == str:
            return type_tuple[1](*value)
        try:
            return type_tuple[1](value)
        except ValueError:
            self.logger.error(
                f"value {value} is not a valid option of {type_tuple[1]}")
            if not self.allow_none:
                raise CastException(input_type=self.value_type,
                                    output_type=type_tuple[1],
                                    message=f"value <{value}> is not a valid option")
            return None

    def _handle_casting(self, type_tuple: Tuple[type], value, multiple: bool):
        if type_tuple[0] == type_tuple[1]:
            return value

        if type_tuple not in self.type_handler.TYPE_MAPPING.keys():
            # treat primitive type mismatch as "real" typeError
            if self.annotated_type in [str, int, float, bool]:
                raise TypeError(f"expected type {self.annotated_type}, received {self.value_type}")
            if isinstance(type_tuple[1], Callable):
                try:
                    if multiple:
                        tempWrapper = ArgFunctionWrapper(self._handle_callables, type_tuple=type_tuple)
                        return list(map(tempWrapper, value))
                    else:
                        return self._handle_callables(value, type_tuple)
            # assume a type_mapping to a complex type is missing
                except CastException as e:
                    raise ValueError(f"Improper Value: {e}")
                except Exception as e:
                    raise NotImplementedError(
                        f"value of type {self.value_type} could not be automatically casted to {self.annotated_type}, " +
                        f"trying yielded Error: {e}")

        cast_fct = self.type_handler.TYPE_MAPPING[type_tuple]
        if multiple:
            return map(cast_fct, value)
        else:
            return cast_fct(value)

    def __set__(self, instance: object, value):
        if self.name.startswith("_"):
            self.name = self.name[1:]

        self.annotated_type = instance.__annotations__[self.name]
        self.value_type = type(value)
        
        if value is self:
            value = self._handle_default_case(instance, value)
            return
        
        if hasattr(self.annotated_type, "__origin__"):
            self._handle_Sequences(instance, value)
            multiple = True
            type_tuple = (self.sub_value_type, self.sub_annotated_type)
        else:
            multiple = False
            type_tuple = (self.value_type, self.annotated_type) 

        if value is None:
            self._handle_None()
            return
        value = self._handle_casting(type_tuple=type_tuple, value=value, multiple=multiple)
        # handle trivial case where types match
        if isinstance(value, self.annotated_type) and self.validator_func is None:
            self._set_attr(instance, value)
            return

        # apply function to clean the possible values
        if self.cleaning_func:
            value = self.cleaning_func(value)

        if self.validator_func is None:
            self._set_attr(instance, value)
            return
        
        self._perform_validation(instance, value)
        return


    def _resolve_instance_attr_ref(self, instance, functionWrapper: FunctionWrapper):
        temp_dict = deepcopy(functionWrapper.kwargs)
        for key, val in temp_dict.items():
            if isinstance(val, list):
                for i, v in enumerate(val):
                    if not isinstance(v, str):
                        continue
                    elif hasattr(instance, v):
                        val[i] = getattr(instance, v)
            else:
                if hasattr(instance, str(val)):
                    temp_dict[key] = getattr(instance, val)
        functionWrapper.kwargs = temp_dict

    def _perform_validation(self, instance, value):
        # for getting proxy reference e.g. outputpath = "inputpath" with "inputpath" being a reference to the
        # field inputpath of the class itself same with the reference nested inside a list
        self._resolve_instance_attr_ref(instance, self.validator_func)
        try:
            if (not isinstance(value, Sequence) or isinstance(value, str))\
                    or self.validation_scope == Scope.COLLECTION:
                msg = self.validator_func(value)
            else:
                if not self.validation_scope == Scope.ITEM:
                    raise ValueError("Improper usage of Validator class")
                msg_list = [self.validator_func(item) for item in value]
                msg_list = [m for m in msg_list if m]
                msg = ",\n".join(msg_list)

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
                 validator_func: FunctionWrapper = None,
                 cleaning_func: FunctionWrapper = None,
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