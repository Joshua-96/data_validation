from datetime import datetime
from math import log2


def _cast_to_bool_from_int(inp: int) -> bool:
    if inp in [0, 1]:
        return bool(inp)
    raise TypeError(f"int value {inp} can not be casted to bool")


def _cast_to_bool_from_str(inp: str) -> bool:
    inp = inp.lower()
    if inp in ["true", "false"]:
        return inp == "true"
    raise ValueError(
        f"string value {inp} can not be read as boolean value, expects 'true' or 'false' without case sensitivity"
    )


def _cast_to_int_from_float(inp: float) -> int:
    if int(inp) == inp:
        return int(inp)
    raise ValueError(
        f"float value {inp} could not be casted to int without loss of presicion")


def _cast_to_datetime_from_str(inp: str, dateformat: str) -> datetime:
    return datetime.strptime(inp, dateformat)


def _cast_to_datetime_from_int(inp: int) -> datetime:
    if log2(inp) > 34:
        inp = inp // 1000
    return datetime.fromtimestamp(inp)