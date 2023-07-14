from datetime import date, datetime

from data_validation.decorators import apply_casting


@apply_casting
def _cast_from_int_to_bool_(inp: int) -> bool:
    if inp in [0, 1]:
        return bool(inp)
    raise TypeError(f"int value {inp} can not be casted to bool")


@apply_casting
def _cast_from_float_to_int(inp: float) -> int:
    if int(inp) == inp:
        return int(inp)
    raise TypeError(
        f"float value {inp} could not be casted to int without loss of precision"
    )


@apply_casting
def _cast_from_str_to_date(inp: str, dateformat: str) -> date:
    return datetime.strptime(inp, dateformat).date()


@apply_casting
def _cast_to_datetime_from_int(inp: int) -> date:
    return datetime.fromtimestamp(inp)
