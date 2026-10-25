"""
QoSense Configuration Module
Defines QoS metrics thresholds, priority mappings, and port classification databases.
"""

from typing import Dict, Any

# Network Link Configuration Defaults
DEFAULT_LINK_CAPACITY_MBPS: float = 50.0  # Simulated bottleneck link capacity
DEFAULT_CONGESTION_THRESHOLD_RATIO: float = 0.85  # 85% link utilization triggers congestion
DEFAULT_BUFFER_SIZE_PACKETS: int = 500  # Queue buffer limit before drop

# QoS Composite Scoring Weights (ITU-T G.107 inspired)
# QoS Score = 100 - (w_L * P_L + w_J * P_J + w_PL * P_PL)
WEIGHT_LATENCY: float = 0.35
WEIGHT_JITTER: float = 0.25
WEIGHT_PACKET_LOSS: float = 0.40

# Maximum tolerance limits for baseline penalty scaling
LATENCY_TOLERANCE_MS: float = 200.0   # Beyond 200ms = 100% latency penalty
JITTER_TOLERANCE_MS: float = 50.0     # Beyond 50ms = 100% jitter penalty
PACKET_LOSS_TOLERANCE_PCT: float = 5.0 # 5% loss = 100% loss penalty

# Priority Classes
PRIORITY_P0_HIGH = "P0 (High - Expedited)"
PRIORITY_P1_MEDIUM = "P1 (Medium - Assured)"
PRIORITY_P2_LOW = "P2 (Low - Best Effort)"

# Application Categories
CAT_GAMING = "Gaming"
CAT_VOIP = "VoIP / Audio"
CAT_VIDEO = "Video Streaming"
CAT_WEB = "Web Browsing"
CAT_BULK = "Bulk Download"
CAT_CONTROL = "DNS / Control"

# Well-known port database for Layer 4 traffic classification
PORT_CLASSIFICATIONS: Dict[int, Dict[str, Any]] = {
    # Gaming Ports
    27015: {"category": CAT_GAMING, "priority": PRIORITY_P0_HIGH, "service": "Steam / Valve Matchmaking", "proto": "UDP"},
    27016: {"category": CAT_GAMING, "priority": PRIORITY_P0_HIGH, "service": "Steam Dedicated Server", "proto": "UDP"},
    3074:  {"category": CAT_GAMING, "priority": PRIORITY_P0_HIGH, "service": "Xbox Live / Halo / COD", "proto": "UDP"},
    7777:  {"category": CAT_GAMING, "priority": PRIORITY_P0_HIGH, "service": "Unreal Engine / Valorant", "proto": "UDP"},
    25565: {"category": CAT_GAMING, "priority": PRIORITY_P0_HIGH, "service": "Minecraft Multiplayer", "proto": "TCP"},
    
    # VoIP & Real-time Communications
    5060:  {"category": CAT_VOIP, "priority": PRIORITY_P0_HIGH, "service": "SIP Signaling", "proto": "UDP"},
    5061:  {"category": CAT_VOIP, "priority": PRIORITY_P0_HIGH, "service": "SIP-TLS", "proto": "TCP"},
    3478:  {"category": CAT_VOIP, "priority": PRIORITY_P0_HIGH, "service": "STUN/TURN WebRTC / Zoom", "proto": "UDP"},
    3479:  {"category": CAT_VOIP, "priority": PRIORITY_P0_HIGH, "service": "Teams / WebRTC Media", "proto": "UDP"},
    
    # Video Streaming
    1935:  {"category": CAT_VIDEO, "priority": PRIORITY_P1_MEDIUM, "service": "RTMP Live Video", "proto": "TCP"},
    8080:  {"category": CAT_VIDEO, "priority": PRIORITY_P1_MEDIUM, "service": "HTTP Alternate / HLS Video", "proto": "TCP"},
    8443:  {"category": CAT_VIDEO, "priority": PRIORITY_P1_MEDIUM, "service": "HTTPS Alternate / DASH Video", "proto": "TCP"},
    
    # Web Browsing
    80:    {"category": CAT_WEB, "priority": PRIORITY_P1_MEDIUM, "service": "HTTP Web", "proto": "TCP"},
    443:   {"category": CAT_WEB, "priority": PRIORITY_P1_MEDIUM, "service": "HTTPS Secure Web", "proto": "TCP"},
    
    # Bulk Downloads & File Transfer
    20:    {"category": CAT_BULK, "priority": PRIORITY_P2_LOW, "service": "FTP Data Transfer", "proto": "TCP"},
    21:    {"category": CAT_BULK, "priority": PRIORITY_P2_LOW, "service": "FTP Control", "proto": "TCP"},
    22:    {"category": CAT_BULK, "priority": PRIORITY_P2_LOW, "service": "SFTP / SSH File Sync", "proto": "TCP"},
    6881:  {"category": CAT_BULK, "priority": PRIORITY_P2_LOW, "service": "BitTorrent Client", "proto": "TCP"},
    6882:  {"category": CAT_BULK, "priority": PRIORITY_P2_LOW, "service": "BitTorrent Peer", "proto": "TCP"},
    
    # Control & Infrastructure
    53:    {"category": CAT_CONTROL, "priority": PRIORITY_P0_HIGH, "service": "DNS Domain Lookup", "proto": "UDP"},
    67:    {"category": CAT_CONTROL, "priority": PRIORITY_P0_HIGH, "service": "DHCP Server", "proto": "UDP"},
    68:    {"category": CAT_CONTROL, "priority": PRIORITY_P0_HIGH, "service": "DHCP Client", "proto": "UDP"},
    123:   {"category": CAT_CONTROL, "priority": PRIORITY_P0_HIGH, "service": "NTP Network Time", "proto": "UDP"},
}
