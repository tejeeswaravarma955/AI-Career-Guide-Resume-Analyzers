import os
from pathlib import Path
from typing import Any


def safe_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower().lstrip('.')


def ensure_directory(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def json_default(value: Any):
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")
