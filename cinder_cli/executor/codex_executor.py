"""
Codex Executor for executing tasks using Codex CLI.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from .codex_utils import is_codex_installed

logger = logging.getLogger(__name__)


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
    
    def execute(
        self,
        task: CodexTask,
        stream_output: bool = False,
        output_callback: Optional[Callable[[str, str], None]] = None,
    ) -> CodexResult:
        """
        Execute a task using Codex CLI.
        
        Args:
            task: The task to execute
            stream_output: Whether to stream output in real-time
            output_callback: Optional callback for real-time output (line, stream_type)
            
        Returns:
            CodexResult containing the execution result
        """
        cmd = self._build_command(task)
        
        if stream_output:
            return self._execute_with_streaming(cmd, task, output_callback)
        else:
            return self._execute_without_streaming(cmd, task)
    
    def _execute_without_streaming(
        self,
        cmd: list[str],
        task: CodexTask
    ) -> CodexResult:
        """Execute without streaming output."""
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
    
    def _execute_with_streaming(
        self,
        cmd: list[str],
        task: CodexTask,
        output_callback: Optional[Callable[[str, str], None]] = None
    ) -> CodexResult:
        """Execute with streaming output."""
        logger.info(f"Starting Codex execution: {' '.join(cmd)}")
        
        if output_callback:
            output_callback(f"Starting Codex execution...\n", "info")
            output_callback(f"Command: {' '.join(cmd)}\n\n", "info")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=task.cwd,
                bufsize=1,
                universal_newlines=True
            )
            
            stdout_lines = []
            stderr_lines = []
            
            import threading
            import queue
            
            output_queue = queue.Queue()
            
            def read_stream(stream, stream_type):
                """Read from a stream and put lines in queue."""
                try:
                    for line in iter(stream.readline, ''):
                        if line:
                            output_queue.put((line, stream_type))
                except Exception as e:
                    logger.error(f"Error reading {stream_type}: {e}")
                finally:
                    stream.close()
            
            stdout_thread = threading.Thread(
                target=read_stream,
                args=(process.stdout, 'stdout'),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=read_stream,
                args=(process.stderr, 'stderr'),
                daemon=True
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            import time
            start_time = time.time()
            
            while True:
                try:
                    line, stream_type = output_queue.get(timeout=0.1)
                    
                    if stream_type == 'stdout':
                        stdout_lines.append(line)
                        logger.debug(f"STDOUT: {line.rstrip()}")
                    else:
                        stderr_lines.append(line)
                        logger.debug(f"STDERR: {line.rstrip()}")
                    
                    if output_callback:
                        output_callback(line, stream_type)
                    
                    if sys.stdout.isatty():
                        if stream_type == 'stdout':
                            print(f"\033[92m{line}\033[0m", end='')
                        else:
                            print(f"\033[93m{line}\033[0m", end='')
                
                except queue.Empty:
                    pass
                
                if process.poll() is not None:
                    break
                
                if task.timeout and (time.time() - start_time) > task.timeout:
                    process.terminate()
                    return CodexResult(
                        success=False,
                        output="",
                        error=f"Execution timed out after {task.timeout} seconds",
                        exit_code=-1
                    )
            
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)
            
            while not output_queue.empty():
                try:
                    line, stream_type = output_queue.get_nowait()
                    if stream_type == 'stdout':
                        stdout_lines.append(line)
                    else:
                        stderr_lines.append(line)
                    
                    if output_callback:
                        output_callback(line, stream_type)
                except queue.Empty:
                    break
            
            stdout_text = ''.join(stdout_lines)
            stderr_text = ''.join(stderr_lines)
            
            exit_code = process.returncode
            
            if output_callback:
                output_callback(f"\nExecution completed with exit code: {exit_code}\n", "info")
            
            logger.info(f"Codex execution completed with exit code: {exit_code}")
            
            return CodexResult(
                success=(exit_code == 0),
                output=stdout_text,
                error=stderr_text if stderr_text else None,
                metadata={
                    "returncode": exit_code,
                    "task_description": task.description
                },
                exit_code=exit_code
            )
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            if output_callback:
                output_callback(f"\nExecution failed: {e}\n", "error")
            
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
