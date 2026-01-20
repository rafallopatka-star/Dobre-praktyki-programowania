import pytest

def calculate_discount(price: float, discount: float) -> float:
    if price < 0 or discount < 0 or discount > 100:
        raise ValueError("Invalid price or discount")
    return price * (1 - discount / 100)

if __name__ == "__main__":
    calculate_discount(100, 20)
    calculate_discount(50, 0)
    calculate_discount(200, 1) 
    calculate_discount(100, 10) 
    calculate_discount(100, 1.5)  


