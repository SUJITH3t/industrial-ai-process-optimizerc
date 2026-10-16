import os
import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, User, SensorData, PredictionHistory, OperatorLog, AgentActionLog, SimulationRun
from crud import (
    create_user,
    get_user_by_username,
    verify_password,
    create_sensor_reading,
    create_prediction_history,
    get_sensor_history,
    get_prediction_history,
    create_operator_log,
    get_operator_logs,
    create_agent_action_log,
    get_agent_action_logs,
    create_simulation_run,
    get_simulation_runs,
)

from services.ml_service import predict_ml
from services.dl_service import predict_dl
from nlp.nlp_service import analyze_log, SAMPLE_LOGS
from slm.slm_service import slm_engine
from genai.genai_service import generate_synthetic_stream, SCENARIO_PROFILES
from agentic.agent_service import agent_brain
from lld.lld_service import get_lld_specs

app = Flask(__name__)
CORS(app)

# Initialize database schema
Base.metadata.create_all(bind=engine)


def seed_default_admin():
    db = SessionLocal()
    try:
        if not get_user_by_username(db, "admin"):
            create_user(db, "admin", "admin123", "admin@smartmfg.local")
    finally:
        db.close()


seed_default_admin()


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "service": "Smart Manufacturing Process Optimization Engine",
        "version": "2.4.0",
        "modules": ["ML (7-Models)", "DL (ANN)", "NLP (NER & Triage)", "SLM (Copilot)", "LLD (C4/OpenAPI)", "Gen AI (Simulator)", "Agentic AI (Closed-Loop)"]
    })


# -------------------------------------------------------------
# User Authentication & Management
# -------------------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    db = SessionLocal()
    try:
        user = get_user_by_username(db, username)
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"success": False, "message": "Invalid username or password"}), 401

        return jsonify({"success": True, "message": "Login successful", "username": user.username})
    finally:
        db.close()


@app.route("/users", methods=["POST"])
def create_new_user():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()
    email = data.get("email")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    db = SessionLocal()
    try:
        if get_user_by_username(db, username):
            return jsonify({"error": "user already exists"}), 409

        user = create_user(db, username, password, email)
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
        }), 201
    finally:
        db.close()


# -------------------------------------------------------------
# Level 1: Machine Learning & Level 2: Deep Learning
# -------------------------------------------------------------
@app.route("/predict/ml", methods=["POST"])
def ml_prediction():
    data = request.get_json(silent=True) or {}
    try:
        prediction = predict_ml(data)

        db = SessionLocal()
        try:
            sensor = create_sensor_reading(db, data, user_id=data.get("user_id"))
            create_prediction_history(
                db,
                model_name=prediction.get("model", "Machine Learning"),
                efficiency=prediction.get("efficiency", 0),
                waste=prediction.get("waste", 0),
                failure=prediction.get("failure", 0),
                message=prediction.get("message", ""),
                user_id=data.get("user_id"),
                sensor_data_id=sensor.id,
            )
        finally:
            db.close()

        return jsonify(prediction)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/predict/dl", methods=["POST"])
def dl_prediction():
    data = request.get_json(silent=True) or {}
    try:
        prediction = predict_dl(data)

        db = SessionLocal()
        try:
            sensor = create_sensor_reading(db, data, user_id=data.get("user_id"))
            create_prediction_history(
                db,
                model_name="Deep Learning (ANN)",
                efficiency=prediction.get("efficiency", 0),
                waste=prediction.get("waste", 0),
                failure=prediction.get("failure", 0),
                message=prediction.get("message", ""),
                user_id=data.get("user_id"),
                sensor_data_id=sensor.id,
            )
        finally:
            db.close()

        return jsonify(prediction)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ml/metrics", methods=["GET"])
def get_ml_metrics():
    """Return 7-model ML comparison metrics, feature importance, confusion matrix, ROC data."""
    base_dir = Path(__file__).resolve().parent
    metrics_path = base_dir / "trained_models" / "ml_metrics.json"
    if not metrics_path.exists():
        metrics_path = base_dir / "ml" / "ml_metrics.json"

    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            return jsonify(json.load(f))

    return jsonify({"error": "ML metrics not generated yet. Run python backend/ml/train_model.py"}), 404


@app.route("/dl/metrics", methods=["GET"])
def get_dl_metrics():
    """Return Deep Learning ANN training history (loss, accuracy curves) and evaluation."""
    base_dir = Path(__file__).resolve().parent
    metrics_path = base_dir / "trained_models" / "dl_metrics.json"
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            return jsonify(json.load(f))

    return jsonify({"error": "DL metrics not generated yet. Run python backend/dl/train_model.py"}), 404


