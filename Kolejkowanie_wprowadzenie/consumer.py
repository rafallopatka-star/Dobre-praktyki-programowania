"""
Consumer - odpowiedzialny za wykonywanie prac z kolejki.
Działa w trybie ciągłym (while True), co 5 sekund sprawdza kolejkę.
Wykonanie każdej pracy trwa 30 sekund.
"""
import csv
import os
import time
from datetime import datetime
import argparse
import filelock

# Nazwa pliku z kolejką zadań
QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue.csv")
LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue.lock")

# Konfiguracja
CHECK_INTERVAL = 5  # sekundy między sprawdzeniami kolejki
TASK_DURATION = 30  # sekundy na wykonanie zadania

def get_lock():
    """Zwraca obiekt blokady pliku dla bezpiecznego dostępu wieloprocesowego."""
    return filelock.FileLock(LOCK_FILE, timeout=10)

def get_pending_task() -> dict:
    """
    Pobiera pierwsze zadanie o statusie 'pending' i zmienia jego status na 'in_progress'.
    
    :return: Słownik z danymi zadania lub None jeśli brak zadań
    """
    lock = get_lock()
    
    with lock:
        if not os.path.exists(QUEUE_FILE):
            return None
        
        # Odczytaj wszystkie zadania
        with open(QUEUE_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            tasks = list(reader)
        
        # Znajdź pierwsze zadanie pending
        task_to_process = None
        for task in tasks:
            if task['status'] == 'pending':
                task_to_process = task
                task['status'] = 'in_progress'
                task['started_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        
        if task_to_process is None:
            return None
        
        # Zapisz zaktualizowane zadania
        with open(QUEUE_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'task_name', 'status', 'created_at', 'started_at', 'finished_at'])
            for task in tasks:
                writer.writerow([task['id'], task['task_name'], task['status'],
                               task['created_at'], task['started_at'], task['finished_at']])
        
        return task_to_process

def mark_task_done(task_id: str):
    """
    Oznacza zadanie jako wykonane (status: done).
    
    :param task_id: ID zadania do oznaczenia
    """
    lock = get_lock()
    
    with lock:
        if not os.path.exists(QUEUE_FILE):
            return
        
        # Odczytaj wszystkie zadania
        with open(QUEUE_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            tasks = list(reader)
        
        # Znajdź i zaktualizuj zadanie
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = 'done'
                task['finished_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        
        # Zapisz zaktualizowane zadania
        with open(QUEUE_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'task_name', 'status', 'created_at', 'started_at', 'finished_at'])
            for task in tasks:
                writer.writerow([task['id'], task['task_name'], task['status'],
                               task['created_at'], task['started_at'], task['finished_at']])

def process_task(task: dict, consumer_id: str):
    """
    Wykonuje zadanie (symulacja pracy przez 30 sekund).
    
    :param task: Słownik z danymi zadania
    :param consumer_id: Identyfikator konsumera
    """
    print(f"[CONSUMER {consumer_id}] Rozpoczynam: {task['task_name']} (ID: {task['id']})")
    print(f"[CONSUMER {consumer_id}] Status: in_progress | Czas wykonania: {TASK_DURATION}s")
    
    # Symulacja pracy - 30 sekund
    for i in range(TASK_DURATION, 0, -1):
        time.sleep(1)
        if i % 10 == 0:  # Wyświetl co 10 sekund
            print(f"[CONSUMER {consumer_id}] {task['task_name']} - pozostało {i}s...")
    
    # Oznacz jako wykonane
    mark_task_done(task['id'])
    print(f"[CONSUMER {consumer_id}] Zakończono: {task['task_name']} (ID: {task['id']}) - status: done")

def show_queue_status(consumer_id: str):
    """Wyświetla aktualny status kolejki."""
    lock = get_lock()
    
    with lock:
        if not os.path.exists(QUEUE_FILE):
            return
        
        with open(QUEUE_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            tasks = list(reader)
        
        pending = sum(1 for t in tasks if t['status'] == 'pending')
        in_progress = sum(1 for t in tasks if t['status'] == 'in_progress')
        done = sum(1 for t in tasks if t['status'] == 'done')
        
        print(f"[CONSUMER {consumer_id}] Status: pending={pending}, in_progress={in_progress}, done={done}")

def run_consumer(consumer_id: str = "1"):
    """
    Główna pętla konsumera - działa w trybie ciągłym.
    
    :param consumer_id: Unikalny identyfikator konsumera
    """
    print(f"[CONSUMER {consumer_id}] Uruchomiono. Sprawdzanie kolejki co {CHECK_INTERVAL}s...")
    print(f"[CONSUMER {consumer_id}] Czas wykonania zadania: {TASK_DURATION}s")
    print("-" * 60)
    
    while True:
        try:
            # Pobierz zadanie do wykonania
            task = get_pending_task()
            
            if task:
                # Mamy zadanie - wykonaj je
                process_task(task, consumer_id)
                show_queue_status(consumer_id)
            else:
                # Brak zadań - czekaj i sprawdź ponownie
                print(f"[CONSUMER {consumer_id}] Brak zadań do wykonania. Czekam {CHECK_INTERVAL}s...")
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print(f"\n[CONSUMER {consumer_id}] Zatrzymano przez użytkownika.")
            break
        except Exception as e:
            print(f"[CONSUMER {consumer_id}] Błąd: {e}. Ponawiam za {CHECK_INTERVAL}s...")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Consumer - wykonuje zadania z kolejki')
    parser.add_argument('--id', '-i', type=str, default="1",
                       help='Unikalny identyfikator konsumera (domyślnie: 1)')
    parser.add_argument('--interval', type=int, default=5,
                       help='Interwał sprawdzania kolejki w sekundach (domyślnie: 5)')
    parser.add_argument('--duration', type=int, default=30,
                       help='Czas wykonania zadania w sekundach (domyślnie: 30)')
    
    args = parser.parse_args()
    
    CHECK_INTERVAL = args.interval
    TASK_DURATION = args.duration
    
    run_consumer(args.id)