"""
QoSense Traffic Classifier
Classifies IP flows based on 5-tuples (Src IP, Dst IP, Src Port, Dst Port, Protocol)
and packet sizing heuristics into QoS application profiles.
"""

from typing import Dict, Any, Optional
from backend.config import (
    PORT_CLASSIFICATIONS,
    PRIORITY_P0_HIGH,
    PRIORITY_P1_MEDIUM,
    PRIORITY_P2_LOW,
    CAT_GAMING,
    CAT_VOIP,
    CAT_VIDEO,
    CAT_WEB,
    CAT_BULK,
    CAT_CONTROL,
)


class TrafficClassifier:
    """
    Stateful and heuristic classifier for layer 4 and application flows.
    """

    @staticmethod
    def classify(
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        protocol: str,
        avg_packet_size: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Classifies an IP packet or flow using port dictionary lookup and behavioral heuristics.
        """
        proto_clean = protocol.upper()

        # Check destination port, then source port (for return traffic)
        matched_rule = PORT_CLASSIFICATIONS.get(dst_port) or PORT_CLASSIFICATIONS.get(src_port)

        if matched_rule:
            category = matched_rule["category"]
            priority = matched_rule["priority"]
            service = matched_rule["service"]
        else:
            # Heuristic Behavioral Classification when port is unmapped
            if proto_clean == "UDP":
                if avg_packet_size and avg_packet_size < 300:
                    # Low packet size, UDP, high rate = classic Gaming / VoIP pattern
                    category = CAT_GAMING
                    priority = PRIORITY_P0_HIGH
                    service = "UDP Real-Time Interactive"
                elif avg_packet_size and avg_packet_size > 1000:
                    category = CAT_VIDEO
                    priority = PRIORITY_P1_MEDIUM
                    service = "UDP Video Stream / QUIC"
                else:
                    category = "General UDP"
                    priority = PRIORITY_P1_MEDIUM
                    service = "Unclassified UDP"
            elif proto_clean == "TCP":
                if avg_packet_size and avg_packet_size > 1300:
                    # Large sustained segments = Bulk Transfer / File Download
                    category = CAT_BULK
                    priority = PRIORITY_P2_LOW
                    service = "Bulk TCP Stream"
                else:
                    category = CAT_WEB
                    priority = PRIORITY_P1_MEDIUM
                    service = "General Web / HTTP"
            elif proto_clean == "ICMP":
                category = CAT_CONTROL
                priority = PRIORITY_P0_HIGH
                service = "ICMP Ping / Diagnostics"
            else:
                category = "Other"
                priority = PRIORITY_P2_LOW
                service = f"Protocol {proto_clean}"

        # Sensitivity indicators
        is_latency_critical = category in (CAT_GAMING, CAT_VOIP, CAT_CONTROL)
        is_jitter_critical = category in (CAT_GAMING, CAT_VOIP)
        is_throughput_critical = category in (CAT_BULK, CAT_VIDEO)

        return {
            "category": category,
            "priority": priority,
            "service": service,
            "latency_sensitive": is_latency_critical,
            "jitter_sensitive": is_jitter_critical,
            "throughput_sensitive": is_throughput_critical,
        }
