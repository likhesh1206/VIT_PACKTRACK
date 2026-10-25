"""
QoSense QoS Metric Calculation Engine
Computes Throughput, Latency, RFC 3550 Jitter, Packet Loss, and Composite QoS Score.
"""

from typing import Dict, Any, List
from backend.config import (
    WEIGHT_LATENCY,
    WEIGHT_JITTER,
    WEIGHT_PACKET_LOSS,
    LATENCY_TOLERANCE_MS,
    JITTER_TOLERANCE_MS,
    PACKET_LOSS_TOLERANCE_PCT,
)


class QoSEngine:
    """
    Evaluates individual and aggregate network Quality of Service parameters.
    """

    @staticmethod
    def calculate_jitter_rfc3550(current_jitter: float, prev_transit: float, curr_transit: float) -> float:
        """
        RFC 3550 Jitter algorithm:
        D(i-1, i) = |(R_i - S_i) - (R_{i-1} - S_{i-1})|
        J_i = J_{i-1} + (|D| - J_{i-1}) / 16
        """
        diff = abs(curr_transit - prev_transit)
        new_jitter = current_jitter + (diff - current_jitter) / 16.0
        return max(0.0, new_jitter)

    @staticmethod
    def compute_qos_score(latency_ms: float, jitter_ms: float, packet_loss_pct: float) -> Dict[str, Any]:
        """
        Calculates a composite QoS Score (0 - 100) based on ITU-T G.107 (E-Model) inspired penalties.
        """
        # Calculate normalized penalties (0 - 100)
        p_latency = min(100.0, (latency_ms / LATENCY_TOLERANCE_MS) * 100.0)
        p_jitter = min(100.0, (jitter_ms / JITTER_TOLERANCE_MS) * 100.0)
        p_loss = min(100.0, (packet_loss_pct / PACKET_LOSS_TOLERANCE_PCT) * 100.0)

        # Weighted composite penalty
        composite_penalty = (
            WEIGHT_LATENCY * p_latency +
            WEIGHT_JITTER * p_jitter +
            WEIGHT_PACKET_LOSS * p_loss
        )

        score = max(0.0, min(100.0, 100.0 - composite_penalty))
        rounded_score = round(score, 1)

        # Categorize
        if rounded_score >= 85.0:
            status = "Excellent"
            status_color = "#10b981"  # Emerald
            description = "Optimal for competitive multiplayer gaming, VoIP audio calls, and ultra-low latency streams."
        elif rounded_score >= 70.0:
            status = "Good"
            status_color = "#06b6d4"  # Cyan
            description = "Seamless HD 4K streaming, smooth video meetings, and fast interactive web browsing."
        elif rounded_score >= 50.0:
            status = "Moderate"
            status_color = "#f59e0b"  # Amber
            description = "Noticeable queueing delay and jitter. Occasional buffering in video and latency in online games."
        else:
            status = "Poor"
            status_color = "#ef4444"  # Red
            description = "Severe network congestion and packet loss. Substantial lag spikes, call drops, and buffering."

        return {
            "score": rounded_score,
            "status": status,
            "status_color": status_color,
            "description": description,
            "penalties": {
                "latency_penalty": round(p_latency, 1),
                "jitter_penalty": round(p_jitter, 1),
                "loss_penalty": round(p_loss, 1),
            }
        }

    @staticmethod
    def aggregate_network_metrics(flow_metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates metrics across all active flows to produce overall network health telemetry.
        """
        if not flow_metrics_list:
            return {
                "total_mbps": 0.0,
                "download_mbps": 0.0,
                "upload_mbps": 0.0,
                "avg_latency_ms": 20.0,
                "avg_jitter_ms": 2.0,
                "avg_packet_loss_pct": 0.0,
                "qos_score": 98.0,
                "qos_status": "Excellent",
                "qos_color": "#10b981",
                "active_flows": 0
            }

        total_mbps = sum(f.get("allocated_mbps", 0.0) for f in flow_metrics_list)
        
        # Estimate upload vs download (in typical client networks, ~80% down, 20% up)
        download_mbps = round(total_mbps * 0.82, 2)
        upload_mbps = round(total_mbps * 0.18, 2)

        # Weighted averages by throughput/importance
        weights = [max(0.1, f.get("allocated_mbps", 1.0)) for f in flow_metrics_list]
        sum_weights = sum(weights)

        avg_latency = sum(f.get("latency_ms", 20.0) * w for f, w in zip(flow_metrics_list, weights)) / sum_weights
        avg_jitter = sum(f.get("jitter_ms", 2.0) * w for f, w in zip(flow_metrics_list, weights)) / sum_weights
        avg_loss = sum(f.get("packet_loss_pct", 0.0) * w for f, w in zip(flow_metrics_list, weights)) / sum_weights

        qos_eval = QoSEngine.compute_qos_score(avg_latency, avg_jitter, avg_loss)

        return {
            "total_mbps": round(total_mbps, 2),
            "download_mbps": download_mbps,
            "upload_mbps": upload_mbps,
            "avg_latency_ms": round(avg_latency, 1),
            "avg_jitter_ms": round(avg_jitter, 1),
            "avg_packet_loss_pct": round(avg_loss, 2),
            "qos_score": qos_eval["score"],
            "qos_status": qos_eval["status"],
            "qos_color": qos_eval["status_color"],
            "qos_description": qos_eval["description"],
            "active_flows": len(flow_metrics_list)
        }
