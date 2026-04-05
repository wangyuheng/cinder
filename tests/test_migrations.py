"""
Unit tests for database migrations.
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from cinder_cli.executor.migrations import (
    migrate_up as migrate_001_up,
    migrate_down as migrate_001_down,
)
from cinder_cli.executor.migrations import (
    migrate_up as migrate_002_up,
    migrate_down as migrate_002_down,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_executions.db"
        
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE executions (
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
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON executions(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON executions(status)")
        conn.commit()
        conn.close()
        
        yield db_path


def test_migration_001_adds_new_fields(temp_db):
    """Test that migration 001 adds new fields to executions table."""
    with patch('cinder_cli.executor.migrations.001_add_progress_tracking_fields.get_db_path', return_value=temp_db):
        migrate_001_up()
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("PRAGMA table_info(executions)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    assert "phase_timestamps" in columns
    assert "progress_data" in columns
    assert "speed_metrics" in columns
    assert "estimation_data" in columns


def test_migration_001_is_idempotent(temp_db):
    """Test that migration 001 can be run multiple times safely."""
    with patch('cinder_cli.executor.migrations.001_add_progress_tracking_fields.get_db_path', return_value=temp_db):
        migrate_001_up()
        migrate_001_up()
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("PRAGMA table_info(executions)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    assert columns.count("phase_timestamps") == 1
    assert columns.count("progress_data") == 1


def test_migration_001_rollback(temp_db):
    """Test that migration 001 can be rolled back."""
    with patch('cinder_cli.executor.migrations.001_add_progress_tracking_fields.get_db_path', return_value=temp_db):
        migrate_001_up()
        migrate_001_down()
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("PRAGMA table_info(executions)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    assert "phase_timestamps" not in columns
    assert "progress_data" not in columns
    assert "speed_metrics" not in columns
    assert "estimation_data" not in columns


def test_migration_002_creates_statistics_table(temp_db):
    """Test that migration 002 creates execution_statistics table."""
    with patch('cinder_cli.executor.migrations.002_create_execution_statistics_table.get_db_path', return_value=temp_db):
        migrate_002_up()
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='execution_statistics'
    """)
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == "execution_statistics"


def test_migration_002_is_idempotent(temp_db):
    """Test that migration 002 can be run multiple times safely."""
    with patch('cinder_cli.executor.migrations.002_create_execution_statistics_table.get_db_path', return_value=temp_db):
        migrate_002_up()
        migrate_002_up()
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("""
        SELECT COUNT(*) FROM sqlite_master 
        WHERE type='table' AND name='execution_statistics'
    """)
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 1


def test_migration_002_rollback(temp_db):
    """Test that migration 002 can be rolled back."""
    with patch('cinder_cli.executor.migrations.002_create_execution_statistics_table.get_db_path', return_value=temp_db):
        migrate_002_up()
        migrate_002_down()
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='execution_statistics'
    """)
    result = cursor.fetchone()
    conn.close()
    
    assert result is None


def test_migration_preserves_existing_data(temp_db):
    """Test that migrations preserve existing data."""
    conn = sqlite3.connect(temp_db)
    conn.execute(
        "INSERT INTO executions (timestamp, goal, status) VALUES (?, ?, ?)",
        ("2026-04-04T12:00:00", "Test goal", "success")
    )
    conn.commit()
    conn.close()
    
    with patch('cinder_cli.executor.migrations.001_add_progress_tracking_fields.get_db_path', return_value=temp_db):
        migrate_001_up()
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.execute("SELECT goal, status FROM executions WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == "Test goal"
    assert row[1] == "success"
