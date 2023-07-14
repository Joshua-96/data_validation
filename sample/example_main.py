from dataclasses import dataclass
from enum import Enum
import json
import pathlib as pl
from typing import List

from data_validation.validation import Validator

path = pl.Path("./sample/example_input.json").resolve()


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


with path.open("r") as inp:
    test_dict = json.load(inp)


@dataclass
class Person:
    first_name: str = Validator()
    last_name: str = Validator()
    gender: Gender = Validator()
    hobbies: List[str] = Validator()
    person_id: int = Validator()
    is_smoker: bool = Validator()
    email: str = Validator()


person = Person(
    first_name="John",
    last_name="Doe",
    gender="male",
    hobbies=["ab"],
    person_id=2,
    is_smoker=True,
    email="asdh",
)
print(person.gender)
