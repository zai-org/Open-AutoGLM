from web_server import save_history, load_history
import time

print("1. Loading history...")
h = load_history()
print(f"Current history length: {len(h)}")

print("2. Saving test item...")
save_history("Test Task", "Test Result", "success", [])

print("3. Reloading history...")
h_new = load_history()
print(f"New history length: {len(h_new)}")

if len(h_new) > len(h):
    print("SUCCESS: History saved.")
else:
    print("FAILURE: History count did not increase.")
