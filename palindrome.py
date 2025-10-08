def is_palindrome(text: str) -> bool:
    text = text.lower().replace(" ", "").replace(",", "").replace(".", "")
    return text == text[::-1]

print(is_palindrome('Kajak'))
print(is_palindrome('Kobyła ma mały bok'))
print(is_palindrome('python'))
print(is_palindrome(''))
print(is_palindrome('A'))
