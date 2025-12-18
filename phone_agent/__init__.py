"""
Phone Agent - An AI-powered phone automation framework.

This package provides tools for automating Android phone interactions
using AI models for visual understanding and decision making.
"""

from phone_agent.agent import PhoneAgent, AgentConfig, StepResult
from phone_agent.model import ModelConfig
from phone_agent.metrics import SessionMetrics, StepMetrics, MetricsCollector
from phone_agent.config.validator import ConfigValidator, SecureConfig, ConfigLoader

__version__ = "0.1.0"
__all__ = [
    # Core
    "PhoneAgent",
    # Configuration
    "AgentConfig",
    "ModelConfig",
    "ConfigValidator",
    "SecureConfig",
    "ConfigLoader",
    # Results and Metrics
    "StepResult",
    "SessionMetrics",
    "StepMetrics",
    "MetricsCollector",
]
