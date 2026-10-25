"""
QoSense Automated Test Suite
Validates Traffic Classification, RFC 3550 Jitter, QoS Composite Scoring,
and Priority Queue Scheduler Behavior.
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.classifier import TrafficClassifier
from backend.qos_engine import QoSEngine
from backend.prioritizer import PriorityScheduler
from backend.config import PRIORITY_P0_HIGH, PRIORITY_P1_MEDIUM, PRIORITY_P2_LOW
import backend.database as db


def test_traffic_classifier():
    print("[*] Testing TrafficClassifier...")
    
    # 1. Gaming Port 27015
    res = TrafficClassifier.classify("192.168.1.10", "1.2.3.4", 51234, 27015, "UDP")
    assert res["category"] == "Gaming", f"Expected Gaming, got {res['category']}"
    assert res["priority"] == PRIORITY_P0_HIGH
    assert res["latency_sensitive"] is True

    # 2. VoIP Port 5060
    res = TrafficClassifier.classify("192.168.1.10", "1.2.3.4", 5060, 5060, "UDP")
    assert res["category"] == "VoIP / Audio"
    assert res["priority"] == PRIORITY_P0_HIGH

    # 3. Bulk Download Port 6881 (BitTorrent)
    res = TrafficClassifier.classify("192.168.1.10", "1.2.3.4", 6881, 6881, "TCP")
    assert res["category"] == "Bulk Download"
    assert res["priority"] == PRIORITY_P2_LOW

    # 4. Web Browsing Port 443
    res = TrafficClassifier.classify("192.168.1.10", "1.2.3.4", 55432, 443, "TCP")
    assert res["category"] == "Web Browsing"
    assert res["priority"] == PRIORITY_P1_MEDIUM

    print("  --> TrafficClassifier passed!")


def test_rfc3550_jitter():
    print("[*] Testing RFC 3550 Jitter Algorithm...")
    # Initial jitter 2.0 ms. Transit difference 18.0 ms.
    # New Jitter = 2.0 + (18.0 - 2.0) / 16 = 2.0 + 1.0 = 3.0 ms
    j = QoSEngine.calculate_jitter_rfc3550(2.0, 10.0, 28.0)
    assert round(j, 3) == 3.0, f"Expected 3.0, got {j}"

    # Another step with 0 diff: Jitter should decay by (0 - 3.0)/16 = -0.1875
    j2 = QoSEngine.calculate_jitter_rfc3550(j, 10.0, 10.0)
    assert round(j2, 4) == 2.8125, f"Expected 2.8125, got {j2}"

    print("  --> RFC 3550 Jitter algorithm passed!")


def test_qos_scoring():
    print("[*] Testing QoS Composite Scoring...")

    # Edge Case 1: Pristine network (20ms latency, 1ms jitter, 0% loss)
    clean = QoSEngine.compute_qos_score(20.0, 1.0, 0.0)
    assert clean["status"] == "Excellent"
    assert clean["score"] >= 90.0, f"Expected >= 90, got {clean['score']}"

    # Edge Case 2: Congested network (180ms latency, 35ms jitter, 4.0% loss)
    congested = QoSEngine.compute_qos_score(180.0, 35.0, 4.0)
    assert congested["status"] == "Poor"
    assert congested["score"] < 50.0, f"Expected < 50, got {congested['score']}"

    print("  --> QoS Scoring passed!")


def test_prioritizer_scheduler():
    print("[*] Testing PriorityScheduler under Congestion...")
    
    scheduler = PriorityScheduler(link_capacity_mbps=50.0)
    
    flows = [
        {"id": "game-1", "priority": PRIORITY_P0_HIGH, "demand_mbps": 2.5, "protocol": "UDP", "base_latency": 15.0, "base_jitter": 1.5},
        {"id": "video-1", "priority": PRIORITY_P1_MEDIUM, "demand_mbps": 18.0, "protocol": "TCP", "base_latency": 25.0, "base_jitter": 3.0},
        {"id": "bulk-1", "priority": PRIORITY_P2_LOW, "demand_mbps": 45.0, "protocol": "TCP", "base_latency": 30.0, "base_jitter": 5.0}
    ]
    # Total demand = 2.5 + 18.0 + 45.0 = 65.5 Mbps (> 50.0 Mbps bottleneck)

    # 1. Test WITH Prioritization ON
    scheduler.set_prioritization_enabled(True)
    res_qos = scheduler.schedule_and_shape(flows)
    
    assert res_qos["is_congested"] is True
    game_qos = res_qos["flow_metrics"]["game-1"]
    bulk_qos = res_qos["flow_metrics"]["bulk-1"]
    
    # Under QoS, Gaming MUST receive full bandwidth with no packet loss
    assert game_qos["allocated_mbps"] == 2.5
    assert game_qos["packet_loss_pct"] == 0.0
    assert game_qos["latency_ms"] < 40.0
    # Bulk MUST be throttled
    assert bulk_qos["throttled"] is True
    assert bulk_qos["allocated_mbps"] < 45.0

    # 2. Test WITHOUT Prioritization (FIFO / Bufferbloat)
    scheduler.set_prioritization_enabled(False)
    res_fifo = scheduler.schedule_and_shape(flows)
    
    game_fifo = res_fifo["flow_metrics"]["game-1"]
    # In FIFO, Gaming suffers packet drops and significant queueing delay (> 80ms vs < 40ms)
    assert game_fifo["latency_ms"] > 80.0, f"Expected bufferbloat latency > 80ms, got {game_fifo['latency_ms']}"
    assert game_fifo["packet_loss_pct"] > 0.0

    print("  --> PriorityScheduler QoS vs FIFO verification passed!")


def test_database():
    print("[*] Testing Database Logging & Analytics Summary...")
    db.init_db()
    db.log_metrics(
        total_mbps=42.5,
        download_mbps=34.8,
        upload_mbps=7.7,
        avg_latency_ms=24.5,
        avg_jitter_ms=2.1,
        packet_loss_pct=0.1,
        qos_score=94.2,
        qos_status="Excellent",
        is_congested=False,
        active_flows_count=4,
        prioritization_enabled=True
    )
    summary = db.get_analytics_summary()
    assert summary["total_samples"] >= 1
    assert summary["avg_qos_score"] > 0.0
    print("  --> Database operations passed!")


if __name__ == "__main__":
    print("=" * 60)
    print(" Running QoSense Verification Tests")
    print("=" * 60)
    test_traffic_classifier()
    test_rfc3550_jitter()
    test_qos_scoring()
    test_prioritizer_scheduler()
    test_database()
    print("=" * 60)
    print(" ALL TESTS PASSED SUCCESSFULLY! ")
    print("=" * 60)
