from __future__ import annotations

import argparse
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "queue.db"


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _init_db() -> None:
    with sqlite3.connect(DB_FILE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                task_name TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT
            )
            """
        )
        connection.commit()


def add_task(task_name: str | None = None) -> dict:
    _init_db()
    task_id = uuid.uuid4().hex[:8]
    if task_name is None:
        task_name = f"Rozmowa telefoniczna #{task_id}"

    created_at = _timestamp()
    task = {
        "id": task_id,
        "task_name": task_name,
        "status": "pending",
        "created_at": created_at,
        "started_at": None,
        "finished_at": None,
    }

    with sqlite3.connect(DB_FILE) as connection:
        connection.execute(
            """
            INSERT INTO jobs (id, task_name, status, created_at, started_at, finished_at)
            VALUES (?, ?, 'pending', ?, NULL, NULL)
            """,
            (task_id, task_name, created_at),
        )
        connection.commit()

    print(
        f"[PRODUCER-SQL] Dodano zadanie: {task['task_name']} (ID: {task['id']}) - status: pending"
    )
    return task


def add_multiple_tasks(count: int) -> list[dict]:
    tasks: list[dict] = []
    for i in range(1, count + 1):
        tasks.append(add_task(f"Rozmowa telefoniczna #{i}"))
    return tasks


def show_queue_status() -> None:
    _init_db()
    with sqlite3.connect(DB_FILE) as connection:
        rows = connection.execute(
            "SELECT status, COUNT(*) as total FROM jobs GROUP BY status"
        ).fetchall()

    summary = {"pending": 0, "in_progress": 0, "done": 0}
    total = 0
    for status, count in rows:
        summary[status] = count
        total += count

    print("\n[STATUS KOLEJKI - SQLite]")
    print(f"  Oczekujące (pending):    {summary['pending']}")
    print(f"  W trakcie (in_progress): {summary['in_progress']}")
    print(f"  Zakończone (done):       {summary['done']}")
    print(f"  RAZEM:                   {total}")


def clear_queue() -> None:
    if not DB_FILE.exists():
        print("[PRODUCER-SQL] Kolejka jest już pusta.")
        return

    with sqlite3.connect(DB_FILE) as connection:
        connection.execute("DELETE FROM jobs")
        connection.commit()
    print("[PRODUCER-SQL] Kolejka została wyczyszczona.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Producer SQL - dodaje zadania do kolejki w SQLite"
    )
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1,
        help="Liczba zadań do dodania (domyślnie: 1)",
    )
    parser.add_argument(
        "--status",
        "-s",
        action="store_true",
        help="Pokaż status kolejki",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Wyczyść kolejkę",
    )
    parser.add_argument(
        "--batch",
        "-b",
        type=int,
        help="Dodaj określoną liczbę zadań (np. 100)",
    )

    args = parser.parse_args()

    if args.clear:
        clear_queue()
    elif args.status:
        show_queue_status()
    elif args.batch:
        print(f"[PRODUCER-SQL] Dodawanie {args.batch} zadań do kolejki...")
        add_multiple_tasks(args.batch)
        print(f"[PRODUCER-SQL] Dodano {args.batch} zadań.")
        show_queue_status()
    else:
        for _ in range(args.count):
            add_task()
        show_queue_status()