# -------------------------------------------------------------
# Level 3: Natural Language Processing (NLP)
# -------------------------------------------------------------
@app.route("/nlp/analyze", methods=["POST"])
def nlp_analyze():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Log text is required"}), 400

    result = analyze_log(text)

    # Persist log to DB
    db = SessionLocal()
    try:
        log_entry = create_operator_log(
            db,
            log_text=text,
            urgency=result["urgency"],
            category=result["category"],
            sentiment_score=result["sentiment_score"],
            entities=result["entities"],
            summary=result["summary"],
            user_id=data.get("user_id")
        )
        result["log_id"] = log_entry.id
    finally:
        db.close()

    return jsonify(result)


@app.route("/nlp/samples", methods=["GET"])
def nlp_samples():
    return jsonify(SAMPLE_LOGS)


@app.route("/nlp/logs", methods=["GET"])
def list_operator_logs():
    db = SessionLocal()
    try:
        logs = get_operator_logs(db, limit=30)
        return jsonify([
            {
                "id": l.id,
                "text": l.log_text,
                "urgency": l.urgency,
                "category": l.category,
                "sentiment_score": l.sentiment_score,
                "entities": json.loads(l.entities_json) if l.entities_json else {},
                "summary": l.summary,
                "created_at": l.created_at.isoformat()
            }
            for l in logs
        ])
    finally:
        db.close()


# -------------------------------------------------------------
# Level 4: Small Language Model (SLM) Copilot
# -------------------------------------------------------------
@app.route("/slm/summarize", methods=["POST"])
def slm_summarize():
    data = request.get_json(silent=True) or {}
    logs = data.get("logs", [])
    if not logs:
        # Default fallback to recent logs or sample
        logs = [s["text"] for s in SAMPLE_LOGS]

    summary_result = slm_engine.summarize_shift(logs)
    return jsonify(summary_result)


@app.route("/slm/recommend", methods=["POST"])
def slm_recommend():
    data = request.get_json(silent=True) or {}
    recommendations = slm_engine.generate_recommendations(data)
    return jsonify({
        "model": slm_engine.model_name,
        "recommendations": recommendations,
        "count": len(recommendations)
    })


@app.route("/slm/ask", methods=["POST"])
def slm_ask():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    response = slm_engine.ask(query, context=data.get("context"))
    return jsonify(response)


# -------------------------------------------------------------
# Level 5: Low-Level Design (LLD) & OpenAPI
# -------------------------------------------------------------
@app.route("/lld/spec", methods=["GET"])
def lld_spec():
    specs = get_lld_specs()
    return jsonify(specs["openapi"])


@app.route("/lld/architecture", methods=["GET"])
def lld_architecture():
    specs = get_lld_specs()
    return jsonify(specs["architecture"])


# -------------------------------------------------------------
# Level 6: Generative AI (Gen AI) Scenario Simulator
# -------------------------------------------------------------
@app.route("/genai/scenarios", methods=["GET"])
def list_scenarios():
    return jsonify([
        {"key": k, "title": v["title"], "description": v["description"]}
        for k, v in SCENARIO_PROFILES.items()
    ])


@app.route("/genai/simulate", methods=["POST"])
def run_simulation():
    data = request.get_json(silent=True) or {}
    scenario_key = data.get("scenario", "thermal_runaway")
    steps = int(data.get("steps", 40))

    sim_result = generate_synthetic_stream(scenario_key=scenario_key, num_steps=steps)

    # Persist simulation run
    db = SessionLocal()
    try:
        create_simulation_run(
            db,
            scenario_type=sim_result["title"],
            sample_count=sim_result["sample_count"],
            fidelity_score=sim_result["fidelity_score"],
            contingency_plan=json.dumps(sim_result["contingency_plan"])
        )
    finally:
        db.close()

    return jsonify(sim_result)


@app.route("/genai/history", methods=["GET"])
def simulation_history():
    db = SessionLocal()
    try:
        runs = get_simulation_runs(db, limit=20)
        return jsonify([
            {
                "id": r.id,
                "scenario_type": r.scenario_type,
                "sample_count": r.sample_count,
                "fidelity_score": r.fidelity_score,
                "contingency_plan": json.loads(r.contingency_plan) if r.contingency_plan else {},
                "created_at": r.created_at.isoformat()
            }
            for r in runs
        ])
    finally:
        db.close()


