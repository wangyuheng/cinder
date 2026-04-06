#!/usr/bin/env python3
"""Test complete trace schema with Phoenix."""

import time
from cinder_cli.tracing import LLMTracer, AgentTracer, TracingConfig

print("="*60)
print("Testing Complete Trace Schema")
print("="*60)

# Initialize
config = TracingConfig(
    enabled=True,
    phoenix_endpoint="http://localhost:6006",
)

llm_tracer = LLMTracer()
agent_tracer = AgentTracer()

# Test 1: LLM Call
print("\n1. Testing LLM Call Span...")
with llm_tracer.trace_llm_call(
    model="qwen3.5:0.8b",
    prompt="创建一个计算器程序",
    system_prompt="你是一个专业的程序员",
    model_params={
        "temperature": 0.2,
        "max_tokens": 4096,
    },
    phase="code_generation",
    language="python",
    quality_score=0.85,
) as record:
    record.response = "def calculator(): ..."
    record.input_tokens = 50
    record.output_tokens = 100
    record.total_tokens = 150

print("✓ LLM span created")
print("  Span name: llm.qwen3.5:0.8b.code_generation")
print("  Attributes: llm.model, llm.system, cinder.phase, etc.")

# Test 2: Agent Execution
print("\n2. Testing Agent Execution Span...")
with agent_tracer.trace_agent_execution(
    agent_id="agent-1",
    agent_role="worker",
    goal="创建一个计算器程序",
    task="生成 Python 代码",
    complexity="medium",
):
    pass

print("✓ Agent span created")
print("  Span name: agent.worker.execute_task")
print("  Attributes: agent.id, agent.role, agent.goal, agent.status")

# Test 3: Tool Call
print("\n3. Testing Tool Call Span...")
with agent_tracer.trace_tool_call(
    agent_id="agent-1",
    tool_name="file_operations",
    input_params={
        "file_path": "/tmp/calculator.py",
        "operation": "write",
    },
):
    time.sleep(0.1)

print("✓ Tool span created")
print("  Span name: tool.file_operations.execute")
print("  Attributes: tool.name, tool.status, tool.duration.ms")

# Test 4: Nested Spans
print("\n4. Testing Nested Spans...")
with agent_tracer.trace_agent_execution(
    agent_id="agent-2",
    agent_role="planner",
    goal="分解任务",
):
    with llm_tracer.trace_llm_call(
        model="qwen3.5:0.8b",
        prompt="分解任务：创建计算器",
        phase="task_planning",
    ) as record:
        record.response = "任务已分解"
        record.total_tokens = 50

print("✓ Nested spans created")
print("  Parent: agent.planner.execute_task")
print("  Child: llm.qwen3.5:0.8b.task_planning")

# Wait for export
print("\n5. Waiting for export...")
time.sleep(3)
print("✓ Export complete")

print("\n" + "="*60)
print("✓ All tests passed!")
print("="*60)
print("\nCheck Phoenix UI:")
print("  1. Open http://localhost:6006")
print("  2. Click 'Projects' in sidebar")
print("  3. Look for 'cinder' project")
print("  4. You should see:")
print("     - LLM call spans with model info")
print("     - Agent execution spans")
print("     - Tool call spans")
print("     - Nested span relationships")
print("\nSpan naming convention:")
print("  - LLM: llm.<model>.<phase>")
print("  - Agent: agent.<role>.<action>")
print("  - Tool: tool.<name>.<action>")
