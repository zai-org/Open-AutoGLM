"""Configuration module for Phone Agent (HarmonyOS only, Chinese prompt)."""

from phone_agent.config.apps_harmonyos import APP_PACKAGES, list_supported_apps
from phone_agent.config.i18n import get_message, get_messages
from phone_agent.config.prompts import SYSTEM_PROMPT
from phone_agent.config.timing import (
    TIMING_CONFIG,
    ActionTimingConfig,
    ConnectionTimingConfig,
    DeviceTimingConfig,
    TimingConfig,
    get_timing_config,
    update_timing_config,
)


    
__all__ = [
    "APP_PACKAGES",
    "list_supported_apps",
    "SYSTEM_PROMPT",
    "get_messages",
    "get_message",
    "TIMING_CONFIG",
    "TimingConfig",
    "ActionTimingConfig",
    "DeviceTimingConfig",
    "ConnectionTimingConfig",
    "get_timing_config",
    "update_timing_config",
]
