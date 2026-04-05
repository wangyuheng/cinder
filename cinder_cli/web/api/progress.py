"""
Web API for real-time execution progress.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from cinder_cli.config import Config
from cinder_cli.executor import ExecutionLogger


router = APIRouter()


def get_logger() -> ExecutionLogger:
    """Get execution logger instance."""
    config = Config()
    return ExecutionLogger(config)


@router.get("/current/progress")
async def stream_current_progress() -> StreamingResponse:
    """
    Stream real-time progress updates via Server-Sent Events.
    
    Returns:
        StreamingResponse with SSE events
    """
    async def event_stream():
        while True:
            try:
                progress_data = {
                    "timestamp": asyncio.get_event_loop().time(),
                    "status": "active",
                    "message": "Progress streaming active",
                }
                yield f"data: {json.dumps(progress_data)}\n\n"
                await asyncio.sleep(1)
            except Exception as e:
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
                break
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/{execution_id}/progress")
async def stream_execution_progress(execution_id: int) -> StreamingResponse:
    """
    Stream progress updates for a specific execution.
    
    Args:
        execution_id: Execution ID to monitor
        
    Returns:
        StreamingResponse with SSE events
    """
    logger = get_logger()
    execution = logger.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")
    
    async def event_stream():
        while True:
            try:
                execution = logger.get_execution(execution_id)
                if not execution:
                    break
                
                progress_data = {
                    "execution_id": execution_id,
                    "status": execution.get("status"),
                    "progress_data": execution.get("progress_data"),
                    "speed_metrics": execution.get("speed_metrics"),
                }
                
                yield f"data: {json.dumps(progress_data, ensure_ascii=False)}\n\n"
                
                if execution.get("status") in ["success", "error", "failed"]:
                    break
                
                await asyncio.sleep(1)
            except Exception as e:
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
                break
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/stats/estimation")
async def get_estimation_stats() -> dict[str, Any]:
    """
    Get execution statistics for estimation.
    
    Returns:
        Execution statistics
    """
    logger = get_logger()
    stats = logger.get_execution_statistics()
    
    return {
        "statistics": stats,
        "timestamp": asyncio.get_event_loop().time(),
    }
