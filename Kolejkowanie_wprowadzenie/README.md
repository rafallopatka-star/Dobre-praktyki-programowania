# System Kolejkowania - Producer/Consumer

System symulujący kolejkowanie zadań (np. rozmów telefonicznych) z wykorzystaniem pliku CSV jako kolejki.

## Pliki

- **producer.py** - dodaje zadania do kolejki
- **consumer.py** - wykonuje zadania z kolejki
- **queue.csv** - plik kolejki (tworzony automatycznie)

## Statusy zadań

| Status | Opis |
|--------|------|
| `pending` | Zadanie czeka na wykonanie |
| `in_progress` | Zadanie jest w trakcie wykonywania |
| `done` | Zadanie zostało wykonane |

## Użycie Producer

```powershell
# Dodaj 1 zadanie
python producer.py

# Dodaj 5 zadań
python producer.py -c 5

# Dodaj 100 zadań (batch)
python producer.py -b 100

# Pokaż status kolejki
python producer.py -s

# Wyczyść kolejkę
python producer.py --clear
```

## Użycie Consumer

```powershell
# Uruchom consumer z ID=1
python consumer.py

# Uruchom consumer z własnym ID
python consumer.py --id 2

# Zmień interwał sprawdzania (domyślnie 5s)
python consumer.py --interval 3

# Zmień czas wykonania zadania (domyślnie 30s)
python consumer.py --duration 10
```

## Uruchomienie wielu konsumerów

Otwórz kilka terminali i uruchom w każdym:

```powershell
# Terminal 1
python consumer.py --id 1

# Terminal 2
python consumer.py --id 2

# Terminal 3
python consumer.py --id 3
```

## Przykładowy scenariusz

1. Wyczyść kolejkę:
   ```powershell
   python producer.py --clear
   ```

2. Dodaj 100 zadań:
   ```powershell
   python producer.py -b 100
   ```

3. Uruchom 3-4 konsumerów w osobnych terminalach:
   ```powershell
   python consumer.py --id 1
   python consumer.py --id 2
   python consumer.py --id 3
   ```

4. Obserwuj jak konsumerzy pobierają i wykonują zadania równolegle.

## Testowanie z krótszym czasem

Dla szybszych testów możesz zmniejszyć czas wykonania:

```powershell
python consumer.py --id 1 --duration 5
```

## Wymagania

- Python 3.x
- filelock (`pip install filelock`)
