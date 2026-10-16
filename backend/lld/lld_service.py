from typing import Dict, Any

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Smart Manufacturing Process Optimization API",
        "description": "Production-grade RESTful API orchestrating Machine Learning, Deep Learning, Natural Language Processing, Small Language Models, Generative AI Scenario Simulations, and Autonomous Agentic AI Control Loops for Smart Manufacturing facilities.",
        "version": "2.4.0",
        "contact": {
            "name": "Industrial AI Engineering Team",
            "email": "mfg-ai@smartmfg.internal"
        }
    },
    "servers": [
        {"url": "http://127.0.0.1:5001", "description": "Local Edge Process Controller"},
        {"url": "https://api.smartmfg.internal/v2", "description": "Enterprise Production Plant Cluster"}
    ],
    "paths": {
        "/predict/ml": {
            "post": {
                "summary": "Execute ML Pipeline Prediction",
                "description": "Predicts manufacturing efficiency, material waste, and failure risk using the benchmarked optimal ML model pipeline.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SensorInput"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "ML Prediction Result",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PredictionResponse"}}}
                    }
                }
            }
        },
        "/predict/dl": {
            "post": {
                "summary": "Execute Deep Learning ANN Prediction",
                "description": "Predicts process efficiency with probability calibration using a 3-layer deep artificial neural network and standard scaler.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SensorInput"}
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Deep Learning Prediction Result",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PredictionResponse"}}}
                    }
                }
            }
        },
        "/nlp/analyze": {
            "post": {
                "summary": "Process Operator Logs & Maintenance Reports",
                "description": "Performs text classification, domain-specific NER (machines, components, metrics, error codes), sentiment analysis, and keyword extraction.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"text": {"type": "string"}},
                                "required": ["text"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "NLP Analysis Extraction"}
                }
            }
        },
        "/slm/summarize": {
            "post": {
                "summary": "Small Language Model Shift Handover Summarizer",
                "description": "Generates a compressed, domain-specific shift handover summary with ROUGE-1/2/L evaluation metrics.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"logs": {"type": "array", "items": {"type": "string"}}}
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "SLM Summary Output"}}
            }
        },
        "/slm/recommend": {
            "post": {
                "summary": "SLM Process Engineering Recommendations",
                "description": "Generates prioritized actionable parameter modifications based on real-time equipment telemetry.",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SensorInput"}}}
                },
                "responses": {"200": {"description": "Actionable Engineering Recommendations"}}
            }
        },
        "/genai/simulate": {
            "post": {
                "summary": "Generative AI Scenario Stress-Testing Simulation",
                "description": "Synthesizes multivariate time-series sensor runs under stress conditions (thermal runaway, bearing wear, pressure leakage, demand surges) and generates contingency plans.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "scenario": {"type": "string", "enum": ["baseline_normal", "thermal_runaway", "bearing_vibration_spike", "pneumatic_pressure_drop", "surge_demand_overclock"]},
                                    "steps": {"type": "integer", "default": 40}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Synthetic Scenario Telemetry and Quality Fidelity"}}
            }
        },
        "/agent/step": {
            "post": {
                "summary": "Execute Autonomous Agentic Control Step",
                "description": "Runs one cycle of the Perception -> Reasoning -> Planning -> Action execution loop with safety guardrail verification.",
                "responses": {"200": {"description": "Agent Decision Step Result"}}
            }
        },
        "/agent/override": {
            "post": {
                "summary": "Human-in-the-Loop Manual Parameter Override",
                "description": "Allows human engineer to manually adjust any process parameter with safety boundary enforcement.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "parameter": {"type": "string"},
                                    "value": {"type": "number"}
                                },
                                "required": ["parameter", "value"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Override Result"}}
            }
        }
    },
    "components": {
        "schemas": {
            "SensorInput": {
                "type": "object",
                "properties": {
                    "temperature": {"type": "number", "example": 75.0, "description": "Spindle/furnace temperature (°C)"},
                    "pressure": {"type": "number", "example": 40.0, "description": "Pneumatic/hydraulic pressure (bar)"},
                    "humidity": {"type": "number", "example": 55.0, "description": "Ambient factory humidity (%)"},
                    "speed": {"type": "number", "example": 140.0, "description": "Assembly line speed (RPM)"},
                    "vibration": {"type": "number", "example": 0.40, "description": "Rotary bearing vibration (mm/s)"},
                    "material": {"type": "number", "example": 220.0, "description": "Material feed quantity (kg/h)"},
                    "power": {"type": "number", "example": 380.0, "description": "Power consumption (kW)"}
                },
                "required": ["temperature", "pressure", "humidity", "speed", "vibration", "material", "power"]
            },
            "PredictionResponse": {
                "type": "object",
                "properties": {
                    "model": {"type": "string"},
                    "efficiency": {"type": "number", "example": 91.5},
                    "waste": {"type": "number", "example": 1.7},
                    "failure": {"type": "number", "example": 1.02},
                    "status": {"type": "string", "example": "Optimal"},
                    "message": {"type": "string"}
                }
            }
        }
    }
}

