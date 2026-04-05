"""
Database migration script to add progress tracking fields.

Migration: 001_add_progress_tracking_fields.py
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
    """Apply migration - add new fields for progress tracking."""
    db_path = get_db_path()
    
    if not db_path.exists():
        print("Database does not exist. It will be created by ExecutionLogger.")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(executions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        migrations_applied = []
        
        if "phase_timestamps" not in columns:
            cursor.execute(
                "ALTER TABLE executions ADD COLUMN phase_timestamps TEXT"
            )
            migrations_applied.append("phase_timestamps")
        
        if "progress_data" not in columns:
            cursor.execute(
                "ALTER TABLE executions ADD COLUMN progress_data TEXT"
            )
            migrations_applied.append("progress_data")
        
        if "speed_metrics" not in columns:
            cursor.execute(
                "ALTER TABLE executions ADD COLUMN speed_metrics TEXT"
            )
            migrations_applied.append("speed_metrics")
        
        if "estimation_data" not in columns:
            cursor.execute(
                "ALTER TABLE executions ADD COLUMN estimation_data TEXT"
            )
            migrations_applied.append("estimation_data")
        
        conn.commit()
        
        if migrations_applied:
            print(f"✓ Migration applied: added fields {', '.join(migrations_applied)}")
        else:
            print("✓ Migration already applied, no changes needed")


def migrate_down():
    """Rollback migration - remove progress tracking fields.
    
    Note: SQLite does not support DROP COLUMN directly.
    This creates a new table without the new fields and copies data.
    """
    db_path = get_db_path()
    
    if not db_path.exists():
        print("Database does not exist. Nothing to rollback.")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(executions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        new_fields = ["phase_timestamps", "progress_data", "speed_metrics", "estimation_data"]
        has_new_fields = any(field in columns for field in new_fields)
        
        if not has_new_fields:
            print("✓ Migration already rolled back, no changes needed")
            return
        
        cursor.execute("""
            CREATE TABLE executions_backup (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                goal TEXT NOT NULL,
                task_tree TEXT,
                results TEXT,
                status TEXT NOT NULL,
                created_files TEXT,
                execution_time REAL
            )
        """)
        
        cursor.execute("""
            INSERT INTO executions_backup 
            SELECT id, timestamp, goal, task_tree, results, status, created_files, execution_time
            FROM executions
        """)
        
        cursor.execute("DROP TABLE executions")
        
        cursor.execute("ALTER TABLE executions_backup RENAME TO executions")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON executions(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON executions(status)")
        
        conn.commit()
        print("✓ Migration rolled back: removed progress tracking fields")


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
