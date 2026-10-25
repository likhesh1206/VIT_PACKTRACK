"""
QoSense & IoT Security Main Application Server
Serves the Computer Networks Review 1 Project:
"Detection of Compromised Smart-Home Devices Using Encrypted Traffic Behaviour"
"""

import os
import asyncio
import json
import time
from typing import Set, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import DEFAULT_LINK_CAPACITY_MBPS
from backend.prioritizer import PriorityScheduler
from backend.qos_engine import QoSEngine
from backend.traffic_generator import TrafficGenerator
from backend.capture_engine import LiveCaptureEngine
import backend.database as db

from backend.iot_classifier import iot_classifier
from backend.iot_traffic_simulator import smart_home_sim
from backend.review_data import REVIEW_DATA

# Directories
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# Core Engine Instances
scheduler = PriorityScheduler(link_capacity_mbps=DEFAULT_LINK_CAPACITY_MBPS)
generator = TrafficGenerator()
capture_engine = LiveCaptureEngine()

# State
CURRENT_MODE = "simulation"
active_websockets: Set[WebSocket] = set()
background_task: asyncio.Task = None
latest_telemetry: Dict[str, Any] = {}
latest_iot_telemetry: Dict[str, Any] = {}


class ModeRequest(BaseModel):
    mode: str


class PrioritizationRequest(BaseModel):
    enabled: bool


class CapacityRequest(BaseModel):
    capacity_mbps: float


class ScenarioRequest(BaseModel):
    scenario: str


class DeviceStateRequest(BaseModel):
    device_id: str
    attack_mode: str  # "normal", "ddos", "scan", "exfil"


class PredictFlowRequest(BaseModel):
    duration: float = 2.0
    avg_packet_size: float = 120.0
    packets_per_sec: float = 5.0
    bytes_per_sec: float = 600.0
    unique_dest_ips: int = 1
    unique_dest_ports: int = 1
    protocol: str = "TCP"


