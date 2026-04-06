#!/usr/bin/env python3
"""Test hierarchical tracing with task, phase, and LLM spans."""

import sys
import time
sys.path.insert(0, "/Users/wangyuheng/code/github.com/wangyuheng/cinder")

from cinder_cli.tracing.config import TracingConfig
from cinder_cli.tracing.phoenix_tracer import PhoenixTracer
from cinder_cli.tracing.agent_tracer import AgentTracer
from cinder_cli.tracing.llm_tracer import LLMTracer

print("="*60)
print("Testing Hierarchical Tracing")
print("="*60)

print(f"\n1. Initializing tracers...")
config = TracingConfig(
    enabled=True,
    phoenix_endpoint="http://localhost:6006",
)

phoenix_tracer = PhoenixTracer(config, service_name="cinder")
agent_tracer = AgentTracer(phoenix_tracer)
llm_tracer = LLMTracer(phoenix_tracer)

print(f"\n2. Creating hierarchical trace...")

# Task level (root span)
with agent_tracer.trace_agent_execution(
    agent_id="test_agent",
    agent_role="coordinator",
    goal="Create a Python Hello World program",
    mode="auto",
) as task_record:
    
    print(f"   [Task] {task_record.task_id}")
    
    # Phase 1: Goal Understanding
    with agent_tracer.trace_phase(
        phase_name="goal_understanding",
        parent_task_id=task_record.task_id,
    ) as phase_record:
        
        print(f"   [Phase] goal_understanding")
        
        # LLM call within phase
        with llm_tracer.trace_llm_call(
            model="qwen3.5:0.8b",
            prompt="Understand the goal: Create a Python Hello World program",
            system_prompt="You are a helpful coding assistant.",
            agent_id="test_agent",
            phase="goal_understanding",
        ) as llm_record:
            
            print(f"   [LLM] Understanding goal...")
            time.sleep(0.1)
            
            llm_tracer.record_response(
                llm_record,
                response="The goal is to create a simple Python script that prints 'Hello World'",
                input_tokens=50,
                output_tokens=30,
            )
    
    # Phase 2: Task Decomposition
    with agent_tracer.trace_phase(
        phase_name="task_decomposition",
        parent_task_id=task_record.task_id,
    ) as phase_record:
        
        print(f"   [Phase] task_decomposition")
        
        # LLM call within phase
        with llm_tracer.trace_llm_call(
            model="qwen3.5:0.8b",
            prompt="Decompose the task into subtasks",
            system_prompt="You are a helpful coding assistant.",
            agent_id="test_agent",
            phase="task_decomposition",
        ) as llm_record:
            
            print(f"   [LLM] Decomposing tasks...")
            time.sleep(0.1)
            
            llm_tracer.record_response(
                llm_record,
                response="1. Create a Python file\n2. Write the print statement\n3. Test the script",
                input_tokens=60,
                output_tokens=40,
            )
    
    # Phase 3: Code Generation
    with agent_tracer.trace_phase(
        phase_name="code_generation",
        parent_task_id=task_record.task_id,
    ) as phase_record:
        
        print(f"   [Phase] code_generation")
        
        # LLM call within phase
        with llm_tracer.trace_llm_call(
            model="qwen3.5:0.8b",
            prompt="Generate Python code for Hello World",
            system_prompt="You are a helpful coding assistant.",
            agent_id="test_agent",
            phase="code_generation",
        ) as llm_record:
            
            print(f"   [LLM] Generating code...")
            time.sleep(0.1)
            
            llm_tracer.record_response(
                llm_record,
                response="print('Hello World')",
                input_tokens=40,
                output_tokens=20,
            )

print(f"\n3. Waiting for data to be exported...")
time.sleep(3)

print(f"\n4. Force flushing...")
if phoenix_tracer.tracer_provider:
    phoenix_tracer.tracer_provider.force_flush()
    time.sleep(2)

print(f"\n✓ Test completed!")

print(f"\n现在请在 Phoenix UI 中检查：")
print(f"1. 打开 http://localhost:6006")
print(f"2. 选择 'cinder' 项目")
print(f"3. 查看最新的 trace")
print(f"4. 应该看到分层结构：")
print(f"   - Task span (root)")
print(f"     - Phase span: goal_understanding")
print(f"       - LLM span")
print(f"     - Phase span: task_decomposition")
print(f"       - LLM span")
print(f"     - Phase span: code_generation")
print(f"       - LLM span")
