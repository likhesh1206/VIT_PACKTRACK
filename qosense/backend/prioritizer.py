"""
QoSense Prioritizer & Queue Scheduler
Simulates Priority Queuing (PQ), Weighted Fair Queuing (WFQ), and dynamic congestion rate-shaping.
"""

from typing import Dict, Any, List
from backend.config import (
    PRIORITY_P0_HIGH,
    PRIORITY_P1_MEDIUM,
    PRIORITY_P2_LOW,
    DEFAULT_LINK_CAPACITY_MBPS,
    DEFAULT_CONGESTION_THRESHOLD_RATIO,
)


class PriorityScheduler:
    """
    Manages queue servicing and dynamic rate-shaping based on QoS policy.
    """

    def __init__(self, link_capacity_mbps: float = DEFAULT_LINK_CAPACITY_MBPS):
        self.link_capacity_mbps = link_capacity_mbps
        self.congestion_threshold_ratio = DEFAULT_CONGESTION_THRESHOLD_RATIO
        self.prioritization_enabled = True
        
        # Simulated buffer queue occupancies (packets)
        self.queue_occupancy = {
            PRIORITY_P0_HIGH: 0,
            PRIORITY_P1_MEDIUM: 0,
            PRIORITY_P2_LOW: 0
        }
        self.queue_capacity = {
            PRIORITY_P0_HIGH: 100,
            PRIORITY_P1_MEDIUM: 200,
            PRIORITY_P2_LOW: 500
        }

    def set_link_capacity(self, capacity_mbps: float):
        self.link_capacity_mbps = max(5.0, min(1000.0, capacity_mbps))

    def set_prioritization_enabled(self, enabled: bool):
        self.prioritization_enabled = enabled

    def schedule_and_shape(
        self,
        flows: List[Dict[str, Any]],
        base_link_delay_ms: float = 20.0
    ) -> Dict[str, Any]:
        """
        Calculates packet queueing delay, drops, and allocated bandwidth
        under current link capacity and prioritization status.
        """
        # Sum raw demand per priority class
        demands = {
            PRIORITY_P0_HIGH: 0.0,
            PRIORITY_P1_MEDIUM: 0.0,
            PRIORITY_P2_LOW: 0.0
        }
        for flow in flows:
            prio = flow.get("priority", PRIORITY_P2_LOW)
            demands[prio] = demands.get(prio, 0.0) + flow.get("demand_mbps", 0.0)

        total_demand = sum(demands.values())
        congestion_threshold = self.link_capacity_mbps * self.congestion_threshold_ratio
        is_congested = total_demand > congestion_threshold
        over_capacity = max(0.0, total_demand - self.link_capacity_mbps)

        allocated_bandwidth = {}
        flow_metrics = {}

        if not self.prioritization_enabled:
            # FIFO / BEST-EFFORT (No QoS):
            # Indiscriminate bufferbloat and tail-drop across all flows.
            if total_demand > self.link_capacity_mbps:
                scale_ratio = self.link_capacity_mbps / total_demand
                loss_ratio = (total_demand - self.link_capacity_mbps) / total_demand
                # Bufferbloat increases queueing delay proportionally
                congestion_delay = min(220.0, (total_demand / self.link_capacity_mbps - 1.0) * 180.0)
                congestion_jitter = min(45.0, congestion_delay * 0.28)
            else:
                scale_ratio = 1.0
                loss_ratio = 0.0
                congestion_delay = 0.0
                congestion_jitter = 0.0

            # Update simulated queue buffer
            self.queue_occupancy[PRIORITY_P0_HIGH] = int(min(100, 20 + congestion_delay * 0.4))
            self.queue_occupancy[PRIORITY_P1_MEDIUM] = int(min(200, 40 + congestion_delay * 0.7))
            self.queue_occupancy[PRIORITY_P2_LOW] = int(min(500, 80 + congestion_delay * 1.8))

            for flow in flows:
                f_id = flow["id"]
                demand = flow.get("demand_mbps", 0.0)
                actual_mbps = demand * scale_ratio
                
                # In FIFO, even gaming suffers severe latency & jitter spikes
                flow_latency = base_link_delay_ms + flow.get("base_latency", 10.0) + congestion_delay
                flow_jitter = flow.get("base_jitter", 2.0) + congestion_jitter
                flow_loss = min(15.0, loss_ratio * 100.0 * (1.2 if flow.get("protocol") == "UDP" else 0.8))

                flow_metrics[f_id] = {
                    "allocated_mbps": round(actual_mbps, 2),
                    "latency_ms": round(flow_latency, 1),
                    "jitter_ms": round(flow_jitter, 1),
                    "packet_loss_pct": round(flow_loss, 2),
                    "queued_packets": int(congestion_delay * 2.5),
                    "throttled": total_demand > self.link_capacity_mbps
                }

        else:
            # INTELLIGENT QoS PRIORITIZATION (Strict Priority + Weighted Fair Queueing):
            # P0 (Gaming, VoIP) receives 100% reservation & minimal queue delay.
            # P1 receives assured forwarding.
            # P2 (Bulk Downloads) absorbs throttling & packet drops.
            remaining_cap = self.link_capacity_mbps

            # 1. P0 Scheduling (Expedited Forwarding)
            p0_alloc = min(demands[PRIORITY_P0_HIGH], remaining_cap)
            remaining_cap = max(0.0, remaining_cap - p0_alloc)

            # 2. P1 Scheduling (Assured Forwarding)
            p1_alloc = min(demands[PRIORITY_P1_MEDIUM], remaining_cap)
            remaining_cap = max(0.0, remaining_cap - p1_alloc)

            # 3. P2 Scheduling (Best Effort - Throttled under congestion)
            p2_alloc = min(demands[PRIORITY_P2_LOW], remaining_cap)

            # Buffer queues under QoS: P0 queue remains near zero
            self.queue_occupancy[PRIORITY_P0_HIGH] = 5 if demands[PRIORITY_P0_HIGH] > 0 else 0
            self.queue_occupancy[PRIORITY_P1_MEDIUM] = int(min(200, 30 if demands[PRIORITY_P1_MEDIUM] > 0 else 0))
            self.queue_occupancy[PRIORITY_P2_LOW] = int(min(500, 150 + (over_capacity * 10))) if over_capacity > 0 else 20

            for flow in flows:
                f_id = flow["id"]
                prio = flow.get("priority", PRIORITY_P2_LOW)
                demand = flow.get("demand_mbps", 0.0)

                if prio == PRIORITY_P0_HIGH:
                    # P0: ZERO congestion delay, minimal jitter, near 0% loss
                    actual_mbps = demand
                    flow_latency = base_link_delay_ms + flow.get("base_latency", 5.0)
                    flow_jitter = flow.get("base_jitter", 1.5)
                    flow_loss = 0.0
                    throttled = False

                elif prio == PRIORITY_P1_MEDIUM:
                    p1_dem = demands[PRIORITY_P1_MEDIUM]
                    ratio = (p1_alloc / p1_dem) if p1_dem > 0 else 1.0
                    actual_mbps = demand * ratio
                    flow_latency = base_link_delay_ms + flow.get("base_latency", 15.0) + (10.0 if is_congested else 0.0)
                    flow_jitter = flow.get("base_jitter", 3.0) + (4.0 if is_congested else 0.0)
                    flow_loss = 0.1 if is_congested else 0.0
                    throttled = ratio < 0.99

                else:  # PRIORITY_P2_LOW
                    p2_dem = demands[PRIORITY_P2_LOW]
                    ratio = (p2_alloc / p2_dem) if p2_dem > 0 else 1.0
                    actual_mbps = demand * ratio
                    # Low priority absorbs queueing delay and drops
                    p2_delay = min(180.0, 30.0 + (over_capacity * 12.0)) if is_congested else 15.0
                    flow_latency = base_link_delay_ms + flow.get("base_latency", 25.0) + p2_delay
                    flow_jitter = flow.get("base_jitter", 8.0) + (20.0 if is_congested else 0.0)
                    flow_loss = min(12.0, (1.0 - ratio) * 100.0) if ratio < 1.0 else 0.0
                    throttled = ratio < 0.99

                flow_metrics[f_id] = {
                    "allocated_mbps": round(actual_mbps, 2),
                    "latency_ms": round(flow_latency, 1),
                    "jitter_ms": round(flow_jitter, 1),
                    "packet_loss_pct": round(flow_loss, 2),
                    "queued_packets": 2 if prio == PRIORITY_P0_HIGH else (25 if prio == PRIORITY_P1_MEDIUM else 180),
                    "throttled": throttled
                }

        return {
            "is_congested": is_congested,
            "total_demand_mbps": round(total_demand, 2),
            "link_capacity_mbps": self.link_capacity_mbps,
            "utilization_pct": round(min(100.0, (total_demand / self.link_capacity_mbps) * 100.0), 1),
            "prioritization_enabled": self.prioritization_enabled,
            "queue_occupancy": self.queue_occupancy,
            "queue_capacity": self.queue_capacity,
            "flow_metrics": flow_metrics,
            "status_message": (
                "Congestion Mitigated: High-Priority Gaming/VoIP packets protected, Bulk traffic throttled"
                if is_congested and self.prioritization_enabled
                else (
                    "CRITICAL: Unmanaged Congestion & Bufferbloat! Latency and packet drops affecting all applications"
                    if is_congested and not self.prioritization_enabled
                    else "Normal Operation: Link utilization within safe limits"
                )
            )
        }
