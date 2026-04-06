"""
Codex Integration Manager for managing Codex executors.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ..config import Config
from .codex_executor import CodexExecExecutor, CodexResult, CodexTask
from .codex_exceptions import CodexError
from .codex_utils import check_codex_availability

logger = logging.getLogger(__name__)


@dataclass
class TaskContext:
    """Context information for task execution."""
    
    soul_profile: dict[str, Any]
    decision_context: dict[str, Any]
    quality_requirements: Optional[dict[str, Any]] = None


class CodexIntegrationManager:
    """
    Manages Codex integration and executor selection.
    
    This manager handles:
    - Executor selection based on task characteristics
    - Soul profile context construction
    - Decision context passing
    - Result unification
    - Fallback mechanisms
    """
    
    def __init__(self, config: Config):
        """
        Initialize CodexIntegrationManager.
        
        Args:
            config: Cinder configuration instance
        """
        self.config = config
        self.codex_config = config.codex
        
        self._validate_configuration()
        
        self._exec_executor: Optional[CodexExecExecutor] = None
        
        self._initialize_executors()
    
    def _validate_configuration(self) -> None:
        """Validate Codex configuration."""
        errors = self.config.validate_codex_config()
        if errors:
            raise CodexError(
                "Invalid Codex configuration",
                details="\n".join(errors)
            )
    
    def _initialize_executors(self) -> None:
        """Initialize Codex executors."""
        if not self.codex_config.get("enabled", False):
            logger.info("Codex integration is disabled")
            return
        
        is_available, message = check_codex_availability()
        if not is_available:
            logger.warning(f"Codex not available: {message}")
            if not self.codex_config.get("fallback_on_error", True):
                raise CodexError(message)
            return
        
        try:
            exec_config = self.codex_config.get("exec", {})
            self._exec_executor = CodexExecExecutor(exec_config)
            logger.info("CodexExecExecutor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CodexExecExecutor: {e}")
            if not self.codex_config.get("fallback_on_error", True):
                raise
    
    def is_available(self) -> bool:
        """
        Check if Codex integration is available.
        
        Returns:
            True if Codex is enabled and executors are initialized
        """
        return (
            self.codex_config.get("enabled", False)
            and self._exec_executor is not None
        )
    
    def execute_task(
        self,
        task_description: str,
        context: TaskContext,
        stream_output: bool = False,
        output_callback: Optional[Callable[[str, str], None]] = None,
        **kwargs: Any
    ) -> CodexResult:
        """
        Execute a task using Codex.
        
        Args:
            task_description: Description of the task to execute
            context: Task context including Soul profile and decision context
            stream_output: Whether to stream output in real-time
            output_callback: Optional callback for real-time output
            **kwargs: Additional task parameters
            
        Returns:
            CodexResult from execution
            
        Raises:
            CodexError: If execution fails and fallback is disabled
        """
        if not self.is_available():
            if self.codex_config.get("fallback_on_error", True):
                raise CodexError(
                    "Codex not available, fallback to CodeGenerator"
                )
            else:
                raise CodexError("Codex integration is not available")
        
        prompt = self._build_task_prompt(task_description, context)
        
        task = self._create_task(prompt, **kwargs)
        
        executor = self._select_executor(task)
        
        try:
            result = executor.execute(
                task,
                stream_output=stream_output,
                output_callback=output_callback
            )
            logger.info(f"Task executed successfully: {task_description[:100]}")
            return result
        except CodexError:
            raise
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            if self.codex_config.get("fallback_on_error", True):
                raise CodexError(
                    "Codex execution failed, fallback to CodeGenerator"
                )
            else:
                raise CodexError(f"Task execution failed: {e}")
    
    def _select_executor(self, task: CodexTask) -> CodexExecExecutor:
        """
        Select the appropriate executor for the task.
        
        Args:
            task: Task to execute
            
        Returns:
            CodexExecExecutor instance
        """
        if self._exec_executor is None:
            raise CodexError("No executor available")
        
        return self._exec_executor
    
    def _build_task_prompt(
        self,
        task_description: str,
        context: TaskContext
    ) -> str:
        """
        Build task prompt with Soul profile and decision context.
        
        Args:
            task_description: Original task description
            context: Task context
            
        Returns:
            Enhanced task prompt with context
        """
        soul = context.soul_profile
        decision = context.decision_context
        
        prompt_parts = ["# 上下文信息\n"]
        
        if soul:
            prompt_parts.append("## 用户性格特征\n")
            traits = soul.get("traits", {})
            if traits:
                for key, value in traits.items():
                    prompt_parts.append(f"- {key}: {value}\n")
            
            preferences = soul.get("preferences", {})
            if preferences:
                prompt_parts.append("\n## 决策偏好\n")
                for key, value in preferences.items():
                    prompt_parts.append(f"- {key}: {value}\n")
        
        if decision:
            prompt_parts.append("\n## 任务理解\n")
            if "goal_type" in decision:
                prompt_parts.append(f"- 目标类型: {decision['goal_type']}\n")
            if "key_features" in decision:
                prompt_parts.append(f"- 关键功能: {decision['key_features']}\n")
            if "tech_stack" in decision:
                prompt_parts.append(f"- 技术栈: {decision['tech_stack']}\n")
        
        if context.quality_requirements:
            prompt_parts.append("\n## 质量要求\n")
            for key, value in context.quality_requirements.items():
                prompt_parts.append(f"- {key}: {value}\n")
        
        prompt_parts.append(f"\n# 任务描述\n{task_description}\n")
        
        return "".join(prompt_parts)
    
    def _create_task(
        self,
        prompt: str,
        **kwargs: Any
    ) -> CodexTask:
        """
        Create CodexTask from prompt and parameters.
        
        Args:
            prompt: Task prompt
            **kwargs: Additional task parameters
            
        Returns:
            CodexTask instance
        """
        exec_config = self.codex_config.get("exec", {})
        
        return CodexTask(
            description=prompt,
            model=kwargs.get("model", exec_config.get("model")),
            sandbox_mode=kwargs.get("sandbox_mode", exec_config.get("sandbox_mode")),
            approval_policy=kwargs.get("approval_policy", exec_config.get("approval_policy")),
            full_auto=kwargs.get("full_auto", False),
            output_schema=kwargs.get("output_schema"),
            cwd=kwargs.get("cwd"),
            timeout=kwargs.get("timeout", exec_config.get("timeout", 300)),
            skip_git_repo_check=exec_config.get("skip_git_repo_check", True),
            ephemeral=exec_config.get("ephemeral", True),
        )
