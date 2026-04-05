"""
Example: Simple Task Execution

This example demonstrates how to use the new dual-agent architecture
for simple task execution.
"""

from cinder_cli.config import Config
from cinder_cli.executor.refactored_autonomous_executor import AutonomousExecutor


def example_simple_task():
    """Execute a simple task using the new architecture."""
    
    # Initialize configuration
    config = Config()
    config.set("model", "qwen3.5:0.8b")
    config.set("soul_path", "soul.md")
    
    # Create executor with new architecture
    executor = AutonomousExecutor(config, legacy_mode=False)
    
    # Define a simple goal
    goal = "Create a Python function that calculates the factorial of a number"
    
    # Execute the goal
    result = executor.execute(goal)
    
    # Check result
    if result["status"] == "success":
        print("✓ Task completed successfully!")
        
        # Access generated code
        worker_result = result["worker_result"]
        if worker_result["output_type"] == "code":
            code = worker_result["data"]["code"]
            quality_score = worker_result["quality_score"]
            
            print(f"\nGenerated Code (Quality: {quality_score:.2f}):")
            print(code)
        
        # View decision history
        print("\nDecision History:")
        for decision in result["decision_history"]:
            print(f"  - {decision['decision_type']}: {decision['reasoning']}")
    
    # Cleanup
    executor.shutdown()
    
    return result


def example_with_constraints():
    """Execute a task with specific constraints."""
    
    config = Config()
    executor = AutonomousExecutor(config, legacy_mode=False)
    
    goal = "Create a REST API endpoint"
    constraints = {
        "language": "python",
        "framework": "fastapi",
        "database": "postgresql",
        "authentication": "jwt",
    }
    
    result = executor.execute(goal, constraints=constraints)
    
    if result["status"] == "success":
        print("✓ API endpoint created with constraints!")
        print(f"Quality Score: {result['worker_result']['quality_score']:.2f}")
    
    executor.shutdown()
    return result


def example_with_quality_threshold():
    """Execute a task with custom quality threshold."""
    
    config = Config()
    config.set("quality_threshold", 0.9)  # Higher quality requirement
    
    executor = AutonomousExecutor(config, legacy_mode=False)
    
    goal = "Create a production-ready authentication system"
    
    result = executor.execute(goal)
    
    if result["status"] == "success":
        quality = result["worker_result"]["quality_score"]
        print(f"✓ Authentication system created (Quality: {quality:.2f})")
        
        # Check if quality threshold was met
        if quality >= 0.9:
            print("  Quality threshold met!")
        else:
            print("  Warning: Quality below threshold")
    
    executor.shutdown()
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: Simple Task")
    print("=" * 60)
    example_simple_task()
    
    print("\n" + "=" * 60)
    print("Example 2: Task with Constraints")
    print("=" * 60)
    example_with_constraints()
    
    print("\n" + "=" * 60)
    print("Example 3: Task with Quality Threshold")
    print("=" * 60)
    example_with_quality_threshold()
