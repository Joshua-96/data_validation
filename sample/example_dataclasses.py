from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Tuple

import sys
import data_validation.init_loggers as log_util
from data_validation.data_parsing import Container
from data_validation.validation import (
    ArgFunctionWrapper,
    FunctionWrapper,
    Scope,
    Validator,
    DefaultTypeHandler,
    Validator_Slotted,
    ValidationMeta,
)
from data_validation.validation_func import has_length
from sample.example_custom_validations import (
    Email_Validation,
    Precise_Email_Validation_dynamic,
)
from sample.example_type_mapping import _cast_from_int_to_bool_, _cast_from_str_to_date


log_util.LoggingConfig.set_log_directory("./logs")
default_date_handler = DefaultTypeHandler(
    source_type=str,
    dest_type=date,
    casting_fct=ArgFunctionWrapper(_cast_from_str_to_date, dateformat="%Y/%m/%d"),
)

special_date_handler = DefaultTypeHandler(
    source_type=str,
    dest_type=date,
    casting_fct=ArgFunctionWrapper(_cast_from_str_to_date, dateformat="%m/%d/%Y"),
)


class Occupations(Enum):
    TEACHER = "Teacher"
    PROFESSOR = "Professor"
    BUS_DRIVER = "Busdriver"
    JANITOR = "Janitor"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


defaultValidator = Validator()
date_Validator = Validator(type_handler=default_date_handler)

commaSeparatedValidator = Validator(
    default=[],
    type_handler=DefaultTypeHandler(
        source_type=str, dest_type=List[str], casting_fct=lambda x: x.split(",")
    ),
)

emailValidator = Validator(
    validator_func=Email_Validation, default=None, allow_none=True
)

validatorWithNone = Validator(allow_none=True)

date_ValidatorWithNone = Validator(
    type_handler=default_date_handler, allow_none=True, default=None
)


@dataclass
class Person(Container):
    first_name: str = validatorWithNone()
    last_name: str = defaultValidator()
    date_of_birth: date = date_Validator()
    occupation: Occupations = defaultValidator()
    gender: Gender = defaultValidator()
    hobbies: List[str] = commaSeparatedValidator()
    person_id: int = defaultValidator()
    is_smoker: bool = defaultValidator()
    email: str = emailValidator()


@dataclass
class UnPrecisePerson(Container):
    first_name: str = defaultValidator()
    last_name: str = defaultValidator()
    date_of_birth: date = date_ValidatorWithNone()
    occupation: Occupations = Validator(allow_none=True, default=None)
    gender: Gender = Validator()
    hobbies: List[str] = Validator(default=[])
    person_id: int = Validator()
    is_smoker: bool = Validator(default=False)
    email: str = Validator(
        validator_func=Email_Validation, default=None, allow_none=True
    )


@dataclass
class PrecisePerson:
    first_name: str = Validator(allow_none=True)
    last_name: str = Validator()
    date_of_birth: date = Validator(type_handler=default_date_handler)
    occupation: Occupations = Validator()
    hobbies: List[str] = Validator(
        allow_none=True,
        validator_func=ArgFunctionWrapper(
            func=has_length, value_kw="value", value_range=[3, None]
        ),
    )
    gender: Gender = Validator()
    person_id: int = Validator()
    is_smoker: bool = Validator(default=False, allow_none=True)
    email: str = Validator(
        validator_func=Precise_Email_Validation_dynamic, default=None, allow_none=True
    )


@dataclass
class Person_with_slots(Container):
    first_name: str = Validator_Slotted()

    def __init__(self, first_name) -> None:
        self.first_name = first_name


@dataclass
class Job_Position(Container):
    occupied_by: Person
    name: str = Validator()
    position_id: int = Validator()


@dataclass
class Team(Container):
    individuals: List[Person]


@dataclass
class Child(Person):
    occupation: Occupations = Validator(allow_none=True)
    school_attendance: bool = Validator()
    parents: Tuple[UnPrecisePerson] = Validator(
        validator_func=ArgFunctionWrapper(has_length, value_range=[None, 2]),
        validation_scope=Scope.COLLECTION,
    )
