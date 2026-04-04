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

    def evaluate_comprehensive(
        self,
        code: str,
        task: dict[str, Any],
        soul_meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive evaluation including code quality, Soul consistency, and risk assessment.

        Args:
            code: Generated code
            task: Task information
            soul_meta: Optional Soul metadata (uses loaded soul if not provided)

        Returns:
            Comprehensive evaluation result
        """
        if soul_meta is None:
            soul_meta = self.soul_meta

        code_quality = self._evaluate_code_quality_detailed(code, task)
        soul_alignment = self._evaluate_soul_alignment(code, task, soul_meta)
        risk_assessment = self._assess_risks(code, task, soul_meta)

        final_score = self._calculate_final_score(code_quality, soul_alignment, risk_assessment)

        return {
            "quality_score": final_score,
            "approved": final_score >= 0.7,
            "code_quality": code_quality,
            "soul_alignment": soul_alignment,
            "risk_assessment": risk_assessment,
            "suggestions": self._generate_suggestions(code_quality, soul_alignment, risk_assessment),
            "risks": risk_assessment.get("risks", []),
        }

    def _evaluate_code_quality_detailed(
        self,
        code: str,
        task: dict[str, Any],
    ) -> dict[str, Any]:
        """Detailed code quality evaluation."""
        scores = {}

        syntax_score = self._check_syntax_quality(code)
        scores["syntax"] = syntax_score

        logic_score = self._check_logic_quality(code, task)
        scores["logic"] = logic_score

        style_score = self._check_style_quality(code)
        scores["style"] = style_score

        doc_score = self._check_documentation_quality(code)
        scores["documentation"] = doc_score

        weights = {
            "syntax": 0.3,
            "logic": 0.35,
            "style": 0.2,
            "documentation": 0.15,
        }

        overall_score = sum(scores[key] * weights[key] for key in scores)

        return {
            "overall_score": round(overall_score, 2),
            "scores": scores,
            "issues": self._identify_quality_issues(scores),
        }

    def _check_syntax_quality(self, code: str) -> float:
        """Check syntax quality."""
        try:
            compile(code, "<string>", "exec")
            return 1.0
        except SyntaxError as e:
            lines = code.split("\n")
            total_lines = len(lines)
            error_line = e.lineno or 0

            if total_lines == 0:
                return 0.0

            error_ratio = 1 - (error_line / total_lines) if error_line > 0 else 0.5
            return max(0.0, min(0.5, error_ratio))

    def _check_logic_quality(self, code: str, task: dict[str, Any]) -> float:
        """Check logic quality."""
        score = 0.5

        description = task.get("description", "").lower()
        code_lower = code.lower()

        logic_indicators = {
            "function": ["def ", "function ", "return "],
            "class": ["class ", "self.", "this."],
            "control_flow": ["if ", "for ", "while ", "try:"],
            "error_handling": ["try:", "except ", "raise "],
        }

        for category, indicators in logic_indicators.items():
            if any(ind in code_lower for ind in indicators):
                score += 0.1

        task_keywords = {
            "web": ["app", "route", "get", "post", "fastapi", "flask"],
            "api": ["api", "endpoint", "request", "response"],
            "database": ["database", "db", "query", "model"],
            "auth": ["auth", "login", "password", "token"],
        }

        for category, keywords in task_keywords.items():
            if category in description:
                if any(kw in code_lower for kw in keywords):
                    score += 0.05

        return min(score, 1.0)

    def _check_style_quality(self, code: str) -> float:
        """Check style quality."""
        score = 0.5

        lines = code.split("\n")
        if not lines:
            return 0.0

        avg_line_length = sum(len(line) for line in lines) / len(lines)
        if avg_line_length < 100:
            score += 0.2

        if "    " in code:
            score += 0.1

        consistent_indent = True
        indent_sizes = set()
        for line in lines:
            if line.strip() and line[0] == " ":
                indent = len(line) - len(line.lstrip())
                indent_sizes.add(indent)

        if len(indent_sizes) <= 2:
            score += 0.1

        return min(score, 1.0)

    def _check_documentation_quality(self, code: str) -> float:
        """Check documentation quality."""
        score = 0.0

        if '"""' in code or "'''" in code:
            score += 0.4

        comment_lines = [line for line in code.split("\n") if line.strip().startswith("#")]
        if comment_lines:
            score += 0.2

        try:
            import ast
            tree = ast.parse(code)
            docstring_count = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    if ast.get_docstring(node):
                        docstring_count += 1

            if docstring_count > 0:
                score += min(0.4, docstring_count * 0.1)
        except:
            pass

        return min(score, 1.0)

    def _identify_quality_issues(self, scores: dict[str, float]) -> list[str]:
        """Identify quality issues from scores."""
        issues = []

        if scores.get("syntax", 1.0) < 1.0:
            issues.append("Syntax errors detected")
        if scores.get("logic", 0) < 0.7:
            issues.append("Logic may not fully address the task")
        if scores.get("style", 0) < 0.7:
            issues.append("Code style needs improvement")
        if scores.get("documentation", 0) < 0.5:
            issues.append("Insufficient documentation")

        return issues

    def _evaluate_soul_alignment(
        self,
        code: str,
        task: dict[str, Any],
        soul_meta: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Evaluate Soul consistency."""
        if not soul_meta:
            return {
                "alignment_score": 1.0,
                "traits_matched": [],
                "suggestions": [],
            }

        traits = soul_meta.get("traits", {})
        scores = {}

        risk_tolerance = traits.get("risk_tolerance", 50)
        risk_score = self._check_risk_tolerance_alignment(code, risk_tolerance)
        scores["risk_tolerance"] = risk_score

        structure = traits.get("structure", 50)
        structure_score = self._check_structure_alignment(code, structure)
        scores["structure"] = structure_score

        detail_orientation = traits.get("detail_orientation", 50)
        detail_score = self._check_detail_alignment(code, detail_orientation)
        scores["detail_orientation"] = detail_score

        alignment_score = sum(scores.values()) / len(scores) if scores else 1.0

        return {
            "alignment_score": round(alignment_score, 2),
            "trait_scores": scores,
            "traits_matched": list(scores.keys()),
            "suggestions": self._generate_soul_suggestions(scores, traits),
        }

    def _check_risk_tolerance_alignment(self, code: str, risk_tolerance: int) -> float:
        """Check if code aligns with risk tolerance."""
        risky_patterns = ["eval(", "exec(", "__import__", "subprocess.call", "os.system"]

        risk_count = sum(1 for pattern in risky_patterns if pattern in code)

        if risk_tolerance < 38:
            if risk_count == 0:
                return 1.0
            else:
                return max(0.0, 1.0 - risk_count * 0.3)
        elif risk_tolerance > 62:
            return 1.0
        else:
            if risk_count <= 1:
                return 1.0
            else:
                return max(0.5, 1.0 - (risk_count - 1) * 0.2)

    def _check_structure_alignment(self, code: str, structure: int) -> float:
        """Check if code aligns with structure preference."""
        score = 1.0

        if structure >= 65:
            if '"""' not in code and "'''" not in code:
                score -= 0.3

            lines = code.split("\n")
            if len(lines) > 20:
                has_sections = any(
                    line.strip().startswith("# ") and len(line.strip()) > 5
                    for line in lines
                )
                if not has_sections:
                    score -= 0.2

        return max(0.0, score)

    def _check_detail_alignment(self, code: str, detail_orientation: int) -> float:
        """Check if code aligns with detail orientation."""
        score = 1.0

        if detail_orientation >= 65:
            comment_lines = [line for line in code.split("\n") if line.strip().startswith("#")]
            code_lines = [line for line in code.split("\n") if line.strip() and not line.strip().startswith("#")]

            if code_lines and len(comment_lines) / len(code_lines) < 0.1:
                score -= 0.2

        return max(0.0, score)

    def _generate_soul_suggestions(self, scores: dict[str, float], traits: dict[str, Any]) -> list[str]:
        """Generate suggestions based on Soul alignment."""
        suggestions = []

        if scores.get("risk_tolerance", 1.0) < 0.7:
            risk_tolerance = traits.get("risk_tolerance", 50)
            if risk_tolerance < 38:
                suggestions.append("Remove risky patterns to match conservative risk profile")
            else:
                suggestions.append("Consider adding more robust error handling")

        if scores.get("structure", 1.0) < 0.7:
            structure = traits.get("structure", 50)
            if structure >= 65:
                suggestions.append("Add more documentation and structure to match preference")

        if scores.get("detail_orientation", 1.0) < 0.7:
            detail_orientation = traits.get("detail_orientation", 50)
            if detail_orientation >= 65:
                suggestions.append("Add more comments and details to match preference")

        return suggestions

    def _assess_risks(
        self,
        code: str,
        task: dict[str, Any],
        soul_meta: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Assess risks in code."""
        risks = []

        security_risks = self._check_security_risks(code)
        risks.extend(security_risks)

        performance_risks = self._check_performance_risks(code)
        risks.extend(performance_risks)

        maintainability_risks = self._check_maintainability_risks(code)
        risks.extend(maintainability_risks)

        risk_score = max(0.0, 1.0 - len(risks) * 0.1)

        return {
            "risk_score": round(risk_score, 2),
            "risks": risks,
            "risk_count": len(risks),
        }

    def _check_security_risks(self, code: str) -> list[str]:
        """Check for security risks."""
        risks = []

        security_patterns = [
            ("eval(", "Use of eval() can be dangerous"),
            ("exec(", "Use of exec() can be dangerous"),
            ("__import__(", "Dynamic imports can be unsafe"),
            ("os.system(", "Shell command execution can be unsafe"),
            ("subprocess.call(", "Subprocess calls need validation"),
            ("pickle.loads(", "Pickle can execute arbitrary code"),
        ]

        for pattern, message in security_patterns:
            if pattern in code:
                risks.append(f"Security: {message}")

        return risks

    def _check_performance_risks(self, code: str) -> list[str]:
        """Check for performance risks."""
        risks = []

        if "for " in code and "for " in code:
            nested_loops = code.count("for ")
            if nested_loops > 2:
                risks.append(f"Performance: {nested_loops} nested loops detected")

        if "import *" in code:
            risks.append("Performance: Wildcard imports can slow down startup")

        return risks

    def _check_maintainability_risks(self, code: str) -> list[str]:
        """Check for maintainability risks."""
        risks = []

        lines = code.split("\n")
        if len(lines) > 100:
            risks.append("Maintainability: Very long file (>100 lines)")

        long_lines = [line for line in lines if len(line) > 120]
        if long_lines:
            risks.append(f"Maintainability: {len(long_lines)} lines exceed 120 characters")

        return risks

    def _calculate_final_score(
        self,
        code_quality: dict[str, Any],
        soul_alignment: dict[str, Any],
        risk_assessment: dict[str, Any],
    ) -> float:
        """Calculate final evaluation score."""
        weights = {
            "code_quality": 0.5,
            "soul_alignment": 0.3,
            "risk_assessment": 0.2,
        }

        score = (
            code_quality.get("overall_score", 0) * weights["code_quality"] +
            soul_alignment.get("alignment_score", 0) * weights["soul_alignment"] +
            risk_assessment.get("risk_score", 0) * weights["risk_assessment"]
        )

        return round(score, 2)

    def _generate_suggestions(
        self,
        code_quality: dict[str, Any],
        soul_alignment: dict[str, Any],
        risk_assessment: dict[str, Any],
    ) -> list[str]:
        """Generate improvement suggestions."""
        suggestions = []

        suggestions.extend(code_quality.get("issues", []))
        suggestions.extend(soul_alignment.get("suggestions", []))

        if risk_assessment.get("risk_count", 0) > 0:
            suggestions.append(f"Address {risk_assessment['risk_count']} identified risks")

        return suggestions

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
