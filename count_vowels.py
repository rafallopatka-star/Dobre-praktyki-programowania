import pytest
def count_vowels(text: str) -> int:
    vowels = "aeiouyAEIOUY" 
    return sum(1 for char in text if char in vowels)

print(count_vowels("Python"))
print("AEIOUY")
print("bcd")
print("")
print("Próba żółwia")