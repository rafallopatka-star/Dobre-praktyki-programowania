import pytest
from lista_zagniezdzona import flatten_list

def test_flatten_list_simple():
    assert flatten_list([1, 2, 3]) == [1, 2, 3]

def test_flatten_list_nested():
    assert flatten_list([1, [2, 3], [4, [5]]]) == [1, 2, 3, 4, 5]

def test_flatten_list_empty():
    assert flatten_list([]) == []

def test_flatten_list_deeply_nested():
    assert flatten_list([[[1]]]) == [1]
    assert flatten_list([1, [2, [3, [4]]]]) == [1, 2, 3, 4]
