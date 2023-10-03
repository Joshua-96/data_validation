
from functools import wraps
from typing import Callable

from data_validation.exceptions import CastException, UnexpectedCastException


def apply_casting(func: Callable) -> Callable:
    """wrapper for calling functions for casting
       Need keyword 'inp' for value other wise first annotated value is
       taken from function signature
    Args:
        func (Callable): function to wrap

    Raises:
        CastException: is raised when value did not comply
        UnexpectedCastException: is raised when other exceptions than ValueError and TypeError were raised

    Returns:
        Callable: inner wrapper function
    """
    input_type: type
    if "inp" in func.__annotations__.keys():
        input_type = func.__annotations__["inp"]
    else:
        input_type = func.__annotations__.values()[0]
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
