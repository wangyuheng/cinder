"""
Database initialization script.
"""

from __future__ import annotations

from cinder_cli.database.connection import DatabaseConnection


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    soul_path TEXT,
    onboarding_completed BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_onboarding ON users(onboarding_completed);

CREATE TABLE IF NOT EXISTS invitation_codes (
    code TEXT PRIMARY KEY,
    is_single_use BOOLEAN NOT NULL,
    used_count INTEGER DEFAULT 0,
    max_uses INTEGER,
    created_at TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS user_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON user_sessions(expires_at);

CREATE TABLE IF NOT EXISTS questionnaire_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_key TEXT NOT NULL,
    choice TEXT NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_answers_user_id ON questionnaire_answers(user_id);
CREATE INDEX IF NOT EXISTS idx_answers_question_key ON questionnaire_answers(question_key);
"""


def init_database() -> None:
    """Initialize database with schema."""
    db = DatabaseConnection()
    db.execute_script(SCHEMA)


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully")
