import requests
import time
import sys

BASE_URL = "http://localhost:5000/api"

def check_status():
    try:
        res = requests.get(f"{BASE_URL}/status")
        return res.json()
    except Exception as e:
        print(f"Error checking status: {e}")
        return None

def reset_status():
    try:
        print(f"Sending POST to {BASE_URL}/status/reset...")
        res = requests.post(f"{BASE_URL}/status/reset")
        print(f"Response Status: {res.status_code}")
        print(f"Response Text: {res.text}")
        return res.json()
    except Exception as e:
        print(f"Error resetting status: {e}")
        return None

def main():
    print("1. Checking initial status...", flush=True)
    status = check_status()
    if status:
        print(f"   Running: {status.get('running')}", flush=True)
        print(f"   Task: {status.get('task')}", flush=True)
    else:
        print("   Failed to get status")

    print("\n2. Calling Reset...", flush=True)
    result = reset_status()
    print(f"   Reset Result: {result}", flush=True)

    print("\n3. Checking status after reset...", flush=True)
    status = check_status()
    if status:
        print(f"   Running: {status.get('running')}", flush=True)
        print(f"   Task: {status.get('task')}", flush=True)
    
        if status.get('task') == "":
             print("\nSUCCESS: Task cleared.", flush=True)
        else:
             print("\nFAILURE: Task not cleared.", flush=True)

if __name__ == "__main__":
    main()
