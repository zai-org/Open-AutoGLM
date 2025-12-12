"""Tests for validation utilities."""

import pytest

from phone_agent.utils.validation import (
    validate_app_name,
    validate_coordinates,
    validate_port,
    validate_relative_coordinates,
    validate_url,
)


class TestValidateCoordinates:
    """Test cases for coordinate validation."""

    def test_validate_coordinates_within_bounds(self):
        """Test coordinates within screen bounds."""
        x, y = validate_coordinates(100, 200, 1080, 1920)
        assert x == 100
        assert y == 200

    def test_validate_coordinates_clamp_to_bounds(self):
        """Test coordinates clamped to screen bounds."""
        x, y = validate_coordinates(-10, 2000, 1080, 1920)
        assert x == 0
        assert y == 1919  # height - 1

    def test_validate_coordinates_float_input(self):
        """Test float coordinates are converted to int."""
        x, y = validate_coordinates(100.7, 200.3, 1080, 1920)
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert x == 100
        assert y == 200


class TestValidateRelativeCoordinates:
    """Test cases for relative coordinate validation."""

    def test_validate_relative_coordinates_valid(self):
        """Test valid relative coordinates."""
        x, y = validate_relative_coordinates([500, 600], 1080, 1920)
        assert x == 540  # 500/1000 * 1080
        assert y == 1152  # 600/1000 * 1920

    def test_validate_relative_coordinates_invalid_format(self):
        """Test invalid coordinate format raises ValueError."""
        with pytest.raises(ValueError):
            validate_relative_coordinates([100], 1080, 1920)

        with pytest.raises(ValueError):
            validate_relative_coordinates("invalid", 1080, 1920)

    def test_validate_relative_coordinates_out_of_range(self):
        """Test coordinates out of 0-1000 range raises ValueError."""
        with pytest.raises(ValueError):
            validate_relative_coordinates([1500, 600], 1080, 1920)

        with pytest.raises(ValueError):
            validate_relative_coordinates([500, -100], 1080, 1920)

    def test_validate_relative_coordinates_float_input(self):
        """Test float coordinates are handled correctly."""
        x, y = validate_relative_coordinates([500.5, 600.7], 1080, 1920)
        assert isinstance(x, int)
        assert isinstance(y, int)


class TestValidateAppName:
    """Test cases for app name validation."""

    def test_validate_app_name_valid(self):
        """Test valid app name."""
        app_name = validate_app_name("微信")
        assert app_name == "微信"

    def test_validate_app_name_with_allowed_list(self):
        """Test app name validation with allowed list."""
        allowed = {"微信", "QQ", "微博"}
        app_name = validate_app_name("微信", allowed)
        assert app_name == "微信"

    def test_validate_app_name_not_in_allowed_list(self):
        """Test app name not in allowed list raises ValueError."""
        allowed = {"微信", "QQ", "微博"}
        with pytest.raises(ValueError):
            validate_app_name("InvalidApp", allowed)

    def test_validate_app_name_empty(self):
        """Test empty app name raises ValueError."""
        with pytest.raises(ValueError):
            validate_app_name("")

        with pytest.raises(ValueError):
            validate_app_name(None)  # type: ignore

    def test_validate_app_name_strips_whitespace(self):
        """Test app name whitespace is stripped."""
        app_name = validate_app_name("  微信  ")
        assert app_name == "微信"


class TestValidatePort:
    """Test cases for port validation."""

    def test_validate_port_valid(self):
        """Test valid port numbers."""
        assert validate_port(5555) == 5555
        assert validate_port(8000) == 8000
        assert validate_port(1) == 1
        assert validate_port(65535) == 65535

    def test_validate_port_invalid_range(self):
        """Test invalid port range raises ValueError."""
        with pytest.raises(ValueError):
            validate_port(0)

        with pytest.raises(ValueError):
            validate_port(65536)

        with pytest.raises(ValueError):
            validate_port(-1)

    def test_validate_port_invalid_type(self):
        """Test invalid port type raises ValueError."""
        with pytest.raises(ValueError):
            validate_port("5555")  # type: ignore


class TestValidateURL:
    """Test cases for URL validation."""

    def test_validate_url_http(self):
        """Test HTTP URL validation."""
        url = validate_url("http://localhost:8000/v1")
        assert url == "http://localhost:8000/v1"

    def test_validate_url_https(self):
        """Test HTTPS URL validation."""
        url = validate_url("https://api.example.com/v1")
        assert url == "https://api.example.com/v1"

    def test_validate_url_invalid_protocol(self):
        """Test URL without http/https raises ValueError."""
        with pytest.raises(ValueError):
            validate_url("ftp://example.com")

        with pytest.raises(ValueError):
            validate_url("localhost:8000")

    def test_validate_url_empty(self):
        """Test empty URL raises ValueError."""
        with pytest.raises(ValueError):
            validate_url("")

        with pytest.raises(ValueError):
            validate_url(None)  # type: ignore

    def test_validate_url_strips_whitespace(self):
        """Test URL whitespace is stripped."""
        url = validate_url("  http://localhost:8000/v1  ")
        assert url == "http://localhost:8000/v1"

