"""
Unit tests for Worker Agent.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch

from cinder_cli.agents.base import AgentState, Message, MessageType, Task
from cinder_cli.agents.worker_agent import WorkerAgent, WorkerOutput
from cinder_cli.config import Config


class TestWorkerAgent(unittest.TestCase):
    """Test cases for WorkerAgent."""
    
    def setUp(self):
        self.config = Config()
        self.config.set("model", "test-model")
        self.config.set("temperature", 0.2)
        
        self.worker = WorkerAgent(
            agent_id="test_worker",
            config=self.config,
            max_iterations=3,
        )
    
    def test_initialization(self):
        self.assertEqual(self.worker.agent_id, "test_worker")
        self.assertEqual(self.worker.agent_type, "worker")
        self.assertEqual(self.worker.state, AgentState.IDLE)
        self.assertEqual(self.worker.max_iterations, 3)
    
    def test_worker_output_to_dict(self):
        output = WorkerOutput(
            output_type="code",
            data={"code": "print('hello')"},
            quality_score=0.9,
            execution_time=1.5,
            iterations=2,
        )
        
        output_dict = output.to_dict()
        
        self.assertEqual(output_dict["output_type"], "code")
        self.assertEqual(output_dict["quality_score"], 0.9)
        self.assertEqual(output_dict["iterations"], 2)
    
    @patch('cinder_cli.agents.worker_agent.WorkerAgent._plan')
    @patch('cinder_cli.agents.worker_agent.WorkerAgent._generate')
    @patch('cinder_cli.agents.worker_agent.WorkerAgent._evaluate')
    def test_execute_task(self, mock_evaluate, mock_generate, mock_plan):
        mock_plan.return_value = {
            "type": "tasks",
            "goal": "test goal",
            "subtasks": [{"description": "test subtask"}],
        }
        
        mock_generate.return_value = {
            "type": "code",
            "code": "print('hello')",
        }
        
        mock_evaluate.return_value = {
            "quality_score": 0.9,
            "approved": True,
            "suggestions": [],
            "risks": [],
        }
        
        task = Task(
            task_id="test_task",
            description="Test task",
        )
        
        result = self.worker.execute(task)
        
        self.assertEqual(result.task_id, "test_task")
        self.assertEqual(result.output_type, "code")
        self.assertGreater(result.quality_score, 0.8)
        self.assertEqual(self.worker.state, AgentState.COMPLETE)
    
    @patch('cinder_cli.agents.worker_agent.WorkerAgent._plan')
    def test_execute_task_with_options(self, mock_plan):
        mock_plan.return_value = {
            "type": "options",
            "context": "Choose database",
            "options": [
                {"text": "PostgreSQL", "risk": "low"},
                {"text": "MongoDB", "risk": "medium"},
            ],
        }
        
        task = Task(
            task_id="test_task",
            description="Test task",
        )
        
        result = self.worker.execute(task)
        
        self.assertEqual(result.output_type, "options")
        self.assertIn("options", result.data)
        self.assertEqual(len(result.data["options"]), 2)
    
    def test_process_message_task(self):
        task_message = Message(
            message_type=MessageType.TASK,
            sender="decision_agent",
            receiver="test_worker",
            data={
                "task_id": "task1",
                "description": "Test task",
                "constraints": {},
            },
        )
        
        with patch.object(self.worker, 'execute') as mock_execute:
            mock_execute.return_value = Mock(
                task_id="task1",
                output_type="code",
                to_dict=lambda: {"output_type": "code"},
            )
            
            response = self.worker.process_message(task_message)
            
            self.assertIsNotNone(response)
            self.assertEqual(response.message_type, MessageType.RESULT)
            self.assertEqual(response.sender, "test_worker")
            self.assertEqual(response.receiver, "decision_agent")
    
    def test_get_execution_history(self):
        output1 = WorkerOutput(
            output_type="code",
            data={"code": "code1"},
            quality_score=0.8,
        )
        output2 = WorkerOutput(
            output_type="code",
            data={"code": "code2"},
            quality_score=0.9,
        )
        
        self.worker.execution_history = [output1, output2]
        
        history = self.worker.get_execution_history()
        self.assertEqual(len(history), 2)
        
        history = self.worker.get_execution_history(limit=1)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].quality_score, 0.9)
    
    def test_clear_history(self):
        self.worker.execution_history = [
            WorkerOutput(output_type="code", data={})
        ]
        
        self.worker.clear_history()
        self.assertEqual(len(self.worker.execution_history), 0)
    
    def test_get_status(self):
        status = self.worker.get_status()
        
        self.assertEqual(status["agent_id"], "test_worker")
        self.assertEqual(status["state"], "idle")
        self.assertIsNone(status["current_task"])
        self.assertEqual(status["execution_count"], 0)
        self.assertEqual(status["max_iterations"], 3)
    
    @patch('cinder_cli.agents.worker_agent.WorkerAgent._plan')
    @patch('cinder_cli.agents.worker_agent.WorkerAgent._generate')
    @patch('cinder_cli.agents.worker_agent.WorkerAgent._evaluate')
    def test_iteration_until_quality_threshold(
        self, mock_evaluate, mock_generate, mock_plan
    ):
        mock_plan.return_value = {
            "type": "tasks",
            "goal": "test",
            "subtasks": [{"description": "test"}],
        }
        
        mock_generate.return_value = {
            "type": "code",
            "code": "test code",
        }
        
        mock_evaluate.side_effect = [
            {"quality_score": 0.6, "approved": False},
            {"quality_score": 0.75, "approved": False},
            {"quality_score": 0.9, "approved": True},
        ]
        
        task = Task(task_id="test", description="test")
        result = self.worker.execute(task)
        
        self.assertEqual(result.quality_score, 0.9)
        self.assertEqual(mock_evaluate.call_count, 3)
    
    def test_error_handling(self):
        task = Task(
            task_id="error_task",
            description="Task that will fail",
        )
        
        with patch.object(self.worker, '_execute_task') as mock_execute:
            mock_execute.side_effect = Exception("Test error")
            
            result = self.worker.execute(task)
            
            self.assertEqual(result.output_type, "error")
            self.assertIn("error", result.data)
            self.assertEqual(self.worker.state, AgentState.ERROR)


if __name__ == "__main__":
    unittest.main()
