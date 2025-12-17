# API Kolejkowanie - RabbitMQ

Asynchroniczny serwis do liczenia osób na zdjęciach. Producer (Flask) wrzuca zadania na kolejkę RabbitMQ, konsumery (osobne procesy) pobierają zadania, analizują obraz z użyciem OpenCV (HOG) i zapisują wynik w lokalnym store + pliku wynikowym.

## Architektura
```
Klient ──▶ /analyze_img (Flask) ──▶ RabbitMQ (durable queue)
                                        │
                                        ├─▶ Consumer #1 ┐
                                        ├─▶ Consumer #2 ├─▶ zapis wyniku w SQLite + plik analyzed_images/{id}-{count}.ext
                                        └─▶ Consumer #n ┘
                                                   │
                                            /result/<task_id>
```

- Producer: endpoint `/analyze_img` tylko publikuje zadania do RabbitMQ.
- Consumer: pobiera, ściąga obraz, liczy osoby, zapisuje wynik i manualnie ackuje wiadomość (auto_ack=false, prefetch=1).
- Task store: SQLite (`tasks.db`) trzyma status, wynik, ścieżkę pliku.
- Artefakty: zapisujemy obraz jako `{task_id}-{person_count}.{ext}` w `analyzed_images/`.

## Wymagania
- Python 3.8+
- Docker (do RabbitMQ) lub własna instancja RabbitMQ
- System: Windows/Linux/macOS

## Uruchomienie RabbitMQ (docker-compose)
```powershell
cd Pliki_zajecia\Kolejkowanie API
docker compose up -d rabbitmq
# panel: http://localhost:8080 (guest/guest)
```

## Instalacja zależności
```powershell
cd Pliki_zajecia\Kolejkowanie API
pip install -r requirements.txt
```

## Start usług
```powershell
# Producer API (port 5000)
python app.py

# Konsumer (można uruchomić wiele terminali)
python consumer.py            # worker #1
python consumer.py 2          # worker #2
python consumer.py 3          # worker #3
```

### Zmienne środowiskowe
- `RABBITMQ_HOST` (domyślnie `localhost`)
- `RABBITMQ_PORT` (domyślnie `5672`)
- `RABBITMQ_USER`, `RABBITMQ_PASS` (opcjonalnie)
- `RABBITMQ_QUEUE` (domyślnie `image_analysis_queue`)

## Endpointy
- **POST/GET** `/analyze_img?url=<url>` – dodaje zadanie do kolejki, zwraca `task_id` (202)
- **GET** `/result/<task_id>` – status (`queued|processing|completed|failed`), `person_count`, `output_path`
- **GET** `/health` – sprawdza połączenie z RabbitMQ i DB

## Jak to działa
1) Klient wysyła URL zdjęcia do `/analyze_img` → zapis statusu `queued` w SQLite → publikacja JSON do RabbitMQ (durable message).
2) Konsumer (prefetch=1, manual ack) pobiera zadanie, ustawia status `processing`, pobiera obraz, liczy osoby (HOG), zapisuje plik wynikowy i status `completed`.
3) Klient odpytuje `/result/<task_id>` aby poznać wynik; w razie błędu status `failed` z opisem.

## Test obciążeniowy
Upewnij się, że API i przynajmniej jeden konsumer działają, potem:
```powershell
python test_api.py
```
Skrypt wysyła 10, 20 i 30 równoległych żądań i raportuje czasy.

## Pliki
- `app.py` – producer/API (Flask + RabbitMQ publish)
- `consumer.py` – worker (RabbitMQ consume, OpenCV HOG)
- `task_store.py` – SQLite na statusy i wyniki
- `docker-compose.yml` – RabbitMQ z panelem zarządzania
- `requirements.txt` – zależności
- `analyzed_images/` – zapisane obrazy `{task_id}-{count}.ext`

## Notatki
- Kolejka i wiadomości są trwałe (durable + delivery_mode=2).
- Manualne ACK (auto_ack=false) zapewnia, że zadanie nie zniknie bez przetworzenia.
- Skalowanie: uruchom więcej konsumentów, aby przyspieszyć przetwarzanie pod obciążeniem.