# -------------------------------------------------------------
# Level 7: Agentic AI Closed-Loop Optimization Controller
# -------------------------------------------------------------
@app.route("/agent/status", methods=["GET"])
def get_agent_status():
    return jsonify(agent_brain.get_status())


@app.route("/agent/step", methods=["POST"])
def step_agent():
    data = request.get_json(silent=True) or {}
    incoming = data.get("sensors")
    step_result = agent_brain.perceive_and_act(incoming)

    # Persist any executed actions
    if step_result.get("executed_actions"):
        db = SessionLocal()
        try:
            for act in step_result["executed_actions"]:
                create_agent_action_log(
                    db,
                    trigger_reason=act["trigger"],
                    parameter_name=act["parameter"],
                    old_value=act["old_val"],
                    new_value=act["new_val"],
                    rationale=act["rationale"],
                    status=act["status"]
                )
        finally:
            db.close()

    return jsonify(step_result)


@app.route("/agent/toggle-auto", methods=["POST"])
def toggle_agent_auto():
    data = request.get_json(silent=True) or {}
    enabled = bool(data.get("enabled", True))
    res = agent_brain.toggle_autonomous(enabled)
    return jsonify(res)


@app.route("/agent/kill-switch", methods=["POST"])
def agent_kill_switch():
    data = request.get_json(silent=True) or {}
    active = bool(data.get("active", True))
    res = agent_brain.set_emergency_stop(active)
    return jsonify(res)


@app.route("/agent/override", methods=["POST"])
def agent_manual_override():
    data = request.get_json(silent=True) or {}
    parameter = data.get("parameter")
    value = data.get("value")
    if parameter is None or value is None:
        return jsonify({"error": "parameter and value are required"}), 400

    res = agent_brain.manual_override(parameter, float(value))

    # Persist to DB
    db = SessionLocal()
    try:
        create_agent_action_log(
            db,
            trigger_reason="MANUAL_OVERRIDE",
            parameter_name=parameter,
            old_value=0.0,
            new_value=float(value),
            rationale="Operator manual override applied from control room.",
            status="Manual"
        )
    finally:
        db.close()

    return jsonify(res)


@app.route("/agent/actions", methods=["GET"])
def list_agent_actions():
    db = SessionLocal()
    try:
        actions = get_agent_action_logs(db, limit=30)
        return jsonify([
            {
                "id": a.id,
                "trigger_reason": a.trigger_reason,
                "parameter_name": a.parameter_name,
                "old_value": a.old_value,
                "new_value": a.new_value,
                "rationale": a.rationale,
                "status": a.status,
                "created_at": a.created_at.isoformat()
            }
            for a in actions
        ])
    finally:
        db.close()


# -------------------------------------------------------------
# Sensor & History Endpoints
# -------------------------------------------------------------
@app.route("/sensor-data", methods=["POST"])
def save_sensor_data():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    db = SessionLocal()
    try:
        sensor = create_sensor_reading(db, data, user_id=user_id)
        return jsonify({
            "id": sensor.id,
            "temperature": sensor.temperature,
            "pressure": sensor.pressure,
            "humidity": sensor.humidity,
            "speed": sensor.speed,
            "vibration": sensor.vibration,
            "material": sensor.material,
            "power": sensor.power,
            "created_at": sensor.created_at.isoformat(),
        }), 201
    finally:
        db.close()


@app.route("/sensor-data", methods=["GET"])
def list_sensor_data():
    user_id = request.args.get("user_id", type=int)
    db = SessionLocal()
    try:
        sensors = get_sensor_history(db, user_id=user_id, limit=50)
        return jsonify([
            {
                "id": item.id,
                "temperature": item.temperature,
                "pressure": item.pressure,
                "humidity": item.humidity,
                "speed": item.speed,
                "vibration": item.vibration,
                "material": item.material,
                "power": item.power,
                "created_at": item.created_at.isoformat(),
                "user_id": item.user_id,
            }
            for item in sensors
        ])
    finally:
        db.close()


@app.route("/predictions", methods=["GET"])
def list_predictions():
    user_id = request.args.get("user_id", type=int)
    db = SessionLocal()
    try:
        predictions = get_prediction_history(db, user_id=user_id, limit=50)
        return jsonify([
            {
                "id": item.id,
                "model_name": item.model_name,
                "efficiency": item.efficiency,
                "waste": item.waste,
                "failure": item.failure,
                "message": item.message,
                "created_at": item.created_at.isoformat(),
                "user_id": item.user_id,
                "sensor_data_id": item.sensor_data_id,
            }
            for item in predictions
        ])
    finally:
        db.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)