# API Kolejkowanie - Analiza Osób na Zdjęciach

System do analizy osób na zdjęciach z internetu z wykorzystaniem architektury Producer-Consumer i kolejkowania zadań.

## 📋 Spis treści
- [Architektura](#architektura)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Uruchomienie](#uruchomienie)
- [Testowanie](#testowanie)
- [Jak to działa](#jak-to-działa)

## 🏗️ Architektura

```
┌──────────────┐      ┌───────────┐      ┌────────────┐
│   Klient     │─────▶│  Producer │─────▶│   Redis    │
│  (Request)   │      │  (app.py) │      │   Queue    │
└──────────────┘      └───────────┘      └──────┬─────┘
                                                 │
                                                 ▼
                      ┌─────────────────────────────────┐
                      │     Consumers (consumer.py)     │
                      │  ┌──────┐ ┌──────┐ ┌──────┐   │
                      │  │ W #1 │ │ W #2 │ │ W #n │   │
                      │  └──────┘ └──────┘ └──────┘   │
                      └─────────────────────────────────┘
                                   │
                                   ▼
                         Wykrywanie osób (HOG)
```

### Komponenty:

1. **Producer (app.py)** - Flask API
   - Endpoint `/analyze_img` (GET/POST) - przyjmuje URL zdjęcia
   - Dodaje zadania do kolejki Redis
   - Zwraca natychmiast `task_id` (202 Accepted)
   - Endpoint `/result/<task_id>` - sprawdzanie wyniku

2. **Consumer (consumer.py)** - Worker procesujący
   - Pobiera zadania z kolejki Redis
   - Ściąga zdjęcia z internetu
   - Wykrywa osoby używając HOG (Histogram of Oriented Gradients)
   - Zapisuje wyniki do Redis
   - Może działać w wielu instancjach jednocześnie

3. **Redis** - Message Broker
   - Kolejka zadań
   - Przechowywanie statusów i wyników

## 📦 Wymagania

- Python 3.8+
- Redis Server
- Zainstalowane biblioteki (patrz requirements.txt)

## 🚀 Instalacja

### 1. Zainstaluj Redis

**Windows:**
```powershell
# Pobierz Redis z GitHub: https://github.com/microsoftarchive/redis/releases
# Lub użyj Chocolatey:
choco install redis-64
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

### 2. Zainstaluj zależności Python

```powershell
pip install -r requirements.txt
```

## ▶️ Uruchomienie

### Krok 1: Uruchom Redis Server

```powershell
# Windows - jeśli nie działa jako usługa:
redis-server

# Linux/macOS:
redis-server
```

### Krok 2: Uruchom Producer (API)

W pierwszym terminalu:

```powershell
python app.py
```

API będzie dostępne na `http://localhost:5000`

### Krok 3: Uruchom Consumer Worker(s)

W drugim terminalu (lub wielu terminalach dla skalowania):

```powershell
# Uruchom pierwszego workera
python consumer.py 1

# W innych terminalach możesz uruchomić więcej workerów:
python consumer.py 2
python consumer.py 3
```

**Uwaga:** Im więcej workerów, tym szybsze przetwarzanie wielu zadań jednocześnie!

## 🧪 Testowanie

### Manualne testowanie

**POST request:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/analyze_img" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"url":"https://images.pexels.com/photos/1054218/pexels-photo-1054218.jpeg"}'
```

**GET request:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/analyze_img?url=https://images.pexels.com/photos/1054218/pexels-photo-1054218.jpeg"
```

**Sprawdzenie wyniku:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/result/TASK_ID"
```

### Automatyczne testowanie obciążenia

Skrypt `test_api.py` testuje API z 10, 20 i 30 jednoczesnymi requestami:

```powershell
python test_api.py
```

Test sprawdza:
- ✅ Czy API odpowiada szybko (kolejkowanie)
- ✅ Czy wszystkie zadania są przetwarzane
- ✅ Czasy odpowiedzi i throughput
- ✅ Stabilność pod obciążeniem

## 🔍 Jak to działa

### Bez kolejkowania (problem):
```
Request → API → [Analiza 5s] → Response ❌
10 requestów = 50 sekund sekwencyjnie
API się blokuje, timeout!
```

### Z kolejkowaniem (rozwiązanie):
```
Request → API → Queue → Response (200ms) ✅
                  ↓
            [Workers przetwarzają async]
            
10 requestów = 2 sekundy (natychmiastowa kolejkowanie)
Przetwarzanie równoległe przez workerów!
```

### Przepływ danych:

1. **Klient** wysyła POST/GET z URL zdjęcia
2. **Producer** (app.py):
   - Generuje `task_id`
   - Dodaje zadanie do kolejki Redis
   - Zwraca `task_id` natychmiast (202 Accepted)
3. **Consumer** (consumer.py):
   - Czeka na zadania w kolejce
   - Pobiera zadanie (BRPOP - blocking)
   - Ściąga zdjęcie z URL
   - Uruchamia detekcję HOG
   - Zapisuje wynik w Redis
4. **Klient** odpytuje `/result/<task_id>`
   - `queued` - czeka w kolejce
   - `processing` - właśnie przetwarzane
   - `completed` - gotowe (z liczbą osób)
   - `failed` - błąd (z komunikatem)

## 📊 Przykładowe wyniki

```
Test: Light Load - 10 concurrent requests
======================================
✓ Request #1: 3 person(s) detected (total: 4.23s)
✓ Request #2: 2 person(s) detected (total: 4.56s)
...

Summary:
  Total requests: 10
  Successful: 10
  Failed: 0
  Total time: 15.34s
  
  Submit time (API response):
    Avg: 0.045s  ← API odpowiada szybko!
  
  Total time (including processing):
    Avg: 12.5s   ← Przetwarzanie w tle
```

## 🔧 Konfiguracja

### Zwiększenie liczby workerów:

Dla szybszego przetwarzania uruchom więcej instancji:

```powershell
# Terminal 1
python consumer.py 1

# Terminal 2
python consumer.py 2

# Terminal 3
python consumer.py 3
```

### Redis Configuration:

Domyślnie: `localhost:6379`

Zmiana w `app.py` i `consumer.py`:
```python
redis_client = redis.Redis(host='localhost', port=6379, db=0)
```

## 📝 Endpointy API

### POST/GET `/analyze_img`
Dodaje zdjęcie do kolejki analizy.

**Request:**
```json
{
  "url": "https://example.com/image.jpg"
}
```

**Response (202):**
```json
{
  "task_id": "uuid-here",
  "status": "queued",
  "message": "Task queued for processing"
}
```

### GET `/result/<task_id>`
Pobiera wynik analizy.

**Response (200):**
```json
{
  "task_id": "uuid-here",
  "status": "completed",
  "person_count": 5
}
```

### GET `/health`
Health check API i Redis.

**Response (200):**
```json
{
  "status": "healthy",
  "redis": "connected"
}
```

## 🎯 Zalety architektury Producer-Consumer

1. ✅ **Szybka odpowiedź API** - natychmiastowe zwracanie task_id
2. ✅ **Skalowalność** - łatwe dodawanie workerów
3. ✅ **Odporność na awarie** - zadania w kolejce nie giną
4. ✅ **Niezależność** - producer i consumer mogą działać niezależnie
5. ✅ **Load balancing** - Redis automatycznie dystrybuuje zadania

## 🐛 Troubleshooting

**Problem:** `Cannot connect to Redis`
```powershell
# Sprawdź czy Redis działa:
redis-cli ping
# Powinno zwrócić: PONG
```

**Problem:** Consumer nie pobiera zadań
```powershell
# Sprawdź długość kolejki:
redis-cli LLEN image_analysis_queue
```

**Problem:** Import errors
```powershell
# Reinstaluj zależności:
pip install -r requirements.txt --upgrade
```

## 📄 Licencja

MIT License - użyj jak chcesz! 🎉
