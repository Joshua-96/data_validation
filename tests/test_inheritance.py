import copy
import json
from typing import Any
from unittest import TestCase
from sample.example_dataclasses import Child
from data_validation.exceptions import CastException, UnexpectedCastException
from tests import TEST_FILE_PATH


class Test_Altering(TestCase):
    TEST_DICT: dict
    cur_test_dict: dict

    def setUp(self) -> None:
        with TEST_FILE_PATH.open() as file:
            self.TEST_DICT = json.load(file)["example_child"]
        self.person = Child(**self.TEST_DICT)
        return super().setUp()
    
    def test_regular(self):
        pass