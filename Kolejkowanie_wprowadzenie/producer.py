import csv
import os
import uuid
from datetime import datetime
import argparse
import filelock


QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue.csv")
LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue.lock")

def get_lock():
    
    return filelock.FileLock(LOCK_FILE, timeout=10)

def init_queue_file():
    if not os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'task_name', 'status', 'created_at', 'started_at', 'finished_at'])

def add_task(task_name: str = None) -> dict:
    lock = get_lock()
    
    with lock:
        init_queue_file()
        
        task_id = str(uuid.uuid4())[:8]
        if task_name is None:
            task_name = f"Rozmowa telefoniczna #{task_id}"
        
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        task = {
            'id': task_id,
            'task_name': task_name,
            'status': 'pending',
            'created_at': created_at,
            'started_at': '',
            'finished_at': ''
        }
        
        with open(QUEUE_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([task['id'], task['task_name'], task['status'], 
                           task['created_at'], task['started_at'], task['finished_at']])
        
        print(f"[PRODUCER] Dodano zadanie: {task['task_name']} (ID: {task['id']}) - status: pending")
        return task

def add_multiple_tasks(count: int) -> list:
    tasks = []
    for i in range(1, count + 1):
        task_name = f"Rozmowa telefoniczna #{i}"
        task = add_task(task_name)
        tasks.append(task)
    return tasks

def show_queue_status():
    if not os.path.exists(QUEUE_FILE):
        print("[PRODUCER] Kolejka jest pusta.")
        return
    
    lock = get_lock()
    with lock:
        with open(QUEUE_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            tasks = list(reader)
        
        pending = sum(1 for t in tasks if t['status'] == 'pending')
        in_progress = sum(1 for t in tasks if t['status'] == 'in_progress')
        done = sum(1 for t in tasks if t['status'] == 'done')
        
        print(f"\n[STATUS KOLEJKI]")
        print(f"  Oczekujące (pending):    {pending}")
        print(f"  W trakcie (in_progress): {in_progress}")
        print(f"  Zakończone (done):       {done}")
        print(f"  RAZEM:                   {len(tasks)}")

def clear_queue():
    if os.path.exists(QUEUE_FILE):
        os.remove(QUEUE_FILE)
        print("[PRODUCER] Kolejka została wyczyszczona.")
    else:
        print("[PRODUCER] Kolejka jest już pusta.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Producer - dodaje zadania do kolejki')
    parser.add_argument('--count', '-c', type=int, default=1, 
                       help='Liczba zadań do dodania (domyślnie: 1)')
    parser.add_argument('--status', '-s', action='store_true',
                       help='Pokaż status kolejki')
    parser.add_argument('--clear', action='store_true',
                       help='Wyczyść kolejkę')
    parser.add_argument('--batch', '-b', type=int,
                       help='Dodaj określoną liczbę zadań (np. 100)')
    
    args = parser.parse_args()
    
    if args.clear:
        clear_queue()
    elif args.status:
        show_queue_status()
    elif args.batch:
        print(f"[PRODUCER] Dodawanie {args.batch} zadań do kolejki...")
        add_multiple_tasks(args.batch)
        print(f"[PRODUCER] Dodano {args.batch} zadań.")
        show_queue_status()
    else:
        for _ in range(args.count):
            add_task()
        show_queue_status()