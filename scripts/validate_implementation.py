"""
Simple validation script to check code structure without running tests.
"""

import ast
import sys
from pathlib import Path


def validate_python_file(filepath: Path) -> tuple[bool, str]:
    """Validate a Python file by parsing its AST."""
    try:
        with open(filepath, encoding='utf-8') as f:
            code = f.read()
        
        ast.parse(code)
        return True, f"✓ {filepath.name}"
    except SyntaxError as e:
        return False, f"✗ {filepath.name}: {e}"
    except Exception as e:
        return False, f"✗ {filepath.name}: {e}"


def main():
    """Validate all new agent files."""
    agent_files = [
        "cinder_cli/agents/base.py",
        "cinder_cli/agents/context.py",
        "cinder_cli/agents/context_manager.py",
        "cinder_cli/agents/orchestrator.py",
        "cinder_cli/agents/worker_agent.py",
        "cinder_cli/agents/decision_agent.py",
        "cinder_cli/extended_proxy_decision.py",
        "cinder_cli/monitoring/performance_monitor.py",
        "cinder_cli/executor/refactored_autonomous_executor.py",
    ]
    
    test_files = [
        "tests/test_context_manager.py",
        "tests/test_orchestrator.py",
        "tests/test_worker_agent.py",
        "tests/test_decision_agent.py",
        "tests/test_integration.py",
    ]
    
    print("=" * 60)
    print("Validating Agent Architecture Implementation")
    print("=" * 60)
    
    all_valid = True
    
    print("\nCore Agent Files:")
    for filepath in agent_files:
        path = Path(filepath)
        if path.exists():
            valid, message = validate_python_file(path)
            print(f"  {message}")
            if not valid:
                all_valid = False
        else:
            print(f"  ✗ {filepath}: File not found")
            all_valid = False
    
    print("\nTest Files:")
    for filepath in test_files:
        path = Path(filepath)
        if path.exists():
            valid, message = validate_python_file(path)
            print(f"  {message}")
            if not valid:
                all_valid = False
        else:
            print(f"  ✗ {filepath}: File not found")
            all_valid = False
    
    print("\n" + "=" * 60)
    if all_valid:
        print("✓ All files validated successfully!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some files have issues")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
