# data_validation package 

## Summary
This Module provides a simplified way of conducting and customizing data validation, type checking and custom casting operation,
it can either be used as stand-alone with classes or in conjunction with dataclasses, which is recommended, it builts upon the Data descriptor implementation of python and has one common descriptor Class which handles all Cases.
The main features include:
- Type Checking with TypeError Exception raised for mismatch
- usage of common validation functions such as "is_in_range", "has_length", "file_exists" etc. more importantly custom validation functions can be added
- implicit and explicit casting to primitive and complex types, such as:
    - str -> pathlib.Path
    - str -> datetime.datetime
    - int -> float
- Support for Inheritance and Composition of validated Classes, see examples
- dict representation of dataclass and flattend reprentation of nested Classes by   prefixing

## Setup 
Installation can be done via pip with the link of the repository:

```sh
pip install https://github.com/Joshua-96/data_validation.git
```
or by referencing the folder
```sh
pip install ./data_validation
```

## Compatibility:
The Module is developed and tested for python versions:
- 3.7, 3.8, 3.9, 3.10

later versions should be fine but are currently not tested with 

## Dependencies
- pandas >= 1.0

# Usage
## Prerequisites
Consider following class "Person" with these generic attributes:
-   person_id
- first_name
- last_name
- gender
- hobbies
- is_smoker
- email

In Order to be more explicit with gender we define an Enum Class Gender:

``` python
class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
```

all of the basic examples are in conjunction with dataclasses, but these are not necessary to use.
the implementation looks like this

``` python
@dataclass
class Person():
    person_id: int
    first_name: str
    last_name: str
    gender: Gender
    hobbies: List[str]
    is_smoker: bool
    email: str
```

## Basic Examples
### 1. Type Checking
    

first we want to perform basic type validation: 


``` python
import pathlib as pl
from data_validation import Validator

@dataclass
class Person():
    person_id: int = Validator()
    first_name: str = Validator()
    last_name: str = Validator()
    date_of_birth: date = field(default=None) 
    occupation: str = Validator()
    gender: str = Validator()
    hobbies: List[str] = Validator()
    is_smoker: bool = Validator()
    email: str = Validator()
    image: pl.Path = Validator()
```
Now the job of the validator is twofold:
- ensure primitive types
- apply the default constructor to value if complex type is annotated

using the class 

``` python
from .example import Person

person = Person(
    person_id=23,
    first_name="John",
    last_name="Doe",
    occupation="Teacher",
    gender="male",
    hobbies=["Baseball", "Soccer"],
    is_smoker=true,
    email="john.doe_94@gmail.com",
    image="example_folder/Profile.jpg"
)
# setting person_id to "abc" with result in a TypeError
person.person_id = "abc"
```
the error message reads:\
``TypeError: invalid type provided for attribute: person_id
  expected type <class 'int'>, received value
  <abc> of type <class 'str'>``

### 2. Default Casting Behavior
The following Casting functions are applied by default:
- str -> bool indifferent to case:
    - ["true",True",TRUE"] -> true
    - ["False","false","FALSE"] -> false
    - other literals -> ValueError