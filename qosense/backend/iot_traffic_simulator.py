"""
Smart Home IoT Traffic Simulator for CN Review 1
Simulates realistic encrypted network flows for popular, widely-known smart-home devices:
- Philips Hue / Wipro Smart WiFi Bulb (Lighting / Actuator)
- Amazon Echo Dot (Alexa Voice Assistant Speaker)
- TP-Link Tapo C200 / Mi 360° Smart Security Camera (Video Surveillance)
- Samsung Smart TV / Amazon Fire TV Stick 4K (Streaming Appliance)
- TP-Link Tapo / Wipro 16A Smart Plug (AC / Geyser Appliance Control)
- Amazon Ring Smart Video Doorbell (Access Control)

Includes real-world CVE citations, brand models, and attacks:
- Clean / Normal (Vendor Cloud Encrypted Telemetry)
- Mirai DDoS Flood (high pps, high bandwidth)
- Mirai Telnet/SSH Port Scan (high unique destination IPs)
- C&C Data Exfiltration / Rogue Communication
"""

import time
import random
from typing import Dict, List, Any
from backend.iot_classifier import iot_classifier

DEVICE_CONFIGS = {
    "bulb": {
        "id": "bulb",
        "name": "Philips Hue / Wipro Smart WiFi Bulb",
        "brand": "Philips / Wipro",
        "model": "Hue White & Color / Wipro 9W WiFi RGB",
        "ip": "192.168.1.101",
        "mac": "68:C6:3A:44:9C:12",
        "type": "Smart Lighting",
        "retail_presence": "Amazon / Flipkart Best-Seller (#1 Entry IoT)",
        "cve_case": "CVE-2020-6007 (Check Point Research demonstrated hacking Philips Hue bulbs to infiltrate home LANs)",
        "normal_service": "MQTT over TLS (Port 8883)",
        "normal_cloud_ip": "34.210.88.19 (Philips / Tuya Cloud)",
        "normal_port": 8883,
        "protocol": "TCP"
    },
    "speaker": {
        "id": "speaker",
        "name": "Amazon Echo Dot (Alexa Smart Speaker)",
        "brand": "Amazon",
        "model": "Echo Dot 4th/5th Gen with Alexa",
        "ip": "192.168.1.102",
        "mac": "FC:65:DE:29:41:88",
        "type": "Voice Assistant",
        "retail_presence": "Over 500M Alexa devices sold globally",
        "cve_case": "CVE-2020-10177 (Remote voice command injection & DNS rebinding)",
        "normal_service": "Alexa Voice Service / TLS 1.3",
        "normal_cloud_ip": "13.224.90.15 (Amazon AWS Cloud)",
        "normal_port": 443,
        "protocol": "TCP"
    },
    "camera": {
        "id": "camera",
        "name": "TP-Link Tapo C200 / Mi 360° Camera",
        "brand": "TP-Link / Xiaomi",
        "model": "Tapo C200 Full HD Pan/Tilt WiFi Cam",
        "ip": "192.168.1.103",
        "mac": "B4:E6:2D:11:8A:4F",
        "type": "Security Camera",
        "retail_presence": "Top-selling home CCTV in India & worldwide",
        "cve_case": "Mirai Botnet / CVE-2021-4045 (RTSP stack buffer overflow)",
        "normal_service": "Encrypted RTSP / TLS Stream",
        "normal_cloud_ip": "52.84.12.89 (Tapo Cloud)",
        "normal_port": 443,
        "protocol": "TCP"
    },
    "tv": {
        "id": "tv",
        "name": "Samsung Smart TV / Fire TV Stick 4K",
        "brand": "Samsung / Amazon",
        "model": "Crystal 4K UHD / Fire TV Stick 4K Max",
        "ip": "192.168.1.104",
        "mac": "00:E0:4C:68:01:23",
        "type": "Smart TV / Streaming",
        "retail_presence": "In 85%+ modern living rooms",
        "cve_case": "Weeping Angel exploit & malicious cryptomining botnet apps",
        "normal_service": "HTTPS / Widevine Encrypted Stream",
        "normal_cloud_ip": "54.239.28.85 (Netflix / Prime Video CDN)",
        "normal_port": 443,
        "protocol": "TCP"
    },
    "plug": {
        "id": "plug",
        "name": "TP-Link Tapo / Wipro 16A Smart Plug",
        "brand": "TP-Link / Wipro",
        "model": "Tapo P110 / Wipro 16A Energy Monitoring Plug",
        "ip": "192.168.1.105",
        "mac": "D8:F1:5B:78:3E:90",
        "type": "Appliance Relay (AC/Geyser)",
        "retail_presence": "Standard smart home plug for high-power appliances",
        "cve_case": "CVE-2023-40152 (Unauthenticated local UDP command injection)",
        "normal_service": "CoAP / Encrypted Telemetry",
        "normal_cloud_ip": "54.187.32.110 (Kasa/Tapo Cloud)",
        "normal_port": 5684,
        "protocol": "UDP"
    },
    "doorbell": {
        "id": "doorbell",
        "name": "Amazon Ring Smart Video Doorbell",
        "brand": "Amazon Ring",
        "model": "Ring Video Doorbell Wired (1080p)",
        "ip": "192.168.1.106",
        "mac": "AC:12:03:88:51:7E",
        "type": "Entrance Security",
        "retail_presence": "Market leader in smart doorbells",
        "cve_case": "CVE-2019-9483 (Wi-Fi password exfiltration via setup mode)",
        "normal_service": "Encrypted SIP / TLS Video Stream",
        "normal_cloud_ip": "52.216.14.92 (Ring AWS Cloud)",
        "normal_port": 443,
        "protocol": "TCP"
    }
}

