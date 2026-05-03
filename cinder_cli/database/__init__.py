"""
Database module for user management and onboarding.
"""

from cinder_cli.database.connection import DatabaseConnection
from cinder_cli.database.init_db import init_database
from cinder_cli.database.models import (
    InvitationCode,
    QuestionnaireAnswer,
    User,
    UserSession,
)

try:
    from cinder_cli.database_legacy import DecisionDatabase
except ImportError:
    DecisionDatabase = None

__all__ = [
    "DatabaseConnection",
    "init_database",
    "User",
    "InvitationCode",
    "UserSession",
    "QuestionnaireAnswer",
    "DecisionDatabase",
]
