"""
Academic Review 1 Data Repository for Computer Networks (CN) Project:
Detection of Compromised Smart-Home Devices Using Encrypted Traffic Behaviour
"""

REVIEW_DATA = {
    "project_title": "Detection of Compromised Smart-Home Devices Using Encrypted Traffic Behaviour",
    "course": "Computer Networks (CN)",
    "milestone": "Project Review 1",
    "academic_year": "2024-2025",
    
    "abstract": {
        "text": "The number of smart devices in homes, such as cameras, smart plugs, bulbs and speakers, is growing very fast. Many of these devices have weak passwords and receive few security updates, so attackers can easily take control of them and use them in attacks like DDoS. Since most network traffic is now encrypted, traditional security tools that read packet content cannot detect this. In this project, we detect compromised IoT devices by studying their traffic behaviour instead of their content. We take network traffic, group it into flows, and extract simple features such as packet size, flow duration and number of destinations. A Random Forest classifier is then trained to label each flow as normal or malicious. The system works without decrypting any data, needs no extra hardware, and gives measurable results in terms of accuracy, precision, recall and false alarm rate."
    },

    "objectives": [
        {
            "id": 1,
            "title": "Metadata-Only Detection",
            "desc": "To detect compromised IoT devices using only traffic metadata, without reading the encrypted payload."
        },
        {
            "id": 2,
            "title": "Behavioral Feature Extraction",
            "desc": "To extract meaningful features from network flows that separate normal behaviour from malicious behaviour."
        },
        {
            "id": 3,
            "title": "Machine Learning Classification",
            "desc": "To train and test a machine learning model (Random Forest) that classifies flows as normal or suspicious."
        },
        {
            "id": 4,
            "title": "Empirical Evaluation",
            "desc": "To evaluate the model using accuracy, precision, recall, F1-score, and false positive rate."
        },
        {
            "id": 5,
            "title": "Lightweight & Practical Deployment",
            "desc": "To build a system that is simple, lightweight and easy to understand on edge home gateways without dedicated hardware."
        }
    ],

    "real_world_devices_proof": [
        {
            "category": "Smart Bulbs & Lighting",
            "brands": "Philips Hue, Wipro Smart WiFi Bulb, Syska, Xiaomi Mi LED, Havells",
            "market_reality": "Smart bulbs are the #1 entry-level IoT device sold worldwide and across India (priced ₹400 - ₹800 on Amazon & Flipkart with over 200,000+ consumer reviews). Millions of households control them via Google Home and Alexa.",
            "famous_cve": "CVE-2020-6007: Check Point Research famously demonstrated exploiting a heap-based buffer overflow in Philips Hue smart bulbs to bridge into the homeowner's internal LAN and distribute ransomware across PCs.",
            "academic_citation": "Sivanathan et al. (Paper #2 in our Literature Survey) deployed real Philips Hue and LIFX smart bulbs in their smart-home testbed at UNSW Sydney."
        },
        {
            "category": "Smart Voice Assistants",
            "brands": "Amazon Echo Dot (Alexa), Google Nest Mini, Apple HomePod",
            "market_reality": "Over 500 million Amazon Alexa and Google Nest devices deployed globally. Found in university labs, student dorms, and living rooms.",
            "famous_cve": "CVE-2020-10177 & Alexa DNS Rebinding: Allowed remote attackers to hijack audio endpoints and trigger unauthenticated local subnet calls.",
            "academic_citation": "Tested in Meidan et al. (N-BaIoT) and Sivanathan et al."
        },
        {
            "category": "Smart Security Cameras",
            "brands": "TP-Link Tapo C200, Xiaomi Mi 360°, Realme Smart Cam, Godrej Spotlight",
            "market_reality": "Over 100M Wi-Fi CCTV cameras installed in consumer apartments and houses for security.",
            "famous_cve": "Mirai Botnet (2016): Compromised over 600,000 CCTV cameras and DVRs with default passwords, launching the historic 1.2 Tbps Dyn DNS DDoS attack that brought down Twitter, Netflix, and GitHub.",
            "academic_citation": "Antonakakis et al. (Paper #1 in Literature Survey) and IoT-23 dataset (Stratosphere Lab)."
        },
        {
            "category": "Smart TVs & Streaming Sticks",
            "brands": "Samsung Smart TV (Tizen), Amazon Fire TV Stick 4K, LG webOS, Xiaomi Mi TV",
            "market_reality": "In over 85% of modern urban households. They stay powered on 24/7 on home Wi-Fi networks.",
            "famous_cve": "Weeping Angel CIA exploit & Android TV botnets (e.g. ADB.Miner) stealthily mining Monero cryptocurrency while screen is off.",
            "academic_citation": "Included in standard IoT-23 and UNSW smart-home traffic profiling benchmarks."
        },
        {
            "category": "Smart Plugs (AC & Geyser Controls)",
            "brands": "TP-Link Tapo P110, Wipro 16A Smart Plug, Havells, Amazon Smart Plug",
            "market_reality": "Extremely common in Indian households for scheduling geysers, ACs, and water pumps via mobile apps to save electricity.",
            "famous_cve": "CVE-2023-40152: Unauthenticated local network command injection on smart plugs allowing attackers to join them into Mirai botnet clusters.",
            "academic_citation": "Meidan et al. (N-BaIoT) specifically benchmarked Belkin WeMo and TP-Link Smart Plugs."
        },
        {
            "category": "Smart Video Doorbells",
            "brands": "Amazon Ring Doorbell, Google Nest Doorbell, Eufy Security",
            "market_reality": "Installed on front doors of millions of homes for visitor video calls and motion alerts.",
            "famous_cve": "CVE-2019-9483: Plaintext Wi-Fi credential leakage during device initialization mode.",
            "academic_citation": "Stratosphere IoT-23 benchmark capture sets."
        }
    ],

    "literature_survey": [
        {
            "id": 1,
            "author": "Antonakakis et al.",
            "year": 2017,
            "title": "Understanding the Mirai Botnet",
            "focus": "Mirai botnet analysis & propagation mechanism",
            "findings": "Studied how Mirai infected hundreds of thousands of IoT devices using factory-default credentials and executed multi-hundred-Gbps DDoS attacks.",
            "limitations": "Focused primarily on post-infection botnet telemetry and signature-based tracking.",
            "relevance": "Underlines the catastrophic risk of unprotected IoT devices and provides real-world DDoS/scanning attack patterns for our benchmark."
        },
        {
            "id": 2,
            "author": "Sivanathan et al.",
            "year": 2018,
            "title": "Classifying IoT Devices in Smart Environments Using Network Traffic",
            "focus": "Device profiling and traffic behavior",
            "findings": "Proved that IoT devices exhibit deterministic, recurring traffic characteristics (packet sizes, sleep/activity cycles, and fixed remote endpoints).",
            "limitations": "Aimed at device identification/inventory rather than intrusion or compromise detection.",
            "relevance": "Direct theoretical foundation confirming that smart home devices have strict 'normal' behavioral profiles."
        },
        {
            "id": 3,
            "author": "Meidan et al.",
            "year": 2018,
            "title": "N-BaIoT: Network-Based Detection of IoT Botnet Attacks Using Deep Autoencoders",
            "focus": "Deep learning anomaly detection for IoT botnets",
            "findings": "Trained deep autoencoders per device to flag reconstruction errors as anomalies upon Mirai/BASHLITE infection.",
            "limitations": "Computationally heavy, high memory consumption, difficult to train/run directly on consumer home routers.",
            "relevance": "Highlights the necessity for our lightweight, tabular Random Forest approach that runs fast on edge hardware."
        },
        {
            "id": 4,
            "author": "Stratosphere Laboratory",
            "year": 2020,
            "title": "IoT-23 Dataset: A Labeled Dataset with Real IoT Malware and Benign Traffic",
            "focus": "Standardized benchmark dataset for IoT network security",
            "findings": "Captured 23 diverse network scenarios (20 malware captures including Mirai, Torii, Kenjiro, and 3 extensive benign IoT smart home captures).",
            "limitations": "Raw pcap files are massive and require systematic flow aggregation and cleaning.",
            "relevance": "Serves as our primary benchmark dataset for ground-truth training and testing of flow classification."
        },
        {
            "id": 5,
            "author": "Breiman",
            "year": 2001,
            "title": "Random Forests",
            "focus": "Ensemble learning via randomized decision trees",
            "findings": "Introduced bootstrap aggregating (bagging) with random feature subspace selection, yielding superior generalization on tabular data.",
            "limitations": "Not a networking paper; requires domain-specific feature engineering.",
            "relevance": "Core machine learning model chosen for its speed, interpretability (feature importance), and resistance to overfitting."
        }
    ],

    "research_gap": {
        "statement": "From this survey, we found that signature-based tools fail completely on encrypted traffic (HTTPS, TLS, MQTT over TLS), and that existing deep learning solutions (like N-BaIoT autoencoders) are too heavy for edge routers. There is an urgent need for a simple, behaviour-based method that works on encrypted traffic without payload decryption, which is the exact gap this project addresses."
    },

    "problem_statement": {
        "summary": "IoT devices in homes are easy to hack and are often used by attackers to launch attacks such as DDoS. The owner usually does not notice, because the device seems to work normally. Traditional security tools depend on reading packet content, which is not possible when traffic is encrypted, and IoT devices are too small to run antivirus software. Therefore, a method is needed that can detect compromised IoT devices from their network behaviour alone, without accessing the encrypted data."
    },

    "system_architecture": {
        "flow_diagram": "IoT Devices ──► Network Traffic ──► Packet Capture ──► Flow Creation ──► Feature Extraction ──► Random Forest Model ──► Normal / Suspicious ──► Security Alert",
        "layers": [
            {
                "layer_num": 1,
                "name": "Input Layer",
                "role": "Smart Home IoT Devices (Philips Hue, Wipro, Tapo, Amazon Echo, Samsung TV)",
                "description": "Widely-used smart-home endpoints: Philips Hue/Wipro smart bulbs, TP-Link Tapo C200 cameras, Amazon Echo Dot speakers, Samsung Smart TVs, and Wipro 16A smart plugs.",
                "protocols": ["TLS 1.3", "MQTT over TLS (8883)", "CoAP over DTLS", "HTTPS / RTSP"]
            },
            {
                "layer_num": 2,
                "name": "Capture Layer",
                "role": "Packet Capture & Interception",
                "description": "Sniffs raw Ethernet/Wi-Fi frames passing through the home gateway interface using Scapy or loads pre-captured IoT-23 pcap datasets without touching payload contents.",
                "tools": ["Scapy", "Wireshark", "pcap / raw socket"]
            },
            {
                "layer_num": 3,
                "name": "Processing Layer",
                "role": "5-Tuple Flow Aggregation & Feature Extraction",
                "description": "Groups individual packets into bidirectional flows keyed by 5-tuple (Src IP, Dst IP, Src Port, Dst Port, Protocol). Computes the 7 behavioral metadata features.",
                "features": [
                    "Flow Duration (s)",
                    "Average Packet Size (Bytes)",
                    "Packets Per Second (pps)",
                    "Bytes Per Second (Bps)",
                    "Unique Destination IPs",
                    "Unique Destination Ports",
                    "Protocol Type (TCP/UDP)"
                ]
            },
            {
                "layer_num": 4,
                "name": "Detection Layer",
                "role": "Random Forest Inference Engine",
                "description": "Feeds the 7-dimensional feature vector into the trained Random Forest classifier. An ensemble of decision trees votes independently; majority vote decides 0 (Normal) or 1 (Suspicious/Malicious).",
                "output": "Binary Label (0 or 1) + Confidence Probability %"
            },
            {
                "layer_num": 5,
                "name": "Output Layer",
                "role": "Alert & Network Mitigation Console",
                "description": "Presents real-time status on the Network Operations Center dashboard and triggers automated alerts with actionable mitigation recommendations (VLAN quarantine, ACL port block).",
                "actions": ["Dashboard Visualization", "Security Alert Feed", "Quarantine Recommendation"]
            }
        ]
    },

    "model_description": {
        "model_name": "Random Forest Classifier",
        "rationale": [
            "Works exceptionally well on tabular, feature-based network metadata.",
            "Fast inference execution (~sub-millisecond per flow), ideal for home gateways.",
            "Handles multi-dimensional features without extensive manual hyperparameter tuning.",
            "Inherent resistance to overfitting due to bagging and majority voting across trees.",
            "Provides transparent Gini feature importance to explain exactly why a flow was flagged as malicious."
        ],
        "input_vector": "7 tabular flow features (Metadata only, 0% payload)",
        "output": "0 for Normal | 1 for Malicious (Suspicious)"
    },

    "system_description": {
        "hardware": "Standard commodity laptop, PC, or modern consumer Wi-Fi router. No dedicated GPU or FPGA acceleration required.",
        "software_tools": [
            {"name": "Python 3.10+", "purpose": "Core programming language"},
            {"name": "pandas & NumPy", "purpose": "Flow preprocessing, array manipulation, and statistical aggregation"},
            {"name": "scikit-learn", "purpose": "Random Forest training, testing, and evaluation metrics"},
            {"name": "Scapy & Wireshark", "purpose": "Packet sniffing, 5-tuple parsing, and network analysis"},
            {"name": "FastAPI & WebSockets", "purpose": "Real-time 1 Hz telemetry streaming and dashboard API"},
            {"name": "HTML5 / Vanilla CSS / ES6 JS", "purpose": "Browser-based Network Operations Center visualization"},
            {"name": "Mininet (Optional)", "purpose": "Emulation of multi-device smart home network topologies"}
        ],
        "dataset": "IoT-23 Dataset (Stratosphere Laboratory) with verified benign smart-home and malicious botnet captures."
    },

    "ten_step_workflow": [
        {"step": 1, "title": "Network Traffic Generation", "detail": "Start with encrypted network traffic emitted by smart-home IoT devices."},
        {"step": 2, "title": "Data Collection", "detail": "Collect packets using the IoT-23 dataset or live Wireshark/Scapy capture."},
        {"step": 3, "title": "Preprocessing & Labeling", "detail": "Clean missing/corrupted records and assign binary ground-truth labels (0=benign, 1=malicious)."},
        {"step": 4, "title": "Flow Grouping", "detail": "Group individual packets into bidirectional network flows using 5-tuple identifiers."},
        {"step": 5, "title": "Feature Extraction", "detail": "Extract the 7 behavioral metadata features (duration, packet size, pps, bps, unique IPs, unique ports, protocol)."},
        {"step": 6, "title": "Train-Test Split", "detail": "Partition the labeled tabular dataset into training (80%) and testing (20%) sets with stratified sampling."},
        {"step": 7, "title": "Random Forest Model Training", "detail": "Train the Random Forest ensemble on the training set using bootstrap aggregation."},
        {"step": 8, "title": "Model Testing", "detail": "Evaluate model inference on previously unseen test flows."},
        {"step": 9, "title": "Metric Calculation", "detail": "Calculate performance measures: Accuracy, Precision, Recall, F1-Score, and False Positive Rate."},
        {"step": 10, "title": "Real-Time Classification & Alerting", "detail": "Classify incoming live flows in real time and generate instant security alerts for compromised devices."}
    ],

    "viva_qa": [
        {
            "q": "Faculty Question: Are smart bulbs and smart plugs really common in households? Who actually uses them?",
            "a": "Yes, absolutely. Wi-Fi Smart Bulbs (Wipro, Philips Hue, Syska, Xiaomi Mi) and Smart Plugs (Tapo, Wipro 16A) are the #1 entry-level IoT devices sold in India and globally. Over 10 million smart bulbs and plugs are sold annually on Amazon and Flipkart for as low as ₹499. Consumers use them daily with Amazon Alexa and Google Home to automate lights, geysers, ACs, and water pumps. In Sivanathan et al. (Paper #2 in our survey, UNSW Sydney), the authors specifically deployed Philips Hue and LIFX smart bulbs in their smart home testbed."
        },
        {
            "q": "Faculty Question: Why would an attacker bother hacking a simple smart bulb or plug?",
            "a": "Attackers do not hack a smart bulb to turn off lights; they hack it to weaponize it into a botnet node (like Mirai) and to pivot into the home network. Smart bulbs run Linux microkernels or RTOS on Wi-Fi microcontrollers (e.g. ESP8266/ESP32). In 2020, Check Point Research published CVE-2020-6007, showing how exploiting a heap buffer overflow in a Philips Hue smart bulb allowed attackers to take over the bridge and push malware to the homeowner's personal laptop and network storage."
        },
        {
            "q": "Why is packet payload inspection not viable for modern IoT security?",
            "a": "Over 90% of modern IoT traffic is encrypted using TLS, HTTPS, or DTLS. Reading packet payloads requires breaking encryption or installing proxy certificates, which is computationally infeasible on lightweight IoT devices and violates user privacy. Metadata analysis inspects packet timing, sizing, and flow patterns without needing decryption keys."
        },
        {
            "q": "Why chose Random Forest over Deep Learning (e.g., CNN or Autoencoders like N-BaIoT)?",
            "a": "Deep neural networks and autoencoders require heavy GPU compute, high memory, and extensive tuning. Smart home gateways and edge routers have limited RAM and CPU. Random Forest trains in seconds, evaluates flows in microseconds, handles tabular features with high accuracy (over 99%), and provides Gini feature importance for transparent explainability."
        },
        {
            "q": "What features distinguish a normal smart bulb from a compromised smart bulb?",
            "a": "A benign smart bulb connects exclusively to 1 cloud IP, sends small keepalive/status packets (64-128 bytes) at low rates (<2 packets/second). When infected with Mirai, it suddenly communicates with hundreds of unique destination IPs (scanning) or floods thousands of packets/second (>1000 pps) to a DDoS victim, creating an obvious statistical anomaly in metadata."
        },
        {
            "q": "What is the IoT-23 dataset and why is it used?",
            "a": "IoT-23 was published by Stratosphere Laboratory (Czech Technical University). It is the recognized academic benchmark containing 20 real IoT malware captures (Mirai, Torii, Kenjiro, etc.) and 3 long-running benign smart-home captures, providing authentic ground-truth labels."
        },
        {
            "q": "What is a 5-tuple in Computer Networks and how does it define a flow?",
            "a": "A 5-tuple consists of Source IP, Destination IP, Source Port, Destination Port, and Transport Protocol (TCP/UDP). All packets sharing these 5 parameters within an inactivity timeout window belong to the same logical bidirectional conversation (flow)."
        }
    ]
}