SYSTEM_ARCHITECTURE = {
    "c4_levels": {
        "level_1_system_context": {
            "title": "C4 Level 1: System Context Diagram",
            "diagram": """
graph TD
    User["👨‍🔧 Plant Operators & Process Engineers"] -->|Interacts via Web UI| System["🏭 Smart Manufacturing Optimization Platform"]
    Sensors["📡 Factory IoT Sensors & PLCs"] -->|Telemetry via Modbus/MQTT| System
    System -->|Adjusts Speed & Pressure Setpoints| Actuators["⚙️ Industrial CNCs, Press, Conveyors"]
    System -->|Alerts & Shift Handover Bulletins| Notification["📱 Plant Maintenance Dispatch (SMS/Email)"]
""",
            "description": "Defines high-level system boundaries and interactions between human operators, factory PLCs/actuators, and the optimization platform."
        },
        "level_2_container": {
            "title": "C4 Level 2: Container Diagram",
            "diagram": """
graph TD
    Client["💻 Single Page Application (HTML5 / Vanilla CSS / Chart.js)"] -->|REST / HTTPS| APIGateway["🌐 Flask Process Optimization Gateway (:5001)"]
    APIGateway --> MLModule["🧠 Machine Learning Engine (7 Models Scikit-Learn/XGB)"]
    APIGateway --> DLModule["⚡ Deep Learning ANN (Keras/TensorFlow)"]
    APIGateway --> NLPModule["📝 NLP Log Triage & Domain NER Service"]
    APIGateway --> SLMModule["💬 Small Language Model Copilot (Quantized SLM)"]
    APIGateway --> GenAIModule["🎲 Generative AI Scenario Simulator"]
    APIGateway --> AgenticLoop["🤖 Agentic Closed-Loop Controller"]
    APIGateway --> DB["💾 SQLite / PostgreSQL Database (SQLAlchemy ORM)"]
""",
            "description": "Breakdown of deployable micro-containers and service boundaries."
        },
        "level_3_component": {
            "title": "C4 Level 3: Component Diagram (Agentic & Analytics Core)",
            "diagram": """
graph LR
    Perception["Perception Module\n(Sensor Telemetry Ingestion)"] --> WorkingMemory["Working Memory Buffer\n(Rolling 50-Step State)"]
    WorkingMemory --> ReasoningEngine["Reasoning Engine\n(Constraint Violation & Root Cause Diagnosis)"]
    ReasoningEngine --> PlanningModule["Planning Module\n(Multi-Step Mitigation Strategy)"]
    PlanningModule --> Guardrails{"Safety Guardrails\nHard Thresholds Check"}
    Guardrails -->|Safe| ActionExec["Action Dispatcher\n(API Parameter Setpoint Adjuster)"]
    Guardrails -->|Breach| HITL["Human-in-the-Loop Gateway\n(Require Engineer Approval)"]
    ActionExec --> AuditLog["Audit Logger\n(DB Action History)"]
""",
            "description": "Internal architectural structure of the autonomous closed-loop agentic control system."
        }
    },
    "er_diagram": {
        "title": "Entity Relationship (ER) Schema",
        "diagram": """
erDiagram
    USERS ||--o{ SENSOR_DATA : records
    USERS ||--o{ PREDICTION_HISTORY : initiates
    USERS ||--o{ OPERATOR_LOGS : files
    SENSOR_DATA ||--o{ PREDICTION_HISTORY : evaluates
    USERS {
        int id PK
        string username
        string password_hash
        string email
        datetime created_at
    }
    SENSOR_DATA {
        int id PK
        float temperature
        float pressure
        float humidity
        float speed
        float vibration
        float material
        float power
        datetime created_at
        int user_id FK
    }
    PREDICTION_HISTORY {
        int id PK
        string model_name
        float efficiency
        float waste
        float failure
        text message
        datetime created_at
        int user_id FK
        int sensor_data_id FK
    }
    OPERATOR_LOGS {
        int id PK
        text log_text
        string urgency
        string category
        float sentiment_score
        text entities_json
        datetime created_at
        int user_id FK
    }
    AGENT_ACTION_LOGS {
        int id PK
        string trigger_reason
        string parameter_name
        float old_value
        float new_value
        text rationale
        string status
        int safety_checked
        datetime created_at
    }
    SIMULATION_RUNS {
        int id PK
        string scenario_type
        int sample_count
        float fidelity_score
        text contingency_plan
        datetime created_at
    }
"""
    },
    "non_functional_requirements": [
        {"criterion": "Inference Latency", "target": "< 50ms for ML/DL inference; < 100ms for SLM generation", "status": "Compliant"},
        {"criterion": "System Reliability", "target": "99.95% operational uptime; zero unhandled exceptions", "status": "Compliant"},
        {"criterion": "Fail-Safe Guardrails", "target": "Hard limits on temperature (<95°C), speed (<190 RPM), vibration (<0.8 mm/s)", "status": "Enforced"},
        {"criterion": "Human Oversight", "target": "Instant Emergency Kill Switch and Manual Parameter Override", "status": "Enforced"},
        {"criterion": "Auditability", "target": "Immutable chronological logging of all agent actions and predictions", "status": "Enforced"}
    ]
}


def get_lld_specs() -> Dict[str, Any]:
    return {
        "openapi": OPENAPI_SPEC,
        "architecture": SYSTEM_ARCHITECTURE
    }
