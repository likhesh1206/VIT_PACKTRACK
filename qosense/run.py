"""
Detection of Compromised Smart-Home Devices Using Encrypted Traffic Behaviour
Computer Networks (CN) — Project Review 1 Visual Evaluation Suite
Starts the FastAPI application with Uvicorn and launches the interactive visualizer.
"""

import sys
import os
import webbrowser
import threading
import time
import uvicorn

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def open_browser_delayed(url: str, delay_sec: float = 1.2):
    time.sleep(delay_sec)
    print(f"\n[CN Review 1] Opening interactive visualizer in browser: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    print("=" * 78)
    print("  Detection of Compromised Smart-Home Devices Using Encrypted Traffic Behaviour")
    print("  Computer Networks (CN) — Project Review 1 Visual Evaluation Suite")
    print("=" * 78)
    print(f"[*] Visualizer Dashboard: {url}")
    print(f"[*] Live IoT Telemetry:    {url}/api/iot/telemetry")
    print(f"[*] Model Evaluation:     {url}/api/iot/model-summary")
    print(f"[*] Review Documentation: {url}/api/iot/review-data")
    print(f"[*] WebSocket Feed:       ws://{host}:{port}/ws/telemetry")
    print("=" * 78)

    # Launch browser in a background daemon thread
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()

    # Run Uvicorn server
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        log_level="info",
        reload=False
    )


if __name__ == "__main__":
    main()
