import requests
import time
import json

BASE_URL = "http://localhost:5000/api"

def reset_status():
    print("Resetting Status...")
    requests.post(f"{BASE_URL}/status/reset")

def start_task(task_name):
    print(f"Starting Task: {task_name}")
    requests.post(f"{BASE_URL}/execute", json={"task": task_name})

def get_history():
    res = requests.get(f"{BASE_URL}/history")
    return res.json().get("history", [])

def main():
    # 1. Start a task
    task_name = f"Archive Test {int(time.time())}"
    start_task(task_name)
    time.sleep(1) # Let it start

    # 2. Reset (New Task) without stopping manually
    print("Clicking 'New Task' (Reset)...")
    reset_status()
    time.sleep(0.5)

    # 3. Check if previous task is in history
    history = get_history()
    print(f"History Length: {len(history)}")
    
    found = False
    for item in history:
        print(f" - {item.get('task')} ({item.get('status')})")
        if item.get('task') == task_name:
            found = True
    
    if found:
        print("SUCCESS: The task was auto-saved to history.")
    else:
        print("FAILURE: The task was lost.")

if __name__ == "__main__":
    main()
