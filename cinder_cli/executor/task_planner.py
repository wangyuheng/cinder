"""
Task Planner - Decomposes goals into executable subtasks.
"""

from __future__ import annotations

from typing import Any

from cinder_cli.config import Config


class TaskPlanner:
    """Decomposes complex goals into executable subtasks."""

    def __init__(self, config: Config):
        self.config = config

    def decompose_goal(
        self,
        goal: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Decompose a goal into a tree of subtasks.

        Args:
            goal: Natural language goal description
            constraints: Optional constraints

        Returns:
            Task tree with subtasks and dependencies
        """
        # Simple heuristic-based decomposition
        # In a real implementation, this would use LLM
        subtasks = self._heuristic_decomposition(goal, constraints)

        return {
            "goal": goal,
            "subtasks": subtasks,
            "constraints": constraints or {},
        }

    def _heuristic_decomposition(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Use heuristics to decompose goal."""
        subtasks = []

        # Detect goal type
        if "web" in goal.lower() or "网站" in goal or "应用" in goal:
            subtasks = self._decompose_web_project(goal, constraints)
        elif "api" in goal.lower():
            subtasks = self._decompose_api_project(goal, constraints)
        elif "python" in goal.lower() or "脚本" in goal:
            subtasks = self._decompose_python_script(goal, constraints)
        else:
            subtasks = self._decompose_generic(goal, constraints)

        return subtasks

    def _decompose_web_project(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Decompose web project goal."""
        return [
            {
                "id": "1",
                "description": "创建项目目录结构",
                "type": "setup",
                "language": "python",
                "file_path": "project/__init__.py",
            },
            {
                "id": "2",
                "description": "创建后端API框架",
                "type": "code",
                "language": "python",
                "file_path": "project/app.py",
            },
            {
                "id": "3",
                "description": "创建前端页面",
                "type": "code",
                "language": "html",
                "file_path": "project/templates/index.html",
            },
            {
                "id": "4",
                "description": "创建配置文件",
                "type": "config",
                "language": "yaml",
                "file_path": "project/config.yaml",
            },
        ]

    def _decompose_api_project(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Decompose API project goal."""
        framework = constraints.get("framework", "fastapi") if constraints else "fastapi"

        return [
            {
                "id": "1",
                "description": f"创建 {framework} API 主文件",
                "type": "code",
                "language": "python",
                "file_path": "api.py",
            },
            {
                "id": "2",
                "description": "创建数据模型",
                "type": "code",
                "language": "python",
                "file_path": "models.py",
            },
            {
                "id": "3",
                "description": "创建API文档",
                "type": "docs",
                "language": "markdown",
                "file_path": "API.md",
            },
        ]

    def _decompose_python_script(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Decompose Python script goal."""
        return [
            {
                "id": "1",
                "description": "创建Python脚本",
                "type": "code",
                "language": "python",
                "file_path": "main.py",
            },
        ]

    def _decompose_generic(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Decompose generic goal."""
        return [
            {
                "id": "1",
                "description": goal,
                "type": "code",
                "language": "python",
                "file_path": "output.py",
            },
        ]

    def build_dependency_graph(
        self,
        subtasks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Build a dependency graph from subtasks.

        Args:
            subtasks: List of subtasks

        Returns:
            Dependency graph with nodes and edges
        """
        nodes = []
        edges = []

        for i, task in enumerate(subtasks):
            nodes.append({
                "id": task["id"],
                "label": task["description"],
                "type": task.get("type", "code"),
            })

            if i > 0:
                edges.append({
                    "from": subtasks[i - 1]["id"],
                    "to": task["id"],
                    "type": "sequential",
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "execution_order": [t["id"] for t in subtasks],
        }

    def estimate_complexity(
        self,
        subtasks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Estimate complexity of subtasks.

        Args:
            subtasks: List of subtasks

        Returns:
            Complexity estimation
        """
        type_weights = {
            "setup": 1,
            "config": 1,
            "code": 3,
            "docs": 1,
            "test": 2,
        }

        language_weights = {
            "python": 1.0,
            "javascript": 1.2,
            "typescript": 1.3,
            "html": 0.5,
            "css": 0.5,
            "yaml": 0.3,
            "markdown": 0.2,
        }

        total_complexity = 0
        task_complexities = []

        for task in subtasks:
            task_type = task.get("type", "code")
            language = task.get("language", "python")

            base = type_weights.get(task_type, 2)
            lang_factor = language_weights.get(language, 1.0)

            complexity = base * lang_factor
            total_complexity += complexity

            task_complexities.append({
                "id": task["id"],
                "complexity": complexity,
                "factors": {
                    "type": task_type,
                    "language": language,
                },
            })

        avg_complexity = total_complexity / len(subtasks) if subtasks else 0

        return {
            "total": round(total_complexity, 2),
            "average": round(avg_complexity, 2),
            "task_count": len(subtasks),
            "estimated_time_minutes": round(total_complexity * 5, 1),
            "task_complexities": task_complexities,
        }

    def replan_tasks(
        self,
        original_plan: dict[str, Any],
        failed_task: dict[str, Any],
        error: str,
    ) -> dict[str, Any]:
        """
        Replan tasks after a failure.

        Args:
            original_plan: Original task plan
            failed_task: The task that failed
            error: Error message

        Returns:
            New task plan
        """
        subtasks = original_plan.get("subtasks", [])
        failed_id = failed_task.get("id")

        new_subtasks = []
        retry_task = None

        for task in subtasks:
            if task["id"] == failed_id:
                retry_task = task.copy()
                retry_task["retry"] = True
                retry_task["previous_error"] = error
                retry_task["id"] = f"{failed_id}_retry"
                new_subtasks.append(retry_task)
            else:
                new_subtasks.append(task)

        return {
            "goal": original_plan.get("goal"),
            "subtasks": new_subtasks,
            "constraints": original_plan.get("constraints", {}),
            "replanned": True,
            "retry_for": failed_id,
        }

    def preview_tasks(
        self,
        goal: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Preview tasks without executing.

        Args:
            goal: Goal description
            constraints: Optional constraints

        Returns:
            Preview of tasks
        """
        plan = self.decompose_goal(goal, constraints)
        dependency_graph = self.build_dependency_graph(plan["subtasks"])
        complexity = self.estimate_complexity(plan["subtasks"])

        return {
            "goal": goal,
            "task_count": len(plan["subtasks"]),
            "tasks": plan["subtasks"],
            "dependency_graph": dependency_graph,
            "complexity": complexity,
            "constraints": constraints or {},
        }

    def visualize_task_tree(
        self,
        subtasks: list[dict[str, Any]],
        format: str = "text",
    ) -> str:
        """
        Visualize task tree.

        Args:
            subtasks: List of subtasks
            format: Output format (text, markdown)

        Returns:
            Visualization string
        """
        if format == "markdown":
            lines = ["## 任务列表\n"]
            for i, task in enumerate(subtasks, 1):
                lines.append(f"{i}. **{task['description']}**")
                lines.append(f"   - 类型: {task.get('type', 'code')}")
                lines.append(f"   - 语言: {task.get('language', 'python')}")
                lines.append(f"   - 文件: `{task.get('file_path', 'N/A')}`")
                lines.append("")
            return "\n".join(lines)
        else:
            lines = ["任务树:"]
            for i, task in enumerate(subtasks):
                prefix = "└── " if i == len(subtasks) - 1 else "├── "
                lines.append(f"  {prefix}[{task['id']}] {task['description']}")
            return "\n".join(lines)
