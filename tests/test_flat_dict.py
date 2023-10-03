import copy
import json
from typing import Any
from unittest import TestCase
from sample.example_dataclasses import Person
from data_validation.exceptions import CastException, UnexpectedCastException
from tests import TEST_FILE_PATH

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
        with self.assertRaises(CastException) as cm:
            self.person.occupation = "invalid"
        # self.assertTrue(isinstance(cm.exception, CastException), f"Exception: {cm.exception}")

    def test_Type_Mismatch(self):
        with self.assertRaises(TypeError) as cm:
            self.person.first_name = 23

    def test_FormatError(self):
        with self.assertRaises(CastException) as cm:
            self.person.date_of_birth = "invalid"

    def test_cast_int_str(self):
        self.person.person_id = 23

    def test_cast_int_float(self):
        self.person.person_id = 23.0

    def test_cast_float_int(self):
        self.person.weight = 79

    def test_cast_int_float_precision_loss(self):
        # self.assertRaises(
        #     CastException,
        #     setattr,
        #     self.person,
        #     23.5)
        with self.assertRaises(Exception) as cm:
            self.person.person_id = 23.5
        self.assertTrue(isinstance(cm.exception, CastException))

    def test_invalid_cast(self):
        with self.assertRaises(Exception) as cm:
            self.person.person_id = "invalid"
        self.assertTrue(isinstance(cm.exception, TypeError))


    def test_cast_bool_int(self):
        self.person.is_smoker = 1
        self.person.is_smoker = 0
    
    def test_cast_bool_str(self):
        self.person.is_smoker = "TRUE"
        self.person.is_smoker = "FALSE"

    def test_list_assignment(self):
        self.person.hobbies = ["auhb", "jiouasn"]

    def test_string_expansion(self):
        self.person.hobbies = "soccer,baseball"
        self.assertIsInstance(self.person.hobbies, list)

    def test_invalid_bool_cast_int(self):
        with self.assertRaises(Exception) as cm:
            self.person.is_smoker = 2
        self.assertTrue(isinstance(cm.exception, CastException))

    def test_invalid_bool_cast_str(self):
        with self.assertRaises(Exception) as cm:
            self.person.is_smoker = "abc"
        self.assertTrue(isinstance(cm.exception, CastException))

    def test_allowed_None(self):
        self.person.first_name = None

    def test_unallowed_None(self):
        with self.assertRaises(ValueError) as cm:
            self.person.last_name = None


class Test_Construction(TestCase):
    TEST_DICT: dict

    def setUp(self) -> None:
        with TEST_FILE_PATH.open() as file:
            self.TEST_DICT = json.load(file)["single_person"]

    def test_unallowed_missing_default(self):
        test_dict = copy.deepcopy(self.TEST_DICT)
        test_dict.pop("first_name")
        with self.assertRaises(TypeError) as cm:
            Person(**test_dict)

    def test_unallowed_missing(self):
        test_dict = copy.deepcopy(self.TEST_DICT)
        test_dict.pop("last_name")
        with self.assertRaises(TypeError) as cm:
            Person(**test_dict)

    def test_bool_missing(self):
        test_dict = copy.deepcopy(self.TEST_DICT)
        test_dict.pop("is_smoker")
        with self.assertRaises(TypeError) as cm:
            Person(**test_dict)


class Test_reprs(TestCase):
    TEST_DICT: dict

    def setUp(self) -> None:
        with TEST_FILE_PATH.open() as file:
            self.TEST_DICT = json.load(file)["single_person"]
            self.person = Person(**self.TEST_DICT)
        return super().setUp()

    def test_dict_repr(self):
        self.person.as_flattened_dict()
