#!/usr/bin/env python3
"""
End-to-end test for Codex execution.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cinder_cli.config import Config
from cinder_cli.executor.codex_integration_manager import (
    CodexIntegrationManager,
    TaskContext,
)

def test_codex_execution():
    """Test basic Codex execution."""
    print("Testing Codex execution...")
    
    config = Config()
    
    if not config.is_codex_enabled():
        print("Codex is disabled. Skipping execution test.")
        return
    
    manager = CodexIntegrationManager(config)
    
    if not manager.is_available():
        print("Codex is not available. Skipping execution test.")
        return
    
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
        },
        quality_requirements={
            "quality_threshold": 0.8
        }
    )
    
    try:
        result = manager.execute_task(
            "Create a simple Python function that adds two numbers",
            context,
            timeout=60
        )
        
        print(f"\nExecution result:")
        print(f"  Success: {result.success}")
        print(f"  Exit code: {result.exit_code}")
        if result.error:
            print(f"  Error: {result.error}")
        if result.output:
            print(f"  Output preview: {result.output[:200]}...")
        
        if result.success:
            print("\n✅ Codex execution test passed!")
        else:
            print("\n⚠️ Codex execution completed with errors")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Codex execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Codex End-to-End Execution Test")
    print("=" * 60)
    
    test_codex_execution()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
