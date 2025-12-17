import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

DB_PATH = Path(__file__).parent / "tasks.db"


def _utc_now() -> str:
    return datetime.utcnow().isoformat()


@contextmanager
def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                person_count INTEGER,
                error TEXT,
                output_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)"
        )


def upsert_task(
    task_id: str,
    url: str,
    status: str,
    person_count: Optional[int] = None,
    error: Optional[str] = None,
    output_path: Optional[str] = None,
) -> None:
    now = _utc_now()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO tasks (task_id, url, status, person_count, error, output_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
                status=excluded.status,
                person_count=excluded.person_count,
                error=excluded.error,
                output_path=excluded.output_path,
                updated_at=excluded.updated_at
            """,
            (task_id, url, status, person_count, error, output_path, now, now),
        )


def mark_status(
    task_id: str,
    status: str,
    person_count: Optional[int] = None,
    error: Optional[str] = None,
    output_path: Optional[str] = None,
) -> None:
    with _connect() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET status = ?,
                person_count = ?,
                error = ?,
                output_path = ?,
                updated_at = ?
            WHERE task_id = ?
            """,
            (status, person_count, error, output_path, _utc_now(), task_id),
        )


def get_task(task_id: str) -> Optional[Dict]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT task_id, url, status, person_count, error, output_path, created_at, updated_at FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        return dict(row) if row else None
