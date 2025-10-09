def count_vowels(text: str) -> int:
    vowels = "aąeęioóuyAĄEĘIOÓUY" 
    return sum(1 for char in text if char in vowels)

if __name__ == '__main__':
    print(count_vowels("Hello World"))
    print(count_vowels("Python"))
    print("AEIOUY")
    print("bcd")
    print("")
    print("Próba żółwia")