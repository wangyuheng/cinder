"""
Feedback API endpoints.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from cinder_cli.config import Config
from cinder_cli.feedback.collector import (
    FeedbackCollector,
    UserFeedback,
    FeedbackType,
)


router = APIRouter()


def get_feedback_collector() -> FeedbackCollector:
    """Get feedback collector instance."""
    config = Config()
    db_path = config.project_root / ".cinder" / "feedback.db"
    return FeedbackCollector(db_path)


class FeedbackSubmission(BaseModel):
    """Feedback submission model."""
    execution_id: int
    feedback_type: str
    rating: int = Field(ge=1, le=5, description="Rating from 1 to 5")
    comment: str | None = None
    estimated_time: float | None = None
    actual_time: float | None = None
    user_id: str | None = None


class FeedbackResponse(BaseModel):
    """Feedback response model."""
    feedback_id: int
    message: str


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackSubmission) -> FeedbackResponse:
    """
    Submit user feedback for an execution.
    
    Args:
        feedback: Feedback submission data
        
    Returns:
        Feedback response with ID
    """
    collector = get_feedback_collector()
    
    estimation_accuracy = None
    if feedback.estimated_time and feedback.actual_time:
        if feedback.actual_time > 0:
            estimation_accuracy = max(0, 100 - abs(
                feedback.estimated_time - feedback.actual_time
            ) / feedback.actual_time * 100)
    
    user_feedback = UserFeedback(
        execution_id=feedback.execution_id,
        feedback_type=feedback.feedback_type,
        rating=feedback.rating,
        comment=feedback.comment,
        estimated_time=feedback.estimated_time,
        actual_time=feedback.actual_time,
        estimation_accuracy=estimation_accuracy,
        user_id=feedback.user_id,
    )
    
    feedback_id = collector.submit_feedback(user_feedback)
    
    return FeedbackResponse(
        feedback_id=feedback_id,
        message="Thank you for your feedback!"
    )


@router.get("/execution/{execution_id}")
async def get_execution_feedback(execution_id: int) -> Dict[str, Any]:
    """
    Get all feedback for an execution.
    
    Args:
        execution_id: Execution ID
        
    Returns:
        List of feedback for the execution
    """
    collector = get_feedback_collector()
    feedback = collector.get_feedback_by_execution(execution_id)
    
    return {
        "execution_id": execution_id,
        "feedback": feedback,
        "count": len(feedback),
    }


@router.get("/statistics")
async def get_feedback_statistics() -> Dict[str, Any]:
    """
    Get overall feedback statistics.
    
    Returns:
        Feedback statistics
    """
    collector = get_feedback_collector()
    stats = collector.get_feedback_statistics()
    
    return stats


@router.get("/estimation-accuracy")
async def get_estimation_accuracy() -> Dict[str, Any]:
    """
    Get estimation accuracy metrics.
    
    Returns:
        Estimation accuracy metrics
    """
    collector = get_feedback_collector()
    metrics = collector.get_estimation_accuracy_metrics()
    
    return metrics


@router.get("/type/{feedback_type}")
async def get_feedback_by_type(
    feedback_type: str,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get feedback by type.
    
    Args:
        feedback_type: Type of feedback
        limit: Maximum number of results
        
    Returns:
        List of feedback of the specified type
    """
    valid_types = [
        FeedbackType.ESTIMATION_ACCURACY,
        FeedbackType.PROGRESS_DISPLAY,
        FeedbackType.PERFORMANCE,
        FeedbackType.BUG_REPORT,
        FeedbackType.FEATURE_REQUEST,
        FeedbackType.GENERAL,
    ]
    
    if feedback_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid feedback type. Valid types: {valid_types}"
        )
    
    collector = get_feedback_collector()
    feedback = collector.get_feedback_by_type(feedback_type, limit)
    
    return {
        "feedback_type": feedback_type,
        "feedback": feedback,
        "count": len(feedback),
    }
