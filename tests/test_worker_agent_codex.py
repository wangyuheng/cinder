"""
Integration tests for Worker Agent with Codex integration.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cinder_cli.config import Config
from cinder_cli.agents.worker_agent import WorkerAgent, WorkerOutput
from cinder_cli.agents.base import Task
from cinder_cli.executor.codex_integration_manager import CodexIntegrationManager


class TestWorkerAgentCodexIntegration:
    """Test Worker Agent integration with Codex."""
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    @patch('cinder_cli.executor.codex_integration_manager.CodexExecExecutor')
    def test_worker_agent_with_codex_enabled(self, mock_executor, mock_check):
        """Test Worker Agent initialization with Codex enabled."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = True
        mock_config.codex = {
            "enabled": True,
            "fallback_on_error": True,
            "exec": {},
        }
        mock_config.validate_codex_config.return_value = []
        
        mock_check.return_value = (True, "Codex available")
        
        agent = WorkerAgent("test_agent", mock_config)
        
        assert agent.codex_manager is not None
        assert agent.codex_manager.is_available()
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    def test_worker_agent_with_codex_disabled(self, mock_check):
        """Test Worker Agent initialization with Codex disabled."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = False
        mock_config.codex = {"enabled": False}
        mock_config.validate_codex_config.return_value = []
        
        agent = WorkerAgent("test_agent", mock_config)
        
        assert agent.codex_manager is None
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    @patch('cinder_cli.executor.codex_integration_manager.CodexExecExecutor')
    def test_should_use_codex_when_enabled(self, mock_executor, mock_check):
        """Test that Codex is used when enabled and available."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = True
        mock_config.codex = {
            "enabled": True,
            "fallback_on_error": True,
            "exec": {},
        }
        mock_config.validate_codex_config.return_value = []
        
        mock_check.return_value = (True, "Codex available")
        
        agent = WorkerAgent("test_agent", mock_config)
        
        task = Task(
            task_id="test_task",
            description="Test task",
            metadata={
                "soul_meta": {"traits": {"risk_tolerance": "moderate"}},
                "decision_context": {"goal_type": "code_generation"}
            }
        )
        
        should_use = agent._should_use_codex(task)
        
        assert should_use is True
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    def test_should_not_use_codex_when_disabled(self, mock_check):
        """Test that Codex is not used when disabled."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = False
        mock_config.codex = {"enabled": False}
        mock_config.validate_codex_config.return_value = []
        
        agent = WorkerAgent("test_agent", mock_config)
        
        task = Task(
            task_id="test_task",
            description="Test task",
        )
        
        should_use = agent._should_use_codex(task)
        
        assert should_use is False
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    @patch('cinder_cli.executor.codex_integration_manager.CodexExecExecutor')
    def test_generate_with_codex(self, mock_executor, mock_check):
        """Test code generation using Codex."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = True
        mock_config.codex = {
            "enabled": True,
            "fallback_on_error": True,
            "exec": {},
        }
        mock_config.validate_codex_config.return_value = []
        
        mock_check.return_value = (True, "Codex available")
        
        agent = WorkerAgent("test_agent", mock_config)
        
        plan = {
            "subtasks": [
                {
                    "description": "Create a function",
                    "language": "python",
                }
            ]
        }
        
        task = Task(
            task_id="test_task",
            description="Test task",
            metadata={
                "soul_meta": {"traits": {"risk_tolerance": "moderate"}},
                "decision_context": {"goal_type": "code_generation"}
            }
        )
        
        mock_codex_result = Mock()
        mock_codex_result.success = True
        mock_codex_result.output = "def add(a, b): return a + b"
        
        agent.codex_manager.execute_task = Mock(return_value=mock_codex_result)
        
        result = agent._generate_with_codex(plan["subtasks"], task)
        
        assert result["type"] == "code"
        assert "def add" in result["code"]
        assert result["executor"] == "codex"
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    def test_generate_with_code_generator_fallback(self, mock_check):
        """Test fallback to CodeGenerator when Codex is not available."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = False
        mock_config.codex = {"enabled": False}
        mock_config.validate_codex_config.return_value = []
        
        agent = WorkerAgent("test_agent", mock_config)
        
        plan = {
            "subtasks": [
                {
                    "description": "Create a function",
                    "language": "python",
                }
            ]
        }
        
        result = agent._generate_with_code_generator(plan["subtasks"])
        
        assert result["type"] == "code"
        assert result["executor"] == "code_generator"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
