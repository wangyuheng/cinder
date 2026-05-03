"""
Database connection manager.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from cinder_cli.config import Config


class DatabaseConnection:
    """Manages SQLite database connection."""
    
    _instance: DatabaseConnection | None = None
    _db_path: Path | None = None
    
    def __new__(cls) -> DatabaseConnection:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._db_path is None:
            config = Config()
            self._db_path = Path(config.get("database_path", "~/.cinder/cinder.db")).expanduser()
    
    @property
    def db_path(self) -> Path:
        """Get database path."""
        return self._db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor
    
    def execute_script(self, script: str) -> None:
        """Execute a script."""
        with self.get_connection() as conn:
            conn.executescript(script)
            conn.commit()
    
    def fetch_one(self, query: str, params: tuple = ()) -> dict[str, Any] | None:
        """Fetch one row."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    def fetch_all(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        """Fetch all rows."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None
        cls._db_path = None
