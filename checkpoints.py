"""
LangGraph LocalAI TV Pipeline — Checkpoint Store
SQLite-based checkpoint persistence for pipeline state recovery.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional


class CheckpointStore:
    """
    SQLite checkpoint store for LangGraph pipeline state persistence.
    Enables recovery from failures at any pipeline stage.
    """

    def __init__(self, db_path: str = "./checkpoints.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the checkpoint database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                stage TEXT NOT NULL,
                state TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_run_stage
            ON checkpoints(run_id, stage)
        """)
        conn.commit()
        conn.close()

    def save(self, run_id: str, stage: str, state: dict) -> int:
        """
        Save a checkpoint for a pipeline run.

        Args:
            run_id: Unique identifier for this pipeline run.
            stage: Pipeline stage name (e.g., 'fetch_headlines').
            state: State dict to persist.

        Returns:
            Checkpoint ID.
        """
        now = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO checkpoints (run_id, stage, state, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (run_id, stage, json.dumps(state), now, now),
        )
        checkpoint_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return checkpoint_id

    def load(self, run_id: str, stage: Optional[str] = None) -> Optional[dict]:
        """
        Load the latest checkpoint for a run (optionally at a specific stage).

        Args:
            run_id: Pipeline run ID.
            stage: Optional stage filter.

        Returns:
            State dict or None if no checkpoint found.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if stage:
            cursor.execute(
                """
                SELECT state FROM checkpoints
                WHERE run_id = ? AND stage = ? AND status = 'active'
                ORDER BY created_at DESC LIMIT 1
                """,
                (run_id, stage),
            )
        else:
            cursor.execute(
                """
                SELECT state FROM checkpoints
                WHERE run_id = ? AND status = 'active'
                ORDER BY created_at DESC LIMIT 1
                """,
                (run_id,),
            )

        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def list_runs(self) -> list[dict]:
        """List all pipeline runs with their latest stage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT run_id, stage, status, MAX(created_at) as latest
            FROM checkpoints
            GROUP BY run_id
            ORDER BY latest DESC
            """
        )
        runs = []
        for row in cursor.fetchall():
            runs.append({
                "run_id": row[0],
                "latest_stage": row[1],
                "status": row[2],
                "latest_checkpoint": row[3],
            })
        conn.close()
        return runs

    def invalidate(self, run_id: str):
        """Mark all checkpoints for a run as invalidated."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE checkpoints SET status = 'invalidated' WHERE run_id = ?",
            (run_id,),
        )
        conn.commit()
        conn.close()
