import copy
import json
from typing import Any
from unittest import TestCase
from sample.example_dataclasses import Job_Position
from data_validation.exceptions import CastException, UnexpectedCastException
import pathlib as pl


TEST_FILE_PATH = pl.Path("./sample/example_input.json")


class Test_Altering(TestCase):
    TEST_DICT: dict
    cur_test_dict: dict

    def setUp(self) -> None:
        with TEST_FILE_PATH.open() as file:
            self.TEST_DICT = json.load(file)["job_position"]
        self.person = Job_Position(**self.TEST_DICT)
        return super().setUp()
    
    def test_regular(self):
        pass