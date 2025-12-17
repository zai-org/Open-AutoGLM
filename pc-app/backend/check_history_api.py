import requests
import json

BASE_URL = "http://localhost:5000/api"

try:
    print("Calling GET /api/history...")
    res = requests.get(f"{BASE_URL}/history")
    history = res.json().get("history", [])
    print(f"API returned {len(history)} items.")
    if len(history) > 0:
        print(f"First item task: {history[0].get('task')}")
        if history[0].get('task') == "Test Task":
            print("SUCCESS: API returns the test task.")
        else:
            print("WARNING: API returns something else.")
    else:
        print("FAILURE: API returns empty history.")
except Exception as e:
    print(f"Error: {e}")
