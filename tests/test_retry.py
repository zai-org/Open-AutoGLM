"""Tests for retry utilities."""

import time
from unittest.mock import Mock, patch

import pytest

from phone_agent.utils.retry import retry, retry_adb_command


class TestRetry:
    """Test cases for retry decorator."""

    def test_retry_success_on_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0

        @retry(max_attempts=3)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_function()
        assert result == "success"
        assert call_count == 1

    def test_retry_success_after_failures(self):
        """Test function succeeds after initial failures."""
        call_count = 0

        @retry(max_attempts=3, delay=0.1)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count == 2

    def test_retry_exhausts_attempts(self):
        """Test retry exhausts all attempts and raises exception."""
        call_count = 0

        @retry(max_attempts=3, delay=0.1)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_failing_function()

        assert call_count == 3

    def test_retry_only_catches_specified_exceptions(self):
        """Test retry only catches specified exceptions."""
        call_count = 0

        @retry(max_attempts=3, delay=0.1, exceptions=(ValueError,))
        def function_raising_different_exception():
            nonlocal call_count
            call_count += 1
            raise TypeError("Different exception")

        with pytest.raises(TypeError):
            function_raising_different_exception()

        assert call_count == 1  # Should not retry

    def test_retry_with_callback(self):
        """Test retry calls callback on each retry."""
        call_count = 0
        retry_callback_calls = []

        def on_retry(exception, attempt):
            retry_callback_calls.append((exception, attempt))

        @retry(max_attempts=3, delay=0.1, on_retry=on_retry)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "success"

        result = flaky_function()
        assert result == "success"
        assert len(retry_callback_calls) == 1
        assert retry_callback_calls[0][1] == 1  # First retry attempt

    def test_retry_with_backoff(self):
        """Test retry uses exponential backoff."""
        call_times = []

        @retry(max_attempts=3, delay=0.1, backoff=2.0)
        def flaky_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = flaky_function()
        assert result == "success"

        # Check that delays increase
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            # Allow some tolerance for timing
            assert delay2 > delay1 * 1.5  # Should be approximately 2x


class TestRetryADBCommand:
    """Test cases for retry_adb_command decorator."""

    def test_retry_adb_command_success(self):
        """Test ADB command succeeds."""
        call_count = 0

        @retry_adb_command(max_attempts=3, delay=0.1)
        def adb_command():
            nonlocal call_count
            call_count += 1
            return "success"

        result = adb_command()
        assert result == "success"
        assert call_count == 1

    def test_retry_adb_command_handles_connection_error(self):
        """Test ADB command retries on ConnectionError."""
        call_count = 0

        @retry_adb_command(max_attempts=3, delay=0.1)
        def flaky_adb_command():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Connection failed")
            return "success"

        result = flaky_adb_command()
        assert result == "success"
        assert call_count == 2

