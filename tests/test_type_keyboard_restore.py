"""Regression tests for Type-action cleanup; all device calls are mocked."""

import types
import unittest
from unittest.mock import Mock, patch

from phone_agent.actions import handler as MODULE


class KeyboardRestorationTests(unittest.TestCase):
    def setUp(self):
        self.device = Mock()
        self.device.detect_and_set_adb_keyboard.return_value = "vendor.keyboard/.IME"
        self.timing = patch.object(
            MODULE.TIMING_CONFIG,
            "action",
            types.SimpleNamespace(
                keyboard_switch_delay=0.11,
                text_clear_delay=0.22,
                text_input_delay=0.33,
                keyboard_restore_delay=0.44,
            ),
        )
        self.timing.start()
        self.addCleanup(self.timing.stop)
        self.get_factory = patch.object(
            MODULE, "get_device_factory", return_value=self.device
        )
        self.get_factory.start()
        self.addCleanup(self.get_factory.stop)
        self.sleep = patch.object(MODULE.time, "sleep")
        self.sleep_mock = self.sleep.start()
        self.addCleanup(self.sleep.stop)
        self.subprocess_run = patch.object(
            MODULE.subprocess,
            "run",
            side_effect=AssertionError("real subprocess forbidden"),
        )
        self.subprocess_run.start()
        self.addCleanup(self.subprocess_run.stop)
        self.subprocess_popen = patch.object(
            MODULE.subprocess,
            "Popen",
            side_effect=AssertionError("real subprocess forbidden"),
        )
        self.subprocess_popen.start()
        self.addCleanup(self.subprocess_popen.stop)
        self.handler = MODULE.ActionHandler(device_id="mock-device")

    def execute(self, name="Type"):
        return self.handler.execute(
            {"_metadata": "do", "action": name, "text": "two\nlines"}, 100, 200
        )

    def assert_restored(self):
        self.device.restore_keyboard.assert_called_once_with(
            "vendor.keyboard/.IME", "mock-device"
        )

    def test_success_preserves_calls_and_restores(self):
        result = self.execute()
        self.assertTrue(result.success)
        self.assertFalse(result.should_finish)
        self.device.type_text.assert_called_once_with("two\nlines", "mock-device")
        self.assert_restored()
        self.assertEqual(
            [call[0] for call in self.device.method_calls],
            [
                "detect_and_set_adb_keyboard",
                "clear_text",
                "type_text",
                "restore_keyboard",
            ],
        )

    def test_type_failure_restores_and_remains_failure(self):
        self.device.type_text.side_effect = RuntimeError("type failed")
        result = self.execute()
        self.assertFalse(result.success)
        self.assertIn("type failed", result.message)
        self.assert_restored()

    def test_clear_failure_restores_without_typing(self):
        self.device.clear_text.side_effect = RuntimeError("clear failed")
        result = self.execute()
        self.assertFalse(result.success)
        self.device.type_text.assert_not_called()
        self.assert_restored()

    def test_switch_delay_failure_restores(self):
        def fail_delay(delay):
            if delay == 0.11:
                raise RuntimeError("switch delay failed")

        self.sleep_mock.side_effect = fail_delay
        self.assertFalse(self.execute().success)
        self.assert_restored()

    def test_post_input_delay_failure_restores(self):
        def fail_delay(delay):
            if delay == 0.33:
                raise RuntimeError("input delay failed")

        self.sleep_mock.side_effect = fail_delay
        self.assertFalse(self.execute().success)
        self.assert_restored()

    def test_keyboard_interrupt_restores_and_propagates(self):
        self.device.type_text.side_effect = KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            self.execute()
        self.assert_restored()

    def test_detection_failure_does_not_restore_unknown_ime(self):
        self.device.detect_and_set_adb_keyboard.side_effect = RuntimeError(
            "detect failed"
        )
        self.assertFalse(self.execute().success)
        self.device.restore_keyboard.assert_not_called()
        self.device.clear_text.assert_not_called()

    def test_cleanup_failure_is_not_reported_as_success(self):
        self.device.restore_keyboard.side_effect = RuntimeError("restore failed")
        result = self.execute()
        self.assertFalse(result.success)
        self.assertIn("restore failed", result.message)
        self.assert_restored()

    def test_empty_original_ime_is_passed_through(self):
        self.device.detect_and_set_adb_keyboard.return_value = ""
        self.assertTrue(self.execute().success)
        self.device.restore_keyboard.assert_called_once_with("", "mock-device")

    def test_type_name_alias_has_the_same_cleanup_contract(self):
        self.device.type_text.side_effect = RuntimeError("type failed")
        self.assertFalse(self.execute("Type_Name").success)
        self.assert_restored()

    def test_primary_interrupt_survives_ordinary_cleanup_failure(self):
        primary = KeyboardInterrupt("user cancelled")
        cleanup = RuntimeError("restore failed")
        self.device.type_text.side_effect = primary
        self.device.restore_keyboard.side_effect = cleanup
        with self.assertRaises(KeyboardInterrupt) as raised:
            self.execute()
        self.assertIs(raised.exception, primary)
        self.assertIs(raised.exception.__cause__, cleanup)
        self.assert_restored()

    def test_cleanup_interrupt_survives_ordinary_primary_failure(self):
        cleanup = KeyboardInterrupt("cancelled during restore")
        self.device.type_text.side_effect = RuntimeError("type failed")
        self.device.restore_keyboard.side_effect = cleanup
        with self.assertRaises(KeyboardInterrupt) as raised:
            self.execute()
        self.assertIs(raised.exception, cleanup)
        self.assert_restored()

    def test_ordinary_double_failure_reports_primary_error(self):
        self.device.type_text.side_effect = RuntimeError("type failed")
        self.device.restore_keyboard.side_effect = RuntimeError("restore failed")
        result = self.execute()
        self.assertFalse(result.success)
        self.assertIn("type failed", result.message)
        self.assert_restored()

    def test_direct_double_failure_keeps_cleanup_as_cause(self):
        primary = RuntimeError("type failed")
        cleanup = RuntimeError("restore failed")
        self.device.type_text.side_effect = primary
        self.device.restore_keyboard.side_effect = cleanup
        with self.assertRaises(RuntimeError) as raised:
            self.handler._handle_type({"text": "test"}, 100, 200)
        self.assertIs(raised.exception, primary)
        self.assertIs(raised.exception.__cause__, cleanup)
        self.assert_restored()
