"""
Health check and monitoring endpoints.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter

from cinder_cli.config import Config
from cinder_cli.executor import ExecutionLogger


router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for progress tracking system.
    
    Returns:
        Health status of all components
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {},
    }
    
    try:
        config = Config()
        logger = ExecutionLogger(config)
        
        executions = logger.list_executions(limit=1)
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful",
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": str(e),
        }
    
    try:
        from cinder_cli.executor.progress_tracker import ProgressTracker
        tracker = ProgressTracker()
        progress = tracker.get_progress()
        
        health_status["components"]["progress_tracker"] = {
            "status": "healthy",
            "message": "Progress tracker operational",
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["progress_tracker"] = {
            "status": "unhealthy",
            "message": str(e),
        }
    
    return health_status


@router.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    """
    Get performance metrics for progress tracking system.
    
    Returns:
        Performance metrics and statistics
    """
    config = Config()
    logger = ExecutionLogger(config)
    
    stats = logger.get_execution_statistics(limit=100)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "total_executions": stats.get("total", 0),
            "avg_execution_time": stats.get("avg_execution_time", 0),
            "avg_tasks_count": stats.get("avg_tasks_count", 0),
            "phase_statistics": stats.get("phase_statistics", {}),
        },
    }


@router.get("/status")
async def get_system_status() -> dict[str, Any]:
    """
    Get overall system status.
    
    Returns:
        System status information
    """
    config = Config()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "operational",
        "version": "1.0.0",
        "config": {
            "progress_tracking_enabled": config.get("progress_tracking", True),
            "estimation_enabled": config.get("estimation", {}).get("enabled", True),
            "max_sse_connections": config.get("web", {}).get("max_sse_connections", 10),
        },
    }
