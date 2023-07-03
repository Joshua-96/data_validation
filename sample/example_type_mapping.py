from datetime import date, datetime
from functools import wraps

from data_validation.exceptions import CastException, UnexpectedCastException


def apply_casting(func: callable):
    input_type: type = func.__annotations__["inp"]
    output_type: type = func.__annotations__["return"]

    @wraps(func)
    def wrapper(*args, **kwargs):        
        try:
            return func(*args, **kwargs)
        except (TypeError, ValueError) as e:
            raise CastException(input_type=input_type,
                                output_type=output_type,
                                message=e)

        except Exception as e:
            raise UnexpectedCastException(input_type=input_type,
                                          output_type=output_type,
                                          message=e)
    return wrapper


@apply_casting
def _cast_to_bool_from_int(inp: int) -> bool:
    if inp in [0, 1]:
        return bool(inp)
    raise TypeError(f"int value {inp} can not be casted to bool")


@apply_casting
def _cast_to_int_from_float(inp: float) -> int:
    if int(inp) == inp:
        return int(inp)
    raise TypeError(
        f"float value {inp} could not be casted to int without loss of presicion")


@apply_casting
def _cast_to_date_from_str(inp: str, dateformat: str) -> date:
    return datetime.strptime(inp, dateformat).date()



def _cast_to_datetime_from_int(inp: int) -> date:
    return datetime.fromtimestamp(inp)
