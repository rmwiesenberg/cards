import pathlib
from typing import TypeAlias

PROJECT_ROOT = pathlib.Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT  / 'data'

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
