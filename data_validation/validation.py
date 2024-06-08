from __future__ import annotations
import logging
from types import MappingProxyType


from data_validation.data_parsing import Container
from data_validation.exceptions import CastException
from data_validation.function_wrappers import ArgFunctionWrapper, FunctionWrapper
import data_validation.init_loggers as log_util
from datetime import datetime
from copy import deepcopy
from collections.abc import Callable
from typing import Any, Generic, Sequence
from enum import Enum, auto
from typing import Dict, Tuple, TypeVar

from data_validation.data_casting_func import (
    _cast_to_bool_from_int,
    _cast_int_to_datetime,
    _cast_float_to_int,
    _cast_to_bool_from_str,
    _cast_int_to_float,
    _cast_str_to_datetime,
)


class Scope(Enum):
    ITEM = auto()
    """maps the validation function onto the individual elements of a Iterable,
    i.e. length > 5 for each of the string values within a list"""
    COLLECTION = auto()
    """checks a certain property on the enclosing Iterable, i.e. length of the list > 5"""


DEFAULT_TYPE_MAPPING: MappingProxyType[Tuple[type], ArgFunctionWrapper] = {
    (int, bool): ArgFunctionWrapper(_cast_to_bool_from_int),
    (float, int): ArgFunctionWrapper(_cast_float_to_int),
    (int, datetime): ArgFunctionWrapper(_cast_int_to_datetime),
    (str, bool): ArgFunctionWrapper(_cast_to_bool_from_str),
    (int, float): ArgFunctionWrapper(_cast_int_to_float),
    (str, datetime): ArgFunctionWrapper(_cast_str_to_datetime),
}


class State(Enum):
    SET = auto()
    NOT_SET = auto()


class DefaultTypeHandler:
    """
    provides a standardized way to handle type casting the default \n
    implementation is meant as a fallback instantiate the class to
    overwrite default behavior

    Attributes:
        TYPE_MAPPING: Dict[Tuple[type], ArgFunctionWrapper]:
            Provides a Mapping composed of original and destination type and cast-function,\n
            this attribute can and should be expanded
    """

    TYPE_MAPPING: MappingProxyType[Tuple[type], ArgFunctionWrapper]

    def __init__(
        self,
        source_type: type = None,
        dest_type: type = None,
        casting_fct: ArgFunctionWrapper = None,
        type_mapping: Dict[Tuple[type], ArgFunctionWrapper] = {},
        omit_default: bool = False,
    ) -> None:
        """Constructs a Instance with or without default types and the custom casting added.

        Args:
            source_type (type, optional): type of the source. Defaults to None.
            dest_type (type, optional): type of the destination. Defaults to None.
            casting_fct (ArgFunctionWrapper, optional): ArgsFunctionWrapper instance. \
                Defaults to None.
            type_mapping(dict): Pre-initialized custom type Mapping of the same Signature or \
                DEFAULT_TYPE_MAPPING
            omit_default (bool, optional): if type_mapping should be pre-initialized or empty. \
                Defaults to False.
        """
        if not omit_default:
            custom_mapping = deepcopy(DEFAULT_TYPE_MAPPING)
            custom_mapping.update(type_mapping)
            self.TYPE_MAPPING = MappingProxyType(custom_mapping)
        elif type_mapping or not omit_default:
            self.TYPE_MAPPING = MappingProxyType(type_mapping)
        else:
            self.TYPE_MAPPING = MappingProxyType(DEFAULT_TYPE_MAPPING)

        if source_type and dest_type and casting_fct:
            assert (
                source_type != dest_type
            ), "source_type and destination type can not be the same!"
            temp_dict = {}
            temp_dict[(source_type, dest_type)] = casting_fct
            self.TYPE_MAPPING = MappingProxyType(temp_dict)
        else:
            assert (
                source_type is None and dest_type is None and casting_fct is None
            ), "either no args or all args need be passed"


ValidatedClass = TypeVar("ValidatedClass")


