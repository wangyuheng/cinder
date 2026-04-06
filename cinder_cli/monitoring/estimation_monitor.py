"""
Estimation accuracy monitoring system.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class EstimationMetrics(BaseModel):
    """Estimation metrics model."""
    total_estimations: int
    accurate_estimations: int
    average_error: float
    average_accuracy: float
    confidence_level: float
    time_period: str


class EstimationMonitor:
    """Monitors and tracks estimation accuracy."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize estimation monitoring database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estimation_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id INTEGER NOT NULL,
                estimated_time REAL NOT NULL,
                actual_time REAL,
                error_percentage REAL,
                accuracy_score REAL,
                phase TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_estimation_execution
            ON estimation_tracking(execution_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_estimation_timestamp
            ON estimation_tracking(timestamp)
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estimation_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                metric_value REAL,
                threshold REAL,
                timestamp TEXT NOT NULL,
                acknowledged INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_estimation(
        self,
        execution_id: int,
        estimated_time: float,
        actual_time: Optional[float] = None,
        phase: Optional[str] = None
    ) -> int:
        """Record an estimation for tracking."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        error_percentage = None
        accuracy_score = None
        
        if actual_time and actual_time > 0:
            error_percentage = abs(estimated_time - actual_time) / actual_time * 100
            accuracy_score = max(0, 100 - error_percentage)
        
        cursor.execute("""
            INSERT INTO estimation_tracking (
                execution_id, estimated_time, actual_time,
                error_percentage, accuracy_score, phase, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            execution_id,
            estimated_time,
            actual_time,
            error_percentage,
            accuracy_score,
            phase,
            datetime.now().isoformat(),
        ))
        
        tracking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        if actual_time:
            self._check_thresholds(accuracy_score, error_percentage)
        
        return tracking_id
    
    def update_actual_time(
        self,
        execution_id: int,
        actual_time: float
    ) -> None:
        """Update actual time for an estimation."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT estimated_time FROM estimation_tracking
            WHERE execution_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (execution_id,))
        
        row = cursor.fetchone()
        if row:
            estimated_time = row[0]
            error_percentage = abs(estimated_time - actual_time) / actual_time * 100
            accuracy_score = max(0, 100 - error_percentage)
            
            cursor.execute("""
                UPDATE estimation_tracking
                SET actual_time = ?, error_percentage = ?, accuracy_score = ?
                WHERE execution_id = ?
            """, (actual_time, error_percentage, accuracy_score, execution_id))
            
            conn.commit()
            
            self._check_thresholds(accuracy_score, error_percentage)
        
        conn.close()
    
    def get_metrics(
        self,
        days: int = 30,
        phase: Optional[str] = None
    ) -> EstimationMetrics:
        """Get estimation metrics for a time period."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        query = """
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN accuracy_score >= 80 THEN 1 END) as accurate,
                AVG(error_percentage) as avg_error,
                AVG(accuracy_score) as avg_accuracy
            FROM estimation_tracking
            WHERE timestamp >= ?
            AND actual_time IS NOT NULL
        """
        
        params = [cutoff_date]
        
        if phase:
            query += " AND phase = ?"
            params.append(phase)
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        total = row[0] or 0
        accurate = row[1] or 0
        avg_error = row[2] or 0.0
        avg_accuracy = row[3] or 0.0
        
        confidence = self._calculate_confidence(total, avg_accuracy)
        
        return EstimationMetrics(
            total_estimations=total,
            accurate_estimations=accurate,
            average_error=avg_error,
            average_accuracy=avg_accuracy,
            confidence_level=confidence,
            time_period=f"{days} days",
        )
    
    def get_trend_data(
        self,
        days: int = 30,
        granularity: str = "daily"
    ) -> List[Dict[str, Any]]:
        """Get estimation accuracy trend over time."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        if granularity == "daily":
            group_by = "date(timestamp)"
        elif granularity == "weekly":
            group_by = "strftime('%Y-%W', timestamp)"
        else:
            group_by = "strftime('%Y-%m', timestamp)"
        
        cursor.execute(f"""
            SELECT
                {group_by} as period,
                COUNT(*) as total,
                AVG(error_percentage) as avg_error,
                AVG(accuracy_score) as avg_accuracy
            FROM estimation_tracking
            WHERE timestamp >= ?
            AND actual_time IS NOT NULL
            GROUP BY {group_by}
            ORDER BY period
        """, (cutoff_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "period": row[0],
                "total": row[1],
                "average_error": row[2],
                "average_accuracy": row[3],
            }
            for row in rows
        ]
    
    def get_alerts(
        self,
        acknowledged: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get estimation alerts."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM estimation_alerts
            WHERE acknowledged = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        cursor.execute(query, (1 if acknowledged else 0, limit))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "alert_type": row[1],
                "message": row[2],
                "metric_value": row[3],
                "threshold": row[4],
                "timestamp": row[5],
                "acknowledged": bool(row[6]),
            }
            for row in rows
        ]
    
    def acknowledge_alert(self, alert_id: int) -> None:
        """Acknowledge an alert."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE estimation_alerts
            SET acknowledged = 1
            WHERE id = ?
        """, (alert_id,))
        
        conn.commit()
        conn.close()
    
    def _check_thresholds(
        self,
        accuracy_score: float,
        error_percentage: float
    ) -> None:
        """Check if metrics exceed thresholds and create alerts."""
        accuracy_threshold = 70.0
        error_threshold = 30.0
        
        if accuracy_score < accuracy_threshold:
            self._create_alert(
                alert_type="low_accuracy",
                message=f"Estimation accuracy below threshold: {accuracy_score:.1f}% < {accuracy_threshold}%",
                metric_value=accuracy_score,
                threshold=accuracy_threshold,
            )
        
        if error_percentage > error_threshold:
            self._create_alert(
                alert_type="high_error",
                message=f"Estimation error above threshold: {error_percentage:.1f}% > {error_threshold}%",
                metric_value=error_percentage,
                threshold=error_threshold,
            )
    
    def _create_alert(
        self,
        alert_type: str,
        message: str,
        metric_value: float,
        threshold: float
    ) -> None:
        """Create an estimation alert."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO estimation_alerts (
                alert_type, message, metric_value, threshold, timestamp
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            alert_type,
            message,
            metric_value,
            threshold,
            datetime.now().isoformat(),
        ))
        
        conn.commit()
        conn.close()
    
    def _calculate_confidence(
        self,
        sample_size: int,
        average_accuracy: float
    ) -> float:
        """Calculate confidence level based on sample size and accuracy."""
        if sample_size < 10:
            return 0.3
        elif sample_size < 50:
            base_confidence = 0.5
        elif sample_size < 100:
            base_confidence = 0.7
        else:
            base_confidence = 0.85
        
        accuracy_factor = average_accuracy / 100.0
        
        return min(0.95, base_confidence * accuracy_factor)
    
    def get_phase_breakdown(self, days: int = 30) -> Dict[str, Dict[str, float]]:
        """Get estimation accuracy breakdown by phase."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT
                phase,
                COUNT(*) as total,
                AVG(error_percentage) as avg_error,
                AVG(accuracy_score) as avg_accuracy
            FROM estimation_tracking
            WHERE timestamp >= ?
            AND actual_time IS NOT NULL
            AND phase IS NOT NULL
            GROUP BY phase
        """, (cutoff_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return {
            row[0]: {
                "total": row[1],
                "average_error": row[2],
                "average_accuracy": row[3],
            }
            for row in rows
        }
