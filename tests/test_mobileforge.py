import json
import unittest

from phone_agent.actions.handler import parse_action
from phone_agent.mobileforge import parse_mobileforge_response


class MobileForgeProtocolTest(unittest.TestCase):
    def parse(self, arguments):
        response = (
            "<thinking>next</thinking><tool_call>"
            + json.dumps({"name": "mobile_use", "arguments": arguments})
            + "</tool_call><conclusion>ok</conclusion>"
        )
        thinking, action = parse_mobileforge_response(response)
        return thinking, action, parse_action(action)

    def test_click(self):
        thinking, action, parsed = self.parse(
            {"action": "click", "coordinate": [250, 750]}
        )
        self.assertEqual(thinking, "next")
        self.assertEqual(action, 'do(action="Tap", element=[250, 750])')
        self.assertEqual(parsed["element"], [250, 750])

    def test_swipe(self):
        _, action, parsed = self.parse(
            {
                "action": "swipe",
                "coordinate": [500, 800],
                "coordinate2": [500, 200],
            }
        )
        self.assertEqual(action, 'do(action="Swipe", start=[500, 800], end=[500, 200])')
        self.assertEqual(parsed["start"], [500, 800])
        self.assertEqual(parsed["end"], [500, 200])

    def test_text_preserves_quotes(self):
        _, _, parsed = self.parse({"action": "type", "text": 'Hello "HarmonyOS"'})
        self.assertEqual(parsed["text"], 'Hello "HarmonyOS"')

    def test_launch(self):
        _, _, parsed = self.parse({"action": "open", "text": "Settings"})
        self.assertEqual(parsed["action"], "Launch")
        self.assertEqual(parsed["app"], "Settings")

    def test_system_and_terminal_actions(self):
        self.assertEqual(
            self.parse({"action": "system_button", "button": "Back"})[2]["action"],
            "Back",
        )
        self.assertEqual(
            self.parse({"action": "terminate", "status": "success"})[2]["_metadata"],
            "finish",
        )

    def test_rejects_unknown_action(self):
        with self.assertRaisesRegex(ValueError, "Unsupported MobileForge action"):
            self.parse({"action": "key", "text": "volume_up"})


if __name__ == "__main__":
    unittest.main()
