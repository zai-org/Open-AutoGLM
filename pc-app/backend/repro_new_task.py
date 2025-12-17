import requests
import time
import json

BASE_URL = "http://localhost:5000/api"

def reset_status():
    print("Resetting Status (Simulating 'New Task' click)...")
    requests.post(f"{BASE_URL}/status/reset")

def get_history():
    res = requests.get(f"{BASE_URL}/history")
    return res.json().get("history", [])

def main():
    # 1. Reset
    reset_status()
    
    # Wait a moment for state update if any (though reset is synchronous)
    time.sleep(0.5)

    # 2. Check History
    print("Fetching History...")
    history = get_history()
    
    if len(history) > 0:
        first = history[0]
        print(f"First Item: ID={first.get('id')}, Task='{first.get('task')}', Status={first.get('status')}")
        
        if first.get('task') == "New Task":
            print("SUCCESS: 'New Task' item appeared in history.")
            if first.get('id'):
                print(f"SUCCESS: Item has ID {first.get('id')}")
            else:
                print("FAILURE: Item missing ID.")
        else:
            print("FAILURE: First item is not 'New Task'.")
            print(f"Found: {first.get('task')}")
    else:
        print("FAILURE: History is empty.")

if __name__ == "__main__":
    main()
