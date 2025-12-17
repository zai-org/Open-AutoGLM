import requests
import json
import time

BASE_URL = "http://localhost:5000/api"
HISTORY_FILE = "task_history.json"

def mock_history_file():
    mock_data = [
        {
            "id": "mock_123",
            "task": "Mock Completed Task",
            "result": "Done",
            "status": "success",
            "steps": [],
            "timestamp": "2025-01-01 12:00:00"
        }
    ]
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, ensure_ascii=False)
    print("Injected 1 mock task into history file.")

def reset_status():
    print("Resetting Status (New Task)...")
    requests.post(f"{BASE_URL}/status/reset")

def get_history():
    res = requests.get(f"{BASE_URL}/history")
    return res.json().get("history", [])

def main():
    # 1. Inject History
    mock_history_file()

    # 2. Reset Status (Start New Session)
    reset_status()
    time.sleep(0.5)

    # 3. Fetch History
    history = get_history()
    print(f"Fetched History Length: {len(history)}")
    
    tasks = [h.get('task') for h in history]
    print(f"Tasks: {tasks}")

    if "New Task" in tasks and "Mock Completed Task" in tasks:
        print("SUCCESS: Both New Task and History are present.")
    elif "New Task" in tasks and len(tasks) == 1:
        print("FAILURE: History was lost! Only New Task remains.")
    else:
        print("FAILURE: Unexpected state.")

if __name__ == "__main__":
    main()
