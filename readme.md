# data_validation package 

## Summary
This Module provides a simplified way of conducting and customizing data validation, type checking and custom casting operation,
it can either be used as stand-alone with classes or in conjunction with dataclass module, which is recommended, it builds upon the Data descriptor implementation of python and has one common descriptor Class which handles all Cases.
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
# setting person_id to "abc" will result in a TypeError
person.person_id = "abc"
```
the error message reads:\
``TypeError: invalid type provided for attribute: 'person_id'
  expected type <class 'int'>, received value
  <abc> of type <class 'str'>``

### 2. Default Casting Behavior
The following Casting functions are applied by default:
- str -> bool, indifferent to case:
    - ["true",True",TRUE"] -> true
    - ["False","false","FALSE"] -> false
    - other literals -> ValueError
- int -> bool, works only for value 0 and 1:
    - 1 -> True
    - 0 -> False
    - other int values -> ValueError
- float -> int, will cast except for floats having decimal places != 0:
    - 2.0 -> 2
    - 2.5 -> ValueError
- int -> datetime, convert unix-timestamp int into datetime:
    - no checking for plausibility by default
- str -> datetime, parse as string formatted time
    - default format is '%Y-%m-%d'

### 2.1 Modification and expansion of casting
The Default Casting behavior is reflected in the class DefaultTypeHandler
it serves as a fallback or baseline, thus it is recommended customize a TypeHandler to your needs.
This can be achieved in two way:
1. Having one type of casting per TypeHandler, e.g. DateTypeHandler, NumericTypeHandler, PathTypeHandler etc.
2. Defining one TypeHandler which includes most or all of the casting functionality

In the first case construct a dict or other mapping type and pass it to the init function:
```python
from datetime import datetime, date

from data_validation.validation import DefaultTypeHandler
from data_validation.decorators import apply_casting

# define custom function for casting
@apply_casting
def _cast_from_str_to_date(inp: str, dateformat: str) -> date:
    return datetime.strptime(inp, dateformat).date()

# case 1: specific handler
customDateHandler = DefaultTypeHandler(
    source_type=str,
    dest_type=date,
    casting_fct=ArgFunctionWrapper(_cast_from_str_to_date, dateformat="%Y/%m/%d"),
    type_mapping=None
)

# case 2: universal handler
common_casting_mapping = {
    (str, date): ArgFunctionWrapper(_cast_from_str_to_date, dateformat="%Y/%m/%d"),
    ...
}

universalDataHandler = DefaultTypeHandler(
    type_mapping = common_casting_mapping
)

```


In the second case use the defined additional type_mapping will overwrite exiting entries or be added to the DEFAULT_TYPE_MAPPING object. In this case a conversion from str -> datetime was already defined but is overwritten by the new definition or in this case the different dateformat is applied. 

### 2.2 Non-trivial custom validation
In order to use any custom validation function itself must return None on success and raise a ValueError Exception on validation-failure. This exception will internally be wrapped into a CastException which in turn can be caught and handled. <br>
Consider the following (incomplete) implementation of a email-validation-function:
```python
def validate_email_precisely(value: str,
                             first_name: str,
                             last_name: str,
                             allowed_domains: List[str]):
    if "@" not in value:
        raise ValueError("Invalid Email, <@> is missing")
    if first_name.lower() not in value.lower():
        raise ValueError(f"first name <{first_name}> missing from email")
    if last_name.lower() not in value.lower():
        raise ValueError(f"last name <{last_name}> missing from email")
    domain = value.split("@")[1]
    enumerated_domains = ",".join(allowed_domains)
    if domain not in allowed_domains:
        raise ValueError(f"domain <{domain}> is not in domain whitelist: <{enumerated_domains}>")
```
For this function to be passed as dataValidator instance, we have to instantiate it as such:

```python
email_Validation = ArgFunctionWrapper(
    func=validate_email_precisely,
    value_kw="value",
    # Pass attribute Name to refer to instance field
    first_name="first_name",
    last_name="last_name",
    # Passing static arguments is also possible
    allowed_domains=allowed_domains)
```

the keyword arguments passed to the eventual function can be statically defined i.e. the allowed_domains variable but they 
can also reference a attribute of the Class, which it will be associated with. Finally for a minimum working example we re-use our Person-Class and drop in the custom email Validator.

```python
@dataclass
class Person():
    first_name: str = defaultValidator()
    last_name: str = defaultValidator()
    email: str = Validator(
        validator_func=email_Validation, default=None, allow_none=True
    )
```
as with the other cases, upon creating an instance and we try to set an invalid value we get:

```python
# Note: because we set "allow_none" to True and provided a default, we can omit the email from the constructor
person: Person = Person(first_name = "John", last_name = "Doe")
person.email = "john.doe@spammer.io"
# Error: ValueError("Validation Test failed for field 'email': domain <spammer.io> is not in domain whitelist: <gmail.com,example_uni.edu,outlook.com>")
```


### 2.3 Working with Iterable Fields (e.g. list and tuples)
A common Use-Case are String-concatenated Field which represent a Collection, generally speaking a string should be expanded into a list, considering the type_mapping object we can utilize the List Object from the typing lib and define:
```python
from typing import List

@apply_casting
def split_str(inp: str, delimiter: str) -> List[str]:
    return inp.split(delimiter)

{(str, List[str]): ArgFunctionWrapper(split_str, delimiter=",")}
``` 

### 3. Inheritance Behavior of Validated Classes  


### 4. Tree-like Structures with Validated Classes

### 5. Usage with DataFrames   


