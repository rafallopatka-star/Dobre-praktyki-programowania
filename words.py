def word_frequencies(text: str) -> dict:
    words = text.split()
    frequencies = {}
    for word in words:
        word = word.lower().strip(",.!?;:\"'()[]{}")
        if word:
            frequencies[word] = frequencies.get(word, 0) + 1
    return frequencies