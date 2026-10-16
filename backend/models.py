from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sensor_data = relationship("SensorData", back_populates="user")
    predictions = relationship("PredictionHistory", back_populates="user")
    logs = relationship("OperatorLog", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    speed = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)
    material = Column(Float, nullable=False)
    power = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="sensor_data")
    predictions = relationship("PredictionHistory", back_populates="sensor_data")

    def __repr__(self):
        return f"<SensorData id={self.id} temperature={self.temperature} speed={self.speed}>"


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(50), nullable=False)
    efficiency = Column(Float, nullable=False)
    waste = Column(Float, nullable=False)
    failure = Column(Float, nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sensor_data_id = Column(Integer, ForeignKey("sensor_data.id"), nullable=True)

    user = relationship("User", back_populates="predictions")
    sensor_data = relationship("SensorData", back_populates="predictions")

    def __repr__(self):
        return f"<PredictionHistory id={self.id} model={self.model_name} efficiency={self.efficiency}>"


class OperatorLog(Base):
    __tablename__ = "operator_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_text = Column(Text, nullable=False)
    urgency = Column(String(30), default="Medium")
    category = Column(String(50), default="General")
    sentiment_score = Column(Float, default=0.0)
    entities_json = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="logs")

    def __repr__(self):
        return f"<OperatorLog id={self.id} urgency={self.urgency} category={self.category}>"


class AgentActionLog(Base):
    __tablename__ = "agent_action_logs"

    id = Column(Integer, primary_key=True, index=True)
    trigger_reason = Column(String(120), nullable=False)
    parameter_name = Column(String(50), nullable=False)
    old_value = Column(Float, nullable=False)
    new_value = Column(Float, nullable=False)
    rationale = Column(Text, nullable=True)
    status = Column(String(30), default="Executed")
    safety_checked = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AgentActionLog id={self.id} param={self.parameter_name} status={self.status}>"


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    scenario_type = Column(String(80), nullable=False)
    sample_count = Column(Integer, default=50)
    fidelity_score = Column(Float, default=95.0)
    contingency_plan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SimulationRun id={self.id} scenario={self.scenario_type}>"
