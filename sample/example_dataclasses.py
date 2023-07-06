from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List

import sys
import data_validation.init_loggers as log_util
from data_validation.data_parsing import DataWrapper
from data_validation.validation import Validator, TypeHandler, Validator_Slotted, ValidationMeta
from sample.example_custom_validations import Email_Validation, Precise_Email_Validation_dynamic
from .example_type_mapping import _cast_to_bool_from_int, _cast_to_date_from_str


log_util.LoggingConfig.set_log_directory("./logs")
TypeHandler.add_type_mapping(
    incoming_type=str,
    casted_type=date,
    func=_cast_to_date_from_str,
    dateformat="%Y/%m/%d"
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


@dataclass
class Person(DataWrapper):
    first_name: str = Validator(allow_none=True)
    last_name: str = Validator()
    date_of_birth: date = Validator()
    occupation: Occupations = Validator()
    gender: Gender = Validator()
    person_id: int = Validator()
    is_smoker: bool = Validator(default=False)
    email: str = Validator(validator_func=Email_Validation,
                           default=None,
                           allow_none=True)


@dataclass
class PrecisePerson():
    first_name: str = Validator(allow_none=True)
    last_name: str = Validator()
    date_of_birth: date = Validator()
    occupation: Occupations = Validator()
    gender: Gender = Validator()
    person_id: int = Validator()
    is_smoker: bool = Validator(default=False)
    email: str = Validator(validator_func=Precise_Email_Validation_dynamic,
                           default=None,
                           allow_none=True)


@dataclass
class Person_with_slots(metaclass=ValidationMeta):
    first_name: str = Validator_Slotted()

    def __init__(self,
                 first_name) -> None:
        self.first_name = first_name


# @dataclass(slots=True)
# class Person_dummy(metaclass=ValidationMeta):
#     first_name: str = Validator(default="hans")

#     def __init__(self, first_name: str):
#         self.first_name = first_name

@dataclass
class Job_Position(DataWrapper):
    occupied_by: Person
    name: str = Validator()
    position_id: int = Validator()


@dataclass
class Team_OLD_TYPING(DataWrapper):
    individuals: List[Person]

@dataclass
class Team_NEW_TYPING(DataWrapper):
    individuals: list[Person]


# personA = Person_with_slots("peter")
# person = Person_with_slots("Hans")
# person.first_name = 2
