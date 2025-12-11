from __future__ import annotations

import argparse
import sqlite3
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "queue.db"

CHECK_INTERVAL = 5
TASK_DURATION = 30


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


def _fetch_pending_task() -> dict | None:
    _init_db()
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            """
            SELECT id, task_name, status, created_at, started_at, finished_at
            FROM jobs
            WHERE status = 'pending'
            ORDER BY created_at
            LIMIT 1
            """
        ).fetchone()

        if row is None:
            connection.commit()
            return None

        started_at = _timestamp()
        updated = connection.execute(
            """
            UPDATE jobs
            SET status = 'in_progress', started_at = ?
            WHERE id = ? AND status = 'pending'
            """,
            (started_at, row["id"]),
        )

        if updated.rowcount != 1:
            connection.rollback()
            return None

        connection.commit()
        task = dict(row)
        task["status"] = "in_progress"
        task["started_at"] = started_at
        return task
    finally:
        connection.close()


def mark_task_done(task_id: str) -> None:
    _init_db()
    with sqlite3.connect(DB_FILE) as connection:
        finished_at = _timestamp()
        connection.execute(
            """
            UPDATE jobs
            SET status = 'done', finished_at = ?
            WHERE id = ?
            """,
            (finished_at, task_id),
        )
        connection.commit()


def show_queue_status(consumer_id: str) -> None:
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

    print(
        f"[CONSUMER-SQL {consumer_id}] Status: pending={summary['pending']}, "
        f"in_progress={summary['in_progress']}, done={summary['done']}"
    )


def process_task(task: dict, consumer_id: str) -> None:
    print(
        f"[CONSUMER-SQL {consumer_id}] Rozpoczynam: {task['task_name']} (ID: {task['id']})"
    )
    print(
        f"[CONSUMER-SQL {consumer_id}] Status: in_progress | Czas wykonania: {TASK_DURATION}s"
    )

    for remaining in range(TASK_DURATION, 0, -1):
        time.sleep(1)
        if remaining % 10 == 0:
            print(
                f"[CONSUMER-SQL {consumer_id}] {task['task_name']} - pozostało {remaining}s..."
            )

    mark_task_done(task["id"])
    print(
        f"[CONSUMER-SQL {consumer_id}] Zakończono: {task['task_name']} (ID: {task['id']}) - status: done"
    )


def run_consumer(consumer_id: str = "1") -> None:
    print(
        f"[CONSUMER-SQL {consumer_id}] Uruchomiono. Sprawdzanie kolejki co {CHECK_INTERVAL}s..."
    )
    print(f"[CONSUMER-SQL {consumer_id}] Czas wykonania zadania: {TASK_DURATION}s")
    print("-" * 60)

    while True:
        try:
            task = _fetch_pending_task()
            if task:
                process_task(task, consumer_id)
                show_queue_status(consumer_id)
            else:
                print(
                    f"[CONSUMER-SQL {consumer_id}] Brak zadań do wykonania. Czekam {CHECK_INTERVAL}s..."
                )
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print(f"\n[CONSUMER-SQL {consumer_id}] Zatrzymano przez użytkownika.")
            break
        except sqlite3.OperationalError as exc:
            print(
                f"[CONSUMER-SQL {consumer_id}] Błąd transakcji ({exc}). Czekam {CHECK_INTERVAL}s..."
            )
            time.sleep(CHECK_INTERVAL)
        except Exception as exc:
            print(
                f"[CONSUMER-SQL {consumer_id}] Nieoczekiwany błąd ({exc}). Czekam {CHECK_INTERVAL}s..."
            )
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Consumer SQL - wykonuje zadania z kolejki w SQLite"
    )
    parser.add_argument(
        "--id",
        "-i",
        type=str,
        default="1",
        help="Unikalny identyfikator konsumera (domyślnie: 1)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Interwał sprawdzania kolejki w sekundach (domyślnie: 5)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Czas wykonania zadania w sekundach (domyślnie: 30)",
    )

    args = parser.parse_args()
    CHECK_INTERVAL = args.interval
    TASK_DURATION = args.duration

    run_consumer(args.id)