"""
Trace Manager - Manages trace data lifecycle.
"""

from __future__ import annotations

import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class TraceManager:
    """Manages trace data lifecycle including cleanup and backup."""
    
    def __init__(
        self,
        trace_dir: Optional[Path] = None,
        retention_days: int = 30,
    ):
        """
        Initialize Trace Manager.
        
        Args:
            trace_dir: Directory where trace data is stored
            retention_days: Number of days to retain trace data
        """
        self.trace_dir = trace_dir or Path.home() / ".cinder" / "traces"
        self.backup_dir = self.trace_dir / "backups"
        self.retention_days = retention_days
        
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def cleanup_old_traces(self, dry_run: bool = False) -> int:
        """
        Clean up traces older than retention period.
        
        Args:
            dry_run: If True, only report what would be deleted
            
        Returns:
            Number of trace files deleted
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        
        for trace_file in self.trace_dir.glob("*.json"):
            if trace_file.is_file():
                file_mtime = datetime.fromtimestamp(trace_file.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    if dry_run:
                        logger.info(f"Would delete: {trace_file}")
                    else:
                        trace_file.unlink()
                        logger.info(f"Deleted: {trace_file}")
                    
                    deleted_count += 1
        
        return deleted_count
    
    def backup_traces(self, backup_name: Optional[str] = None) -> Path:
        """
        Create a backup of all trace data.
        
        Args:
            backup_name: Custom backup name (optional)
            
        Returns:
            Path to backup file
        """
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"trace_backup_{timestamp}"
        
        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
        
        import tarfile
        
        with tarfile.open(backup_file, "w:gz") as tar:
            for trace_file in self.trace_dir.glob("*.json"):
                if trace_file.is_file():
                    tar.add(trace_file, arcname=trace_file.name)
        
        logger.info(f"Created backup: {backup_file}")
        return backup_file
    
    def restore_backup(self, backup_file: Path) -> None:
        """
        Restore traces from a backup file.
        
        Args:
            backup_file: Path to backup file
        """
        import tarfile
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(path=self.trace_dir)
        
        logger.info(f"Restored backup from: {backup_file}")
    
    def get_trace_stats(self) -> dict:
        """
        Get statistics about trace data.
        
        Returns:
            Dictionary with trace statistics
        """
        trace_files = list(self.trace_dir.glob("*.json"))
        backup_files = list(self.backup_dir.glob("*.tar.gz"))
        
        total_size = sum(f.stat().st_size for f in trace_files if f.is_file())
        backup_size = sum(f.stat().st_size for f in backup_files if f.is_file())
        
        return {
            "trace_count": len(trace_files),
            "total_size_mb": total_size / (1024 * 1024),
            "backup_count": len(backup_files),
            "backup_size_mb": backup_size / (1024 * 1024),
            "retention_days": self.retention_days,
        }
    
    def list_backups(self) -> list[Path]:
        """
        List all available backups.
        
        Returns:
            List of backup file paths
        """
        return sorted(self.backup_dir.glob("*.tar.gz"))
    
    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """
        Clean up old backups, keeping only the most recent ones.
        
        Args:
            keep_count: Number of backups to keep
            
        Returns:
            Number of backups deleted
        """
        backups = self.list_backups()
        deleted_count = 0
        
        if len(backups) > keep_count:
            for backup in backups[:-keep_count]:
                backup.unlink()
                logger.info(f"Deleted old backup: {backup}")
                deleted_count += 1
        
        return deleted_count
