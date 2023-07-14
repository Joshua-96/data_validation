import copy
import json
from typing import Any
from unittest import TestCase
from sample.example_dataclasses import PrecisePerson
from data_validation.exceptions import CastException, UnexpectedCastException

from tests import TEST_FILE_PATH

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
        with self.assertRaises(ValueError) as cm:
            self.person.email = "john@gmail.com"

    def test_invalid_email_last_name(self):
        with self.assertRaises(ValueError) as cm:
            self.person.email = "doe@gmail.com"

    def test_invalid_email_domain(self):
        with self.assertRaises(ValueError) as cm:
            self.person.email = "john.doe@spammer.io"

    def test_sequence_validation(self):
        self.person.hobbies = ["asdf", "qwert", "ops"]

    def test_sequence_validation_fail(self):
        with self.assertRaises(ValueError) as cm:
            self.person.hobbies = ["asd", "at", "asdt"]
