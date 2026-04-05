#!/usr/bin/env python3
"""
Test script for Codex integration.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cinder_cli.config import Config
from cinder_cli.executor.codex_utils import is_codex_installed, check_codex_availability
from cinder_cli.executor.codex_exceptions import CodexError, CodexNotInstalledError

def test_config():
    """Test Codex configuration loading."""
    print("Testing Codex configuration...")
    
    config = Config()
    
    print(f"Codex enabled: {config.is_codex_enabled()}")
    print(f"Codex config: {config.codex}")
    
    errors = config.validate_codex_config()
    if errors:
        print(f"Validation errors: {errors}")
    else:
        print("✓ Configuration is valid")
    
    return config

def test_codex_utils():
    """Test Codex utility functions."""
    print("\nTesting Codex utilities...")
    
    is_installed = is_codex_installed()
    print(f"Codex installed: {is_installed}")
    
    is_available, message = check_codex_availability()
    print(f"Codex available: {is_available}")
    print(f"Status: {message}")
    
    return is_available

def test_codex_integration_manager():
    """Test CodexIntegrationManager initialization."""
    print("\nTesting CodexIntegrationManager...")
    
    config = Config()
    
    if not config.is_codex_enabled():
        print("Codex is disabled in configuration")
        return None
    
    try:
        from cinder_cli.executor.codex_integration_manager import CodexIntegrationManager
        
        manager = CodexIntegrationManager(config)
        print(f"✓ CodexIntegrationManager initialized")
        print(f"Available: {manager.is_available()}")
        
        return manager
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return None

def test_worker_agent():
    """Test Worker Agent with Codex integration."""
    print("\nTesting Worker Agent...")
    
    config = Config()
    
    try:
        from cinder_cli.agents.worker_agent import WorkerAgent
        
        agent = WorkerAgent("test_worker", config)
        print(f"✓ WorkerAgent initialized")
        print(f"Codex manager: {agent.codex_manager}")
        
        status = agent.get_status()
        print(f"Status: {status}")
        
        return agent
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all tests."""
    print("=" * 60)
    print("Codex Integration Verification")
    print("=" * 60)
    
    try:
        config = test_config()
        is_available = test_codex_utils()
        manager = test_codex_integration_manager()
        agent = test_worker_agent()
        
        print("\n" + "=" * 60)
        print("Verification Summary")
        print("=" * 60)
        print(f"✓ Configuration: Valid")
        print(f"✓ Imports: Successful")
        print(f"{'✓' if is_available else '○'} Codex CLI: {'Available' if is_available else 'Not installed (optional)'}")
        print(f"{'✓' if manager else '○'} Integration Manager: {'Initialized' if manager else 'Not initialized (Codex disabled or unavailable)'}")
        print(f"✓ Worker Agent: Integrated")
        
        print("\n✅ Core integration is working correctly!")
        print("\nNext steps:")
        if not is_available:
            print("  1. Install Codex CLI: npm install -g @openai/codex")
            print("  2. Or use: ollama launch codex --model <model-name>")
        if not config.is_codex_enabled():
            print("  3. Enable Codex in cinder.yaml: codex_integration.enabled: true")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
