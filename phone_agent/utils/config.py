"""Configuration validation and management utilities."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates configuration parameters."""

    REQUIRED_KEYS = {
        "model": ["base_url", "api_key", "model_name"],
        "agent": ["max_steps", "lang"],
        "adb": ["device_id"],
    }

    VALID_RANGES = {
        "max_steps": (1, 1000),
        "temperature": (0.0, 2.0),
        "top_p": (0.0, 1.0),
        "frequency_penalty": (-2.0, 2.0),
    }

    VALID_LANGUAGES = ["cn", "en"]

    @staticmethod
    def validate_model_config(config: Dict[str, Any]) -> bool:
        """
        Validate model configuration.

        Args:
            config: Model configuration dictionary.

        Returns:
            True if valid, raises ValueError otherwise.
        """
        required = ConfigValidator.REQUIRED_KEYS.get("model", [])
        for key in required:
            if key not in config:
                raise ValueError(f"Missing required model config: {key}")

        # Validate ranges
        if "temperature" in config:
            val = config["temperature"]
            min_val, max_val = ConfigValidator.VALID_RANGES["temperature"]
            if not min_val <= val <= max_val:
                raise ValueError(
                    f"temperature must be between {min_val} and {max_val}, got {val}"
                )

        if "max_tokens" in config and config["max_tokens"] <= 0:
            raise ValueError("max_tokens must be positive")

        logger.info("Model configuration validated successfully")
        return True

    @staticmethod
    def validate_agent_config(config: Dict[str, Any]) -> bool:
        """Validate agent configuration."""
        if config.get("max_steps", 100) <= 0:
            raise ValueError("max_steps must be positive")

        if config.get("lang", "cn") not in ConfigValidator.VALID_LANGUAGES:
            raise ValueError(
                f"lang must be one of {ConfigValidator.VALID_LANGUAGES}"
            )

        logger.info("Agent configuration validated successfully")
        return True

    @staticmethod
    def validate_env_vars() -> Dict[str, Optional[str]]:
        """
        Validate and collect environment variables.

        Returns:
            Dictionary of environment variables.
        """
        env_vars = {
            "PHONE_AGENT_BASE_URL": os.getenv("PHONE_AGENT_BASE_URL"),
            "PHONE_AGENT_API_KEY": os.getenv("PHONE_AGENT_API_KEY"),
            "PHONE_AGENT_MODEL": os.getenv("PHONE_AGENT_MODEL"),
            "PHONE_AGENT_DEVICE_ID": os.getenv("PHONE_AGENT_DEVICE_ID"),
            "PHONE_AGENT_MAX_STEPS": os.getenv("PHONE_AGENT_MAX_STEPS"),
        }

        missing = [k for k, v in env_vars.items() if v is None]
        if missing:
            logger.warning(f"Missing environment variables: {missing}")

        return env_vars


class ConfigLoader:
    """Load configuration from various sources."""

    @staticmethod
    def from_env() -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return {
            "base_url": os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1"),
            "api_key": os.getenv("PHONE_AGENT_API_KEY", "EMPTY"),
            "model_name": os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b"),
            "device_id": os.getenv("PHONE_AGENT_DEVICE_ID"),
            "max_steps": int(os.getenv("PHONE_AGENT_MAX_STEPS", "100")),
            "lang": os.getenv("PHONE_AGENT_LANG", "cn"),
        }

    @staticmethod
    def from_file(config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file.

        Args:
            config_path: Path to configuration file (JSON or YAML).

        Returns:
            Configuration dictionary.

        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValueError: If file format is unsupported.
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if path.suffix == ".json":
            import json
            with open(path) as f:
                config = json.load(f)
        elif path.suffix in [".yaml", ".yml"]:
            try:
                import yaml
                with open(path) as f:
                    config = yaml.safe_load(f)
            except ImportError:
                raise ValueError("PyYAML is required for YAML config files")
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")

        logger.info(f"Configuration loaded from {config_path}")
        return config

    @staticmethod
    def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries.

        Later configs override earlier ones.

        Args:
            *configs: Configuration dictionaries to merge.

        Returns:
            Merged configuration.
        """
        result = {}
        for config in configs:
            result.update(config)
        return result
