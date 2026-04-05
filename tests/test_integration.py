"""
Integration tests for Decision Agent + Worker Agent.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import tempfile
from pathlib import Path

from cinder_cli.agents.base import Task
from cinder_cli.agents.decision_agent import DecisionAgent
from cinder_cli.agents.worker_agent import WorkerAgent
from cinder_cli.agents.orchestrator import AgentOrchestrator
from cinder_cli.agents.context_manager import ContextManager
from cinder_cli.config import Config


class TestDecisionWorkerIntegration(unittest.TestCase):
    """Integration tests for Decision and Worker agents."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_context.db"
        
        self.config = Config()
        self.config.set("model", "test-model")
        
        self.soul_meta = {
            "traits": {
                "risk_tolerance": 50,
                "structure": 50,
                "detail_orientation": 50,
            }
        }
        
        self.context_manager = ContextManager(
            db_path=self.db_path,
            user_id="test_user",
            project_id="test_project",
        )
        
        self.orchestrator = AgentOrchestrator(max_concurrent_workers=2)
        
        self.decision_agent = DecisionAgent(
            agent_id="decision_agent",
            config=self.config,
            soul_meta=self.soul_meta,
            context_manager=self.context_manager,
        )
        
        self.worker_agent = WorkerAgent(
            agent_id="worker_agent",
            config=self.config,
        )
        
        self.decision_agent.set_worker(self.worker_agent)
        
        self.orchestrator.register_agent(self.decision_agent)
        self.orchestrator.register_agent(self.worker_agent)
    
    def tearDown(self):
        self.orchestrator.shutdown()
        if self.db_path.exists():
            self.db_path.unlink()
    
    @patch('cinder_cli.agents.worker_agent.WorkerAgent._execute_task')
    def test_full_execution_flow(self, mock_execute):
        mock_execute.return_value = Mock(
            output_type="code",
            data={"code": "print('hello')"},
            quality_score=0.9,
            to_dict=lambda: {
                "output_type": "code",
                "data": {"code": "print('hello')"},
                "quality_score": 0.9,
            },
        )
        
        task = Task(
            task_id="integration_test",
            description="Create a simple function",
        )
        
        result = self.decision_agent.execute(task)
        
        self.assertEqual(result["status"], "complete")
        self.assertIn("worker_result", result)
        self.assertGreater(len(result["decision_history"]), 0)
    
    @patch('cinder_cli.agents.worker_agent.WorkerAgent._execute_task')
    def test_decision_loop_with_improvement(self, mock_execute):
        mock_execute.side_effect = [
            Mock(
                output_type="code",
                data={"code": "code_v1"},
                quality_score=0.6,
                to_dict=lambda: {"output_type": "code", "data": {"code": "code_v1"}, "quality_score": 0.6},
            ),
            Mock(
                output_type="code",
                data={"code": "code_v2"},
                quality_score=0.85,
                to_dict=lambda: {"output_type": "code", "data": {"code": "code_v2"}, "quality_score": 0.85},
            ),
        ]
        
        task = Task(
            task_id="improvement_test",
            description="Create function that needs improvement",
        )
        
        result = self.decision_agent.execute(task)
        
        self.assertEqual(result["status"], "complete")
        self.assertGreaterEqual(result["worker_result"]["quality_score"], 0.8)
    
    def test_orchestrator_message_passing(self):
        from cinder_cli.agents.base import MessageType
        
        message = self.orchestrator.send_message(
            sender_id="decision_agent",
            receiver_id="worker_agent",
            message_type=MessageType.TASK,
            data={"task_id": "test", "description": "test task"},
        )
        
        self.assertEqual(message.sender, "decision_agent")
        self.assertEqual(message.receiver, "worker_agent")
        self.assertEqual(len(self.worker_agent.message_history), 1)
    
    def test_context_persistence_across_decisions(self):
        self.context_manager.set("test_key", "test_value")
        self.context_manager.save()
        
        self.context_manager.set("another_key", "another_value")
        
        value = self.context_manager.get("test_key")
        self.assertEqual(value, "test_value")


class TestTechChoiceScenario(unittest.TestCase):
    """Test technology choice decision scenarios."""
    
    def setUp(self):
        self.config = Config()
        self.soul_meta = {
            "traits": {
                "risk_tolerance": 30,  # Conservative
            }
        }
    
    def test_conservative_tech_choice(self):
        from cinder_cli.extended_proxy_decision import ExtendedProxyDecisionMaker, DecisionType
        
        decision_maker = ExtendedProxyDecisionMaker(self.soul_meta)
        
        options = [
            {"text": "PostgreSQL", "risk": "low", "performance": "high"},
            {"text": "MongoDB", "risk": "medium", "performance": "high"},
            {"text": "Redis", "risk": "high", "performance": "very_high"},
        ]
        
        result = decision_maker.make_decision(
            context="Choose database for production",
            options=options,
            decision_type=DecisionType.TECH_CHOICE,
        )
        
        self.assertEqual(result["decision"]["text"], "PostgreSQL")
        self.assertGreater(result["confidence"], 0.5)


class TestArchitectureDecisionScenario(unittest.TestCase):
    """Test architecture decision scenarios."""
    
    def setUp(self):
        self.config = Config()
        self.soul_meta = {
            "traits": {
                "structure": 70,  # Prefers structure
            }
        }
    
    def test_structured_architecture_choice(self):
        from cinder_cli.extended_proxy_decision import ExtendedProxyDecisionMaker, DecisionType
        
        decision_maker = ExtendedProxyDecisionMaker(self.soul_meta)
        
        options = [
            {"text": "Monolithic", "complexity": "low", "scalability": "medium"},
            {"text": "Microservices", "complexity": "high", "scalability": "high"},
            {"text": "Modular Monolith", "complexity": "medium", "scalability": "medium"},
        ]
        
        result = decision_maker.make_decision(
            context="Choose architecture for enterprise app",
            options=options,
            decision_type=DecisionType.ARCHITECTURE,
        )
        
        self.assertIn(result["decision"]["text"], ["Microservices", "Modular Monolith"])


if __name__ == "__main__":
    unittest.main()
