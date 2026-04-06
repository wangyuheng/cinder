#!/usr/bin/env python3
"""
Test script for Codex streaming output.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cinder_cli.config import Config
from cinder_cli.executor.codex_integration_manager import (
    CodexIntegrationManager,
    TaskContext,
)


def test_streaming_output():
    """Test Codex execution with streaming output."""
    print("=" * 60)
    print("Codex Streaming Output Test")
    print("=" * 60)
    
    config = Config()
    
    if not config.is_codex_enabled():
        print("✗ Codex is disabled")
        return 1
    
    manager = CodexIntegrationManager(config)
    
    if not manager.is_available():
        print("✗ Codex is not available")
        return 1
    
    print("✓ Codex is enabled and available")
    print("\nExecuting task with streaming output...\n")
    
    context = TaskContext(
        soul_profile={
            "traits": {
                "risk_tolerance": "moderate",
                "communication_style": "concise"
            }
        },
        decision_context={
            "goal_type": "code_generation",
            "key_features": ["simple", "readable"]
        }
    )
    
    def output_callback(line: str, stream_type: str):
        """Callback for streaming output."""
        if stream_type == "stdout":
            print(f"\033[92m{line}\033[0m", end='')
        elif stream_type == "stderr":
            print(f"\033[93m{line}\033[0m", end='')
        else:
            print(f"\033[94m{line}\033[0m", end='')
    
    try:
        result = manager.execute_task(
            "Create a simple Python function that adds two numbers",
            context,
            stream_output=True,
            output_callback=output_callback,
            timeout=60
        )
        
        print("\n" + "=" * 60)
        print("Execution Result")
        print("=" * 60)
        print(f"Success: {result.success}")
        print(f"Exit code: {result.exit_code}")
        
        if result.error:
            print(f"\nError: {result.error}")
        
        if result.success:
            print("\n✅ Codex streaming test passed!")
            return 0
        else:
            print("\n⚠️ Codex execution completed with errors")
            return 1
            
    except Exception as e:
        print(f"\n✗ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_streaming_output())
