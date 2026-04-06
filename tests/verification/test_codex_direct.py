#!/usr/bin/env python3
"""
Direct Codex execution test (bypassing Decision Agent).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cinder_cli.config import Config
from cinder_cli.executor.codex_integration_manager import (
    CodexIntegrationManager,
    TaskContext,
)

def main():
    print("=" * 60)
    print("Direct Codex Execution Test")
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
    print("\nExecuting task with Codex...")
    
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
    
    try:
        result = manager.execute_task(
            "Create a simple Python function that adds two numbers and returns the result",
            context,
            timeout=60,
            sandbox_mode="danger-full-access"
        )
        
        print("\n" + "=" * 60)
        print("Execution Result")
        print("=" * 60)
        print(f"Success: {result.success}")
        print(f"Exit code: {result.exit_code}")
        
        if result.error:
            print(f"\nError: {result.error}")
        
        if result.output:
            print(f"\nOutput:\n{result.output}")
        
        if result.metadata:
            print(f"\nMetadata: {result.metadata}")
        
        if result.success:
            print("\n✅ Codex execution successful!")
            print("\nGenerated code can be saved to a file if needed.")
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
    sys.exit(main())
