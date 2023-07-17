import copy
import json
from typing import Any
from unittest import TestCase
from sample.example_dataclasses import Job_Position
from data_validation.exceptions import CastException, UnexpectedCastException
from tests import TEST_FILE_PATH


class Test_Altering(TestCase):
    TEST_DICT: dict
    cur_test_dict: dict

    def setUp(self) -> None:
        with TEST_FILE_PATH.open() as file:
            self.TEST_DICT = json.load(file)["job_position"]
        self.job = Job_Position(**self.TEST_DICT)
        return super().setUp()
    
    def test_regular(self):
        pass

    def test_repr(self):
        self.job.as_dict()

    def test_flat_repr(self):
        self.job.as_flattened_dict()

    def test_other_repr(self):
        self.job.other_dict()

    def test_nested_invalid(self):
        with self.assertRaises(CastException) as cm:
            self.job.occupied_by.date_of_birth = "invalid"
