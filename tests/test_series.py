import copy
import json
from typing import Any, List
from unittest import TestCase
from sample.example_dataclasses import Person
from data_validation.exceptions import CastException, UnexpectedCastException
import pathlib as pl
import sys

if sys.version.startswith("3.9"):
    from sample.example_dataclasses import Team_OLD_TYPING as Team
else:
    from sample.example_dataclasses import Team_NEW_TYPING as Team


TEST_FILE_PATH = pl.Path("./sample/example_input.json")


class Test_Altering(TestCase):
    PERSONS: List[Person]
    TEAM: Team
    cur_test_dict: dict

    def setUp(self) -> None:
        with TEST_FILE_PATH.open() as file:
            self.PERSONS = json.load(file)["team"]
        return super().setUp()

    def test_regular(self):
        Team(individuals=self.PERSONS)

    def test_single_item_list(self):
        Team(individuals=[self.PERSONS[0]])
