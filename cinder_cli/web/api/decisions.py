"""
Decisions API - REST endpoints for decision history management.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from cinder_cli.config import Config
from cinder_cli.database import DecisionDatabase

router = APIRouter()


def get_decision_db() -> DecisionDatabase:
    """Get decision database instance."""
    config = Config()
    return DecisionDatabase(config.database_path)


@router.get("")
async def list_decisions(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    """List all decisions with pagination."""
    db = get_decision_db()
    decisions = db.list_decisions(limit=limit + offset)

    return {
        "decisions": decisions[offset : offset + limit],
        "total": len(decisions),
        "limit": limit,
        "offset": offset,
    }


@router.get("/stats")
async def get_decision_stats() -> dict[str, Any]:
    """Get decision statistics."""
    db = get_decision_db()
    stats = db.get_statistics()

    return stats


@router.get("/{decision_id}")
async def get_decision(decision_id: int) -> dict[str, Any]:
    """Get decision details by ID."""
    db = get_decision_db()
    decisions = db.get_all_decisions()

    for decision in decisions:
        if decision.get("id") == decision_id:
            return decision

    raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
