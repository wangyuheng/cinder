"""
Unit tests for Decision Agent.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import tempfile
from pathlib import Path

from cinder_cli.agents.base import AgentState, Message, MessageType, Task
from cinder_cli.agents.decision_agent import DecisionAgent, DecisionState
from cinder_cli.agents.context_manager import ContextManager
from cinder_cli.config import Config


class TestDecisionAgent(unittest.TestCase):
    """Test cases for DecisionAgent."""
    
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
        
        self.decision_agent = DecisionAgent(
            agent_id="test_decision",
            config=self.config,
            soul_meta=self.soul_meta,
            context_manager=self.context_manager,
        )
    
    def tearDown(self):
        if self.db_path.exists():
            self.db_path.unlink()
    
    def test_initialization(self):
        self.assertEqual(self.decision_agent.agent_id, "test_decision")
        self.assertEqual(self.decision_agent.agent_type, "decision")
        self.assertEqual(self.decision_agent.state, AgentState.IDLE)
        self.assertEqual(self.decision_agent.state_machine, DecisionState.UNDERSTAND)
        self.assertEqual(self.decision_agent.max_decision_loops, 10)
    
    def test_state_machine_transitions(self):
        self.assertEqual(self.decision_agent.state_machine, DecisionState.UNDERSTAND)
        
        self.decision_agent.state_machine = DecisionState.ANALYZE
        self.assertEqual(self.decision_agent.state_machine, DecisionState.ANALYZE)
        
        self.decision_agent.state_machine = DecisionState.DECIDE
        self.assertEqual(self.decision_agent.state_machine, DecisionState.DECIDE)
    
    @patch('cinder_cli.agents.decision_agent.DecisionAgent._understand_intent')
    @patch('cinder_cli.agents.decision_agent.DecisionAgent._analyze_situation')
    @patch('cinder_cli.agents.decision_agent.DecisionAgent._make_decision')
    @patch('cinder_cli.agents.decision_agent.DecisionAgent._delegate_to_worker')
    @patch('cinder_cli.agents.decision_agent.DecisionAgent._evaluate_result')
    def test_process_goal(
        self,
        mock_evaluate,
        mock_delegate,
        mock_decision,
        mock_analyze,
        mock_understand,
    ):
        mock_understand.return_value = None
        mock_analyze.return_value = None
        mock_decision.return_value = Mock(decision_type="code_accept", confidence=0.9)
        mock_delegate.return_value = {"quality_score": 0.9}
        mock_evaluate.return_value = False
        
        task = Task(
            task_id="test_task",
            description="Test goal",
        )
        
        result = self.decision_agent.execute(task)
        
        self.assertEqual(result["status"], "complete")
        self.assertIn("worker_result", result)
    
    def test_understand_intent(self):
        task = Task(
            task_id="test",
            description="Create a REST API",
        )
        
        self.decision_agent.current_task = task
        self.decision_agent._understand_intent()
        
        understanding = self.context_manager.get("understanding")
        self.assertIsNotNone(understanding)
        self.assertEqual(self.decision_agent.state_machine, DecisionState.ANALYZE)
    
    def test_analyze_situation(self):
        self.context_manager.set(
            "worker_result",
            {"quality_score": 0.85, "output_type": "code"},
        )
        
        self.decision_agent.state_machine = DecisionState.ANALYZE
        self.decision_agent._analyze_situation()
        
        analysis = self.context_manager.get("analysis")
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis["quality_score"], 0.85)
        self.assertEqual(self.decision_agent.state_machine, DecisionState.DECIDE)
    
    def test_make_decision_code_accept(self):
        self.context_manager.set(
            "analysis",
            {"quality_score": 0.9, "needs_improvement": False},
        )
        
        self.decision_agent.state_machine = DecisionState.DECIDE
        decision = self.decision_agent._make_decision()
        
        self.assertEqual(decision.decision_type, "code_accept")
        self.assertGreater(decision.confidence, 0.8)
    
    def test_make_decision_improve(self):
        self.context_manager.set(
            "analysis",
            {"quality_score": 0.6, "needs_improvement": True},
        )
        
        self.decision_agent.state_machine = DecisionState.DECIDE
        decision = self.decision_agent._make_decision()
        
        self.assertEqual(decision.decision_type, "improve")
        self.assertLess(decision.confidence, 0.8)
    
    def test_decision_loop_protection(self):
        self.decision_agent.max_decision_loops = 3
        
        for i in range(5):
            self.decision_agent.decision_loop_count += 1
            
            if self.decision_agent.decision_loop_count >= self.decision_agent.max_decision_loops:
                break
        
        self.assertEqual(self.decision_agent.decision_loop_count, 3)
    
    def test_detect_repeated_decision(self):
        decision1 = Mock(
            decision_type="improve",
            confidence=0.7,
            context="test",
        )
        
        decision2 = Mock(
            decision_type="improve",
            confidence=0.7,
            context="test",
        )
        
        self.decision_agent.decision_history = [decision1]
        
        is_repeated = self.decision_agent._is_repeated_decision(decision2)
        self.assertTrue(is_repeated)
    
    def test_explain_decision(self):
        decision = Mock(
            decision_id="dec_1",
            decision_type="code_accept",
            context="Test context",
            confidence=0.9,
            reasoning="High quality score",
            soul_rules_applied=["risk_tolerance"],
        )
        
        self.decision_agent.decision_history = [decision]
        
        explanation = self.decision_agent.explain_decision("dec_1")
        
        self.assertIsNotNone(explanation)
        self.assertEqual(explanation["decision_type"], "code_accept")
        self.assertIn("reasoning", explanation)
    
    def test_get_decision_history(self):
        decision1 = Mock(decision_id="dec_1", to_dict=lambda: {"id": "dec_1"})
        decision2 = Mock(decision_id="dec_2", to_dict=lambda: {"id": "dec_2"})
        
        self.decision_agent.decision_history = [decision1, decision2]
        
        history = self.decision_agent.get_decision_history()
        self.assertEqual(len(history), 2)
        
        history = self.decision_agent.get_decision_history(limit=1)
        self.assertEqual(len(history), 1)
    
    def test_process_message(self):
        message = Message(
            message_type=MessageType.RESULT,
            sender="worker",
            receiver="test_decision",
            data={"quality_score": 0.9},
        )
        
        response = self.decision_agent.process_message(message)
        
        self.assertIsNone(response)
        self.assertEqual(len(self.decision_agent.message_history), 1)
    
    def test_get_statistics(self):
        stats = self.decision_agent.get_statistics()
        
        self.assertEqual(stats["agent_id"], "test_decision")
        self.assertEqual(stats["state"], "idle")
        self.assertEqual(stats["state_machine"], "understand")
        self.assertEqual(stats["decision_loop_count"], 0)
        self.assertEqual(stats["decision_history_size"], 0)
    
    @patch('cinder_cli.agents.decision_agent.DecisionAgent._run_decision_loop')
    def test_execute(self, mock_loop):
        mock_loop.return_value = {
            "status": "complete",
            "worker_result": {"quality_score": 0.9},
        }
        
        task = Task(
            task_id="test_task",
            description="Test task",
        )
        
        result = self.decision_agent.execute(task)
        
        self.assertEqual(result["status"], "complete")
        self.assertEqual(self.decision_agent.state, AgentState.COMPLETE)
    
    def test_execute_error_handling(self):
        task = Task(
            task_id="error_task",
            description="Task that will fail",
        )
        
        with patch.object(self.decision_agent, '_run_decision_loop') as mock_loop:
            mock_loop.side_effect = Exception("Test error")
            
            result = self.decision_agent.execute(task)
            
            self.assertEqual(result["status"], "error")
            self.assertIn("error", result)
            self.assertEqual(self.decision_agent.state, AgentState.ERROR)


if __name__ == "__main__":
    unittest.main()
