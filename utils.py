"""General-purpose utility functions."""

from typing import Any


def flatten(nested: list) -> list:
    """Recursively flatten a nested list."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def chunk(lst: list, size: int) -> list[list]:
    """Split a list into chunks of the given size."""
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge two dicts; override values win on conflicts."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def clamp(value: float, lo: float, hi: float) -> float:
    """Return value clamped to the range [lo, hi]."""
    return max(lo, min(value, hi))