async def telemetry_broadcaster():
    """
    Periodic background loop (1 Hz) that samples traffic,
    evaluates QoS, generates smart-home encrypted IoT traffic,
    and broadcasts to connected WebSockets.
    """
    global latest_telemetry, latest_iot_telemetry
    capture_engine.start()

    while True:
        try:
            t_start = time.time()
            
            # --- 1. Smart Home Encrypted Traffic & RF Detection ---
            iot_tick = smart_home_sim.generate_tick()
            latest_iot_telemetry = iot_tick

            # --- 2. QoS Telemetry ---
            if CURRENT_MODE == "simulation":
                flows = generator.generate_tick()
            else:
                if_metrics = capture_engine.get_interface_throughput()
                real_rtt = capture_engine.measure_real_rtt()
                live_dict = list(capture_engine.active_live_flows.values())
                if live_dict:
                    flows = live_dict
                else:
                    flows = [{
                        "id": "live-host-1",
                        "app_name": "Host Network Traffic",
                        "src_ip": "Local Host",
                        "dst_ip": "Internet Gateway",
                        "src_port": 0,
                        "dst_port": 443,
                        "protocol": "TCP",
                        "category": "Web Browsing",
                        "priority": "P1 (Medium - Assured)",
                        "service": "General Web / Interface I/O",
                        "demand_mbps": max(0.2, if_metrics["total_mbps"]),
                        "base_latency": real_rtt,
                        "base_jitter": 3.0,
                        "avg_packet_size": 1200,
                        "packet_count": 50,
                        "byte_count": int(if_metrics["total_mbps"] * 125000),
                        "start_time": time.time()
                    }]

            schedule_result = scheduler.schedule_and_shape(flows)
            flow_metrics = schedule_result["flow_metrics"]
            combined_flows = []
            flow_metrics_list = []

            for f in flows:
                f_id = f["id"]
                m = flow_metrics.get(f_id, {
                    "allocated_mbps": f.get("demand_mbps", 0.0),
                    "latency_ms": 20.0,
                    "jitter_ms": 2.0,
                    "packet_loss_pct": 0.0,
                    "queued_packets": 0,
                    "throttled": False
                })
                
                f_qos = QoSEngine.compute_qos_score(
                    m["latency_ms"], m["jitter_ms"], m["packet_loss_pct"]
                )
                
                flow_data = {
                    **f,
                    **m,
                    "qos_score": f_qos["score"],
                    "qos_status": f_qos["status"],
                    "qos_color": f_qos["status_color"]
                }
                combined_flows.append(flow_data)
                flow_metrics_list.append(m)

            network_metrics = QoSEngine.aggregate_network_metrics(flow_metrics_list)

            db.log_metrics(
                total_mbps=network_metrics["total_mbps"],
                download_mbps=network_metrics["download_mbps"],
                upload_mbps=network_metrics["upload_mbps"],
                avg_latency_ms=network_metrics["avg_latency_ms"],
                avg_jitter_ms=network_metrics["avg_jitter_ms"],
                packet_loss_pct=network_metrics["avg_packet_loss_pct"],
                qos_score=network_metrics["qos_score"],
                qos_status=network_metrics["qos_status"],
                is_congested=schedule_result["is_congested"],
                active_flows_count=len(combined_flows),
                prioritization_enabled=scheduler.prioritization_enabled,
                timestamp=t_start
            )

            latest_telemetry = {
                "timestamp": time.strftime("%H:%M:%S"),
                "mode": CURRENT_MODE,
                "prioritization_enabled": scheduler.prioritization_enabled,
                "link_capacity_mbps": scheduler.link_capacity_mbps,
                "is_congested": schedule_result["is_congested"],
                "utilization_pct": schedule_result["utilization_pct"],
                "network_metrics": network_metrics,
                "queue_occupancy": schedule_result["queue_occupancy"],
                "queue_capacity": schedule_result["queue_capacity"],
                "flows": combined_flows,
                "iot_telemetry": iot_tick  # Include smart-home telemetry
            }

            # Broadcast via WebSockets
            if active_websockets:
                payload_str = json.dumps(latest_telemetry)
                disconnected = set()
                for ws in active_websockets:
                    try:
                        await ws.send_text(payload_str)
                    except Exception:
                        disconnected.add(ws)
                active_websockets.difference_update(disconnected)

        except Exception as e:
            print(f"[Telemetry Broadcaster Error]: {e}")

        await asyncio.sleep(1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global background_task
    background_task = asyncio.create_task(telemetry_broadcaster())
    yield
    if background_task:
        background_task.cancel()
    capture_engine.stop()


app = FastAPI(title="Smart Home IoT Intrusion Detection API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- IoT Project Review 1 Specific Endpoints ---

@app.get("/api/iot/telemetry")
async def get_iot_telemetry():
    """Returns current live IoT smart-home traffic & Random Forest telemetry."""
    return JSONResponse(latest_iot_telemetry or smart_home_sim.generate_tick())


@app.get("/api/iot/model-summary")
async def get_iot_model_summary():
    """Returns Random Forest model performance, confusion matrix, and feature importances."""
    return JSONResponse(iot_classifier.get_model_summary())


@app.post("/api/iot/device-state")
async def set_device_attack_mode(req: DeviceStateRequest):
    """Toggles attack injection on smart-home devices (normal, ddos, scan, exfil)."""
    smart_home_sim.set_device_state(req.device_id, req.attack_mode)
    return {
        "status": "ok",
        "device_id": req.device_id,
        "attack_mode": req.attack_mode,
        "current_states": smart_home_sim.device_states
    }


@app.post("/api/iot/predict")
async def predict_custom_flow(req: PredictFlowRequest):
    """Classifies any user-supplied flow feature vector using the Random Forest model."""
    result = iot_classifier.predict_flow(req.dict())
    return JSONResponse(result)


@app.get("/api/iot/review-data")
async def get_review_data():
    """Returns complete academic Review 1 documentation and viva Q&A."""
    return JSONResponse(REVIEW_DATA)


# --- Legacy QoS Endpoints for Compatibility ---

@app.get("/api/telemetry")
async def get_telemetry():
    return JSONResponse(latest_telemetry or {})


@app.get("/api/history")
async def get_history(limit: int = 60):
    history = db.get_recent_metrics(limit=limit)
    return JSONResponse(history)


@app.get("/api/report")
async def get_report():
    summary = db.get_analytics_summary()
    return JSONResponse({
        "project": REVIEW_DATA["project_title"],
        "course": "Computer Networks (CN)",
        "milestone": "Project Review 1",
        "current_mode": CURRENT_MODE,
        "summary": summary,
        "model_summary": iot_classifier.get_model_summary()
    })


@app.post("/api/control/prioritization")
async def set_prioritization(req: PrioritizationRequest):
    scheduler.set_prioritization_enabled(req.enabled)
    return {"status": "ok", "prioritization_enabled": scheduler.prioritization_enabled}


@app.post("/api/control/capacity")
async def set_capacity(req: CapacityRequest):
    scheduler.set_link_capacity(req.capacity_mbps)
    return {"status": "ok", "link_capacity_mbps": scheduler.link_capacity_mbps}


@app.post("/api/control/scenario")
async def set_scenario(req: ScenarioRequest):
    generator.load_scenario(req.scenario)
    return {"status": "ok", "scenario": req.scenario}


@app.post("/api/control/mode")
async def set_mode(req: ModeRequest):
    global CURRENT_MODE
    if req.mode in ("simulation", "live"):
        CURRENT_MODE = req.mode
        return {"status": "ok", "mode": CURRENT_MODE}
    raise HTTPException(status_code=400, detail="Invalid mode.")


@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)
    try:
        if latest_telemetry:
            await websocket.send_text(json.dumps(latest_telemetry))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception:
        active_websockets.discard(websocket)


# Mount static frontend directory
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"error": "Dashboard index.html not yet built."}, status_code=404)
