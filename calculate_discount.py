import pytest

def calculate_discount(price: float, discount: float) -> float:
    if price < 0 or discount < 0 or discount > 100:
        raise ValueError("Invalid price or discount")
    return price * (1 - discount / 100)

calculate_discount(100, 0.2)
calculate_discount(50, 0)
calculate_discount(200, 1) 
calculate_discount(100, -0.1) 
calculate_discount(100, 1.5)


