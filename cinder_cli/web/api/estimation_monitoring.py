"""
Estimation monitoring API endpoints.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from cinder_cli.config import Config
from cinder_cli.monitoring.estimation_monitor import EstimationMonitor


router = APIRouter()


def get_estimation_monitor() -> EstimationMonitor:
    """Get estimation monitor instance."""
    config = Config()
    db_path = config.project_root / ".cinder" / "estimation_tracking.db"
    return EstimationMonitor(db_path)


@router.get("/metrics")
async def get_estimation_metrics(
    days: int = Query(default=30, ge=1, le=365),
    phase: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get estimation accuracy metrics.
    
    Args:
        days: Number of days to include in metrics
        phase: Filter by specific phase
        
    Returns:
        Estimation metrics
    """
    monitor = get_estimation_monitor()
    metrics = monitor.get_metrics(days=days, phase=phase)
    
    return metrics.dict()


@router.get("/trend")
async def get_estimation_trend(
    days: int = Query(default=30, ge=1, le=365),
    granularity: str = Query(default="daily", regex="^(daily|weekly|monthly)$")
) -> Dict[str, Any]:
    """
    Get estimation accuracy trend over time.
    
    Args:
        days: Number of days to include
        granularity: Time granularity (daily, weekly, monthly)
        
    Returns:
        Trend data
    """
    monitor = get_estimation_monitor()
    trend = monitor.get_trend_data(days=days, granularity=granularity)
    
    return {
        "granularity": granularity,
        "days": days,
        "data": trend,
    }


@router.get("/phase-breakdown")
async def get_phase_breakdown(
    days: int = Query(default=30, ge=1, le=365)
) -> Dict[str, Any]:
    """
    Get estimation accuracy breakdown by phase.
    
    Args:
        days: Number of days to include
        
    Returns:
        Phase breakdown
    """
    monitor = get_estimation_monitor()
    breakdown = monitor.get_phase_breakdown(days=days)
    
    return {
        "days": days,
        "phases": breakdown,
    }


@router.get("/alerts")
async def get_estimation_alerts(
    acknowledged: bool = False,
    limit: int = Query(default=100, ge=1, le=1000)
) -> Dict[str, Any]:
    """
    Get estimation alerts.
    
    Args:
        acknowledged: Include acknowledged alerts
        limit: Maximum number of alerts to return
        
    Returns:
        List of alerts
    """
    monitor = get_estimation_monitor()
    alerts = monitor.get_alerts(acknowledged=acknowledged, limit=limit)
    
    return {
        "acknowledged": acknowledged,
        "alerts": alerts,
        "count": len(alerts),
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int) -> Dict[str, Any]:
    """
    Acknowledge an estimation alert.
    
    Args:
        alert_id: Alert ID to acknowledge
        
    Returns:
        Acknowledgment status
    """
    monitor = get_estimation_monitor()
    monitor.acknowledge_alert(alert_id)
    
    return {
        "alert_id": alert_id,
        "status": "acknowledged",
    }


@router.post("/record")
async def record_estimation(
    execution_id: int,
    estimated_time: float,
    actual_time: Optional[float] = None,
    phase: Optional[str] = None
) -> Dict[str, Any]:
    """
    Record an estimation for tracking.
    
    Args:
        execution_id: Execution ID
        estimated_time: Estimated time in seconds
        actual_time: Actual time in seconds (optional)
        phase: Phase name (optional)
        
    Returns:
        Recording status
    """
    monitor = get_estimation_monitor()
    tracking_id = monitor.record_estimation(
        execution_id=execution_id,
        estimated_time=estimated_time,
        actual_time=actual_time,
        phase=phase
    )
    
    return {
        "tracking_id": tracking_id,
        "status": "recorded",
    }


@router.put("/update-actual")
async def update_actual_time(
    execution_id: int,
    actual_time: float
) -> Dict[str, Any]:
    """
    Update actual time for an estimation.
    
    Args:
        execution_id: Execution ID
        actual_time: Actual time in seconds
        
    Returns:
        Update status
    """
    monitor = get_estimation_monitor()
    monitor.update_actual_time(
        execution_id=execution_id,
        actual_time=actual_time
    )
    
    return {
        "execution_id": execution_id,
        "status": "updated",
    }
