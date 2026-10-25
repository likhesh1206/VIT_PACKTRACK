"""
QoSense Database Module
SQLite persistence for time-series QoS metrics, active flow records, and congestion incidents.
"""

import sqlite3
import os
import time
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qosense.db")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables for QoS metric logs, flow stats, and congestion alerts."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # QoS Metric snapshots over time (1s intervals)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qos_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                total_mbps REAL NOT NULL,
                download_mbps REAL NOT NULL,
                upload_mbps REAL NOT NULL,
                avg_latency_ms REAL NOT NULL,
                avg_jitter_ms REAL NOT NULL,
                packet_loss_pct REAL NOT NULL,
                qos_score REAL NOT NULL,
                qos_status TEXT NOT NULL,
                is_congested INTEGER NOT NULL,
                active_flows_count INTEGER NOT NULL,
                prioritization_enabled INTEGER NOT NULL
            )
        """)
        
        # Historical Flow sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flow_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flow_id TEXT NOT NULL,
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL,
                src_ip TEXT NOT NULL,
                dst_ip TEXT NOT NULL,
                src_port INTEGER NOT NULL,
                dst_port INTEGER NOT NULL,
                protocol TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                packet_count INTEGER NOT NULL,
                byte_count INTEGER NOT NULL,
                avg_mbps REAL NOT NULL,
                avg_latency_ms REAL NOT NULL,
                avg_jitter_ms REAL NOT NULL,
                packet_loss_pct REAL NOT NULL
            )
        """)
        
        # Congestion events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS congestion_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                utilization_pct REAL NOT NULL,
                reason TEXT NOT NULL,
                prioritization_active INTEGER NOT NULL,
                action_taken TEXT NOT NULL
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_ts ON qos_metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_flow_last_seen ON flow_records(last_seen)")
        conn.commit()


def log_metrics(
    total_mbps: float,
    download_mbps: float,
    upload_mbps: float,
    avg_latency_ms: float,
    avg_jitter_ms: float,
    packet_loss_pct: float,
    qos_score: float,
    qos_status: str,
    is_congested: bool,
    active_flows_count: int,
    prioritization_enabled: bool,
    timestamp: Optional[float] = None
):
    ts = timestamp or time.time()
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO qos_metrics (
                    timestamp, total_mbps, download_mbps, upload_mbps,
                    avg_latency_ms, avg_jitter_ms, packet_loss_pct,
                    qos_score, qos_status, is_congested,
                    active_flows_count, prioritization_enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts, total_mbps, download_mbps, upload_mbps,
                avg_latency_ms, avg_jitter_ms, packet_loss_pct,
                qos_score, qos_status, 1 if is_congested else 0,
                active_flows_count, 1 if prioritization_enabled else 0
            ))
            conn.commit()
    except Exception as e:
        print(f"[Database] Error logging metrics: {e}")


def log_congestion_event(utilization_pct: float, reason: str, prioritization_active: bool, action_taken: str):
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO congestion_events (
                    timestamp, utilization_pct, reason, prioritization_active, action_taken
                ) VALUES (?, ?, ?, ?, ?)
            """, (time.time(), utilization_pct, reason, 1 if prioritization_active else 0, action_taken))
            conn.commit()
    except Exception as e:
        print(f"[Database] Error logging congestion event: {e}")


def get_recent_metrics(limit: int = 60) -> List[Dict[str, Any]]:
    """Returns the last N metric records in chronological order for graphs."""
    try:
        with get_db_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM (
                    SELECT * FROM qos_metrics ORDER BY timestamp DESC LIMIT ?
                ) ORDER BY timestamp ASC
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"[Database] Error fetching metrics: {e}")
        return []


def get_analytics_summary() -> Dict[str, Any]:
    """Generates an academic project report summary with key statistics."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Overall metric statistics
            stats = cursor.execute("""
                SELECT 
                    COUNT(*) as total_samples,
                    AVG(total_mbps) as avg_throughput,
                    MAX(total_mbps) as peak_throughput,
                    AVG(avg_latency_ms) as avg_latency,
                    MIN(avg_latency_ms) as min_latency,
                    MAX(avg_latency_ms) as max_latency,
                    AVG(avg_jitter_ms) as avg_jitter,
                    AVG(packet_loss_pct) as avg_packet_loss,
                    AVG(qos_score) as avg_qos_score,
                    SUM(CASE WHEN is_congested = 1 THEN 1 ELSE 0 END) as congestion_ticks
                FROM qos_metrics
            """).fetchone()

            events = cursor.execute("""
                SELECT COUNT(*) as incident_count FROM congestion_events
            """).fetchone()

            return {
                "total_samples": stats["total_samples"] if stats else 0,
                "avg_throughput_mbps": round(stats["avg_throughput"] or 0, 2),
                "peak_throughput_mbps": round(stats["peak_throughput"] or 0, 2),
                "avg_latency_ms": round(stats["avg_latency"] or 0, 2),
                "min_latency_ms": round(stats["min_latency"] or 0, 2),
                "max_latency_ms": round(stats["max_latency"] or 0, 2),
                "avg_jitter_ms": round(stats["avg_jitter"] or 0, 2),
                "avg_packet_loss_pct": round(stats["avg_packet_loss"] or 0, 2),
                "avg_qos_score": round(stats["avg_qos_score"] or 0, 1),
                "congestion_incidents": events["incident_count"] if events else 0,
            }
    except Exception as e:
        print(f"[Database] Error generating report summary: {e}")
        return {}


# Auto-initialize database on import
init_db()
