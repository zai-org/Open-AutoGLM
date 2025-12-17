import requests
import json

BASE_URL = "http://localhost:5000/api"

try:
    res = requests.get(f"{BASE_URL}/status")
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(e)
