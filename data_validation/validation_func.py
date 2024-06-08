import pathlib as pl
import re
from typing import List, Union

LOG_DIRECTORY: pl.Path = None

IS_FILE_MSG = "path to directory was expected but filepath was given:"
IS_DIR_MSG = "filepath was expected, but path to directory was given:"
FILE_MISSING_MSG = "file not found at location:"
DIR_MISSING_MSG = "directory not found at location:"


def extract_digits_from_string(value: str):
    candidates = re.findall(pattern=r'\d+', string=value)
    if candidates:
        return candidates[0]


def begins_with(value: str, start_val: str):
    if value.startswith(start_val):
        return
    else:
        raise ValueError(f"Value <{value}> does not begin with '{start_val}'")


def is_positive(value: Union[int, float]) -> None:
    if value >= 0:
        return
    else:
        raise ValueError(f"Value <{value}> must be positive")


def is_between(value: Union[int, float],
               value_range: List[Union[int, float]]) -> None:

    min_val, max_val = value_range
    if max_val is not None:
        if value > max_val:
            raise ValueError(
                f"Value <{value}> is too large must be equal or smaller than {max_val}")

    if min_val is not None:
        if value < min_val:
            raise ValueError(
                f"Value <{value}> is too small must be equal or grater than {min_val}")
    return


def has_length(value: list, lower_bound: int = None, upper_bound: int = None) -> None:
    """checks if the length of the list is within the interval specified

    Args:
        value (list): list of values to check
        lower_bound (int): lower bound of the length must be >=1
        upper_bound (int): upper bound of the length

    Raises:
        ValueError: length of the list is not within the bounds
        TypeError: bounds are not of type int
    """
    if upper_bound is not None:
        if not isinstance(upper_bound, int):
            raise ValueError(
                f"List of Elements <'{value}'> is too long must be at most {upper_bound} \
                    elements long")
        if isinstance(value, int):
            value = str(value)
        if len(value) > upper_bound:
            raise TypeError(
                f"max_value must be of type Int received type {type(value)}!")

    if lower_bound is not None:
        if not isinstance(lower_bound, int):
            raise TypeError(
                f"min_value must be of type Int, received type {type(value)}!")
        if lower_bound < 0:
            raise ValueError(
                f"minsize '{lower_bound}' is negative which is not allowed as a lower bound"
            )
        if len(value) < lower_bound:
            raise ValueError(
                f"List of Elements '{value}' is too short must at least {lower_bound}\
                      elements long")
    return


def is_in(value: str, value_list: list) -> None:
    if value in value_list:
        return
    else:
        raise ValueError(
            f"Value <{value}> is not a included in {value_list}")


def is_optional_dir(value: pl.Path) -> str:
    if value.is_dir() and value.exists():
        return
    elif value.is_file():
        is_file_msg = f"{IS_FILE_MSG} {value}"
        raise NotADirectoryError(is_file_msg)
    missing_dir_msg = f"{DIR_MISSING_MSG} {value}"
    value.mkdir(parents=True, exist_ok=True)
    return missing_dir_msg + "creating directory"


def is_dir(value: pl.Path) -> None:
    """checks if a directory exists, raises an appropriate error if not

    Args:
        value (pl.Path): path of directory

    Raises:
        ValueError: path given is not a directory or  file does not exists
    """
    if value.is_dir() and value.exists():
        return
    elif value.is_file():
        is_file_msg = f"{IS_FILE_MSG} {value}"
        raise ValueError(is_file_msg)

    missing_dir_msg = f"{DIR_MISSING_MSG} {value}"
    raise ValueError(missing_dir_msg)


def is_optional_file(value: pl.Path) -> str:
    if value.is_file():
        return
    elif value.is_dir():
        is_dir_msg = f"{IS_DIR_MSG} {value}"
        return is_dir_msg
    file_missing_msg = f"{FILE_MISSING_MSG} {value}"
    return file_missing_msg


def is_file(value: pl.Path) -> None:
    """Checks if file exists or is a directory, raises and error or returns a
       warning.

    Args:
        value (pl.Path): path of the file

    Raises:
        IsADirectoryError: expected file, but found a directory instead
        FileNotFoundError: file not found at given path
    """
    if value.is_file():
        return
    elif value.is_dir():
        is_dir_msg = f"{IS_DIR_MSG} {value}"
        raise IsADirectoryError(is_dir_msg)
    file_missing_msg = f"{FILE_MISSING_MSG} {value}"
    raise FileNotFoundError(file_missing_msg)


def is_divisible(value: int, divisor: int):
    if value % divisor == 0:
        return
    else:
        raise ValueError(f"value {value} must be divisible by {divisor}")
