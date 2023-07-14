import copy
import json
from typing import Any, List
from unittest import TestCase
from sample.example_dataclasses import Person
from data_validation.exceptions import CastException, UnexpectedCastException
import pathlib as pl
import sys

from sample.example_dataclasses import Team as Team
from tests import TEST_FILE_PATH


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
