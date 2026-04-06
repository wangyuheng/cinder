"""
Tracing Configuration - Manages tracing settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TracingConfig:
    """Configuration for tracing and observability."""
    
    enabled: bool = True
    phoenix_endpoint: str = ""
    phoenix_host: str = "localhost"
    phoenix_port: int = 6006
    sample_rate: float = 1.0
    retention_days: int = 30
    compression_threshold: int = 1024
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Validate configuration values."""
        if not 0.0 <= self.sample_rate <= 1.0:
            raise ValueError(
                f"sample_rate must be between 0.0 and 1.0, got {self.sample_rate}"
            )
        
        if self.retention_days < 1:
            raise ValueError(
                f"retention_days must be at least 1, got {self.retention_days}"
            )
        
        if self.compression_threshold < 0:
            raise ValueError(
                f"compression_threshold must be non-negative, got {self.compression_threshold}"
            )
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TracingConfig:
        """
        Create TracingConfig from dictionary.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            TracingConfig instance
        """
        tracing_data = data.get("tracing", {})
        
        if isinstance(tracing_data, bool):
            return cls(enabled=tracing_data)
        
        return cls(
            enabled=tracing_data.get("enabled", True),
            phoenix_endpoint=tracing_data.get("phoenix_endpoint", ""),
            phoenix_host=tracing_data.get("phoenix_host", "localhost"),
            phoenix_port=tracing_data.get("phoenix_port", 6006),
            sample_rate=tracing_data.get("sample_rate", 1.0),
            retention_days=tracing_data.get("retention_days", 30),
            compression_threshold=tracing_data.get("compression_threshold", 1024),
        )
    
    @classmethod
    def from_config(cls, config: Any) -> TracingConfig:
        """
        Create TracingConfig from Config object.
        
        Args:
            config: Config object with get() method
            
        Returns:
            TracingConfig instance
        """
        return cls(
            enabled=config.get("tracing", {}).get("enabled", True),
            phoenix_endpoint=config.get("tracing", {}).get("phoenix_endpoint", ""),
            phoenix_host=config.get("tracing", {}).get("phoenix_host", "localhost"),
            phoenix_port=config.get("tracing", {}).get("phoenix_port", 6006),
            sample_rate=config.get("tracing", {}).get("sample_rate", 1.0),
            retention_days=config.get("tracing", {}).get("retention_days", 30),
            compression_threshold=config.get("tracing", {}).get("compression_threshold", 1024),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert TracingConfig to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            "enabled": self.enabled,
            "phoenix_endpoint": self.phoenix_endpoint,
            "phoenix_host": self.phoenix_host,
            "phoenix_port": self.phoenix_port,
            "sample_rate": self.sample_rate,
            "retention_days": self.retention_days,
            "compression_threshold": self.compression_threshold,
        }
    
    def get_phoenix_endpoint(self) -> str:
        """
        Get Phoenix endpoint, returning default if not set.
        
        Returns:
            Phoenix endpoint URL
        """
        return self.phoenix_endpoint or "http://localhost:6006"
    
    def should_trace(self) -> bool:
        """
        Check if tracing should be performed based on sample rate.
        
        Returns:
            True if this request should be traced
        """
        if not self.enabled:
            return False
        
        import random
        return random.random() < self.sample_rate
