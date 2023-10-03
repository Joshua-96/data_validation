from datetime import date, datetime
from typing import List
import pathlib as pl

from data_validation.decorators import apply_casting


@apply_casting
def _cast_from_str_to_date(inp: str, dateformat: str) -> date:
    return datetime.strptime(inp, dateformat).date()


@apply_casting
def _cast_to_datetime_from_int(inp: int) -> date:
    return datetime.fromtimestamp(inp)

@apply_casting
def _cast_from_path_pattern_to_list(inp: str, folder: pl.Path) -> List[pl.Path]:
    resolved_paths = list(folder.rglob(inp))
    if not resolved_paths:
        raise ValueError(
            f"No files found match the pattern {inp} inside folder {folder}"
        )
    return resolved_paths
