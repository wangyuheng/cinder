"""
Codex CLI utility functions.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Optional


def is_codex_installed() -> bool:
    """
    Check if Codex CLI is installed and available.
    
    Returns:
        True if Codex CLI is installed, False otherwise.
    """
    return shutil.which("codex") is not None


def get_codex_version() -> Optional[str]:
    """
    Get the version of installed Codex CLI.
    
    Returns:
        Version string if Codex is installed, None otherwise.
    """
    if not is_codex_installed():
        return None
    
    try:
        result = subprocess.run(
            ["codex", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass
    
    return None


def check_codex_availability() -> tuple[bool, str]:
    """
    Check if Codex CLI is available and return detailed status.
    
    Returns:
        Tuple of (is_available, status_message)
    """
    if not is_codex_installed():
        return (
            False,
            "Codex CLI is not installed. Please install it using:\n"
            "  npm install -g @openai/codex\n"
            "  or\n"
            "  ollama launch codex --model <model-name>\n"
            "See https://github.com/openai/codex for more information."
        )
    
    version = get_codex_version()
    if version:
        return True, f"Codex CLI is available (version: {version})"
    else:
        return True, "Codex CLI is available (version unknown)"


def validate_codex_authentication() -> tuple[bool, str]:
    """
    Validate that Codex CLI is properly authenticated.
    
    Returns:
        Tuple of (is_authenticated, status_message)
    """
    if not is_codex_installed():
        return False, "Codex CLI is not installed"
    
    try:
        result = subprocess.run(
            ["codex", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "Codex CLI is authenticated"
        else:
            return (
                False,
                "Codex CLI is not authenticated. Please run:\n"
                "  codex auth login"
            )
    except subprocess.TimeoutExpired:
        return False, "Codex CLI authentication check timed out"
    except subprocess.SubprocessError as e:
        return False, f"Failed to check Codex authentication: {e}"
