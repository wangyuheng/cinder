"""
Task Planner - Decomposes goals into executable subtasks.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
import json
import ollama

from cinder_cli.config import Config
from cinder_cli.executor.token_tracker import TokenTracker

if TYPE_CHECKING:
    from cinder_cli.tracing import LLMTracer


class TaskPlanner:
    """Decomposes complex goals into executable subtasks."""

    def __init__(
        self,
        config: Config,
        token_tracker: TokenTracker | None = None,
        llm_tracer: LLMTracer | None = None,
    ):
        self.config = config
        self.model_name = config.get("model", "qwen3.5:0.8b")
        self.temperature = config.get("temperature", 0.2)
        self.base_url = config.get("ollama_base_url", "http://localhost:11434")
        self.keep_alive = config.get("ollama_keep_alive", "10m")
        self.debug = config.get("ollama_debug", False)
        self.client = ollama.Client(host=self.base_url)
        self.token_tracker = token_tracker
        self.llm_tracer = llm_tracer

    def understand_goal_with_llm(
        self,
        goal: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Use LLM to understand goal semantics and extract key requirements.

        Args:
            goal: Natural language goal description
            constraints: Optional constraints

        Returns:
            Understanding result with semantic components
        """
        system_prompt = """你是一个任务分析专家。请分析用户的目标并提取以下信息：
1. 主要目标类型（web应用、API、脚本、工具等）
2. 关键功能需求
3. 技术栈要求
4. 隐含的依赖关系
5. 复杂度评估

请以JSON格式返回结果，格式如下：
{
  "goal_type": "目标类型",
  "key_features": ["功能1", "功能2"],
  "tech_stack": {
    "language": "编程语言",
    "framework": "框架",
    "database": "数据库"
  },
  "dependencies": ["依赖1", "依赖2"],
  "complexity": "low/medium/high",
  "estimated_tasks": 5
}"""

        user_prompt = f"""请分析以下目标：
目标：{goal}
约束：{constraints or '无'}

请提取关键信息并返回JSON格式的分析结果。"""

        if self.llm_tracer:
            with self.llm_tracer.trace_llm_call(
                model=self.model_name,
                prompt=user_prompt,
                system_prompt=system_prompt,
                model_params={"temperature": 0.3},
                phase="goal_understanding",
                goal=goal,
            ) as record:
                result = self._execute_understand_llm_call(
                    goal, constraints, system_prompt, user_prompt
                )
                if record and result.get("success"):
                    self.llm_tracer.record_response(
                        record,
                        result.get("raw_response", ""),
                        result.get("input_tokens", 0),
                        result.get("output_tokens", 0)
                    )
                return result
        else:
            return self._execute_understand_llm_call(
                goal, constraints, system_prompt, user_prompt
            )

    def _execute_understand_llm_call(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        """
        Execute LLM call for goal understanding.
        
        Args:
            goal: Goal to understand
            constraints: Optional constraints
            system_prompt: System prompt
            user_prompt: User prompt
            
        Returns:
            Understanding result
        """
        try:
            if self.debug:
                print(f"\n[DEBUG] TaskPlanner LLM Request:")
                print(f"  Goal: {goal}")
                print(f"  Constraints: {constraints}")

            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={
                    "temperature": 0.3,
                    "num_ctx": 2048,
                },
                keep_alive=self.keep_alive,
            )

            if self.debug:
                print(f"\n[DEBUG] TaskPlanner LLM Response Type:")
                print(f"  {type(response)}")
                print(f"\n[DEBUG] Response Attributes (all):")
                attrs = [a for a in dir(response) if not a.startswith('_')]
                for attr in attrs:
                    try:
                        value = getattr(response, attr)
                        if not callable(value):
                            print(f"  {attr}: {value}")
                    except:
                        pass

            content = response.message.content if hasattr(response, 'message') else response.get("message", {}).get("content", "")
            
            input_tokens_raw = getattr(response, 'prompt_eval_count', None) or response.get("prompt_eval_count")
            output_tokens_raw = getattr(response, 'eval_count', None) or response.get("eval_count")
            
            input_tokens = input_tokens_raw if input_tokens_raw is not None else 0
            output_tokens = output_tokens_raw if output_tokens_raw is not None else 0
            
            if self.debug:
                print(f"\n[DEBUG] Token Extraction:")
                print(f"  Has prompt_eval_count attr: {hasattr(response, 'prompt_eval_count')}")
                print(f"  Has eval_count attr: {hasattr(response, 'eval_count')}")
                print(f"  input_tokens_raw: {input_tokens_raw}")
                print(f"  output_tokens_raw: {output_tokens_raw}")
                print(f"  input_tokens: {input_tokens}")
                print(f"  output_tokens: {output_tokens}")
            
            if self.token_tracker:
                self.token_tracker.record_call(
                    phase="plan",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    model=self.model_name,
                )

            if self.debug:
                print(f"\n[DEBUG] Content Preview:")
                print(f"  {content[:200]}...")

            json_match = content
            if "```json" in content:
                json_match = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_match = content.split("```")[1].split("```")[0].strip()

            understanding = json.loads(json_match)

            return {
                "goal": goal,
                "understanding": understanding,
                "raw_response": content,
                "success": True,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }

        except Exception as e:
            if self.debug:
                print(f"\n[DEBUG] TaskPlanner LLM Error: {e}")

            return {
                "goal": goal,
                "understanding": None,
                "error": str(e),
                "success": False,
            }

    def infer_project_name(
        self,
        goal: str,
        constraints: dict[str, Any] | None = None,
    ) -> str:
        """
        Infer a suitable project name from the goal description.
        
        Args:
            goal: Natural language goal description
            constraints: Optional constraints
            
        Returns:
            A suitable project directory name
        """
        import re
        
        system_prompt = """你是一个项目命名专家。根据用户的目标描述，生成一个合适的项目目录名称。

要求：
1. 名称应该简洁、有意义、易于理解
2. 只使用小写字母、数字和连字符(-)
3. 不要使用空格或特殊字符
4. 名称应该反映项目的主要功能或目的
5. 如果目标中包含具体的应用名称，优先使用它
6. 名称长度建议在 3-30 个字符之间

返回格式：
{
  "project_name": "项目名称",
  "reasoning": "命名理由（简短说明）"
}"""

        user_prompt = f"""请为以下目标生成一个合适的项目名称：

目标：{goal}

约束条件：{constraints or '无'}

请返回 JSON 格式的结果。"""

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={
                    "temperature": 0.3,
                    "num_ctx": 1024,
                },
                keep_alive=self.keep_alive,
            )

            content = response.message.content if hasattr(response, 'message') else response.get("message", {}).get("content", "")
            
            json_match = content
            if "```json" in content:
                json_match = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_match = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(json_match)
            project_name = result.get("project_name", "project")
            
            project_name = re.sub(r'[^a-z0-9-]', '-', project_name.lower())
            project_name = re.sub(r'-+', '-', project_name)
            project_name = project_name.strip('-')
            
            if not project_name or len(project_name) < 2:
                project_name = "project"
            
            if self.debug:
                print(f"\n[DEBUG] Inferred project name: {project_name}")
                print(f"[DEBUG] Reasoning: {result.get('reasoning', 'N/A')}")
            
            return project_name

        except Exception as e:
            if self.debug:
                print(f"\n[DEBUG] Failed to infer project name: {e}")
            
            keywords = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', goal)
            if keywords:
                first_keyword = keywords[0].lower()
                project_name = re.sub(r'[^a-z0-9-]', '-', first_keyword)
                return project_name.strip('-') or "project"
            
            return "project"


    def decompose_goal_with_llm(
        self,
        goal: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Decompose goal using LLM understanding.

        Args:
            goal: Natural language goal description
            constraints: Optional constraints

        Returns:
            Task plan with dependency graph and complexity
        """
        understanding = self.understand_goal_with_llm(goal, constraints)

        if not understanding.get("success"):
            return self.decompose_goal(goal, constraints)

        understanding_data = understanding.get("understanding", {})

        subtasks = self._generate_tasks_from_understanding(
            understanding_data,
            constraints
        )

        dependency_graph = self.build_dependency_graph(subtasks)
        complexity = self.estimate_complexity(subtasks)

        return {
            "goal": goal,
            "subtasks": subtasks,
            "constraints": constraints or {},
            "understanding": understanding_data,
            "dependency_graph": dependency_graph,
            "complexity": complexity,
        }

    def _generate_tasks_from_understanding(
        self,
        understanding: dict[str, Any],
        constraints: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """
        Generate tasks from LLM understanding.

        Args:
            understanding: Understanding from LLM
            constraints: Optional constraints

        Returns:
            List of subtasks
        """
        goal_type = understanding.get("goal_type", "generic")
        key_features = understanding.get("key_features", [])
        tech_stack = understanding.get("tech_stack", {})
        estimated_tasks = understanding.get("estimated_tasks", 3)

        language = tech_stack.get("language", constraints.get("language", "python") if constraints else "python")
        framework = tech_stack.get("framework", constraints.get("framework", "fastapi") if constraints else "fastapi")

        subtasks = []

        if "web" in goal_type.lower() or "应用" in goal_type:
            subtasks = self._decompose_web_project_with_features(
                goal_type,
                key_features,
                language,
                framework
            )
        elif "api" in goal_type.lower():
            subtasks = self._decompose_api_project_with_features(
                goal_type,
                key_features,
                language,
                framework
            )
        else:
            subtasks = self._decompose_generic_with_features(
                goal_type,
                key_features,
                language
            )

        return subtasks

    def validate_plan(
        self,
        plan: dict[str, Any],
        understanding: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Validate a task plan for completeness, feasibility, and quality.

        Args:
            plan: Task plan to validate
            understanding: Optional LLM understanding for comparison

        Returns:
            Validation result with quality score
        """
        subtasks = plan.get("subtasks", [])

        completeness = self._check_completeness(plan, understanding)
        feasibility = self._check_feasibility(plan)
        dependency_correctness = self._check_dependency_correctness(subtasks)

        quality_score = self._calculate_plan_quality(
            completeness,
            feasibility,
            dependency_correctness
        )

        return {
            "valid": quality_score >= 0.7,
            "quality_score": quality_score,
            "completeness": completeness,
            "feasibility": feasibility,
            "dependency_correctness": dependency_correctness,
            "issues": self._identify_issues(completeness, feasibility, dependency_correctness),
        }

    def _check_completeness(
        self,
        plan: dict[str, Any],
        understanding: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Check if plan covers all requirements."""
        subtasks = plan.get("subtasks", [])
        goal = plan.get("goal", "")

        coverage_score = 1.0
        missing_requirements = []

        if understanding:
            key_features = understanding.get("key_features", [])
            task_descriptions = " ".join([t.get("description", "") for t in subtasks])

            covered_features = []
            for feature in key_features:
                if feature in task_descriptions or any(
                    feature in t.get("description", "") for t in subtasks
                ):
                    covered_features.append(feature)
                else:
                    missing_requirements.append(feature)

            coverage_score = len(covered_features) / len(key_features) if key_features else 1.0

        return {
            "score": coverage_score,
            "missing_requirements": missing_requirements,
            "task_count": len(subtasks),
        }

    def _check_feasibility(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Check if plan is feasible to execute."""
        subtasks = plan.get("subtasks", [])
        issues = []

        for task in subtasks:
            file_path = task.get("file_path", "")
            if file_path and ".." in file_path:
                issues.append(f"Invalid file path: {file_path}")

        complexity = self.estimate_complexity(subtasks)
        avg_complexity = complexity.get("average", 0)

        if avg_complexity > 5:
            issues.append(f"High average complexity: {avg_complexity}")

        score = 1.0 - (len(issues) * 0.2)

        return {
            "score": max(0.0, score),
            "issues": issues,
            "average_complexity": avg_complexity,
        }

    def _check_dependency_correctness(self, subtasks: list[dict[str, Any]]) -> dict[str, Any]:
        """Check if dependencies are correct and no circular dependencies exist."""
        if not subtasks:
            return {"score": 1.0, "issues": []}

        issues = []
        task_ids = {t.get("id") for t in subtasks}

        for task in subtasks:
            dependencies = task.get("dependencies", [])
            for dep_id in dependencies:
                if dep_id not in task_ids:
                    issues.append(f"Invalid dependency: {task.get('id')} -> {dep_id}")

        if self._has_circular_dependencies(subtasks):
            issues.append("Circular dependencies detected")

        score = 1.0 - (len(issues) * 0.3)

        return {
            "score": max(0.0, score),
            "issues": issues,
            "has_circular_deps": self._has_circular_dependencies(subtasks),
        }

    def _has_circular_dependencies(self, subtasks: list[dict[str, Any]]) -> bool:
        """Check if there are circular dependencies."""
        visited = set()
        rec_stack = set()

        def visit(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            task = next((t for t in subtasks if t.get("id") == task_id), None)
            if task:
                for dep_id in task.get("dependencies", []):
                    if dep_id not in visited:
                        if visit(dep_id):
                            return True
                    elif dep_id in rec_stack:
                        return True

            rec_stack.remove(task_id)
            return False

        for task in subtasks:
            task_id = task.get("id")
            if task_id not in visited:
                if visit(task_id):
                    return True

        return False

    def _calculate_plan_quality(
        self,
        completeness: dict[str, Any],
        feasibility: dict[str, Any],
        dependency_correctness: dict[str, Any],
    ) -> float:
        """Calculate overall plan quality score."""
        coverage_weight = 0.4
        dependency_weight = 0.3
        feasibility_weight = 0.3

        score = (
            completeness.get("score", 0) * coverage_weight +
            dependency_correctness.get("score", 0) * dependency_weight +
            feasibility.get("score", 0) * feasibility_weight
        )

        return round(score, 2)

    def _identify_issues(
        self,
        completeness: dict[str, Any],
        feasibility: dict[str, Any],
        dependency_correctness: dict[str, Any],
    ) -> list[str]:
        """Identify all issues in the plan."""
        issues = []

        issues.extend(completeness.get("missing_requirements", []))
        issues.extend(feasibility.get("issues", []))
        issues.extend(dependency_correctness.get("issues", []))

        return issues

    def decompose_goal_with_validation(
        self,
        goal: str,
        constraints: dict[str, Any] | None = None,
        max_retries: int = 2,
        quality_threshold: float = 0.7,
    ) -> dict[str, Any]:
        """
        Decompose goal with validation and regeneration on low quality.

        Args:
            goal: Natural language goal description
            constraints: Optional constraints
            max_retries: Maximum number of regeneration attempts
            quality_threshold: Minimum quality score required

        Returns:
            Validated task plan
        """
        if self.llm_tracer:
            with self.llm_tracer.trace_llm_call(
                model=self.model_name,
                prompt=goal,
                model_params={
                    "max_retries": max_retries,
                    "quality_threshold": quality_threshold,
                },
                phase="validated_decomposition",
            ) as record:
                result = self._execute_validation_decomposition(
                    goal, constraints, max_retries, quality_threshold
                )
                if record:
                    self.llm_tracer.record_response(
                        record,
                        str(result.get("subtasks", [])),
                        0,
                        0
                    )
                    record.metadata["validation_score"] = result.get("validation", {}).get("quality_score", 0)
                    record.metadata["attempts"] = result.get("attempts", 1)
                return result
        else:
            return self._execute_validation_decomposition(
                goal, constraints, max_retries, quality_threshold
            )

    def _execute_validation_decomposition(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
        max_retries: int,
        quality_threshold: float,
    ) -> dict[str, Any]:
        """
        Execute goal decomposition with validation.
        
        Args:
            goal: Goal to decompose
            constraints: Optional constraints
            max_retries: Maximum retries
            quality_threshold: Quality threshold
            
        Returns:
            Validated task plan
        """
        understanding = self.understand_goal_with_llm(goal, constraints)
        understanding_data = understanding.get("understanding") if understanding.get("success") else None

        for attempt in range(max_retries + 1):
            if attempt == 0:
                plan = self.decompose_goal_with_llm(goal, constraints)
            else:
                plan = self._regenerate_plan_with_feedback(
                    goal,
                    constraints,
                    previous_plan,
                    validation,
                    understanding_data
                )

            validation = self.validate_plan(plan, understanding_data)

            if validation.get("quality_score", 0) >= quality_threshold:
                plan["validation"] = validation
                plan["attempts"] = attempt + 1
                return plan

            previous_plan = plan

        plan["validation"] = validation
        plan["attempts"] = max_retries + 1
        plan["quality_warning"] = True

        return plan

    def _regenerate_plan_with_feedback(
        self,
        goal: str,
        constraints: dict[str, Any] | None,
        previous_plan: dict[str, Any],
        validation: dict[str, Any],
        understanding: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        Regenerate plan with feedback from validation.

        Args:
            goal: Original goal
            constraints: Optional constraints
            previous_plan: Previous plan that failed validation
            validation: Validation result
            understanding: LLM understanding

        Returns:
            Regenerated plan
        """
        issues = validation.get("issues", [])
        missing = validation.get("completeness", {}).get("missing_requirements", [])

        feedback_prompt = f"""之前的计划存在以下问题：
问题：{', '.join(issues)}
缺失需求：{', '.join(missing)}

请重新分析并生成更完善的任务计划。"""

        enhanced_constraints = constraints or {}
        enhanced_constraints["feedback"] = feedback_prompt
        enhanced_constraints["missing_requirements"] = missing

        return self.decompose_goal_with_llm(goal, enhanced_constraints)

    def _decompose_web_project_with_features(
        self,
        goal_type: str,
        key_features: list[str],
        language: str,
        framework: str,
    ) -> list[dict[str, Any]]:
        """Decompose web project with specific features."""
        subtasks = [
            {
                "id": "1",
                "description": "创建项目目录结构",
                "type": "setup",
                "language": language,
                "file_path": "project/__init__.py",
            },
            {
                "id": "2",
                "description": f"创建 {framework} 应用主文件",
                "type": "code",
                "language": language,
                "file_path": "project/app.py",
            },
        ]

        for i, feature in enumerate(key_features, start=3):
            feature_id = str(i)
            feature_file = feature.lower().replace(" ", "_").replace("/", "_")

            subtasks.append({
                "id": feature_id,
                "description": f"实现{feature}功能",
                "type": "code",
                "language": language,
                "file_path": f"project/{feature_file}.py",
                "dependencies": ["2"],
            })

        subtasks.extend([
            {
                "id": str(len(subtasks) + 1),
                "description": "创建配置文件",
                "type": "config",
                "language": "yaml",
                "file_path": "project/config.yaml",
            },
            {
                "id": str(len(subtasks) + 2),
                "description": "创建README文档",
                "type": "docs",
                "language": "markdown",
                "file_path": "project/README.md",
            },
        ])

        return subtasks

    def _decompose_api_project_with_features(
        self,
        goal_type: str,
        key_features: list[str],
        language: str,
        framework: str,
    ) -> list[dict[str, Any]]:
        """Decompose API project with specific features."""
        subtasks = [
            {
                "id": "1",
                "description": f"创建 {framework} API 主文件",
                "type": "code",
                "language": language,
                "file_path": "api.py",
            },
            {
                "id": "2",
                "description": "创建数据模型",
                "type": "code",
                "language": language,
                "file_path": "models.py",
            },
        ]

        for i, feature in enumerate(key_features, start=3):
            subtasks.append({
                "id": str(i),
                "description": f"实现{feature}端点",
                "type": "code",
                "language": language,
                "file_path": "api.py",
                "dependencies": ["1", "2"],
            })

        subtasks.append({
            "id": str(len(subtasks) + 1),
            "description": "创建API文档",
            "type": "docs",
            "language": "markdown",
            "file_path": "API.md",
        })

        return subtasks

    def _decompose_generic_with_features(
        self,
        goal_type: str,
        key_features: list[str],
        language: str,
    ) -> list[dict[str, Any]]:
        """Decompose generic project with features."""
        if not key_features:
            return [
                {
                    "id": "1",
                    "description": f"创建{goal_type}",
                    "type": "code",
                    "language": language,
                    "file_path": "main.py",
                },
            ]

        subtasks = []
        for i, feature in enumerate(key_features, start=1):
            subtasks.append({
                "id": str(i),
                "description": f"实现{feature}",
                "type": "code",
                "language": language,
                "file_path": f"{feature.lower().replace(' ', '_')}.py",
            })

        return subtasks

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
