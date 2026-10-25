"""
QoSense End-to-End Server & WebSocket Integration Test
Spins up uvicorn server on localhost:8008, verifies:
1. Static files serving (HTML, CSS, JS, Chart.js)
2. All REST API endpoints (GET /api/telemetry, GET /api/history, GET /api/report, POST controls)
3. WebSocket streaming (/ws/telemetry)
4. QoS priorization effect in live simulation (FIFO bufferbloat vs QoS protection)
"""

import sys
import os
import time
import json
import threading
import urllib.request
import urllib.error
import asyncio
import websockets

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn
from backend.main import app

TEST_HOST = "127.0.0.1"
TEST_PORT = 8008
BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}"
WS_URL = f"ws://{TEST_HOST}:{TEST_PORT}/ws/telemetry"


class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        config = uvicorn.Config(app, host=TEST_HOST, port=TEST_PORT, log_level="warning")
        self.server = uvicorn.Server(config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def http_get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.getcode(), response.read()


def http_post_json(path, data):
    url = f"{BASE_URL}{path}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.getcode(), json.loads(response.read().decode("utf-8"))


async def test_websocket():
    print("[*] Connecting to WebSocket: " + WS_URL)
    async with websockets.connect(WS_URL) as ws:
        msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
        data = json.loads(msg)
        assert "timestamp" in data, "Missing timestamp in WS payload"
        assert "network_metrics" in data, "Missing network_metrics in WS payload"
        assert "flows" in data, "Missing flows in WS payload"
        assert "queue_occupancy" in data, "Missing queue_occupancy in WS payload"
        print(f"  --> WebSocket received telemetry tick! Active flows: {len(data['flows'])}, QoS: {data['network_metrics']['qos_score']}")


def run_all_tests():
    print("=" * 70)
    print(" QoSense Comprehensive End-to-End System Verification")
    print("=" * 70)

    # 1. Start Server
    print("[1/5] Starting QoSense Uvicorn server in background...")
    server_thread = ServerThread()
    server_thread.start()

    # Wait for server ready
    ready = False
    for _ in range(15):
        try:
            code, _ = http_get("/")
            if code == 200:
                ready = True
                break
        except Exception:
            time.sleep(0.5)

    assert ready, "Server failed to start within 7.5 seconds!"
    print("  --> Server successfully running at " + BASE_URL)

    # Give broadcaster 1.2s to generate first telemetry tick
    time.sleep(1.2)

    try:
        # 2. Test Static Files
        print("[2/5] Verifying Static Web Assets...")
        
        # Index HTML
        code, html_bytes = http_get("/")
        assert code == 200
        html = html_bytes.decode("utf-8")
        assert "QoSense" in html
        assert "COMPUTER NETWORKS LAB" in html
        print("  --> GET / (index.html): OK (Found brand title)")

        # CSS
        code, css_bytes = http_get("/static/css/style.css")
        assert code == 200
        assert b"--accent-cyan" in css_bytes
        print("  --> GET /static/css/style.css: OK (Design system tokens verified)")

        # Chart.js local bundle
        code, chart_bytes = http_get("/static/js/chart.umd.min.js")
        assert code == 200 and len(chart_bytes) > 50000
        print(f"  --> GET /static/js/chart.umd.min.js: OK ({len(chart_bytes)} bytes)")

        # App JS
        code, js_bytes = http_get("/static/js/app.js")
        assert code == 200 and b"initCharts" in js_bytes
        print("  --> GET /static/js/app.js: OK (Found application script)")

        # 3. Test REST API Endpoints
        print("[3/5] Verifying REST APIs...")
        
        # /api/telemetry
        code, body = http_get("/api/telemetry")
        assert code == 200
        telem = json.loads(body.decode("utf-8"))
        assert "network_metrics" in telem
        print(f"  --> GET /api/telemetry: OK (Throughput: {telem['network_metrics']['total_mbps']} Mbps, Score: {telem['network_metrics']['qos_score']})")

        # /api/history
        code, body = http_get("/api/history?limit=10")
        assert code == 200
        hist = json.loads(body.decode("utf-8"))
        assert isinstance(hist, list) and len(hist) >= 1
        print(f"  --> GET /api/history: OK (Retrieved {len(hist)} historical data points)")

        # /api/report
        code, body = http_get("/api/report")
        assert code == 200
        report = json.loads(body.decode("utf-8"))
        assert "summary" in report
        print(f"  --> GET /api/report: OK (Total logged samples: {report['summary']['total_samples']})")

        # POST /api/control/capacity
        code, resp = http_post_json("/api/control/capacity", {"capacity_mbps": 40.0})
        assert code == 200 and resp["link_capacity_mbps"] == 40.0
        print("  --> POST /api/control/capacity: OK (Updated bottleneck to 40.0 Mbps)")

        # POST /api/control/scenario
        code, resp = http_post_json("/api/control/scenario", {"scenario": "heavy_congestion"})
        assert code == 200 and resp["scenario"] == "heavy_congestion"
        print("  --> POST /api/control/scenario: OK (Loaded 'heavy_congestion')")

        # POST /api/control/prioritization
        code, resp = http_post_json("/api/control/prioritization", {"enabled": True})
        assert code == 200 and resp["prioritization_enabled"] is True
        print("  --> POST /api/control/prioritization (True): OK")

        # POST /api/control/mode
        code, resp = http_post_json("/api/control/mode", {"mode": "live"})
        assert code == 200 and resp["mode"] == "live"
        print("  --> POST /api/control/mode (live): OK")
        # switch back to simulation
        code, resp = http_post_json("/api/control/mode", {"mode": "simulation"})
        assert code == 200 and resp["mode"] == "simulation"
        print("  --> POST /api/control/mode (simulation): OK")

        # 4. Test WebSocket Stream
        print("[4/5] Verifying WebSocket Real-Time Telemetry Stream...")
        asyncio.run(test_websocket())

        # 5. Live Scenario Verification: QoS vs FIFO
        print("[5/5] Testing QoS Prioritization Mechanics in Live Flow...")
        
        # Load heavy congestion scenario with link capacity = 40 Mbps
        http_post_json("/api/control/capacity", {"capacity_mbps": 40.0})
        http_post_json("/api/control/scenario", {"scenario": "heavy_congestion"})
        
        # Part A: With Prioritization ON
        http_post_json("/api/control/prioritization", {"enabled": True})
        time.sleep(1.5)  # Wait for broadcast tick
        _, body = http_get("/api/telemetry")
        t_qos = json.loads(body.decode("utf-8"))
        assert t_qos["is_congested"] is True, "Link should be congested under heavy scenario"
        
        game_flow_qos = next(f for f in t_qos["flows"] if "Gaming" in f["category"] or "game" in f["id"])
        torrent_flow_qos = next(f for f in t_qos["flows"] if "Bulk" in f["category"] or "torrent" in f["id"])
        
        print(f"  [QoS Active] Gaming Latency: {game_flow_qos['latency_ms']} ms | Loss: {game_flow_qos['packet_loss_pct']}%")
        print(f"  [QoS Active] Bulk Torrent Throttled: {torrent_flow_qos['throttled']} | Allocated: {torrent_flow_qos['allocated_mbps']} Mbps")
        assert game_flow_qos["latency_ms"] <= 45.0, f"Gaming latency too high under QoS: {game_flow_qos['latency_ms']}"
        assert game_flow_qos["packet_loss_pct"] == 0.0, "Gaming suffered packet loss under QoS!"
        assert torrent_flow_qos["throttled"] is True, "Bulk flow was not throttled under congestion!"

        # Part B: With Prioritization OFF (FIFO Bufferbloat)
        http_post_json("/api/control/prioritization", {"enabled": False})
        time.sleep(1.5)  # Wait for broadcast tick
        _, body = http_get("/api/telemetry")
        t_fifo = json.loads(body.decode("utf-8"))
        
        game_flow_fifo = next(f for f in t_fifo["flows"] if "Gaming" in f["category"] or "game" in f["id"])
        print(f"  [FIFO / Unmanaged] Gaming Latency: {game_flow_fifo['latency_ms']} ms | Loss: {game_flow_fifo['packet_loss_pct']}%")
        assert game_flow_fifo["latency_ms"] > 80.0, f"Expected bufferbloat latency > 80ms, got {game_flow_fifo['latency_ms']}"
        assert game_flow_fifo["packet_loss_pct"] > 0.0, "Expected packet loss in FIFO buffer overflow"

        print("  --> QoS vs FIFO real-time behavior successfully demonstrated!")

        print("=" * 70)
        print(" ALL END-TO-END VERIFICATIONS PASSED WITH ZERO ERRORS! ")
        print("=" * 70)

    finally:
        server_thread.stop()


if __name__ == "__main__":
    run_all_tests()
