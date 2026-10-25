"""
QoSense Live Packet Capture & Hardware Interface Monitor
Monitors local network interfaces using psutil and Scapy packet sniffing.
"""

import time
import socket
import threading
from typing import Dict, Any, List, Optional
import psutil
from backend.classifier import TrafficClassifier

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
    SCAPY_AVAILABLE = True
except Exception:
    SCAPY_AVAILABLE = False


class LiveCaptureEngine:
    """
    Captures live network packets and host interface I/O counters.
    """

    def __init__(self):
        self.is_running = False
        self.active_live_flows: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        
        # IO Counters tracking
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.last_check_time = time.time()
        
        # Initialize initial counters
        try:
            net_io = psutil.net_io_counters()
            self.last_bytes_sent = net_io.bytes_sent
            self.last_bytes_recv = net_io.bytes_recv
        except Exception:
            pass

    def start(self):
        """Starts live sniffer in a background daemon thread."""
        if self.is_running:
            return
        self.is_running = True
        
        if SCAPY_AVAILABLE:
            t = threading.Thread(target=self._sniff_worker, daemon=True)
            t.start()

    def stop(self):
        self.is_running = False

    def _sniff_worker(self):
        """Background thread sniffing live packets safely."""
        def packet_handler(pkt):
            if not self.is_running:
                return
            if not pkt.haslayer(IP):
                return
            
            try:
                ip_layer = pkt[IP]
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
                proto_name = "TCP" if pkt.haslayer(TCP) else ("UDP" if pkt.haslayer(UDP) else ("ICMP" if pkt.haslayer(ICMP) else "OTHER"))
                
                src_port = 0
                dst_port = 0
                if pkt.haslayer(TCP):
                    src_port = pkt[TCP].sport
                    dst_port = pkt[TCP].dport
                elif pkt.haslayer(UDP):
                    src_port = pkt[UDP].sport
                    dst_port = pkt[UDP].dport

                flow_key = f"{proto_name}:{src_ip}:{src_port}->{dst_ip}:{dst_port}"
                pkt_len = len(pkt)

                with self.lock:
                    if flow_key not in self.active_live_flows:
                        classification = TrafficClassifier.classify(
                            src_ip=src_ip,
                            dst_ip=dst_ip,
                            src_port=src_port,
                            dst_port=dst_port,
                            protocol=proto_name,
                            avg_packet_size=pkt_len
                        )
                        self.active_live_flows[flow_key] = {
                            "id": f"live-{len(self.active_live_flows) + 1}",
                            "app_name": classification["service"],
                            "src_ip": src_ip,
                            "dst_ip": dst_ip,
                            "src_port": src_port,
                            "dst_port": dst_port,
                            "protocol": proto_name,
                            "category": classification["category"],
                            "priority": classification["priority"],
                            "service": classification["service"],
                            "base_demand_mbps": 0.5,
                            "demand_mbps": 0.5,
                            "base_latency": 25.0,
                            "base_jitter": 2.0,
                            "avg_packet_size": pkt_len,
                            "packet_count": 1,
                            "byte_count": pkt_len,
                            "last_seen": time.time()
                        }
                    else:
                        flow = self.active_live_flows[flow_key]
                        flow["packet_count"] += 1
                        flow["byte_count"] += pkt_len
                        flow["last_seen"] = time.time()
                        
                        # Retain only recently active flows (last 10s)
                        if len(self.active_live_flows) > 50:
                            cutoff = time.time() - 10
                            self.active_live_flows = {
                                k: v for k, v in self.active_live_flows.items() if v["last_seen"] > cutoff
                            }
            except Exception:
                pass

        try:
            # Sniff with small batches to remain responsive
            while self.is_running:
                sniff(prn=packet_handler, count=25, timeout=1.0, store=False)
        except Exception:
            # Permissions or missing Npcap will safely fallback to psutil interface metrics
            pass

    def get_interface_throughput(self) -> Dict[str, float]:
        """Calculates host upload/download throughput in Mbps using psutil."""
        now = time.time()
        elapsed = max(0.2, now - self.last_check_time)
        try:
            net_io = psutil.net_io_counters()
            bytes_sent_delta = max(0, net_io.bytes_sent - self.last_bytes_sent)
            bytes_recv_delta = max(0, net_io.bytes_recv - self.last_bytes_recv)

            self.last_bytes_sent = net_io.bytes_sent
            self.last_bytes_recv = net_io.bytes_recv
            self.last_check_time = now

            # Bytes * 8 / (1,000,000 * elapsed) = Mbps
            upload_mbps = round((bytes_sent_delta * 8) / (1_000_000 * elapsed), 2)
            download_mbps = round((bytes_recv_delta * 8) / (1_000_000 * elapsed), 2)
            total_mbps = round(upload_mbps + download_mbps, 2)

            return {
                "upload_mbps": upload_mbps,
                "download_mbps": download_mbps,
                "total_mbps": total_mbps
            }
        except Exception:
            return {"upload_mbps": 0.0, "download_mbps": 0.0, "total_mbps": 0.0}

    def measure_real_rtt(self, host: str = "1.1.1.1", port: int = 53, timeout: float = 1.0) -> float:
        """Measures real socket round-trip time in milliseconds."""
        t0 = time.perf_counter()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            s.close()
            rtt_ms = (time.perf_counter() - t0) * 1000.0
            return max(5.0, round(rtt_ms, 1))
        except Exception:
            return 28.0
