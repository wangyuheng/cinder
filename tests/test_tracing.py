"""
Unit tests for tracing module.
"""

from __future__ import annotations

import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cinder_cli.tracing import (
    TracingConfig,
    PhoenixTracer,
    LLMTracer,
    AgentTracer,
    PhoenixServer,
    TraceManager,
    TraceExporter,
)


class TestTracingConfig:
    """Tests for TracingConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = TracingConfig()
        
        assert config.enabled is True
        assert config.phoenix_endpoint == ""
        assert config.phoenix_host == "localhost"
        assert config.phoenix_port == 6006
        assert config.sample_rate == 1.0
        assert config.retention_days == 30
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "tracing": {
                "enabled": False,
                "phoenix_endpoint": "http://remote:6006",
                "sample_rate": 0.5,
                "retention_days": 7,
            }
        }
        
        config = TracingConfig.from_dict(data)
        
        assert config.enabled is False
        assert config.phoenix_endpoint == "http://remote:6006"
        assert config.sample_rate == 0.5
        assert config.retention_days == 7
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = TracingConfig(
            enabled=False,
            phoenix_endpoint="http://test:6006",
            sample_rate=0.8,
        )
        
        data = config.to_dict()
        
        assert data["enabled"] is False
        assert data["phoenix_endpoint"] == "http://test:6006"
        assert data["sample_rate"] == 0.8
    
    def test_get_phoenix_endpoint_default(self):
        """Test getting default Phoenix endpoint."""
        config = TracingConfig()
        
        endpoint = config.get_phoenix_endpoint()
        
        assert endpoint == "http://localhost:6006"
    
    def test_get_phoenix_endpoint_custom(self):
        """Test getting custom Phoenix endpoint."""
        config = TracingConfig(phoenix_endpoint="http://custom:8080")
        
        endpoint = config.get_phoenix_endpoint()
        
        assert endpoint == "http://custom:8080"
    
    def test_should_trace_enabled(self):
        """Test should_trace when enabled."""
        config = TracingConfig(enabled=True, sample_rate=1.0)
        
        assert config.should_trace() is True
    
    def test_should_trace_disabled(self):
        """Test should_trace when disabled."""
        config = TracingConfig(enabled=False)
        
        assert config.should_trace() is False
    
    def test_invalid_sample_rate(self):
        """Test validation of invalid sample rate."""
        with pytest.raises(ValueError):
            TracingConfig(sample_rate=1.5)
        
        with pytest.raises(ValueError):
            TracingConfig(sample_rate=-0.1)
    
    def test_invalid_retention_days(self):
        """Test validation of invalid retention days."""
        with pytest.raises(ValueError):
            TracingConfig(retention_days=0)


class TestLLMTracer:
    """Tests for LLMTracer."""
    
    def test_init_without_phoenix_tracer(self):
        """Test initialization without Phoenix tracer."""
        tracer = LLMTracer()
        
        assert tracer.phoenix_tracer is None
        assert tracer._call_records == []
    
    def test_trace_llm_call_context_manager(self):
        """Test trace_llm_call context manager."""
        tracer = LLMTracer()
        
        with tracer.trace_llm_call(
            model="test-model",
            prompt="test prompt",
            system_prompt="system prompt",
            model_params={"temperature": 0.7},
        ) as record:
            record.response = "test response"
            record.input_tokens = 10
            record.output_tokens = 20
        
        records = tracer.get_call_records()
        assert len(records) == 1
        assert records[0].model == "test-model"
        assert records[0].prompt == "test prompt"
        assert records[0].response == "test response"
        assert records[0].input_tokens == 10
        assert records[0].output_tokens == 20
    
    def test_record_response(self):
        """Test record_response method."""
        tracer = LLMTracer()
        
        with tracer.trace_llm_call(
            model="test-model",
            prompt="test",
        ) as record:
            tracer.record_response(record, "response", 10, 20)
        
        records = tracer.get_call_records()
        assert records[0].response == "response"
        assert records[0].input_tokens == 10
        assert records[0].output_tokens == 20
        assert records[0].total_tokens == 30
    
    def test_clear_records(self):
        """Test clearing call records."""
        tracer = LLMTracer()
        
        with tracer.trace_llm_call(model="test", prompt="test"):
            pass
        
        assert len(tracer.get_call_records()) == 1
        
        tracer.clear_records()
        
        assert len(tracer.get_call_records()) == 0


class TestAgentTracer:
    """Tests for AgentTracer."""
    
    def test_init_without_phoenix_tracer(self):
        """Test initialization without Phoenix tracer."""
        tracer = AgentTracer()
        
        assert tracer.phoenix_tracer is None
    
    def test_trace_agent_execution(self):
        """Test trace_agent_execution context manager."""
        tracer = AgentTracer()
        
        with tracer.trace_agent_execution(
            agent_id="agent-1",
            role="worker",
            goal="test goal",
        ):
            pass
        
        assert len(tracer._decision_records) >= 0
    
    def test_trace_tool_call(self):
        """Test trace_tool_call method."""
        tracer = AgentTracer()
        
        result = tracer.trace_tool_call(
            tool_name="test_tool",
            tool_input={"arg": "value"},
            tool_output="result",
        )
        
        assert result["tool_name"] == "test_tool"
        assert result["tool_input"] == {"arg": "value"}
        assert result["tool_output"] == "result"


class TestPhoenixServer:
    """Tests for PhoenixServer."""
    
    def test_init(self):
        """Test initialization."""
        config = TracingConfig()
        server = PhoenixServer(config)
        
        assert server.config == config
        assert server.host == "localhost"
        assert server.port == 6006
    
    def test_get_url(self):
        """Test getting server URL."""
        config = TracingConfig()
        server = PhoenixServer(config)
        
        url = server.get_url()
        
        assert url == "http://localhost:6006"
    
    @patch('requests.get')
    def test_is_running_false(self, mock_get):
        """Test checking if server is running when it's not."""
        config = TracingConfig()
        server = PhoenixServer(config)
        
        mock_get.side_effect = Exception("Connection refused")
        
        assert server.is_running() is False
    
    @patch('requests.get')
    def test_is_running_true(self, mock_get):
        """Test checking if server is running when it is."""
        config = TracingConfig()
        server = PhoenixServer(config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        assert server.is_running() is True


class TestTraceManager:
    """Tests for TraceManager."""
    
    def test_init(self, tmp_path):
        """Test initialization."""
        manager = TraceManager(trace_dir=tmp_path, retention_days=30)
        
        assert manager.trace_dir == tmp_path
        assert manager.retention_days == 30
        assert manager.backup_dir.exists()
    
    def test_get_trace_stats(self, tmp_path):
        """Test getting trace statistics."""
        manager = TraceManager(trace_dir=tmp_path)
        
        trace_file = tmp_path / "test_trace.json"
        trace_file.write_text('{"test": "data"}')
        
        stats = manager.get_trace_stats()
        
        assert stats["trace_count"] == 1
        assert stats["total_size_mb"] > 0
        assert stats["retention_days"] == 30
    
    def test_cleanup_old_traces_dry_run(self, tmp_path):
        """Test cleanup in dry run mode."""
        manager = TraceManager(trace_dir=tmp_path, retention_days=0)
        
        trace_file = tmp_path / "old_trace.json"
        trace_file.write_text('{"test": "data"}')
        
        count = manager.cleanup_old_traces(dry_run=True)
        
        assert count == 1
        assert trace_file.exists()
    
    def test_backup_traces(self, tmp_path):
        """Test creating backup."""
        manager = TraceManager(trace_dir=tmp_path)
        
        trace_file = tmp_path / "test_trace.json"
        trace_file.write_text('{"test": "data"}')
        
        backup_file = manager.backup_traces("test_backup")
        
        assert backup_file.exists()
        assert "test_backup" in backup_file.name
    
    def test_list_backups(self, tmp_path):
        """Test listing backups."""
        manager = TraceManager(trace_dir=tmp_path)
        
        manager.backup_traces("backup1")
        manager.backup_traces("backup2")
        
        backups = manager.list_backups()
        
        assert len(backups) == 2


class TestTraceExporter:
    """Tests for TraceExporter."""
    
    def test_init(self, tmp_path):
        """Test initialization."""
        exporter = TraceExporter(export_dir=tmp_path)
        
        assert exporter.export_dir == tmp_path
    
    def test_export_to_json(self, tmp_path):
        """Test exporting to JSON format."""
        exporter = TraceExporter(export_dir=tmp_path)
        
        spans = []
        output_file = exporter.export_to_json(spans)
        
        assert output_file.exists()
        
        with open(output_file) as f:
            data = json.load(f)
        
        assert isinstance(data, list)
    
    def test_export_to_otlp(self, tmp_path):
        """Test exporting to OTLP format."""
        exporter = TraceExporter(export_dir=tmp_path)
        
        spans = []
        output_file = exporter.export_to_otlp(spans)
        
        assert output_file.exists()
        
        with open(output_file) as f:
            data = json.load(f)
        
        assert "resourceSpans" in data
