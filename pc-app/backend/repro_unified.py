import requests
import time
import json

BASE_URL = "http://localhost:5000/api"

def reset_status():
    requests.post(f"{BASE_URL}/status/reset")

def start_task(task_name):
    requests.post(f"{BASE_URL}/execute", json={"task": task_name})

def get_history():
    res = requests.get(f"{BASE_URL}/history")
    return res.json().get("history", [])

def main():
    print("1. Resetting Status...")
    reset_status()

    print("2. Starting Task 'Unified Test'...")
    start_task("Unified Test")
    
    # Wait a moment for thread to start
    time.sleep(0.5)

    print("3. Fetching History...")
    history = get_history()
    
    if len(history) > 0:
        first = history[0]
        print(f"First Item: ID={first.get('id')}, Task={first.get('task')}, Status={first.get('status')}")
        
        if first.get('task') == "Unified Test" and first.get('status') == "running":
            print("SUCCESS: Running task appears in history!")
        else:
            print("FAILURE: First item is not the running task.")
    else:
        print("FAILURE: History is empty.")

if __name__ == "__main__":
    main()
