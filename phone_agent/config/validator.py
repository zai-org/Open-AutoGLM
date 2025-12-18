"""Configuration validation and management utilities."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validates configuration parameters."""

    @staticmethod
    def validate_model_config(config: Dict[str, Any]) -> bool:
        """
        Validate model configuration.

        Args:
            config: Configuration dictionary.

        Returns:
            True if valid, raises ValueError otherwise.

        Raises:
            ValueError: If configuration is invalid.
        """
        # Check required fields
        required_fields = ["base_url", "api_key", "model_name"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")

        # Validate base_url format
        base_url = config.get("base_url", "")
        if not base_url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid base_url format: {base_url}")

        # Validate numerical parameters
        max_tokens = config.get("max_tokens", 3000)
        if max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {max_tokens}")

        temperature = config.get("temperature", 0.0)
        if not 0.0 <= temperature <= 2.0:
            raise ValueError(
                f"temperature must be between 0.0 and 2.0, got {temperature}"
            )

        top_p = config.get("top_p", 0.85)
        if not 0.0 <= top_p <= 1.0:
            raise ValueError(f"top_p must be between 0.0 and 1.0, got {top_p}")

        logger.debug("Model configuration validation passed")
        return True

    @staticmethod
    def validate_agent_config(config: Dict[str, Any]) -> bool:
        """
        Validate agent configuration.

        Args:
            config: Configuration dictionary.

        Returns:
            True if valid, raises ValueError otherwise.

        Raises:
            ValueError: If configuration is invalid.
        """
        max_steps = config.get("max_steps", 100)
        if max_steps <= 0:
            raise ValueError(f"max_steps must be positive, got {max_steps}")

        lang = config.get("lang", "cn")
        if lang not in ("cn", "en"):
            raise ValueError(f"Invalid language: {lang}")

        logger.debug("Agent configuration validation passed")
        return True

    @staticmethod
    def validate_adb_config() -> bool:
        """
        Validate ADB environment configuration.

        Returns:
            True if ADB is properly configured.

        Raises:
            ValueError: If ADB configuration is invalid.
        """
        import shutil

        # Check if ADB is available
        if shutil.which("adb") is None:
            raise ValueError("ADB is not installed or not in PATH")

        logger.debug("ADB configuration validation passed")
        return True


class SecureConfig:
    """Secure configuration management with environment variable support."""

    @staticmethod
    def load_from_env() -> Dict[str, Any]:
        """
        Load configuration from environment variables.

        Environment variables:
        - PHONE_AGENT_BASE_URL: Model API base URL
        - PHONE_AGENT_MODEL: Model name
        - PHONE_AGENT_API_KEY: API key
        - PHONE_AGENT_MAX_STEPS: Max steps per task
        - PHONE_AGENT_DEVICE_ID: ADB device ID
        - PHONE_AGENT_LOG_LEVEL: Logging level

        Returns:
            Configuration dictionary.
        """
        return {
            "base_url": os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1"),
            "model_name": os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b"),
            "api_key": os.getenv("PHONE_AGENT_API_KEY", "EMPTY"),
            "max_steps": int(os.getenv("PHONE_AGENT_MAX_STEPS", "100")),
            "device_id": os.getenv("PHONE_AGENT_DEVICE_ID"),
            "log_level": os.getenv("PHONE_AGENT_LOG_LEVEL", "INFO"),
        }

    @staticmethod
    def mask_sensitive_value(value: str, visible_chars: int = 4) -> str:
        """
        Mask sensitive configuration value for logging.

        Args:
            value: The value to mask.
            visible_chars: Number of visible characters.

        Returns:
            Masked value string.
        """
        if not value or len(value) <= visible_chars:
            return "*" * len(value)
        return value[:visible_chars] + "*" * (len(value) - visible_chars)

    @staticmethod
    def log_config_summary(config: Dict[str, Any]) -> None:
        """
        Log configuration summary with sensitive values masked.

        Args:
            config: Configuration dictionary.
        """
        logger.info("=" * 60)
        logger.info("📋 Configuration Summary")
        logger.info("=" * 60)

        # Log non-sensitive config
        for key, value in config.items():
            if key == "api_key":
                masked = SecureConfig.mask_sensitive_value(str(value))
                logger.info(f"  {key}: {masked}")
            elif key != "password":  # Skip other sensitive fields
                logger.info(f"  {key}: {value}")

        logger.info("=" * 60)


class ConfigLoader:
    """Load configuration from various sources."""

    @staticmethod
    def load_yaml(path: Path) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            path: Path to YAML file.

        Returns:
            Configuration dictionary.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If YAML parsing fails.
        """
        try:
            import yaml

            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {path}")
                return config or {}
        except ImportError:
            raise ValueError("PyYAML is required to load YAML files")
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {path}")
        except Exception as e:
            raise ValueError(f"Failed to load YAML configuration: {e}")

    @staticmethod
    def load_json(path: Path) -> Dict[str, Any]:
        """
        Load configuration from JSON file.

        Args:
            path: Path to JSON file.

        Returns:
            Configuration dictionary.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If JSON parsing fails.
        """
        import json

        try:
            with open(path, encoding="utf-8") as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {path}")
                return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON configuration: {e}")

    @staticmethod
    def load_from_file(path: Path) -> Dict[str, Any]:
        """
        Auto-detect file format and load configuration.

        Supports: JSON, YAML

        Args:
            path: Path to configuration file.

        Returns:
            Configuration dictionary.

        Raises:
            ValueError: If file format is not supported.
        """
        suffix = path.suffix.lower()

        if suffix == ".json":
            return ConfigLoader.load_json(path)
        elif suffix in (".yaml", ".yml"):
            return ConfigLoader.load_yaml(path)
        else:
            raise ValueError(
                f"Unsupported configuration format: {suffix}. "
                "Use .json or .yaml"
            )
