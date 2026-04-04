#!/usr/bin/env python3
"""Test script for PGE flow with logging."""

import sys
import os
sys.path.insert(0, '/Users/wangyuheng/code/github.com/wangyuheng/cinder')

from cinder_cli.config import Config
from cinder_cli.executor.task_planner import TaskPlanner
from cinder_cli.executor.code_generator import CodeGenerator
from cinder_cli.executor.reflection_engine import ReflectionEngine
import json

def test_plan_phase():
    """Test Plan phase with logging."""
    print("\n" + "="*60)
    print("PHASE 1: PLAN")
    print("="*60)
    
    config = Config()
    planner = TaskPlanner(config)
    
    goal = "创建一个简单的Python计算器程序，支持加减乘除"
    print(f"\nGoal: {goal}")
    
    plan = planner.decompose_goal_with_validation(goal, max_retries=1)
    
    print(f"\n✓ Plan generated:")
    print(f"  - Tasks: {len(plan.get('subtasks', []))}")
    print(f"  - Quality Score: {plan.get('validation', {}).get('quality_score', 0):.2f}")
    print(f"  - Attempts: {plan.get('attempts', 1)}")
    
    if plan.get('subtasks'):
        print(f"\n  Task list:")
        for i, task in enumerate(plan['subtasks'][:3], 1):
            print(f"    {i}. {task.get('description', 'N/A')}")
    
    return plan

def test_generation_phase(plan):
    """Test Generation phase with logging."""
    print("\n" + "="*60)
    print("PHASE 2: GENERATION")
    print("="*60)
    
    config = Config()
    generator = CodeGenerator(config)
    
    subtask = plan['subtasks'][0] if plan.get('subtasks') else None
    if not subtask:
        print("No subtasks to generate")
        return None
    
    print(f"\nGenerating code for: {subtask['description']}")
    
    result = generator.generate_with_iterations(
        subtask['description'],
        language=subtask.get('language', 'python'),
        max_iterations=2,
        quality_threshold=0.7
    )
    
    print(f"\n✓ Code generated:")
    print(f"  - Iterations: {result.get('iterations', 1)}")
    print(f"  - Final Score: {result.get('final_score', 0):.2f}")
    print(f"  - Quality Threshold Met: {result.get('quality_threshold_met', False)}")
    
    code = result.get('code', '')
    if code:
        print(f"\n  Generated code preview (first 200 chars):")
        print(f"  {code[:200]}...")
    
    return result

def test_evaluation_phase(code_result):
    """Test Evaluation phase with logging."""
    print("\n" + "="*60)
    print("PHASE 3: EVALUATION")
    print("="*60)
    
    if not code_result or not code_result.get('code'):
        print("No code to evaluate")
        return None
    
    config = Config()
    engine = ReflectionEngine(config)
    
    code = code_result['code']
    task = {"description": "Calculator program", "language": "python"}
    
    print(f"\nEvaluating generated code...")
    
    evaluation = engine.evaluate_comprehensive(code, task)
    
    print(f"\n✓ Evaluation complete:")
    print(f"  - Quality Score: {evaluation.get('quality_score', 0):.2f}")
    print(f"  - Approved: {evaluation.get('approved', False)}")
    print(f"  - Code Quality: {evaluation.get('code_quality', {}).get('overall_score', 0):.2f}")
    print(f"  - Soul Alignment: {evaluation.get('soul_alignment', {}).get('alignment_score', 0):.2f}")
    print(f"  - Risk Score: {evaluation.get('risk_assessment', {}).get('risk_score', 0):.2f}")
    
    if evaluation.get('suggestions'):
        print(f"\n  Suggestions:")
        for i, suggestion in enumerate(evaluation['suggestions'][:3], 1):
            print(f"    {i}. {suggestion}")
    
    return evaluation

def save_to_workspace(code_result, plan):
    """Save generated code to workspace."""
    print("\n" + "="*60)
    print("SAVING TO WORKSPACE")
    print("="*60)
    
    if not code_result or not code_result.get('code'):
        print("No code to save")
        return
    
    workspace_dir = "/Users/wangyuheng/code/github.com/wangyuheng/cinder/workspace"
    os.makedirs(workspace_dir, exist_ok=True)
    
    filename = "calculator.py"
    filepath = os.path.join(workspace_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write(code_result['code'])
    
    print(f"\n✓ File saved: {filepath}")
    print(f"  - Size: {len(code_result['code'])} bytes")
    
    return filepath

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Strict PGE Executor Flow")
    print("With Logging and Workspace Output")
    print("="*60)
    
    try:
        plan = test_plan_phase()
        code_result = test_generation_phase(plan)
        evaluation = test_evaluation_phase(code_result)
        filepath = save_to_workspace(code_result, plan)
        
        print("\n" + "="*60)
        print("✓ All Tests Passed!")
        print("="*60)
        
        if filepath:
            print(f"\nGenerated file: {filepath}")
            print(f"Workspace directory: /Users/wangyuheng/code/github.com/wangyuheng/cinder/workspace")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