class Validator(Generic[ValidatedClass]):
    """
    This Descriptor class manages the general UseCase of Type Checking and Data validation
    
    Attributes:
        annotated_type (type): type hint from assigned field\n
        value_type (type): type of the passed value
        sub_value_type (type): type of the items of a Sequence type (e.g. list, tuple, set)
        sub_annotated_type (type): type of the type hints of the items of a Sequence e.g. List[str]
    Raises:
        ValueError: if the Validation fails
    """

    _annotated_type: type
    _value_type: type
    _sub_value_type: type
    _sub_annotated_type: type = type(None)

    def __init__(
        self,
        cleaning_func: ArgFunctionWrapper = None,
        type_handler: DefaultTypeHandler = DefaultTypeHandler(),
        validator_func: ArgFunctionWrapper = None,
        default: Any = State.NOT_SET,
        allow_none: bool = False,
        validation_scope: Scope = Scope.ITEM,
        logger: logging.Logger = None,
        omit_logging: bool = False,
    ):
        """
        Args:
            cleaning_func (FunctionWrapper, optional): \
                custom preprocessing before value is passed to type_handler instance and \
                validation func. Defaults to None.\n
            type_handler (DefaultTypeHandler, optional): \
                Custom TypeHandler to include. Defaults to DefaultTypeHandler().\n
            validator_func (FunctionWrapper, optional): \
                custom Validation Functionality. Defaults to None.
            default (Any, optional):\n
                Default for value the Descriptor is assigned to. Defaults to False.\n
            allow_none (bool, optional):\n
                if None is a valid Value. Defaults to False.\n
            validation_scope (Scope, optional): if the assigned field is of type Sequence \
                (e.g. list, tuple, sets), determines whether the validation is applied to the \
                elements or the collection itself. Defaults to Scope.ITEM.
            omit_logging (bool, optional):\n
                option to suppress all logging caused by the field. Defaults to False.
        """
        self._cleaning_func = cleaning_func
        self._type_handler = type_handler
        self._validator_func = validator_func
        self._allow_none = allow_none
        self._default = default
        self._validation_scope = validation_scope
        self._omit_logging = omit_logging
        if logger:
            self._logger = logger
        else:
            self.init_logger()

    def init_logger(self):
        self._logger = logging.getLogger()
        self._logger = log_util.init_console_logger(self._logger)
        self._logger = log_util.init_file_logger(self._logger)

    def __call__(
        self,
        type_handler: DefaultTypeHandler = None,
        validator_func: ArgFunctionWrapper = None,
        cleaning_func: ArgFunctionWrapper = None,
        default: Any = State.NOT_SET,
        allow_none: bool = None,
        validation_scope: Scope = None,
        omit_logging: bool = False,
    ) -> Validator:
        """ factory method, will invoke the instance with predefined settings, but enables \
            overwriting of specific values
        Args:
            type_handler (DefaultTypeHandler, optional): Custom TypeHandler to include.\
                  Defaults to DefaultTypeHandler().\n
            validator_func (FunctionWrapper, optional):\n
                custom Validation Functionality. Defaults to None.\n
            cleaning_func (FunctionWrapper, optional):\n
                custom preprocessing before value is passed to type_handler instance and\
                    validation func. Defaults to None.\n
            default (Any, optional):\n
                Default for value the Descriptor is assigned to. Defaults to False.\n
            allow_none (bool, optional):\n
                if None is a valid Value. Defaults to False.\n
            validation_scope (Scope, optional): if the assigned field is of type Sequence \
                (e.g. list, tuple, sets), determined whether the validation is applied to \
                the elements or the collection itself. Defaults to Scope.ITEM.\n
            omit_logging (bool, optional):\n
                option to suppress all logging caused by the field. Defaults to False.
        """

        type_handler = self._type_handler if type_handler is None else type_handler
        validator_func = (
            self._validator_func if validator_func is None else validator_func
        )
        cleaning_func = self._cleaning_func if cleaning_func is None else cleaning_func
        default = self._default if default == State.NOT_SET else default
        allow_none = self._allow_none if allow_none is None else allow_none
        validation_scope = (
            self._validation_scope if validation_scope is None else validation_scope
        )
        omit_logging = self._omit_logging if omit_logging is None else omit_logging

        return Validator(
            cleaning_func=cleaning_func,
            type_handler=type_handler,
            validator_func=validator_func,
            default=default,
            allow_none=allow_none,
            validation_scope=validation_scope,
            logger=self._logger,
            omit_logging=omit_logging,
        )

    def __repr__(self) -> str:
        return str(self._default)

    def __set_name__(self, owner, name: str):
        if name.startswith("_"):
            self._name = name[1:]
        else:
            self._name = name

    def __get__(self, instance: ValidatedClass, owner):
        if not instance:
            return self
        return instance.__dict__.get(self._name, self._default)

    def __delete__(self, instance):
        del instance.__dict__[self._name]

    def _set_attr(self, instance, value):
        instance.__dict__[self._name] = value

    def _handle_None(self):
        if not self._allow_none:
            raise ValueError(
                f"field <{self._name}> is not allowed to be None, if this is undesired, "
                + "consider changing this behavior by setting <allow_none=True> in Validator-"
                + "Constructor"
            )
        return None

    def _handle_default_case(self, instance, value):
        if self._default == State.NOT_SET:
            raise TypeError(
                f"{instance.__class__.__name__}() missing 1 required "
                + f"positional argument: '{self._name}' with no default value defined"
            )

        if not self._omit_logging and value is None:
            self._logger.warn(
                f"field '{self._name}' in Parent-field "
                + f"'{instance.__class__.__name__}' was not passed defaulting to {self._default}"
            )
        # handle case where a field is equal to another field,
        # e.g. output_dir = input_dir
        if isinstance(self._default, str) and hasattr(instance, self._default):
            value = getattr(instance, self._default)
        else:
            value = self._default
        return value

    def _handle_Sequences(self, instance, value):
        self._sub_annotated_type = self._annotated_type.__args__[0]
        self._annotated_type = getattr(self._annotated_type, "__origin__")
        # return if list is empty
        if not value:
            self._sub_value_type = None
            return
        self._sub_value_type = type(value[0])

    def _handle_callables(self, value, type_tuple):
        if type_tuple[0] == dict:
            return type_tuple[1](**value)
        if isinstance(type_tuple[0], Sequence) and not type_tuple[1] == str:
            return type_tuple[1](*value)
        try:
            return type_tuple[1](value)
        except ValueError:
            self._logger.error(
                f"value {value} is not a valid option of {type_tuple[1]}"
            )
            if not self._allow_none:
                raise CastException(
                    input_type=self._value_type,
                    output_type=type_tuple[1],
                    message=f"value '{value}' is not a valid option",
                )
            return None

    def _handle_casting(self, instance, type_tuple: Tuple[type], value, multiple: bool):
        if type_tuple[0] == type_tuple[1]:
            return value

        if type_tuple not in self._type_handler.TYPE_MAPPING.keys():
            # treat primitive type mismatch as "real" typeError
            if self._annotated_type in [str, int, float, bool]:
                raise TypeError(
                    f"invalid type provided for attribute: {self._name} \n"
                    + f"  expected type {self._annotated_type}, received <value> \n"
                    + f"  {value} of type {self._value_type}"
                )
            if isinstance(type_tuple[1], Callable):
                try:
                    if multiple:
                        tempWrapper = ArgFunctionWrapper(
                            self._handle_callables, type_tuple=type_tuple
                        )
                        return list(map(tempWrapper, value))
                    else:
                        return self._handle_callables(value, type_tuple)
                # assume a type_mapping to a complex type is missing
                except CastException as e:
                    raise e
                except Exception as e:
                    raise NotImplementedError(
                        f"value of type {self._value_type} could not be automatically casted to {self._annotated_type}, "
                        + f"trying yielded Error: {e}"
                    )
        cast_fct = self._type_handler.TYPE_MAPPING[type_tuple]
        self._resolve_instance_attr_ref(instance, cast_fct)
        if multiple:
            return map(cast_fct, value)
        else:
            return cast_fct(value)

    def __set__(self, instance: ValidatedClass, value):
        if self._name.startswith("_"):
            self._name = self._name[1:]

        self._annotated_type = instance.__annotations__[self._name]
        self._value_type = type(value)

        if value is self:
            value = self._handle_default_case(instance, value)
            return

        if (
            hasattr(self._annotated_type, "__origin__")
            and isinstance(value, Sequence)
            and not isinstance(value, str)
        ):
            self._handle_Sequences(instance, value)
            multiple = True
            type_tuple = (self._sub_value_type, self._sub_annotated_type)
        else:
            multiple = False
            type_tuple = (self._value_type, self._annotated_type)

        if value is None:
            self._handle_None()
            return
        try:
            value = self._handle_casting(
                instance=instance, type_tuple=type_tuple, value=value, multiple=multiple
            )
        except CastException as e:
            if issubclass(self._annotated_type, Container):
                raise CastException(
                    f"Subclass {instance.__class__.__name__} with field name {self._name} failed to initialize due to:\n {e}"
                )
            else:
                raise CastException(
                    f"attribute '{self._name}' in Class '{instance.__class__.__name__}' could not be set due to:\n {e}"
                )

        # apply function to clean the possible values
        if self._cleaning_func:
            self._resolve_instance_attr_ref(instance, self._cleaning_func)
            value = self._cleaning_func(value)

        # handle trivial case where types match
        try:
            if isinstance(value, self._annotated_type) and self._validator_func is None:
                self._set_attr(instance, value)
                return
        except TypeError:
            pass
        if self._validator_func is None:
            self._set_attr(instance, value)
            return

        self._perform_validation(instance, value)
        return

    def _resolve_instance_attr_ref(
        self, instance: ValidatedClass, functionWrapper: FunctionWrapper
    ):
        """for getting proxy reference e.g. output_path = "input_path" with "input_path" being a
        reference to the field input_path of the class itself same with the reference nested
        inside a list

        Args:
            instance (_type_): _description_
            functionWrapper (FunctionWrapper): _description_
        """
        temp_dict = deepcopy(functionWrapper.kwargs)
        for key, val in temp_dict.items():
            if isinstance(val, Sequence) and not isinstance(val, str):
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

        self._resolve_instance_attr_ref(instance, self._validator_func)
        try:
            if (
                not isinstance(value, Sequence) or isinstance(value, str)
            ) or self._validation_scope == Scope.COLLECTION:
                msg = self._validator_func(value)
            else:
                if not self._validation_scope == Scope.ITEM:
                    raise ValueError("Improper usage of Validator class")
                msg_list = [self._validator_func(item) for item in value]
                msg_list = [m for m in msg_list if m]
                msg = ",\n".join(msg_list)

            if msg is not None:
                self._logger.error(msg)
        except ValueError as e:
            raise ValueError(f"Validation Test failed for field '{self._name}': {e}")
        self._set_attr(instance, value)


class Validator_Slotted(Validator):
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

    # annotated_type: type
    # value_type: type
    # sub_value_type: type
    # sub_annotated_type: type = type(None)
    __slots__ = (
        "_name",
        "_annotated_type",
        "_value_type",
        "_sub_value_type",
        "_sub_annotated_type",
        "_cleaning_func",
        "_validator_func",
        "_default",
        "_allow_none",
        "_omit_logging",
        "_logger",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def init_logger(self):
        self.logger = logging.getLogger()
        self.logger = log_util.init_console_logger(self.logger)
        self.logger = log_util.init_file_logger(self.logger)

    def __repr__(self) -> str:
        return str(self.default)

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, instance, owner):
        if not instance:
            return self
        return getattr(instance, "_" + self._name)

    def __delete__(self, instance):
        delattr(instance, "_" + self._name)

    def _set_attr(self, instance, value):
        setattr(instance, "_" + self._name, value)
