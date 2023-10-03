from typing import Any, List
from unittest import TestCase
import numpy as np

import pandas as pd
from sample.example_dataclasses import Person

from sample.example_dataclasses import Team as Team
from tests import TEST_CSV_PATH


class Test_tabular(TestCase):
    PERSONS: List[Person]
    TEAM: Team
    cur_test_dict: dict

    def setUp(self) -> None:
        self.df = pd.read_csv(TEST_CSV_PATH)
        self.PERSONS = self.df.to_dict(orient="records")
        return super().setUp()

    def test_regular(self):
        Team(individuals=self.PERSONS)

    def test_single_item_list(self):
        Team(individuals=[self.PERSONS[0]])

    def test_without_object_mapping(self):
        valid_values = []
        for row in self.df.iterrows():
            kwargs = {k: v for k, v in row[1].items()}
            valid_values.append(Person.static_validation(**kwargs))
        self.df["valid"] = valid_values