class SmartHomeSimulator:
    def __init__(self):
        self.device_states = {
            "bulb": "normal",
            "speaker": "normal",
            "camera": "normal",
            "tv": "normal",
            "plug": "normal",
            "doorbell": "normal"
        }
        self.alerts_history: List[Dict[str, Any]] = []
        self.recent_flows: List[Dict[str, Any]] = []
        self.stats_history: List[Dict[str, Any]] = []
        self.flow_counter = 1000

    def set_device_state(self, device_id: str, attack_mode: str):
        if device_id in self.device_states:
            self.device_states[device_id] = attack_mode
            if attack_mode != "normal":
                cfg = DEVICE_CONFIGS[device_id]
                self._record_alert(
                    device_id=device_id,
                    device_name=cfg["name"],
                    ip=cfg["ip"],
                    attack_type=attack_mode,
                    severity="HIGH" if attack_mode == "ddos" else "CRITICAL" if attack_mode == "scan" else "MEDIUM"
                )

    def _record_alert(self, device_id: str, device_name: str, ip: str, attack_type: str, severity: str):
        attack_descriptions = {
            "ddos": "High-volume UDP/SYN flood detected. Packets/sec > 1000 pps targeting single external host.",
            "scan": "Mirai botnet scanning propagation detected. Device scanning multiple random external IPs on port 23/2323.",
            "exfil": "Encrypted outbound data surge detected contacting suspicious unauthenticated endpoint."
        }
        mitigations = {
            "ddos": "Rate-limit traffic at Gateway firewall, isolate device to Quarantine VLAN (VLAN 99).",
            "scan": "Block outbound TCP ports 23/2323/5555, trigger router ACL drop rule for MAC address.",
            "exfil": "Terminate active TCP session, reset device auth tokens, alert network administrator."
        }
        alert = {
            "id": f"ALT-{int(time.time())}-{random.randint(100, 999)}",
            "timestamp": time.strftime("%H:%M:%S"),
            "device_id": device_id,
            "device_name": device_name,
            "ip": ip,
            "attack_type": attack_type.upper(),
            "severity": severity,
            "description": attack_descriptions.get(attack_type, "Abnormal encrypted flow behavior detected."),
            "mitigation": mitigations.get(attack_type, "Isolate device from network.")
        }
        self.alerts_history.insert(0, alert)
        if len(self.alerts_history) > 35:
            self.alerts_history.pop()

    def generate_tick(self) -> Dict[str, Any]:
        """
        Generates 1-second simulation tick across all smart-home IoT devices.
        Returns full telemetry including flows, predictions, alerts, and aggregate stats.
        """
        self.flow_counter += 1
        current_time = time.strftime("%H:%M:%S")
        tick_flows = []
        total_pps = 0.0
        total_bps = 0.0
        malicious_count = 0

        for dev_id, state in self.device_states.items():
            cfg = DEVICE_CONFIGS[dev_id]
            proto = cfg["protocol"]

            if state == "normal":
                # Benign baseline: small packets, periodic pps, 1 cloud IP
                if dev_id == "bulb":
                    duration = round(random.uniform(0.5, 3.0), 2)
                    avg_pkt = round(random.uniform(64, 128), 1)
                    pps = round(random.uniform(0.8, 3.5), 1)
                elif dev_id == "speaker":
                    duration = round(random.uniform(1.0, 5.0), 2)
                    avg_pkt = round(random.uniform(200, 500), 1)
                    pps = round(random.uniform(2.0, 8.0), 1)
                elif dev_id == "camera":
                    duration = round(random.uniform(2.0, 8.0), 2)
                    avg_pkt = round(random.uniform(600, 1100), 1)
                    pps = round(random.uniform(14.0, 30.0), 1)
                elif dev_id == "tv":
                    duration = round(random.uniform(3.0, 12.0), 2)
                    avg_pkt = round(random.uniform(800, 1350), 1)
                    pps = round(random.uniform(18.0, 40.0), 1)
                elif dev_id == "plug":
                    duration = round(random.uniform(0.5, 2.0), 2)
                    avg_pkt = round(random.uniform(70, 140), 1)
                    pps = round(random.uniform(0.5, 2.0), 1)
                else:  # doorbell
                    duration = round(random.uniform(1.5, 6.0), 2)
                    avg_pkt = round(random.uniform(450, 950), 1)
                    pps = round(random.uniform(4.0, 14.0), 1)

                bps = round(pps * avg_pkt, 1)
                unique_ips = 1
                unique_ports = 1
                dst_ip = cfg["normal_cloud_ip"]
                dst_port = cfg["normal_port"]

            elif state == "ddos":
                # Mirai DDoS Attack: massive packet rate, saturated bandwidth, target IP
                duration = round(random.uniform(5.0, 25.0), 2)
                avg_pkt = round(random.choice([64.0, 512.0, 1280.0]) + random.uniform(-10, 10), 1)
                pps = round(random.uniform(650.0, 2800.0), 1)
                bps = round(pps * avg_pkt, 1)
                unique_ips = random.choice([1, 2])
                unique_ports = random.choice([1, 2])
                dst_ip = "198.51.100.42 (DDoS Victim)"
                dst_port = random.choice([80, 443, 8080, 53])
                proto = "UDP"

            elif state == "scan":
                # Mirai Telnet Scanner: scans hundreds of IPs, small SYN packets
                duration = round(random.uniform(0.5, 2.0), 2)
                avg_pkt = round(random.uniform(54.0, 68.0), 1)
                pps = round(random.uniform(180.0, 550.0), 1)
                bps = round(pps * avg_pkt, 1)
                unique_ips = random.randint(25, 180)
                unique_ports = random.randint(3, 15)
                dst_ip = f"{random.randint(11, 200)}.{random.randint(1, 254)}.0.0/16 (Scanning)"
                dst_port = 23  # Telnet
                proto = "TCP"

            elif state == "exfil":
                # C&C Beaconing / Data Exfiltration
                duration = round(random.uniform(8.0, 30.0), 2)
                avg_pkt = round(random.uniform(800.0, 1350.0), 1)
                pps = round(random.uniform(60.0, 180.0), 1)
                bps = round(pps * avg_pkt, 1)
                unique_ips = random.randint(2, 6)
                unique_ports = random.randint(2, 4)
                dst_ip = "185.220.101.5 (Rogue C&C)"
                dst_port = 4444
                proto = "TCP"

            flow_dict = {
                "flow_id": f"FLW-{self.flow_counter}-{dev_id[:3].upper()}",
                "timestamp": current_time,
                "device_id": dev_id,
                "device_name": cfg["name"],
                "brand": cfg["brand"],
                "model": cfg["model"],
                "src_ip": cfg["ip"],
                "src_mac": cfg["mac"],
                "dst_ip": dst_ip,
                "dst_port": dst_port,
                "protocol": proto,
                "duration": duration,
                "avg_packet_size": avg_pkt,
                "packets_per_sec": pps,
                "bytes_per_sec": bps,
                "unique_dest_ips": unique_ips,
                "unique_dest_ports": unique_ports,
                "compromise_state": state
            }

            # Run Random Forest Classifier
            classification = iot_classifier.predict_flow(flow_dict)
            flow_dict.update({
                "prediction": classification["prediction"],
                "classification_label": classification["label"],
                "confidence": classification["confidence"],
                "tree_votes": classification["tree_votes"],
                "anomalies": classification["anomalies"]
            })

            if classification["prediction"] == 1:
                malicious_count += 1

            total_pps += pps
            total_bps += bps
            tick_flows.append(flow_dict)

        # Update recent flows window (keep last 50)
        self.recent_flows = (tick_flows + self.recent_flows)[:50]

        # Aggregate stats
        mbps = round((total_bps * 8) / 1_000_000, 3)
        stat_snapshot = {
            "timestamp": current_time,
            "total_pps": round(total_pps, 1),
            "bandwidth_mbps": mbps,
            "active_flows": len(tick_flows),
            "malicious_flows": malicious_count,
            "normal_flows": len(tick_flows) - malicious_count
        }
        self.stats_history.append(stat_snapshot)
        if len(self.stats_history) > 30:
            self.stats_history.pop(0)

        # Device status summary for Topology Canvas
        devices_summary = []
        for dev_id, cfg in DEVICE_CONFIGS.items():
            state = self.device_states[dev_id]
            dev_flow = next((f for f in tick_flows if f["device_id"] == dev_id), None)
            devices_summary.append({
                "id": dev_id,
                "name": cfg["name"],
                "brand": cfg["brand"],
                "model": cfg["model"],
                "ip": cfg["ip"],
                "mac": cfg["mac"],
                "type": cfg["type"],
                "retail_presence": cfg["retail_presence"],
                "cve_case": cfg["cve_case"],
                "service": cfg["normal_service"],
                "compromise_state": state,
                "status": "COMPROMISED" if state != "normal" else "SECURE",
                "current_pps": dev_flow["packets_per_sec"] if dev_flow else 0,
                "current_kbps": round((dev_flow["bytes_per_sec"] * 8) / 1000, 1) if dev_flow else 0,
                "confidence": dev_flow["confidence"] if dev_flow else 100.0,
                "anomalies": dev_flow["anomalies"] if dev_flow else []
            })

        return {
            "timestamp": current_time,
            "current_tick": self.flow_counter,
            "devices": devices_summary,
            "latest_flows": tick_flows,
            "aggregate_stats": stat_snapshot,
            "alerts": self.alerts_history[:12],
            "total_alerts_count": len(self.alerts_history)
        }

# Global singleton
smart_home_sim = SmartHomeSimulator()
