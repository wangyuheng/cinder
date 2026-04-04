"""
Soul API - REST endpoints for Soul configuration management.
"""

from __future__ import annotations

from typing import Any

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cinder_cli.config import Config

router = APIRouter()


class SoulTraits(BaseModel):
    """Soul traits model."""

    risk_tolerance: int = 50
    structure: int = 50
    detail_orientation: int = 50
    communication_style: str = "balanced"


class SoulConfig(BaseModel):
    """Soul configuration model."""

    traits: SoulTraits = SoulTraits()


def get_soul_path() -> tuple[Any, str]:
    """Get soul configuration path and data."""
    config = Config()
    soul_path = config.get("soul_path", "soul.md")
    meta_path = soul_path.replace(".md", ".meta.yaml")

    try:
        with open(meta_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        data = {"traits": SoulTraits().model_dump()}

    return data, meta_path


@router.get("")
async def get_soul() -> dict[str, Any]:
    """Get current Soul configuration."""
    data, _ = get_soul_path()
    return data


@router.put("")
async def update_soul(config: SoulConfig) -> dict[str, Any]:
    """Update Soul configuration."""
    data, meta_path = get_soul_path()

    data["traits"] = config.traits.model_dump()

    with open(meta_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)

    return {"status": "updated", "traits": config.traits.model_dump()}


@router.post("/init")
async def init_soul() -> dict[str, Any]:
    """Initialize Soul configuration with defaults."""
    _, meta_path = get_soul_path()

    default_config = SoulConfig()
    data = {"traits": default_config.traits.model_dump()}

    with open(meta_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)

    return {"status": "initialized", "traits": default_config.traits.model_dump()}
