#!/usr/bin/env python3
"""
Simple Codex integration verification script.
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_codex_cli():
    """Test if Codex CLI is available."""
    print("\n1. Testing Codex CLI...")
    
    try:
        result = subprocess.run(
            ["codex", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"   ✓ Codex CLI available: {result.stdout.strip()}")
            return True
        else:
            print(f"   ✗ Codex CLI error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("   ✗ Codex CLI not found")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_config():
    """Test Codex configuration."""
    print("\n2. Testing Codex configuration...")
    
    from cinder_cli.config import Config
    
    config = Config()
    
    print(f"   Codex enabled: {config.is_codex_enabled()}")
    print(f"   Configuration: {config.codex}")
    
    errors = config.validate_codex_config()
    if errors:
        print(f"   ✗ Validation errors: {errors}")
        return False
    else:
        print("   ✓ Configuration valid")
        return True

def test_integration_manager():
    """Test CodexIntegrationManager initialization."""
    print("\n3. Testing CodexIntegrationManager...")
    
    from cinder_cli.config import Config
    from cinder_cli.executor.codex_integration_manager import CodexIntegrationManager
    
    config = Config()
    
    if not config.is_codex_enabled():
        print("   ○ Codex disabled, skipping")
        return None
    
    try:
        manager = CodexIntegrationManager(config)
        print(f"   ✓ Manager initialized")
        print(f"   Available: {manager.is_available()}")
        return manager
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return None

def test_worker_agent():
    """Test Worker Agent integration."""
    print("\n4. Testing Worker Agent integration...")
    
    from cinder_cli.config import Config
    from cinder_cli.agents.worker_agent import WorkerAgent
    
    config = Config()
    
    try:
        agent = WorkerAgent("test", config)
        print(f"   ✓ Worker Agent initialized")
        print(f"   Codex manager: {agent.codex_manager is not None}")
        
        if agent.codex_manager:
            print(f"   Codex available: {agent.codex_manager.is_available()}")
        
        return agent
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_simple_codex_call():
    """Test a simple Codex CLI call."""
    print("\n5. Testing simple Codex CLI call...")
    
    try:
        result = subprocess.run(
            ["codex", "exec", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("   ✓ Codex exec command available")
            print(f"   Help preview: {result.stdout[:200]}...")
            return True
        else:
            print(f"   ✗ Codex exec error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Codex Integration Verification")
    print("=" * 60)
    
    results = {
        "Codex CLI": test_codex_cli(),
        "Configuration": test_config(),
        "Integration Manager": test_integration_manager() is not None,
        "Worker Agent": test_worker_agent() is not None,
        "Codex Exec": test_simple_codex_call(),
    }
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"{status} {name}: {'Pass' if passed else 'Fail'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ All tests passed!")
        print("\nCodex integration is working correctly.")
        print("You can now use Codex for code generation tasks.")
    else:
        print("\n⚠️ Some tests failed")
        print("\nPlease check the errors above and fix them.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
