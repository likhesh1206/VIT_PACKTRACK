import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print("Python version:", sys.version)

modules = ["fastapi", "uvicorn", "psutil", "scapy", "websockets", "sqlite3"]
for mod in modules:
    try:
        __import__(mod)
        print(f"[OK] {mod} is installed and imported successfully.")
    except ImportError as e:
        print(f"[FAIL] {mod}: {e}")
