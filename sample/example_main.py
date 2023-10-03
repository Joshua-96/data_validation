from dataclasses import dataclass
from enum import Enum
import json
import pathlib as pl
from typing import List

from data_validation.validation import Validator
from sample.example_custom_validations import Precise_Email_Validation_dynamic
from sample.example_dataclasses import PrecisePerson, Gender
import sample.config as global_vars

path = pl.Path("./sample/example_input.json").resolve()

# simulate command line args or config
input_args = {"dbConfig": "testDB://db@user:pw"}
global_vars.dbConfig = input_args["dbConfig"]


with path.open("r") as inp:
    test_dict = json.load(inp)

person = PrecisePerson(
    first_name="John",
    last_name="Doe",
    date_of_birth="1992/07/26",
    occupation="Professor",
    gender="male",
    hobbies=["abc"],
    person_id=2,
    is_smoker=True,
    email="asdh",
)
print(person.gender)
