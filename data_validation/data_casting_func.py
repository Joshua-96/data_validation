from datetime import datetime
from math import log2

from data_validation.decorators import apply_casting
from defaults import DATEFORMAT

@apply_casting
def _cast_to_bool_from_int(inp: int) -> bool:
    if inp in [0, 1]:
        return bool(inp)
    raise ValueError(f"int value {inp} can not be casted to bool")


@apply_casting
def _cast_to_bool_from_str(inp: str) -> bool:
    inp = inp.lower()
    if inp in ["true", "false"]:
        return inp == "true"
    raise ValueError(
        f"string value {inp} can not be read as boolean value, expects 'true' or 'false' without case sensitivity"
    )


@apply_casting
def _cast_float_to_int(inp: float) -> int:
    """casts float to integer if possible without precision loss

    Args:
        inp (float): input value

    Raises:
        ValueError: if float contains decimal places

    Returns:
        int: casted value
    """
    if int(inp) == inp:
        return int(inp)
    raise ValueError(
        f"float value {inp} could not be casted to int without loss of precision")


@apply_casting
def _cast_int_to_float(inp: int) -> float:
    return float(inp)


@apply_casting
def _cast_str_to_datetime(inp: str, dateformat: str = None) -> datetime:
    if dateformat is None:
        dateformat = DATEFORMAT
    return datetime.strptime(inp, dateformat)


@apply_casting
def _cast_int_to_datetime(inp: int) -> datetime:
    return datetime.fromtimestamp(inp)