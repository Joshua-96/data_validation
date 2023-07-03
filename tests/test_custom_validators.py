import copy
import json
from typing import Any
from unittest import TestCase
from sample.example_dataclasses import PrecisePerson
from data_validation.exceptions import CastException, UnexpectedCastException
import pathlib as pl


TEST_FILE_PATH = pl.Path("./sample/example_input.json")


class Test_Altering(TestCase):
    TEST_DICT: dict
    cur_test_dict: dict

    def setUp(self) -> None:
        with TEST_FILE_PATH.open() as file:
            self.TEST_DICT = json.load(file)["single_person"]
        self.person = PrecisePerson(**self.TEST_DICT)
        return super().setUp()

    def test_regular(self):
        pass

    def test_invalid_email_first_name(self):
        self.assertRaises(
            ValueError,
            setattr,
            *[self.person, "email", "john@gmail.com"]
        )
    
    def test_invalid_email_last_name(self):
        self.assertRaises(
            ValueError,
            setattr,
            *[self.person, "email", "doe@gmail.com"]
        )
    
    def test_invalid_email_domain(self):
        self.assertRaises(
            ValueError,
            setattr,
            *[self.person, "email", "john.doe@spammer.io"]
        ) 