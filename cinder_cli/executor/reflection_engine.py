"""
Reflection Engine - Evaluates execution results based on soul profile.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from cinder_cli.config import Config


class ReflectionEngine:
    """Evaluates execution results based on soul profile."""

    def __init__(self, config: Config):
        self.config = config
        self.soul_meta = self._load_soul_meta()
        self.reflection_history: list[dict[str, Any]] = []
        self.history_file = Path.home() / ".cinder" / "reflection_history.json"
        self._load_history()

    def evaluate_execution(
        self,
        code: str,
        task: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate execution result.

        Args:
            code: Generated code
            task: Task information

        Returns:
            Evaluation result with approval and suggestions
        """
        evaluation = {
            "approved": True,
            "quality_score": 0.8,
            "suggestions": [],
            "risks": [],
        }

        # Check risk consistency
        risk_evaluation = self._check_risk_consistency(code, task)
        evaluation["risks"].extend(risk_evaluation.get("risks", []))

        # Check style consistency
        style_evaluation = self._check_style_consistency(code)
        evaluation["suggestions"].extend(style_evaluation.get("suggestions", []))

        # Check code quality
        quality_evaluation = self._check_code_quality(code)
        evaluation["quality_score"] = quality_evaluation.get("score", 0.8)

        # Make approval decision
        if evaluation["quality_score"] < 0.5:
            evaluation["approved"] = False
            evaluation["suggestions"].append("代码质量过低，需要重新生成")

        return evaluation

    def _check_risk_consistency(
        self,
        code: str,
        task: dict[str, Any],
    ) -> dict[str, Any]:
        """Check if code matches user's risk tolerance."""
        risks = []

        if not self.soul_meta:
            return {"risks": risks}

        traits = self.soul_meta.get("traits", {})
        risk_tolerance = traits.get("risk_tolerance", 50)

        # Check for risky patterns
        risky_patterns = [
            ("eval(", "使用 eval() 可能存在安全风险"),
            ("exec(", "使用 exec() 可能存在安全风险"),
            ("__import__", "动态导入可能存在安全风险"),
            ("subprocess.call", "子进程调用需要谨慎"),
        ]

        for pattern, message in risky_patterns:
            if pattern in code:
                risks.append(message)
                if risk_tolerance < 38:  # Conservative
                    risks.append(f"保守型用户应避免: {pattern}")

        return {"risks": risks}

    def _check_style_consistency(self, code: str) -> dict[str, Any]:
        """Check if code style matches user preferences."""
        suggestions = []

        if not self.soul_meta:
            return {"suggestions": suggestions}

        traits = self.soul_meta.get("traits", {})
        structure = traits.get("structure", 50)

        # Check documentation
        if structure >= 65:  # High structure need
            if '"""' not in code and "'''" not in code:
                suggestions.append("建议添加详细的文档字符串")

        # Check comments
        comment_lines = [line for line in code.split("\n") if line.strip().startswith("#")]
        code_lines = [line for line in code.split("\n") if line.strip() and not line.strip().startswith("#")]

        if len(code_lines) > 10 and len(comment_lines) < 2:
            suggestions.append("建议添加更多注释以提高可读性")

        return {"suggestions": suggestions}

    def _check_code_quality(self, code: str) -> dict[str, Any]:
        """Check code quality."""
        score = 0.8

        # Basic quality checks
        lines = code.split("\n")

        # Penalize very short code
        if len(lines) < 5:
            score -= 0.2

        # Reward documentation
        if '"""' in code or "'''" in code:
            score += 0.1

        # Reward comments
        if any(line.strip().startswith("#") for line in lines):
            score += 0.05

        # Penalize syntax errors (basic check)
        try:
            compile(code, "<string>", "exec")
        except SyntaxError:
            score -= 0.3

        return {"score": min(1.0, max(0.0, score))}

    def _load_soul_meta(self) -> dict[str, Any]:
        """Load soul metadata."""
        import yaml

        soul_path = self.config.get("soul_path", "soul.md")
        meta_path = self.config.get("meta_path", "")

        if not meta_path:
            meta_path = soul_path.replace(".md", ".meta.yaml")

        try:
            with open(meta_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def iterative_refinement(
        self,
        code: str,
        task: dict[str, Any],
        generate_func: callable,
        max_iterations: int = 3,
        quality_threshold: float = 0.7,
    ) -> dict[str, Any]:
        """
        Iteratively refine code until quality threshold is met.

        Args:
            code: Initial code
            task: Task information
            generate_func: Function to regenerate code
            max_iterations: Maximum refinement iterations
            quality_threshold: Target quality score

        Returns:
            Final code and refinement history
        """
        current_code = code
        history = []
        best_code = code
        best_score = 0

        for iteration in range(max_iterations):
            evaluation = self.evaluate_execution(current_code, task)

            history.append({
                "iteration": iteration + 1,
                "quality_score": evaluation["quality_score"],
                "approved": evaluation["approved"],
                "suggestions": evaluation["suggestions"],
                "risks": evaluation["risks"],
            })

            if evaluation["quality_score"] > best_score:
                best_score = evaluation["quality_score"]
                best_code = current_code

            if evaluation["quality_score"] >= quality_threshold:
                return {
                    "code": current_code,
                    "final_score": evaluation["quality_score"],
                    "iterations": iteration + 1,
                    "approved": True,
                    "history": history,
                }

            if iteration < max_iterations - 1:
                improvement_prompt = self._build_improvement_prompt(
                    current_code,
                    evaluation,
                    task,
                )
                current_code = generate_func(
                    description=improvement_prompt,
                    language=task.get("language", "python"),
                )

        return {
            "code": best_code,
            "final_score": best_score,
            "iterations": max_iterations,
            "approved": best_score >= quality_threshold,
            "history": history,
        }

    def _build_improvement_prompt(
        self,
        code: str,
        evaluation: dict[str, Any],
        task: dict[str, Any],
    ) -> str:
        """Build prompt for code improvement."""
        suggestions = evaluation.get("suggestions", [])
        risks = evaluation.get("risks", [])

        prompt_parts = [
            f"改进以下代码，任务: {task.get('description', '未知任务')}",
            "",
            "当前代码:",
            "```",
            code,
            "```",
            "",
        ]

        if suggestions:
            prompt_parts.append("改进建议:")
            for s in suggestions:
                prompt_parts.append(f"- {s}")
            prompt_parts.append("")

        if risks:
            prompt_parts.append("风险问题:")
            for r in risks:
                prompt_parts.append(f"- {r}")
            prompt_parts.append("")

        prompt_parts.append("请生成改进后的代码。")

        return "\n".join(prompt_parts)

    def track_reflection_history(
        self,
        execution_id: str,
        evaluation: dict[str, Any],
        task: dict[str, Any],
    ) -> None:
        """
        Track reflection history for analysis.

        Args:
            execution_id: Execution identifier
            evaluation: Evaluation result
            task: Task information
        """
        entry = {
            "execution_id": execution_id,
            "timestamp": datetime.now().isoformat(),
            "task_description": task.get("description", ""),
            "quality_score": evaluation.get("quality_score", 0),
            "approved": evaluation.get("approved", False),
            "suggestions_count": len(evaluation.get("suggestions", [])),
            "risks_count": len(evaluation.get("risks", [])),
        }

        self.reflection_history.append(entry)
        self._save_history()

    def get_reflection_stats(self) -> dict[str, Any]:
        """
        Get statistics from reflection history.

        Returns:
            Statistics about reflections
        """
        if not self.reflection_history:
            return {
                "total_reflections": 0,
                "approval_rate": 0,
                "average_quality": 0,
            }

        total = len(self.reflection_history)
        approved = sum(1 for r in self.reflection_history if r["approved"])
        total_quality = sum(r["quality_score"] for r in self.reflection_history)

        return {
            "total_reflections": total,
            "approval_rate": approved / total if total > 0 else 0,
            "average_quality": total_quality / total if total > 0 else 0,
            "recent_reflections": self.reflection_history[-10:],
        }

    def _load_history(self) -> None:
        """Load reflection history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, encoding="utf-8") as f:
                    self.reflection_history = json.load(f)
        except (json.JSONDecodeError, IOError):
            self.reflection_history = []

    def _save_history(self) -> None:
        """Save reflection history to file."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.reflection_history[-100:], f, ensure_ascii=False, indent=2)
