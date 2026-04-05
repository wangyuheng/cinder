"""
Codex Executor for executing tasks using Codex CLI.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .codex_utils import is_codex_installed


@dataclass
class CodexTask:
    """Represents a task to be executed by Codex."""
    
    description: str
    model: Optional[str] = None
    sandbox_mode: Optional[str] = None
    approval_policy: Optional[str] = None
    full_auto: bool = False
    output_schema: Optional[dict[str, Any]] = None
    cwd: Optional[Path] = None
    timeout: int = 300
    skip_git_repo_check: bool = True
    ephemeral: bool = True


@dataclass
class CodexResult:
    """Represents the result of a Codex execution."""
    
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    exit_code: int = 0


class CodexExecExecutor:
    """
    Executor that uses Codex CLI in non-interactive mode.
    
    This executor runs `codex exec` commands with various options
    to execute tasks programmatically.
    """
    
    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize CodexExecExecutor.
        
        Args:
            config: Configuration dictionary for Codex execution
        """
        self.config = config or {}
        
        if not is_codex_installed():
            raise RuntimeError(
                "Codex CLI is not installed. Please install it using:\n"
                "  npm install -g @openai/codex\n"
                "  or\n"
                "  ollama launch codex --model <model-name>"
            )
    
    def execute(self, task: CodexTask) -> CodexResult:
        """
        Execute a task using Codex CLI.
        
        Args:
            task: The task to execute
            
        Returns:
            CodexResult containing the execution result
        """
        cmd = self._build_command(task)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=task.timeout,
                cwd=task.cwd
            )
            
            return self._parse_result(result, task)
            
        except subprocess.TimeoutExpired:
            return CodexResult(
                success=False,
                output="",
                error=f"Execution timed out after {task.timeout} seconds",
                exit_code=-1
            )
        except subprocess.SubprocessError as e:
            return CodexResult(
                success=False,
                output="",
                error=f"Execution failed: {e}",
                exit_code=-1
            )
    
    def _build_command(self, task: CodexTask) -> list[str]:
        """
        Build the codex exec command with all options.
        
        Args:
            task: The task to execute
            
        Returns:
            List of command arguments
        """
        cmd = [
            "codex",
            "exec",
            "--json",
        ]
        
        if task.skip_git_repo_check:
            cmd.append("--skip-git-repo-check")
        
        if task.ephemeral:
            cmd.append("--ephemeral")
        
        if task.model:
            cmd.extend(["--model", task.model])
        
        if task.sandbox_mode:
            cmd.extend(["--sandbox", task.sandbox_mode])
        
        if task.full_auto:
            cmd.append("--full-auto")
        
        if task.output_schema:
            schema_file = self._write_schema_file(task.output_schema)
            cmd.extend(["--output-schema", schema_file])
        
        if task.cwd:
            cmd.extend(["--cd", str(task.cwd)])
        
        cmd.append(task.description)
        
        return cmd
    
    def _write_schema_file(self, schema: dict[str, Any]) -> str:
        """
        Write JSON schema to a temporary file.
        
        Args:
            schema: JSON schema dictionary
            
        Returns:
            Path to the temporary schema file
        """
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        ) as f:
            json.dump(schema, f)
            return f.name
    
    def _parse_result(
        self,
        result: subprocess.CompletedProcess[str],
        task: CodexTask
    ) -> CodexResult:
        """
        Parse the execution result.
        
        Args:
            result: Completed process result
            task: The executed task
            
        Returns:
            CodexResult with parsed output
        """
        if result.returncode != 0:
            return CodexResult(
                success=False,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode
            )
        
        output = self._parse_jsonl_output(result.stdout)
        
        return CodexResult(
            success=True,
            output=output,
            metadata={
                "returncode": result.returncode,
                "task_description": task.description
            },
            exit_code=result.returncode
        )
    
    def _parse_jsonl_output(self, stdout: str) -> str:
        """
        Parse JSONL output from Codex CLI.
        
        Args:
            stdout: Raw stdout from Codex execution
            
        Returns:
            Extracted output text
        """
        lines = stdout.strip().split('\n')
        output_parts = []
        
        for line in lines:
            if not line.strip():
                continue
            
            try:
                data = json.loads(line)
                
                if isinstance(data, dict):
                    if "text" in data:
                        output_parts.append(data["text"])
                    elif "content" in data:
                        output_parts.append(data["content"])
                    elif "message" in data:
                        output_parts.append(data["message"])
            except json.JSONDecodeError:
                output_parts.append(line)
        
        return '\n'.join(output_parts)
