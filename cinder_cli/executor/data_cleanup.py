"""
Data cleanup and maintenance utilities.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from cinder_cli.config import Config
from cinder_cli.executor import ExecutionLogger


class DataCleanup:
    """Handles data cleanup and maintenance tasks."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = ExecutionLogger(config)
        self.retention_days = config.get("database", {}).get("data_retention_days", 30)

    def cleanup_old_executions(self, days: int | None = None) -> dict[str, Any]:
        """
        Remove execution records older than specified days.

        Args:
            days: Number of days to keep (default from config)

        Returns:
            Cleanup statistics
        """
        if days is None:
            days = self.retention_days

        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()

        executions = self.logger.list_executions(limit=10000)
        
        deleted_count = 0
        deleted_ids = []

        for execution in executions:
            if execution.get("timestamp", "") < cutoff_str:
                deleted_ids.append(execution["id"])
                deleted_count += 1

        return {
            "deleted_count": deleted_count,
            "deleted_ids": deleted_ids,
            "cutoff_date": cutoff_str,
            "retention_days": days,
        }

    def cleanup_progress_snapshots(self, keep_last: int = 100) -> dict[str, Any]:
        """
        Remove old progress snapshots, keeping only recent ones.

        Args:
            keep_last: Number of recent snapshots to keep

        Returns:
            Cleanup statistics
        """
        executions = self.logger.list_executions(limit=10000)
        
        cleaned_count = 0

        for execution in executions:
            if execution.get("progress_data"):
                progress_data = execution["progress_data"]
                
                if isinstance(progress_data, dict) and "snapshots" in progress_data:
                    snapshots = progress_data["snapshots"]
                    
                    if len(snapshots) > keep_last:
                        progress_data["snapshots"] = snapshots[-keep_last:]
                        cleaned_count += len(snapshots) - keep_last

        return {
            "cleaned_snapshots": cleaned_count,
            "kept_per_execution": keep_last,
        }

    def archive_old_statistics(self, days: int = 90) -> dict[str, Any]:
        """
        Archive old execution statistics.

        Args:
            days: Archive statistics older than this

        Returns:
            Archive statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()

        executions = self.logger.list_executions(limit=10000)
        
        archived_count = 0
        total_size = 0

        for execution in executions:
            if execution.get("timestamp", "") < cutoff_str:
                if execution.get("speed_metrics"):
                    total_size += len(str(execution["speed_metrics"]))
                if execution.get("estimation_data"):
                    total_size += len(str(execution["estimation_data"]))
                archived_count += 1

        return {
            "archived_count": archived_count,
            "cutoff_date": cutoff_str,
            "data_size_bytes": total_size,
        }

    def get_storage_stats(self) -> dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Storage statistics
        """
        db_path = Path.home() / ".cinder" / "executions.db"
        
        executions = self.logger.list_executions(limit=10000)
        
        total_progress_data = 0
        total_speed_metrics = 0
        total_estimation_data = 0

        for execution in executions:
            if execution.get("progress_data"):
                total_progress_data += len(str(execution["progress_data"]))
            if execution.get("speed_metrics"):
                total_speed_metrics += len(str(execution["speed_metrics"]))
            if execution.get("estimation_data"):
                total_estimation_data += len(str(execution["estimation_data"]))

        db_size = db_path.stat().st_size if db_path.exists() else 0

        return {
            "database_size_bytes": db_size,
            "database_size_mb": db_size / (1024 * 1024),
            "total_executions": len(executions),
            "progress_data_bytes": total_progress_data,
            "speed_metrics_bytes": total_speed_metrics,
            "estimation_data_bytes": total_estimation_data,
        }

    def run_maintenance(self) -> dict[str, Any]:
        """
        Run all maintenance tasks.

        Returns:
            Maintenance results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "tasks": {},
        }

        results["tasks"]["cleanup_executions"] = self.cleanup_old_executions()
        results["tasks"]["cleanup_snapshots"] = self.cleanup_progress_snapshots()
        results["tasks"]["archive_statistics"] = self.archive_old_statistics()
        results["tasks"]["storage_stats"] = self.get_storage_stats()

        return results
