import json
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User, SensorData, PredictionHistory, OperatorLog, AgentActionLog, SimulationRun

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(db: Session, username: str, password: str, email: str = None):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return None

    user = User(
        username=username,
        password_hash=hash_password(password),
        email=email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_sensor_reading(db: Session, data: dict, user_id: int = None):
    sensor = SensorData(
        temperature=float(data.get("temperature", 0)),
        pressure=float(data.get("pressure", 0)),
        humidity=float(data.get("humidity", 0)),
        speed=float(data.get("speed", 0)),
        vibration=float(data.get("vibration", 0)),
        material=float(data.get("material", 0)),
        power=float(data.get("power", 0)),
        user_id=user_id,
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return sensor


def get_sensor_history(db: Session, user_id: int = None, limit: int = 50):
    query = db.query(SensorData)
    if user_id is not None:
        query = query.filter(SensorData.user_id == user_id)
    return query.order_by(SensorData.created_at.desc()).limit(limit).all()


def create_prediction_history(db: Session, model_name: str, efficiency: float, waste: float, failure: float,
                             message: str, user_id: int = None, sensor_data_id: int = None):
    prediction = PredictionHistory(
        model_name=model_name,
        efficiency=float(efficiency),
        waste=float(waste),
        failure=float(failure),
        message=message,
        user_id=user_id,
        sensor_data_id=sensor_data_id,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def get_prediction_history(db: Session, user_id: int = None, limit: int = 50):
    query = db.query(PredictionHistory)
    if user_id is not None:
        query = query.filter(PredictionHistory.user_id == user_id)
    return query.order_by(PredictionHistory.created_at.desc()).limit(limit).all()


def create_operator_log(db: Session, log_text: str, urgency: str, category: str,
                        sentiment_score: float, entities: dict, summary: str = None, user_id: int = None):
    log_entry = OperatorLog(
        log_text=log_text,
        urgency=urgency,
        category=category,
        sentiment_score=float(sentiment_score),
        entities_json=json.dumps(entities),
        summary=summary,
        user_id=user_id
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def get_operator_logs(db: Session, limit: int = 30):
    return db.query(OperatorLog).order_by(OperatorLog.created_at.desc()).limit(limit).all()


def create_agent_action_log(db: Session, trigger_reason: str, parameter_name: str,
                            old_value: float, new_value: float, rationale: str, status: str = "Executed"):
    action = AgentActionLog(
        trigger_reason=trigger_reason,
        parameter_name=parameter_name,
        old_value=float(old_value),
        new_value=float(new_value),
        rationale=rationale,
        status=status,
        safety_checked=1
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def get_agent_action_logs(db: Session, limit: int = 30):
    return db.query(AgentActionLog).order_by(AgentActionLog.created_at.desc()).limit(limit).all()


def create_simulation_run(db: Session, scenario_type: str, sample_count: int, fidelity_score: float, contingency_plan: str):
    sim = SimulationRun(
        scenario_type=scenario_type,
        sample_count=sample_count,
        fidelity_score=fidelity_score,
        contingency_plan=contingency_plan
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)
    return sim


def get_simulation_runs(db: Session, limit: int = 20):
    return db.query(SimulationRun).order_by(SimulationRun.created_at.desc()).limit(limit).all()
