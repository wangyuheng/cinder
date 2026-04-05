"""
Data Export Utilities - Export execution data in various formats.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from cinder_cli.config import Config
from cinder_cli.executor import ExecutionLogger


class DataExporter:
    """Exports execution data in various formats."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = ExecutionLogger(config)

    def export_to_json(
        self,
        output_path: str | Path,
        limit: int = 1000,
        include_progress: bool = True,
    ) -> dict[str, Any]:
        """
        Export executions to JSON file.

        Args:
            output_path: Output file path
            limit: Maximum number of executions to export
            include_progress: Include progress data

        Returns:
            Export statistics
        """
        executions = self.logger.list_executions(limit=limit)
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_executions": len(executions),
            "executions": [],
        }
        
        for ex in executions:
            ex_data = {
                "id": ex["id"],
                "timestamp": ex["timestamp"],
                "goal": ex["goal"],
                "status": ex["status"],
                "execution_time": ex.get("execution_time"),
                "created_files": ex.get("created_files", []),
            }
            
            if include_progress:
                ex_data["phase_timestamps"] = ex.get("phase_timestamps")
                ex_data["progress_data"] = ex.get("progress_data")
                ex_data["speed_metrics"] = ex.get("speed_metrics")
            
            export_data["executions"].append(ex_data)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return {
            "format": "json",
            "output_path": str(output_path),
            "total_exported": len(executions),
            "file_size": output_path.stat().st_size,
        }

    def export_to_csv(
        self,
        output_path: str | Path,
        limit: int = 1000,
    ) -> dict[str, Any]:
        """
        Export executions to CSV file.

        Args:
            output_path: Output file path
            limit: Maximum number of executions to export

        Returns:
            Export statistics
        """
        executions = self.logger.list_executions(limit=limit)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        fieldnames = [
            "id",
            "timestamp",
            "goal",
            "status",
            "execution_time",
            "files_created",
            "tasks_count",
            "avg_speed",
        ]
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for ex in executions:
                tasks_count = 0
                if ex.get("task_tree") and ex["task_tree"].get("subtasks"):
                    tasks_count = len(ex["task_tree"]["subtasks"])
                
                avg_speed = 0
                if ex.get("speed_metrics") and ex["speed_metrics"].get("tasks_per_minute"):
                    avg_speed = ex["speed_metrics"]["tasks_per_minute"]
                
                writer.writerow({
                    "id": ex["id"],
                    "timestamp": ex["timestamp"],
                    "goal": ex["goal"],
                    "status": ex["status"],
                    "execution_time": ex.get("execution_time", 0),
                    "files_created": len(ex.get("created_files", [])),
                    "tasks_count": tasks_count,
                    "avg_speed": f"{avg_speed:.2f}",
                })
        
        return {
            "format": "csv",
            "output_path": str(output_path),
            "total_exported": len(executions),
            "file_size": output_path.stat().st_size,
        }

    def export_statistics(
        self,
        output_path: str | Path,
    ) -> dict[str, Any]:
        """
        Export execution statistics.

        Args:
            output_path: Output file path

        Returns:
            Export statistics
        """
        from cinder_cli.executor.data_analyzer import DataAnalyzer
        
        analyzer = DataAnalyzer(self.config)
        report = analyzer.generate_report(days=30)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return {
            "format": "json",
            "output_path": str(output_path),
            "file_size": output_path.stat().st_size,
        }

    def export_all(self, output_dir: str | Path) -> dict[str, Any]:
        """
        Export all data to multiple formats.

        Args:
            output_dir: Output directory

        Returns:
            Export statistics
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {
            "exported_at": datetime.now().isoformat(),
            "output_dir": str(output_dir),
            "files": {},
        }
        
        results["files"]["executions_json"] = self.export_to_json(
            output_dir / f"executions_{timestamp}.json"
        )
        
        results["files"]["executions_csv"] = self.export_to_csv(
            output_dir / f"executions_{timestamp}.csv"
        )
        
        results["files"]["statistics"] = self.export_statistics(
            output_dir / f"statistics_{timestamp}.json"
        )
        
        return results
