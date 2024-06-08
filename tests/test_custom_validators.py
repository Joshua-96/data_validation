import json
from unittest import TestCase
from sample.example_dataclasses import PrecisePerson

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
        with self.assertRaises(ValueError):
            self.person.email = "john@gmail.com"

    def test_invalid_email_last_name(self):
        with self.assertRaises(ValueError):
            self.person.email = "doe@gmail.com"

    def test_invalid_email_domain(self):
        with self.assertRaises(ValueError):
            self.person.email = "john.doe@spammer.io"

    def test_sequence_validation(self):
        self.person.hobbies = ["asdf", "qwert", "ops"]

    def test_sequence_validation_fail(self):
        with self.assertRaises(ValueError):
            self.person.hobbies = ["asd", "at"]
