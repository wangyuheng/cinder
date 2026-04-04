"""
Backward compatibility layer for old cli.py and chat.py scripts.
This module provides compatibility wrappers that delegate to the new CLI.
"""

from __future__ import annotations

import sys
import warnings


def run_cli_compat() -> None:
    """Compatibility wrapper for old cli.py usage."""
    warnings.warn(
        "Direct use of cli.py is deprecated. Please use 'cinder init' instead. "
        "Run 'cinder --help' for more information.",
        DeprecationWarning,
        stacklevel=2,
    )

    from cinder_cli.cli import cli

    args = sys.argv[1:]
    args = ["init"] + args

    sys.argv = [sys.argv[0]] + args
    cli()


def run_chat_compat() -> None:
    """Compatibility wrapper for old chat.py usage."""
    warnings.warn(
        "Direct use of chat.py is deprecated. Please use 'cinder chat' instead. "
        "Run 'cinder --help' for more information.",
        DeprecationWarning,
        stacklevel=2,
    )

    from cinder_cli.cli import cli

    args = sys.argv[1:]
    args = ["chat"] + args

    sys.argv = [sys.argv[0]] + args
    cli()


if __name__ == "__main__":
    if "cli" in sys.argv[0]:
        run_cli_compat()
    elif "chat" in sys.argv[0]:
        run_chat_compat()
