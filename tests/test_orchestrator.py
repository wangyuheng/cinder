"""
Unit tests for agent orchestration system.
"""

import unittest
from unittest.mock import Mock, MagicMock
import time

from cinder_cli.agents.base import (
    AgentState,
    BaseAgent,
    Message,
    MessageType,
    Result,
    Task,
)
from cinder_cli.agents.orchestrator import AgentOrchestrator


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def __init__(self, agent_id: str, agent_type: str = "mock"):
        super().__init__(agent_id, agent_type)
        self.processed_messages: list[Message] = []
        self.executed_tasks: list[Task] = []
    
    def process_message(self, message: Message) -> Message | None:
        self.processed_messages.append(message)
        if message.message_type == MessageType.QUESTION:
            return Message(
                message_type=MessageType.ANSWER,
                sender=self.agent_id,
                receiver=message.sender,
                data={"answer": "test_answer"},
            )
        return None
    
    def execute(self, task: Task) -> Result:
        self.executed_tasks.append(task)
        time.sleep(0.1)  # Simulate work
        return Result(
            task_id=task.task_id,
            output_type="test",
            data={"result": "success"},
            quality_score=0.9,
        )


class TestAgentOrchestrator(unittest.TestCase):
    """Test cases for AgentOrchestrator."""
    
    def setUp(self):
        self.orchestrator = AgentOrchestrator(max_concurrent_workers=2)
        self.agent1 = MockAgent("agent1", "decision")
        self.agent2 = MockAgent("agent2", "worker")
        
        self.orchestrator.register_agent(self.agent1)
        self.orchestrator.register_agent(self.agent2)
    
    def tearDown(self):
        self.orchestrator.shutdown()
    
    def test_register_agent(self):
        self.assertIn("agent1", self.orchestrator.agents)
        self.assertIn("agent2", self.orchestrator.agents)
    
    def test_unregister_agent(self):
        self.assertTrue(self.orchestrator.unregister_agent("agent1"))
        self.assertNotIn("agent1", self.orchestrator.agents)
        self.assertFalse(self.orchestrator.unregister_agent("nonexistent"))
    
    def test_send_message(self):
        message = self.orchestrator.send_message(
            sender_id="agent1",
            receiver_id="agent2",
            message_type=MessageType.TASK,
            data={"task": "test"},
        )
        
        self.assertEqual(message.sender, "agent1")
        self.assertEqual(message.receiver, "agent2")
        self.assertEqual(len(self.agent2.message_history), 1)
    
    def test_send_message_unknown_sender(self):
        with self.assertRaises(ValueError):
            self.orchestrator.send_message(
                sender_id="unknown",
                receiver_id="agent2",
                message_type=MessageType.TASK,
                data={},
            )
    
    def test_send_message_unknown_receiver(self):
        with self.assertRaises(ValueError):
            self.orchestrator.send_message(
                sender_id="agent1",
                receiver_id="unknown",
                message_type=MessageType.TASK,
                data={},
            )
    
    def test_broadcast_message(self):
        agent3 = MockAgent("agent3", "worker")
        self.orchestrator.register_agent(agent3)
        
        messages = self.orchestrator.broadcast_message(
            sender_id="agent1",
            message_type=MessageType.STATUS,
            data={"status": "test"},
        )
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(len(self.agent2.message_history), 1)
        self.assertEqual(len(agent3.message_history), 1)
    
    def test_broadcast_message_with_exclude(self):
        agent3 = MockAgent("agent3", "worker")
        self.orchestrator.register_agent(agent3)
        
        messages = self.orchestrator.broadcast_message(
            sender_id="agent1",
            message_type=MessageType.STATUS,
            data={"status": "test"},
            exclude=["agent3"],
        )
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(len(self.agent2.message_history), 1)
        self.assertEqual(len(agent3.message_history), 0)
    
    def test_delegate_task(self):
        task = Task(
            task_id="task1",
            description="Test task",
        )
        
        future = self.orchestrator.delegate_task(
            delegator_id="agent1",
            worker_id="agent2",
            task=task,
        )
        
        self.assertIn("task1", self.orchestrator.active_tasks)
        self.assertEqual(self.agent2.get_state(), AgentState.RUNNING)
        
        result = future.result(timeout=5)
        self.assertEqual(result.task_id, "task1")
        self.assertEqual(result.quality_score, 0.9)
    
    def test_get_task_result(self):
        task = Task(
            task_id="task1",
            description="Test task",
        )
        
        self.orchestrator.delegate_task(
            delegator_id="agent1",
            worker_id="agent2",
            task=task,
        )
        
        result = self.orchestrator.get_task_result("task1", timeout=5)
        self.assertEqual(result.task_id, "task1")
    
    def test_get_task_result_unknown_task(self):
        with self.assertRaises(ValueError):
            self.orchestrator.get_task_result("unknown_task")
    
    def test_get_agent_state(self):
        self.assertEqual(
            self.orchestrator.get_agent_state("agent1"),
            AgentState.IDLE
        )
        
        self.assertIsNone(
            self.orchestrator.get_agent_state("unknown")
        )
    
    def test_get_all_agent_states(self):
        states = self.orchestrator.get_all_agent_states()
        
        self.assertEqual(len(states), 2)
        self.assertEqual(states["agent1"], AgentState.IDLE)
        self.assertEqual(states["agent2"], AgentState.IDLE)
    
    def test_message_logging(self):
        self.orchestrator.send_message(
            sender_id="agent1",
            receiver_id="agent2",
            message_type=MessageType.TASK,
            data={"task": "test"},
        )
        
        logs = self.orchestrator.get_message_log()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["sender"], "agent1")
        self.assertEqual(logs[0]["receiver"], "agent2")
    
    def test_message_log_filtering(self):
        self.orchestrator.send_message(
            sender_id="agent1",
            receiver_id="agent2",
            message_type=MessageType.TASK,
            data={},
        )
        
        self.orchestrator.send_message(
            sender_id="agent2",
            receiver_id="agent1",
            message_type=MessageType.RESULT,
            data={},
        )
        
        logs = self.orchestrator.get_message_log(agent_id="agent1")
        self.assertEqual(len(logs), 2)
        
        logs = self.orchestrator.get_message_log(message_type=MessageType.TASK)
        self.assertEqual(len(logs), 1)
    
    def test_clear_message_log(self):
        self.orchestrator.send_message(
            sender_id="agent1",
            receiver_id="agent2",
            message_type=MessageType.TASK,
            data={},
        )
        
        self.orchestrator.clear_message_log()
        self.assertEqual(len(self.orchestrator.message_log), 0)
    
    def test_get_statistics(self):
        stats = self.orchestrator.get_statistics()
        
        self.assertEqual(stats["total_agents"], 2)
        self.assertEqual(stats["active_tasks"], 0)
        self.assertEqual(stats["max_concurrent_workers"], 2)
    
    def test_concurrent_task_limit(self):
        tasks = [
            Task(task_id=f"task{i}", description=f"Task {i}")
            for i in range(3)
        ]
        
        futures = []
        for task in tasks:
            future = self.orchestrator.delegate_task(
                delegator_id="agent1",
                worker_id="agent2",
                task=task,
            )
            futures.append(future)
        
        for future in futures:
            result = future.result(timeout=10)
            self.assertEqual(result.output_type, "test")


if __name__ == "__main__":
    unittest.main()
