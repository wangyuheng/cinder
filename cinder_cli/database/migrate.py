"""
Database migration script for user onboarding feature.

Usage:
    python -m cinder_cli.database.migrate
"""

from __future__ import annotations

from pathlib import Path

from cinder_cli.config import Config
from cinder_cli.database.connection import DatabaseConnection
from cinder_cli.database.init_db import init_database, SCHEMA


def migrate() -> None:
    """Run database migration."""
    config = Config()
    db_path = Path(config.get("database_path", "~/.cinder/cinder.db")).expanduser()
    
    if db_path.exists():
        print(f"Database already exists at {db_path}")
        print("Checking for missing tables...")
        
        db = DatabaseConnection()
        existing_tables = set()
        rows = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
        for row in rows:
            existing_tables.add(row["name"])
        
        required_tables = {"users", "invitation_codes", "user_sessions", "questionnaire_answers"}
        missing_tables = required_tables - existing_tables
        
        if missing_tables:
            print(f"Creating missing tables: {missing_tables}")
            db.execute_script(SCHEMA)
            print("Migration completed successfully")
        else:
            print("All tables exist, no migration needed")
    else:
        print(f"Creating new database at {db_path}")
        init_database()
        print("Database initialized successfully")


def rollback() -> None:
    """Rollback migration by dropping new tables."""
    config = Config()
    db_path = Path(config.get("database_path", "~/.cinder/cinder.db")).expanduser()
    
    if not db_path.exists():
        print("Database does not exist, nothing to rollback")
        return
    
    db = DatabaseConnection()
    
    tables = ["questionnaire_answers", "user_sessions", "invitation_codes", "users"]
    for table in tables:
        db.execute(f"DROP TABLE IF EXISTS {table}")
    
    print("Rollback completed successfully")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
