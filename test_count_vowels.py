import pytest
from count_vowels import count_vowels

def test_count_vowels_basic():
    assert count_vowels("Hello World") == 3
    assert count_vowels("Python") == 2
    assert count_vowels("AEIOUY") == 6
    assert count_vowels("bcd") == 0
    assert count_vowels("") == 0

def test_count_vowels_polish_chars():
    assert count_vowels("Próba żółwia") == 5

def test_count_vowels_mixed_case():
    assert count_vowels("TeStInG") == 2
