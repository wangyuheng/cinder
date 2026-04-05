"""
Unit tests for CodexIntegrationManager.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cinder_cli.config import Config
from cinder_cli.executor.codex_integration_manager import (
    CodexIntegrationManager,
    TaskContext,
)
from cinder_cli.executor.codex_exceptions import CodexError


class TestTaskContext:
    """Test TaskContext dataclass."""
    
    def test_context_creation_minimal(self):
        """Test creating context with minimal parameters."""
        context = TaskContext(
            soul_profile={},
            decision_context={},
        )
        
        assert context.soul_profile == {}
        assert context.decision_context == {}
        assert context.quality_requirements is None
    
    def test_context_creation_full(self):
        """Test creating context with all parameters."""
        context = TaskContext(
            soul_profile={"traits": {"risk_tolerance": "high"}},
            decision_context={"goal_type": "code_generation"},
            quality_requirements={"quality_threshold": 0.8},
        )
        
        assert context.soul_profile == {"traits": {"risk_tolerance": "high"}}
        assert context.decision_context == {"goal_type": "code_generation"}
        assert context.quality_requirements == {"quality_threshold": 0.8}


class TestCodexIntegrationManager:
    """Test CodexIntegrationManager class."""
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    def test_init_codex_disabled(self, mock_check):
        """Test initialization when Codex is disabled."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = False
        mock_config.codex = {"enabled": False}
        mock_config.validate_codex_config.return_value = []
        
        manager = CodexIntegrationManager(mock_config)
        
        assert manager.is_available() is False
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    @patch('cinder_cli.executor.codex_integration_manager.CodexExecExecutor')
    def test_init_codex_enabled(self, mock_executor, mock_check):
        """Test initialization when Codex is enabled."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = True
        mock_config.codex = {
            "enabled": True,
            "fallback_on_error": True,
            "exec": {},
        }
        mock_config.validate_codex_config.return_value = []
        
        mock_check.return_value = (True, "Codex available")
        
        manager = CodexIntegrationManager(mock_config)
        
        assert manager.is_available() is True
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    def test_build_task_prompt(self, mock_check):
        """Test building task prompt with context."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = False
        mock_config.codex = {"enabled": False}
        mock_config.validate_codex_config.return_value = []
        
        manager = CodexIntegrationManager(mock_config)
        
        context = TaskContext(
            soul_profile={
                "traits": {
                    "risk_tolerance": "moderate",
                    "communication_style": "concise"
                }
            },
            decision_context={
                "goal_type": "code_generation",
                "key_features": ["simple", "readable"]
            },
            quality_requirements={
                "quality_threshold": 0.8
            }
        )
        
        prompt = manager._build_task_prompt("Create a function", context)
        
        assert "上下文信息" in prompt
        assert "用户性格特征" in prompt
        assert "risk_tolerance" in prompt
        assert "moderate" in prompt
        assert "任务理解" in prompt
        assert "目标类型" in prompt  # 中文翻译
        assert "code_generation" in prompt
        assert "质量要求" in prompt
        assert "任务描述" in prompt
        assert "Create a function" in prompt
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    def test_build_task_prompt_empty_context(self, mock_check):
        """Test building task prompt with empty context."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = False
        mock_config.codex = {"enabled": False}
        mock_config.validate_codex_config.return_value = []
        
        manager = CodexIntegrationManager(mock_config)
        
        context = TaskContext(
            soul_profile={},
            decision_context={},
        )
        
        prompt = manager._build_task_prompt("Simple task", context)
        
        assert "任务描述" in prompt
        assert "Simple task" in prompt
    
    @patch('cinder_cli.executor.codex_integration_manager.check_codex_availability')
    def test_create_task(self, mock_check):
        """Test creating CodexTask from parameters."""
        mock_config = Mock(spec=Config)
        mock_config.is_codex_enabled.return_value = False
        mock_config.codex = {
            "enabled": False,
            "exec": {
                "model": "gpt-5.4",
                "sandbox_mode": "workspace-write",
                "timeout": 300,
            }
        }
        mock_config.validate_codex_config.return_value = []
        
        manager = CodexIntegrationManager(mock_config)
        
        task = manager._create_task(
            "Test prompt",
            model="gpt-5.3",
            timeout=600
        )
        
        assert task.description == "Test prompt"
        assert task.model == "gpt-5.3"
        assert task.sandbox_mode == "workspace-write"
        assert task.timeout == 600


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
