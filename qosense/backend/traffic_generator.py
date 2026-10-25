"""
QoSense Traffic Simulator
Generates realistic multi-flow synthetic traffic and interactive demonstration scenarios.
"""

import time
import random
from typing import List, Dict, Any
from backend.classifier import TrafficClassifier
from backend.config import (
    DEFAULT_LINK_CAPACITY_MBPS,
    PRIORITY_P0_HIGH,
    PRIORITY_P1_MEDIUM,
    PRIORITY_P2_LOW,
)


class TrafficGenerator:
    """
    Maintains simulated flows and produces realistic network telemetry.
    """

    def __init__(self):
        self.current_scenario = "clean_gaming"
        self.flows: List[Dict[str, Any]] = []
        self.load_scenario("clean_gaming")

    def load_scenario(self, scenario_name: str):
        """Loads a predefined traffic mix scenario."""
        self.current_scenario = scenario_name

        if scenario_name == "clean_gaming":
            # Scenario 1: Clean network with Gaming + Light Web
            self.flows = [
                self._create_flow(
                    flow_id="flow-game-1",
                    app_name="CS:GO / Valorant Match",
                    src_ip="192.168.1.105",
                    dst_ip="162.254.192.40",
                    src_port=52114,
                    dst_port=27015,
                    proto="UDP",
                    base_demand=2.2,
                    base_latency=18.0,
                    base_jitter=1.8,
                    avg_pkt_size=128
                ),
                self._create_flow(
                    flow_id="flow-web-1",
                    app_name="Wikipedia / Web Browsing",
                    src_ip="192.168.1.102",
                    dst_ip="198.35.26.96",
                    src_port=49882,
                    dst_port=443,
                    proto="TCP",
                    base_demand=1.4,
                    base_latency=35.0,
                    base_jitter=3.5,
                    avg_pkt_size=850
                ),
                self._create_flow(
                    flow_id="flow-dns-1",
                    app_name="DNS Resolver Queries",
                    src_ip="192.168.1.1",
                    dst_ip="1.1.1.1",
                    src_port=58912,
                    dst_port=53,
                    proto="UDP",
                    base_demand=0.2,
                    base_latency=12.0,
                    base_jitter=1.0,
                    avg_pkt_size=75
                ),
            ]

        elif scenario_name == "streaming_work":
            # Scenario 2: 4K Video Streaming + Zoom Conference
            self.flows = [
                self._create_flow(
                    flow_id="flow-stream-1",
                    app_name="YouTube 4K Ultra HD",
                    src_ip="192.168.1.110",
                    dst_ip="142.250.190.46",
                    src_port=54122,
                    dst_port=443,
                    proto="TCP",
                    base_demand=18.5,
                    base_latency=38.0,
                    base_jitter=4.2,
                    avg_pkt_size=1420
                ),
                self._create_flow(
                    flow_id="flow-voip-1",
                    app_name="Zoom Team Conference",
                    src_ip="192.168.1.108",
                    dst_ip="3.235.111.45",
                    src_port=51120,
                    dst_port=3478,
                    proto="UDP",
                    base_demand=2.8,
                    base_latency=28.0,
                    base_jitter=2.4,
                    avg_pkt_size=240
                ),
                self._create_flow(
                    flow_id="flow-web-2",
                    app_name="Cloud Docs Collaboration",
                    src_ip="192.168.1.104",
                    dst_ip="52.96.166.130",
                    src_port=50212,
                    dst_port=443,
                    proto="TCP",
                    base_demand=2.1,
                    base_latency=32.0,
                    base_jitter=3.0,
                    avg_pkt_size=920
                )
            ]

        elif scenario_name == "heavy_congestion":
            # Scenario 3: Massive Congestion (Gaming + 4K Stream + Huge Torrent/File Download)
            self.flows = [
                self._create_flow(
                    flow_id="flow-game-1",
                    app_name="Competitive Online Gaming",
                    src_ip="192.168.1.105",
                    dst_ip="162.254.192.40",
                    src_port=52114,
                    dst_port=27015,
                    proto="UDP",
                    base_demand=2.5,
                    base_latency=20.0,
                    base_jitter=2.0,
                    avg_pkt_size=128
                ),
                self._create_flow(
                    flow_id="flow-stream-1",
                    app_name="Netflix 4K HDR Stream",
                    src_ip="192.168.1.110",
                    dst_ip="198.38.118.151",
                    src_port=56100,
                    dst_port=443,
                    proto="TCP",
                    base_demand=16.0,
                    base_latency=36.0,
                    base_jitter=4.0,
                    avg_pkt_size=1420
                ),
                self._create_flow(
                    flow_id="flow-torrent-1",
                    app_name="BitTorrent Peer Sync",
                    src_ip="192.168.1.120",
                    dst_ip="185.125.190.39",
                    src_port=6881,
                    dst_port=6881,
                    proto="TCP",
                    base_demand=28.0,
                    base_latency=45.0,
                    base_jitter=6.0,
                    avg_pkt_size=1480
                ),
                self._create_flow(
                    flow_id="flow-bulk-2",
                    app_name="Steam 80GB Game Update",
                    src_ip="192.168.1.105",
                    dst_ip="151.101.1.69",
                    src_port=58990,
                    dst_port=80,
                    proto="TCP",
                    base_demand=22.0,
                    base_latency=40.0,
                    base_jitter=5.5,
                    avg_pkt_size=1460
                ),
            ]

        elif scenario_name == "voip_under_fire":
            # Scenario 4: VoIP call during aggressive file backups
            self.flows = [
                self._create_flow(
                    flow_id="flow-voip-1",
                    app_name="Executive VoIP Phone Call",
                    src_ip="192.168.1.15",
                    dst_ip="216.58.214.206",
                    src_port=5060,
                    dst_port=5060,
                    proto="UDP",
                    base_demand=0.8,
                    base_latency=22.0,
                    base_jitter=1.2,
                    avg_pkt_size=180
                ),
                self._create_flow(
                    flow_id="flow-ftp-1",
                    app_name="Offsite Database FTP Backup",
                    src_ip="192.168.1.200",
                    dst_ip="104.26.10.155",
                    src_port=20,
                    dst_port=20,
                    proto="TCP",
                    base_demand=48.0,
                    base_latency=42.0,
                    base_jitter=7.0,
                    avg_pkt_size=1480
                ),
                self._create_flow(
                    flow_id="flow-web-3",
                    app_name="Web Portal Checkout",
                    src_ip="192.168.1.103",
                    dst_ip="151.101.65.140",
                    src_port=51104,
                    dst_port=443,
                    proto="TCP",
                    base_demand=1.8,
                    base_latency=30.0,
                    base_jitter=2.5,
                    avg_pkt_size=750
                )
            ]

    def _create_flow(
        self,
        flow_id: str,
        app_name: str,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        proto: str,
        base_demand: float,
        base_latency: float,
        base_jitter: float,
        avg_pkt_size: int
    ) -> Dict[str, Any]:
        classification = TrafficClassifier.classify(
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=proto,
            avg_packet_size=avg_pkt_size
        )
        return {
            "id": flow_id,
            "app_name": app_name,
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": proto,
            "category": classification["category"],
            "priority": classification["priority"],
            "service": classification["service"],
            "base_demand_mbps": base_demand,
            "demand_mbps": base_demand,
            "base_latency": base_latency,
            "base_jitter": base_jitter,
            "avg_packet_size": avg_pkt_size,
            "packet_count": random.randint(150, 600),
            "byte_count": int(base_demand * 125000 * 10),
            "start_time": time.time() - random.randint(30, 300)
        }

    def generate_tick(self) -> List[Dict[str, Any]]:
        """
        Adds realistic slight jitter/variance to flow demands each second,
        simulating live packet traffic.
        """
        active_flows = []
        for flow in self.flows:
            # Add natural 3-6% fluctuation
            variance = random.uniform(0.96, 1.04)
            current_demand = round(flow["base_demand_mbps"] * variance, 2)
            flow["demand_mbps"] = current_demand
            
            # Increment packet & byte counts
            pkt_rate = max(10, int((current_demand * 125000) / flow["avg_packet_size"]))
            flow["packet_count"] += pkt_rate
            flow["byte_count"] += int(current_demand * 125000)
            
            active_flows.append(dict(flow))
            
        return active_flows
