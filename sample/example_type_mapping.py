from datetime import date, datetime

from data_validation.decorators import apply_casting


@apply_casting
def _cast_from_str_to_date(inp: str, dateformat: str) -> date:
    return datetime.strptime(inp, dateformat).date()


@apply_casting
def _cast_to_datetime_from_int(inp: int) -> date:
    return datetime.fromtimestamp(inp)
