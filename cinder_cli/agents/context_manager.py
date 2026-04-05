"""
Complete context management system with short-term and long-term storage.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from cinder_cli.agents.context import (
    BaseContextManager,
    ContextEntry,
    InMemoryContextManager,
)


class ContextManager(BaseContextManager):
    """
    Complete context manager with short-term (memory) and long-term (SQLite) storage.
    """
    
    def __init__(
        self,
        db_path: Path,
        user_id: str = "default",
        project_id: str = "default",
        session_id: str | None = None,
        max_memory_mb: int = 100,
        sync_interval_seconds: int = 30,
        retention_days: int = 30,
    ):
        self.db_path = Path(db_path)
        self.user_id = user_id
        self.project_id = project_id
        self.session_id = session_id or f"session_{datetime.now().timestamp()}"
        
        self.short_term = InMemoryContextManager(max_size_mb=max_memory_mb)
        self.sync_interval = timedelta(seconds=sync_interval_seconds)
        self.retention_days = retention_days
        
        self.last_sync = datetime.now()
        self._init_database()
        
    def _init_database(self) -> None:
        """Initialize SQLite database for long-term storage."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_entries (
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    session_id TEXT,
                    metadata TEXT,
                    PRIMARY KEY (key, user_id, project_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON context_entries(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_project 
                ON context_entries(user_id, project_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session 
                ON context_entries(session_id)
            """)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context (checks short-term first, then long-term)."""
        value = self.short_term.get(key, None)
        if value is not None:
            return value
        
        entry = self._load_from_db(key)
        if entry is not None:
            self.short_term.set(entry.key, entry.value, entry.scope)
            return entry.value
        
        return default
    
    def set(self, key: str, value: Any, scope: str = "session") -> None:
        """Set a value in context."""
        self.short_term.set(key, value, scope)
        self._auto_sync()
    
    def delete(self, key: str) -> bool:
        """Delete a value from context."""
        deleted = self.short_term.delete(key)
        if deleted:
            self._delete_from_db(key)
        return deleted
    
    def query(self, filter_dict: dict[str, Any]) -> list[ContextEntry]:
        """Query context entries matching filter."""
        results = self.short_term.query(filter_dict)
        
        if not results:
            results = self._query_from_db(filter_dict)
        
        return results
    
    def clear(self, scope: str | None = None) -> None:
        """Clear context entries."""
        self.short_term.clear(scope)
        self._clear_from_db(scope)
    
    def save(self) -> None:
        """Persist all short-term context to long-term storage."""
        entries = self.short_term.query({})
        
        with sqlite3.connect(self.db_path) as conn:
            for entry in entries:
                conn.execute("""
                    INSERT OR REPLACE INTO context_entries 
                    (key, value, timestamp, scope, user_id, project_id, session_id, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.key,
                    json.dumps(entry.value),
                    entry.timestamp.isoformat(),
                    entry.scope,
                    self.user_id,
                    self.project_id,
                    self.session_id if entry.scope == "session" else None,
                    json.dumps(entry.metadata),
                ))
        
        self.last_sync = datetime.now()
    
    def load(self) -> None:
        """Load context from long-term storage."""
        entries = self._query_from_db({
            "user_id": self.user_id,
            "project_id": self.project_id,
        })
        
        for entry in entries:
            self.short_term.set(entry.key, entry.value, entry.scope)
    
    def get_size(self) -> int:
        """Get size of short-term context in bytes."""
        return self.short_term.get_size()
    
    def get_entry_count(self) -> int:
        """Get number of entries in short-term context."""
        return self.short_term.get_entry_count()
    
    def _load_from_db(self, key: str) -> ContextEntry | None:
        """Load a single entry from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key, value, timestamp, scope, metadata
                FROM context_entries
                WHERE key = ? AND user_id = ? AND project_id = ?
            """, (key, self.user_id, self.project_id))
            
            row = cursor.fetchone()
            if row is None:
                return None
            
            return ContextEntry(
                key=row[0],
                value=json.loads(row[1]),
                timestamp=datetime.fromisoformat(row[2]),
                scope=row[3],
                metadata=json.loads(row[4]) if row[4] else {},
            )
    
    def _delete_from_db(self, key: str) -> None:
        """Delete an entry from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM context_entries
                WHERE key = ? AND user_id = ? AND project_id = ?
            """, (key, self.user_id, self.project_id))
    
    def _query_from_db(self, filter_dict: dict[str, Any]) -> list[ContextEntry]:
        """Query entries from database."""
        query = """
            SELECT key, value, timestamp, scope, metadata
            FROM context_entries
            WHERE user_id = ? AND project_id = ?
        """
        params = [self.user_id, self.project_id]
        
        if "scope" in filter_dict:
            query += " AND scope = ?"
            params.append(filter_dict["scope"])
        
        if "session_id" in filter_dict:
            query += " AND session_id = ?"
            params.append(filter_dict["session_id"])
        
        if "after" in filter_dict:
            query += " AND timestamp >= ?"
            params.append(filter_dict["after"].isoformat())
        
        if "before" in filter_dict:
            query += " AND timestamp <= ?"
            params.append(filter_dict["before"].isoformat())
        
        query += " ORDER BY timestamp DESC"
        
        entries = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            for row in cursor:
                entries.append(ContextEntry(
                    key=row[0],
                    value=json.loads(row[1]),
                    timestamp=datetime.fromisoformat(row[2]),
                    scope=row[3],
                    metadata=json.loads(row[4]) if row[4] else {},
                ))
        
        return entries
    
    def _clear_from_db(self, scope: str | None) -> None:
        """Clear entries from database."""
        query = "DELETE FROM context_entries WHERE user_id = ? AND project_id = ?"
        params = [self.user_id, self.project_id]
        
        if scope is not None:
            query += " AND scope = ?"
            params.append(scope)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)
    
    def _auto_sync(self) -> None:
        """Auto-sync to database if interval has passed."""
        if datetime.now() - self.last_sync >= self.sync_interval:
            self.save()
    
    def cleanup_old_entries(self) -> int:
        """Remove entries older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM context_entries
                WHERE timestamp < ? AND scope != 'user'
            """, (cutoff.isoformat(),))
            
            return cursor.rowcount
    
    def get_statistics(self) -> dict[str, Any]:
        """Get context statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_entries,
                    COUNT(CASE WHEN scope = 'session' THEN 1 END) as session_entries,
                    COUNT(CASE WHEN scope = 'user' THEN 1 END) as user_entries,
                    COUNT(CASE WHEN scope = 'project' THEN 1 END) as project_entries
                FROM context_entries
                WHERE user_id = ? AND project_id = ?
            """, (self.user_id, self.project_id))
            
            row = cursor.fetchone()
            
            return {
                "total_entries": row[0],
                "session_entries": row[1],
                "user_entries": row[2],
                "project_entries": row[3],
                "short_term_size_bytes": self.get_size(),
                "short_term_entries": self.get_entry_count(),
                "last_sync": self.last_sync.isoformat(),
            }
