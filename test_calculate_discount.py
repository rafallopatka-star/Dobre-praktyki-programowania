import pytest
from calculate_discount import calculate_discount

def test_calculate_discount_valid():
    assert calculate_discount(100, 20) == 80
    assert calculate_discount(50, 10) == 45
    assert calculate_discount(200, 1) == 198
    assert calculate_discount(100, 1.5) == 98.5

def test_calculate_discount_zero_discount():
    assert calculate_discount(50, 0) == 50

def test_calculate_discount_invalid_input():
    with pytest.raises(ValueError):
        calculate_discount(-100, 20)
    with pytest.raises(ValueError):
        calculate_discount(100, -20)
    with pytest.raises(ValueError):
        calculate_discount(100, 120)
