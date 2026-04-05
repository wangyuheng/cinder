"""
Execution Logger - Logs execution events and history.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from cinder_cli.config import Config


class ExecutionLogger:
    """Logs execution events and manages history."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        goal TEXT NOT NULL,
        task_tree TEXT,
        results TEXT,
        status TEXT NOT NULL,
        created_files TEXT,
        execution_time REAL,
        phase_timestamps TEXT,
        progress_data TEXT,
        speed_metrics TEXT,
        estimation_data TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_timestamp ON executions(timestamp);
    CREATE INDEX IF NOT EXISTS idx_status ON executions(status);
    """

    def __init__(self, config: Config):
        self.config = config
        self.db_path = self._get_db_path()
        self._init_db()

    def log_execution(
        self,
        goal: str,
        task_tree: dict[str, Any],
        results: list[dict[str, Any]],
        phase_timestamps: dict[str, Any] | None = None,
        progress_data: dict[str, Any] | None = None,
        speed_metrics: dict[str, Any] | None = None,
        estimation_data: dict[str, Any] | None = None,
    ) -> int:
        """
        Log an execution.

        Args:
            goal: Execution goal
            task_tree: Task tree
            results: Execution results
            phase_timestamps: Phase-level timestamps
            progress_data: Progress tracking data
            speed_metrics: Speed metrics
            estimation_data: Estimation data

        Returns:
            Execution ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO executions
                (timestamp, goal, task_tree, results, status, created_files,
                 phase_timestamps, progress_data, speed_metrics, estimation_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(),
                    goal,
                    json.dumps(task_tree, ensure_ascii=False),
                    json.dumps(results, ensure_ascii=False),
                    "success",
                    json.dumps(
                        [r["file_result"]["file_path"] for r in results if "file_result" in r],
                        ensure_ascii=False,
                    ),
                    json.dumps(phase_timestamps, ensure_ascii=False) if phase_timestamps else None,
                    json.dumps(progress_data, ensure_ascii=False) if progress_data else None,
                    json.dumps(speed_metrics, ensure_ascii=False) if speed_metrics else None,
                    json.dumps(estimation_data, ensure_ascii=False) if estimation_data else None,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def list_executions(
        self,
        limit: int = 10,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        List executions.

        Args:
            limit: Maximum number of executions to return
            status: Filter by status

        Returns:
            List of executions
        """
        query = "SELECT * FROM executions"
        params = []

        if status:
            query += " WHERE status = ?"
            params.append(status)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_execution(self, execution_id: int) -> dict[str, Any] | None:
        """
        Get a specific execution.

        Args:
            execution_id: Execution ID

        Returns:
            Execution details or None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM executions WHERE id = ?",
                (execution_id,),
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
        return None

    def _get_db_path(self) -> Path:
        """Get database path."""
        db_dir = Path.home() / ".cinder"
        db_dir.mkdir(parents=True, exist_ok=True)
        return db_dir / "executions.db"

    def _init_db(self) -> None:
        """Initialize database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(self.SCHEMA)
            conn.commit()

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert database row to dictionary."""
        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "goal": row["goal"],
            "task_tree": json.loads(row["task_tree"]) if row["task_tree"] else None,
            "results": json.loads(row["results"]) if row["results"] else None,
            "status": row["status"],
            "created_files": json.loads(row["created_files"]) if row["created_files"] else [],
            "execution_time": row["execution_time"],
            "phase_timestamps": json.loads(row["phase_timestamps"]) if row["phase_timestamps"] else None,
            "progress_data": json.loads(row["progress_data"]) if row["progress_data"] else None,
            "speed_metrics": json.loads(row["speed_metrics"]) if row["speed_metrics"] else None,
            "estimation_data": json.loads(row["estimation_data"]) if row["estimation_data"] else None,
        }

    def generate_report(
        self,
        execution_id: int | None = None,
        format: str = "text",
    ) -> str:
        """
        Generate execution report.

        Args:
            execution_id: Specific execution ID, or None for summary
            format: Output format (text, markdown, json)

        Returns:
            Report content
        """
        if execution_id:
            execution = self.get_execution(execution_id)
            if not execution:
                return f"执行记录 #{execution_id} 不存在"
            return self._format_single_report(execution, format)
        else:
            executions = self.list_executions(limit=20)
            stats = self._calculate_stats(executions)
            return self._format_summary_report(executions, stats, format)

    def _format_single_report(
        self,
        execution: dict[str, Any],
        format: str,
    ) -> str:
        """Format a single execution report."""
        if format == "json":
            return json.dumps(execution, ensure_ascii=False, indent=2)

        lines = []
        lines.append(f"# 执行报告 #{execution['id']}")
        lines.append("")
        lines.append(f"**时间**: {execution['timestamp']}")
        lines.append(f"**目标**: {execution['goal']}")
        lines.append(f"**状态**: {execution['status']}")
        lines.append("")

        if execution.get("created_files"):
            lines.append("## 创建的文件")
            for f in execution["created_files"]:
                lines.append(f"- {f}")
            lines.append("")

        if execution.get("task_tree"):
            lines.append("## 任务树")
            subtasks = execution["task_tree"].get("subtasks", [])
            for task in subtasks:
                lines.append(f"- [{task.get('id')}] {task.get('description')}")
            lines.append("")

        return "\n".join(lines)

    def _format_summary_report(
        self,
        executions: list[dict[str, Any]],
        stats: dict[str, Any],
        format: str,
    ) -> str:
        """Format a summary report."""
        if format == "json":
            return json.dumps({"stats": stats, "executions": executions}, ensure_ascii=False, indent=2)

        lines = []
        lines.append("# 执行统计报告")
        lines.append("")
        lines.append("## 统计概览")
        lines.append(f"- 总执行次数: {stats['total']}")
        lines.append(f"- 成功次数: {stats['success_count']}")
        lines.append(f"- 成功率: {stats['success_rate']:.1%}")
        lines.append(f"- 创建文件总数: {stats['total_files']}")
        lines.append("")

        lines.append("## 最近执行")
        for ex in executions[:10]:
            status_icon = "✓" if ex["status"] == "success" else "✗"
            lines.append(f"- {status_icon} [{ex['id']}] {ex['goal'][:50]}... ({ex['timestamp'][:10]})")

        return "\n".join(lines)

    def _calculate_stats(
        self,
        executions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Calculate statistics from executions."""
        if not executions:
            return {
                "total": 0,
                "success_count": 0,
                "success_rate": 0,
                "total_files": 0,
            }

        success_count = sum(1 for e in executions if e["status"] == "success")
        total_files = sum(len(e.get("created_files", [])) for e in executions)

        return {
            "total": len(executions),
            "success_count": success_count,
            "success_rate": success_count / len(executions),
            "total_files": total_files,
        }

    def replay_execution(
        self,
        execution_id: int,
    ) -> dict[str, Any]:
        """
        Replay an execution to show what happened.

        Args:
            execution_id: Execution ID to replay

        Returns:
            Replay information
        """
        execution = self.get_execution(execution_id)
        if not execution:
            return {"error": f"执行记录 #{execution_id} 不存在"}

        replay_steps = []

        if execution.get("task_tree"):
            subtasks = execution["task_tree"].get("subtasks", [])
            for i, task in enumerate(subtasks, 1):
                replay_steps.append({
                    "step": i,
                    "action": "task_start",
                    "description": task.get("description"),
                    "type": task.get("type"),
                })

        if execution.get("results"):
            for i, result in enumerate(execution["results"], 1):
                if "file_result" in result:
                    replay_steps.append({
                        "step": len(subtasks) + i if execution.get("task_tree") else i,
                        "action": "file_created",
                        "path": result["file_result"].get("file_path"),
                    })

        return {
            "execution_id": execution_id,
            "goal": execution["goal"],
            "timestamp": execution["timestamp"],
            "status": execution["status"],
            "steps": replay_steps,
        }

    def analyze_patterns(
        self,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Analyze execution patterns.

        Args:
            days: Number of days to analyze

        Returns:
            Pattern analysis results
        """
        executions = self.list_executions(limit=100)

        if not executions:
            return {"patterns": [], "insights": []}

        goal_keywords = {}
        file_types = {}
        hourly_distribution = {}

        for ex in executions:
            goal = ex.get("goal", "").lower()
            words = goal.split()
            for word in words:
                if len(word) > 3:
                    goal_keywords[word] = goal_keywords.get(word, 0) + 1

            for f in ex.get("created_files", []):
                ext = Path(f).suffix
                file_types[ext] = file_types.get(ext, 0) + 1

            timestamp = ex.get("timestamp", "")
            if timestamp:
                try:
                    hour = datetime.fromisoformat(timestamp).hour
                    hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
                except ValueError:
                    pass

        top_keywords = sorted(goal_keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        top_file_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]

        insights = []
        if top_keywords:
            insights.append(f"最常见目标关键词: {', '.join(k for k, _ in top_keywords[:5])}")
        if top_file_types:
            insights.append(f"最常创建文件类型: {', '.join(f'{k}({v})' for k, v in top_file_types)}")

        return {
            "top_keywords": top_keywords,
            "file_types": top_file_types,
            "hourly_distribution": hourly_distribution,
            "insights": insights,
        }

    def update_progress(
        self,
        execution_id: int,
        progress_data: dict[str, Any],
    ) -> None:
        """
        Update progress data for an execution.

        Args:
            execution_id: Execution ID
            progress_data: Progress data to update
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE executions
                SET progress_data = ?
                WHERE id = ?
                """,
                (json.dumps(progress_data, ensure_ascii=False), execution_id),
            )
            conn.commit()

    def update_speed_metrics(
        self,
        execution_id: int,
        speed_metrics: dict[str, Any],
    ) -> None:
        """
        Update speed metrics for an execution.

        Args:
            execution_id: Execution ID
            speed_metrics: Speed metrics to update
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE executions
                SET speed_metrics = ?
                WHERE id = ?
                """,
                (json.dumps(speed_metrics, ensure_ascii=False), execution_id),
            )
            conn.commit()

    def get_execution_statistics(
        self,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Get execution statistics for estimation.

        Args:
            limit: Maximum number of executions to analyze

        Returns:
            Execution statistics
        """
        executions = self.list_executions(limit=limit)
        
        if not executions:
            return {
                "total": 0,
                "avg_execution_time": 0,
                "avg_tasks_count": 0,
                "phase_statistics": {},
            }
        
        total_time = 0
        total_tasks = 0
        phase_times = {}
        
        for ex in executions:
            if ex.get("execution_time"):
                total_time += ex["execution_time"]
            
            if ex.get("task_tree"):
                tasks = ex["task_tree"].get("subtasks", [])
                total_tasks += len(tasks)
            
            if ex.get("phase_timestamps"):
                for phase, data in ex["phase_timestamps"].items():
                    if phase not in phase_times:
                        phase_times[phase] = []
                    if data.get("duration"):
                        phase_times[phase].append(data["duration"])
        
        phase_statistics = {}
        for phase, times in phase_times.items():
            if times:
                phase_statistics[phase] = {
                    "avg_duration": sum(times) / len(times),
                    "min_duration": min(times),
                    "max_duration": max(times),
                    "count": len(times),
                }
        
        return {
            "total": len(executions),
            "avg_execution_time": total_time / len(executions) if executions else 0,
            "avg_tasks_count": total_tasks / len(executions) if executions else 0,
            "phase_statistics": phase_statistics,
        }
