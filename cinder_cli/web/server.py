"""
FastAPI Server - Main application for web dashboard.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cinder_cli.config import Config
from cinder_cli.web.api import executions, soul, decisions, tasks


def create_app(config: Config | None = None) -> FastAPI:
    """
    Create FastAPI application.

    Args:
        config: Optional configuration object

    Returns:
        FastAPI application instance
    """
    if config is None:
        config = Config()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        yield

    app = FastAPI(
        title="Cinder Dashboard API",
        description="REST API for Cinder Web Dashboard",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(executions.router, prefix="/api/executions", tags=["executions"])
    app.include_router(soul.router, prefix="/api/soul", tags=["soul"])
    app.include_router(decisions.router, prefix="/api/decisions", tags=["decisions"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

    @app.get("/api/health")
    async def health_check():
        return {"status": "ok"}

    return app
