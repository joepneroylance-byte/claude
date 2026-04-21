import pytest
from utils import flatten, chunk, deep_merge, clamp


def test_flatten_empty():
    assert flatten([]) == []


def test_flatten_flat():
    assert flatten([1, 2, 3]) == [1, 2, 3]


def test_flatten_nested():
    assert flatten([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5]


def test_chunk_even():
    assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_chunk_remainder():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_chunk_empty():
    assert chunk([], 3) == []


def test_deep_merge_simple():
    assert deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


def test_deep_merge_override():
    assert deep_merge({"a": 1}, {"a": 2}) == {"a": 2}


def test_deep_merge_nested():
    result = deep_merge({"a": {"x": 1, "y": 2}}, {"a": {"y": 99, "z": 3}})
    assert result == {"a": {"x": 1, "y": 99, "z": 3}}


def test_clamp_within():
    assert clamp(5.0, 0.0, 10.0) == 5.0


def test_clamp_below():
    assert clamp(-1.0, 0.0, 10.0) == 0.0


def test_clamp_above():
    assert clamp(11.0, 0.0, 10.0) == 10.0
