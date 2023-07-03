from example_dataclasses import Person
import json
import pathlib as pl

path = pl.Path("./sample/example_input.json").resolve()


with path.open("r") as inp:
    test_dict = json.load(inp)

print(Person(**test_dict))
