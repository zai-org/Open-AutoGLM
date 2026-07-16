"""Unit tests for the ``Wait`` action handler.

These tests exercise ``ActionHandler._handle_wait`` via the public ``execute``
entry point. They are pure and deterministic — ``time.sleep`` is patched so no
real time is spent and no device or network access is required.
"""

from unittest.mock import patch

from phone_agent.actions.handler import ActionHandler


def _wait_action(**kwargs):
    action = {"_metadata": "do", "action": "Wait"}
    action.update(kwargs)
    return action


class TestHandleWait:
    """Tests for ``ActionHandler._handle_wait`` robustness."""

    def test_string_duration_with_unit(self):
        handler = ActionHandler()
        with patch("phone_agent.actions.handler.time.sleep") as sleep:
            result = handler.execute(_wait_action(duration="3 seconds"), 1080, 1920)
        assert result.success is True
        assert result.should_finish is False
        sleep.assert_called_once_with(3.0)

    def test_string_duration_without_unit(self):
        handler = ActionHandler()
        with patch("phone_agent.actions.handler.time.sleep") as sleep:
            result = handler.execute(_wait_action(duration="2"), 1080, 1920)
        assert result.success is True
        sleep.assert_called_once_with(2.0)

    def test_default_duration_when_missing(self):
        handler = ActionHandler()
        with patch("phone_agent.actions.handler.time.sleep") as sleep:
            result = handler.execute(_wait_action(), 1080, 1920)
        assert result.success is True
        sleep.assert_called_once_with(1.0)

    def test_integer_duration_does_not_crash(self):
        """A bare int duration must not raise AttributeError.

        Previously ``int.replace`` raised ``AttributeError`` which the
        ``except ValueError`` clause did not catch, so the wait silently
        failed with ``success=False``.
        """
        handler = ActionHandler()
        with patch("phone_agent.actions.handler.time.sleep") as sleep:
            result = handler.execute(_wait_action(duration=3), 1080, 1920)
        assert result.success is True
        sleep.assert_called_once_with(3.0)

    def test_float_duration(self):
        handler = ActionHandler()
        with patch("phone_agent.actions.handler.time.sleep") as sleep:
            result = handler.execute(_wait_action(duration=1.5), 1080, 1920)
        assert result.success is True
        sleep.assert_called_once_with(1.5)

    def test_unparseable_duration_falls_back(self):
        handler = ActionHandler()
        with patch("phone_agent.actions.handler.time.sleep") as sleep:
            result = handler.execute(_wait_action(duration="soon"), 1080, 1920)
        assert result.success is True
        sleep.assert_called_once_with(1.0)

    def test_negative_duration_is_clamped(self):
        """A negative duration must be clamped so time.sleep does not raise."""
        handler = ActionHandler()
        with patch("phone_agent.actions.handler.time.sleep") as sleep:
            result = handler.execute(_wait_action(duration="-5 seconds"), 1080, 1920)
        assert result.success is True
        sleep.assert_called_once_with(1.0)

    def test_non_finite_duration_falls_back(self):
        """NaN and infinite durations must fall back to the default."""
        handler = ActionHandler()
        for raw in ("nan", "inf", "NaN", "+Infinity"):
            with patch("phone_agent.actions.handler.time.sleep") as sleep:
                result = handler.execute(_wait_action(duration=raw), 1080, 1920)
            assert result.success is True, f"duration={raw!r} should not fail"
            sleep.assert_called_once_with(1.0)
            sleep.reset_mock()

    def test_zero_duration_is_allowed(self):
        """Zero is a legitimate finite duration and should not be clamped."""
        handler = ActionHandler()
        with patch("phone_agent.actions.handler.time.sleep") as sleep:
            result = handler.execute(_wait_action(duration="0 seconds"), 1080, 1920)
        assert result.success is True
        sleep.assert_called_once_with(0.0)
