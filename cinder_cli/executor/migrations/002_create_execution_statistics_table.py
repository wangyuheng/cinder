"""
Database migration script to create execution statistics table.

Migration: 002_create_execution_statistics_table.py
Created: 2026-04-04
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    """Get database path."""
    db_dir = Path.home() / ".cinder"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "executions.db"


def migrate_up():
    """Apply migration - create execution statistics table."""
    db_path = get_db_path()
    
    if not db_path.exists():
        print("Database does not exist. It will be created by ExecutionLogger.")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='execution_statistics'
        """)
        
        if cursor.fetchone():
            print("✓ Migration already applied, execution_statistics table exists")
            return
        
        cursor.execute("""
            CREATE TABLE execution_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                goal_type TEXT,
                total_tasks INTEGER,
                execution_time REAL,
                phase_breakdown TEXT,
                speed_metrics TEXT,
                quality_score REAL,
                success BOOLEAN
            )
        """)
        
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_stats_timestamp ON execution_statistics(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_stats_goal_type ON execution_statistics(goal_type)"
        )
        
        conn.commit()
        print("✓ Migration applied: created execution_statistics table")


def migrate_down():
    """Rollback migration - drop execution statistics table."""
    db_path = get_db_path()
    
    if not db_path.exists():
        print("Database does not exist. Nothing to rollback.")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='execution_statistics'
        """)
        
        if not cursor.fetchone():
            print("✓ Migration already rolled back, execution_statistics table does not exist")
            return
        
        cursor.execute("DROP TABLE execution_statistics")
        
        conn.commit()
        print("✓ Migration rolled back: dropped execution_statistics table")


def main():
    """Run migration."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        print("Rolling back migration...")
        migrate_down()
    else:
        print("Applying migration...")
        migrate_up()


if __name__ == "__main__":
    main()
