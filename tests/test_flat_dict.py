import copy
import json
from typing import Any
from unittest import TestCase
from sample.example_dataclasses import Person
from data_validation.exceptions import CastException, UnexpectedCastException
import pathlib as pl


TEST_FILE_PATH = pl.Path("./sample/example_input.json")


class Test_Altering(TestCase):
    TEST_DICT: dict
    cur_test_dict: dict

    def setUp(self) -> None:
        with TEST_FILE_PATH.open() as file:
            self.TEST_DICT = json.load(file)["single_person"]
        self.person = Person(**self.TEST_DICT)
        return super().setUp()

    def test_regular(self):
        pass

    def test_Enum_Mismatch(self):
        self.assertRaises(
             CastException,
             setattr,
             *[self.person, "occupation", "invalid"])

    def test_Type_Mismatch(self):
        self.assertRaises(
            TypeError,
            setattr,
            *[self.person, "first_name", 23]
        )

    def test_FormatError(self):
        self.assertRaises(
            CastException,
            setattr,
            *[self.person, "date_of_birth", "invalid"]
        )

    def test_cast_int_str(self):
        self.person.person_id = 23

    def test_cast_int_float(self):
        self.person.person_id = 23.0

    def test_cast_int_float_precision_loss(self):
        self.assertRaises(
            ValueError,
            setattr,
            *[self.person, "person_id", 23.5]
        )

    def test_invalid_cast(self):
        self.assertRaises(
            ValueError,
            setattr,
            *[self.person, "person_id", "invalid"]
        )

    def test_cast_bool_int(self):
        self.person.is_smoker = 1
        self.person.is_smoker = 0
    
    def test_cast_bool_str(self):
        self.person.is_smoker = "TRUE"
        self.person.is_smoker = "FALSE"

    def test_invalid_bool_cast_int(self):
        self.assertRaises(
            TypeError,
            setattr,
            *[self.person, "is_smoker", 2]
        )

    def test_invalid_bool_cast_str(self):
        self.assertRaises(
            ValueError,
            setattr,
            *[self.person, "is_smoker", "abc"]
        )

    def test_allowed_None(self):
        self.person.first_name = None

    def test_unallowed_None(self):
        self.assertRaises(
            ValueError,
            setattr,
            *[self.person, "last_name", None]
        )


class Test_Construction(TestCase):
    TEST_DICT: dict

    def setUp(self) -> None:
        with TEST_FILE_PATH.open() as file:
            self.TEST_DICT = json.load(file)["single_person"]

    def test_unallowed_missing_default(self):
        test_dict = copy.deepcopy(self.TEST_DICT)
        test_dict.pop("first_name")
        self.assertRaises(
            TypeError,
            Person,
            **test_dict
        )

    def test_unallowed_missing(self):
        test_dict = copy.deepcopy(self.TEST_DICT)
        test_dict.pop("last_name")
        self.assertRaises(
            TypeError,
            Person,
            **test_dict
        )
