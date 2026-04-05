"""
Custom exceptions for Codex integration.
"""

from __future__ import annotations


class CodexError(Exception):
    """Base exception for Codex-related errors."""
    
    def __init__(self, message: str, details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}\n\nDetails: {self.details}"
        return self.message


class CodexNotInstalledError(CodexError):
    """Raised when Codex CLI is not installed."""
    
    def __init__(self):
        super().__init__(
            "Codex CLI is not installed",
            details=(
                "Please install Codex CLI using one of the following methods:\n"
                "  1. npm install -g @openai/codex\n"
                "  2. ollama launch codex --model <model-name>\n\n"
                "See https://github.com/openai/codex for more information."
            )
        )


class CodexTimeoutError(CodexError):
    """Raised when Codex execution times out."""
    
    def __init__(self, timeout_seconds: int, task_description: str | None = None):
        self.timeout_seconds = timeout_seconds
        self.task_description = task_description
        
        message = f"Codex execution timed out after {timeout_seconds} seconds"
        if task_description:
            message += f" for task: {task_description[:100]}..."
        
        super().__init__(message)


class CodexExecutionError(CodexError):
    """Raised when Codex execution fails."""
    
    def __init__(
        self,
        exit_code: int,
        stderr: str | None = None,
        task_description: str | None = None
    ):
        self.exit_code = exit_code
        self.stderr = stderr
        self.task_description = task_description
        
        message = f"Codex execution failed with exit code {exit_code}"
        if task_description:
            message += f" for task: {task_description[:100]}..."
        
        super().__init__(message, details=stderr)


class CodexOutputError(CodexError):
    """Raised when Codex output is invalid or cannot be parsed."""
    
    def __init__(self, reason: str, raw_output: str | None = None):
        self.raw_output = raw_output
        
        super().__init__(
            f"Failed to parse Codex output: {reason}",
            details=raw_output[:500] if raw_output else None
        )


class CodexAuthenticationError(CodexError):
    """Raised when Codex CLI is not properly authenticated."""
    
    def __init__(self):
        super().__init__(
            "Codex CLI is not authenticated",
            details=(
                "Please authenticate Codex CLI by running:\n"
                "  codex auth login\n\n"
                "This will open a browser window for authentication."
            )
        )


class CodexConfigurationError(CodexError):
    """Raised when Codex configuration is invalid."""
    
    def __init__(self, config_key: str, reason: str):
        super().__init__(
            f"Invalid Codex configuration for '{config_key}'",
            details=reason
        )
