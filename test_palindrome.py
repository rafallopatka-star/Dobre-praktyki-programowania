<<<<<<< HEAD
import pytest
from palindrome import is_palindrome

def test_is_palindrome_true():
    assert is_palindrome('Kajak') == True
    assert is_palindrome('Kobyła ma mały bok') == True
    assert is_palindrome('') == True
    assert is_palindrome('A') == True

def test_is_palindrome_false():
    assert is_palindrome('python') == False

def test_is_palindrome_with_punctuation():
    assert is_palindrome('A to kanapa, na kota.') == True
=======
import pytest
from palindrome import is_palindrome

def test_is_palindrome_true():
    assert is_palindrome('Kajak') == True
    assert is_palindrome('Kobyła ma mały bok') == True
    assert is_palindrome('') == True
    assert is_palindrome('A') == True

def test_is_palindrome_false():
    assert is_palindrome('python') == False

def test_is_palindrome_with_punctuation():
    assert is_palindrome('A to kanapa, na kota.') == True
>>>>>>> 7c2f1b7dc9c66f6952e87a6df74538b3e844c054
