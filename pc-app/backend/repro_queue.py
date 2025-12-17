import requests
import time
import json

BASE_URL = "http://localhost:5000/api"

def stop_task():
    try:
        requests.post(f"{BASE_URL}/stop")
        print("Sent Stop signal.")
    except:
        pass

def wait_for_idle():
    print("Waiting for idle...")
    for _ in range(10):
        s = get_status()
        if not s.get('running'):
            print("System is IDLE.")
            return True
        time.sleep(1)
    print("Timeout waiting for idle.")
    return False

def add_to_queue(task="Queue Test Task Idle"):
    print(f"Adding task to queue: {task}")
    try:
        res = requests.post(f"{BASE_URL}/queue/add", json={"task": task})
        print(f"Add Result: {res.json()}")
    except Exception as e:
        print(f"Error adding to queue: {e}")

def get_queue():
    try:
        res = requests.get(f"{BASE_URL}/queue/list")
        q = res.json().get("queue", [])
        return q
    except:
        return []

def get_status():
    try:
        res = requests.get(f"{BASE_URL}/status")
        return res.json()
    except:
        return {}

def main():
    print("--- Queue Reproduction Test (Idle) ---")
    
    # Ensure IDLE
    stop_task()
    if not wait_for_idle():
        print("Could not get to idle state.")
        return

    # Add to queue
    add_to_queue()

    # Rapidly check queue
    print("\nChecking Queue immediately...")
    for i in range(5):
        q = get_queue()
        print(f"Queue Length check {i}: {len(q)}")
        if len(q) > 0:
            print("  -> Found in queue!")
        time.sleep(0.5)

    status = get_status()
    print(f"\nFinal Status: Running={status.get('running')}, Task='{status.get('task')}'")
    
    if status.get('running') and "Queue Test Task Idle" in status.get('task'):
        print("\nCONCLUSION: Task moved from Queue to Running.")
    elif len(q) > 0:
        print("\nCONCLUSION: Task stuck in Queue (Process thread didn't pick it up?)")
    else:
        print("\nCONCLUSION: Task LOST? (Not in queue, not running)")

if __name__ == "__main__":
    main()
