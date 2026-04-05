"""
Data Analysis Module - Analyzes historical execution data.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from cinder_cli.config import Config
from cinder_cli.executor import ExecutionLogger


class DataAnalyzer:
    """Analyzes historical execution data."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = ExecutionLogger(config)

    def analyze_execution_times(self, days: int = 30) -> dict[str, Any]:
        """
        Analyze execution time distribution.

        Args:
            days: Number of days to analyze

        Returns:
            Time distribution analysis
        """
        cutoff = datetime.now() - timedelta(days=days)
        executions = self.logger.list_executions(limit=1000)
        
        times = []
        for ex in executions:
            if ex.get("timestamp"):
                ex_time = datetime.fromisoformat(ex["timestamp"])
                if ex_time > cutoff and ex.get("execution_time"):
                    times.append(ex["execution_time"])
        
        if not times:
            return {
                "total": 0,
                "avg": 0,
                "min": 0,
                "max": 0,
                "median": 0,
                "distribution": {},
            }
        
        times.sort()
        
        return {
            "total": len(times),
            "avg": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
            "median": times[len(times) // 2],
            "distribution": self._calculate_distribution(times),
        }

    def _calculate_distribution(self, times: list[float]) -> dict[str, int]:
        """Calculate time distribution."""
        distribution = {
            "0-30s": 0,
            "30-60s": 0,
            "1-5min": 0,
            "5-15min": 0,
            "15-30min": 0,
            "30min+": 0,
        }
        
        for t in times:
            if t < 30:
                distribution["0-30s"] += 1
            elif t < 60:
                distribution["30-60s"] += 1
            elif t < 300:
                distribution["1-5min"] += 1
            elif t < 900:
                distribution["5-15min"] += 1
            elif t < 1800:
                distribution["15-30min"] += 1
            else:
                distribution["30min+"] += 1
        
        return distribution

    def analyze_phase_performance(self, days: int = 30) -> dict[str, Any]:
        """
        Analyze phase-level performance.

        Args:
            days: Number of days to analyze

        Returns:
            Phase performance analysis
        """
        cutoff = datetime.now() - timedelta(days=days)
        executions = self.logger.list_executions(limit=1000)
        
        phase_data = {}
        
        for ex in executions:
            if not ex.get("timestamp"):
                continue
            
            ex_time = datetime.fromisoformat(ex["timestamp"])
            if ex_time <= cutoff:
                continue
            
            if ex.get("phase_timestamps"):
                for phase, data in ex["phase_timestamps"].items():
                    if phase not in phase_data:
                        phase_data[phase] = []
                    
                    if data.get("duration"):
                        phase_data[phase].append(data["duration"])
        
        analysis = {}
        for phase, durations in phase_data.items():
            if durations:
                durations.sort()
                analysis[phase] = {
                    "count": len(durations),
                    "avg": sum(durations) / len(durations),
                    "min": min(durations),
                    "max": max(durations),
                    "median": durations[len(durations) // 2],
                }
        
        return analysis

    def analyze_speed_trends(self, days: int = 30) -> dict[str, Any]:
        """
        Analyze speed trends over time.

        Args:
            days: Number of days to analyze

        Returns:
            Speed trend analysis
        """
        cutoff = datetime.now() - timedelta(days=days)
        executions = self.logger.list_executions(limit=1000)
        
        daily_speeds = {}
        
        for ex in executions:
            if not ex.get("timestamp"):
                continue
            
            ex_time = datetime.fromisoformat(ex["timestamp"])
            if ex_time <= cutoff:
                continue
            
            date_key = ex_time.strftime("%Y-%m-%d")
            
            if ex.get("speed_metrics") and ex["speed_metrics"].get("tasks_per_minute"):
                if date_key not in daily_speeds:
                    daily_speeds[date_key] = []
                daily_speeds[date_key].append(ex["speed_metrics"]["tasks_per_minute"])
        
        trends = []
        for date in sorted(daily_speeds.keys()):
            speeds = daily_speeds[date]
            trends.append({
                "date": date,
                "avg_speed": sum(speeds) / len(speeds),
                "max_speed": max(speeds),
                "count": len(speeds),
            })
        
        return {
            "trends": trends,
            "total_days": len(trends),
        }

    def analyze_success_rate(self, days: int = 30) -> dict[str, Any]:
        """
        Analyze execution success rate.

        Args:
            days: Number of days to analyze

        Returns:
            Success rate analysis
        """
        cutoff = datetime.now() - timedelta(days=days)
        executions = self.logger.list_executions(limit=1000)
        
        total = 0
        success = 0
        daily_stats = {}
        
        for ex in executions:
            if not ex.get("timestamp"):
                continue
            
            ex_time = datetime.fromisoformat(ex["timestamp"])
            if ex_time <= cutoff:
                continue
            
            total += 1
            if ex.get("status") == "success":
                success += 1
            
            date_key = ex_time.strftime("%Y-%m-%d")
            if date_key not in daily_stats:
                daily_stats[date_key] = {"total": 0, "success": 0}
            
            daily_stats[date_key]["total"] += 1
            if ex.get("status") == "success":
                daily_stats[date_key]["success"] += 1
        
        daily_rates = []
        for date in sorted(daily_stats.keys()):
            stats = daily_stats[date]
            rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            daily_rates.append({
                "date": date,
                "success_rate": rate,
                "total": stats["total"],
                "success": stats["success"],
            })
        
        return {
            "overall_rate": success / total if total > 0 else 0,
            "total_executions": total,
            "successful_executions": success,
            "daily_rates": daily_rates,
        }

    def generate_report(self, days: int = 30) -> dict[str, Any]:
        """
        Generate comprehensive analysis report.

        Args:
            days: Number of days to analyze

        Returns:
            Comprehensive analysis report
        """
        return {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "execution_times": self.analyze_execution_times(days),
            "phase_performance": self.analyze_phase_performance(days),
            "speed_trends": self.analyze_speed_trends(days),
            "success_rate": self.analyze_success_rate(days),
        }
