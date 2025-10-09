import pytest
from fibonacci import fibonacci

@pytest.mark.parametrize("input_value, expected", [
    (0, 0),
    (1, 1),
    (2, 1),
    (3, 2),
    (4, 3),
    (5, 5),
    (6, 8),
    (7, 13),
    (8, 21),
    (9, 34),
    (10, 55),
])
def test_fibonacci_valid(input_value, expected):
    assert fibonacci(input_value) == expected

def test_fibonacci_negative_input():
    with pytest.raises(ValueError):
        fibonacci(-1)
