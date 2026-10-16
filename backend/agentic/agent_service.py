import time
import datetime
from typing import Dict, Any, List

# Operational Safety Guardrails (Hard bounds that the agent can never exceed)
SAFETY_GUARDRAILS = {
    "temperature": {"min": 50.0, "max": 95.0, "optimal": (65.0, 78.0), "unit": "°C"},
    "pressure": {"min": 20.0, "max": 65.0, "optimal": (38.0, 48.0), "unit": "bar"},
    "speed": {"min": 80.0, "max": 190.0, "optimal": (130.0, 155.0), "unit": "RPM"},
    "vibration": {"min": 0.05, "max": 0.80, "optimal": (0.15, 0.35), "unit": "mm/s"},
    "material": {"min": 150.0, "max": 300.0, "optimal": (200.0, 240.0), "unit": "kg/h"},
    "power": {"min": 250.0, "max": 520.0, "optimal": (340.0, 420.0), "unit": "kW"}
}


class AgenticManufacturingBrain:
    """
    Autonomous closed-loop Agentic AI controller for Smart Manufacturing Optimization.
    Implements Perception -> Working Memory -> Reasoning -> Planning -> Action execution with HITL safety guardrails.
    """

    def __init__(self):
        self.is_autonomous_enabled = True
        self.emergency_stop_active = False
        self.human_in_the_loop_required = False

        # Working Memory (Short-term buffer of recent states and decisions)
        self.current_state = {
            "temperature": 75.0,
            "pressure": 40.0,
            "humidity": 55.0,
            "speed": 145.0,
            "vibration": 0.35,
            "material": 220.0,
            "power": 380.0,
            "efficiency": 90.5,
            "waste": 1.9,
            "failure_risk": 1.1
        }
        self.action_history: List[Dict[str, Any]] = []
        self.anomaly_log: List[str] = []
        self.step_counter = 0

    def get_status(self) -> Dict[str, Any]:
        """Return the current agent status, telemetry, and safety posture."""
        return {
            "autonomous_mode": self.is_autonomous_enabled,
            "emergency_stop": self.emergency_stop_active,
            "hitl_required": self.human_in_the_loop_required,
            "current_state": self.current_state,
            "recent_actions": self.action_history[-8:],
            "guardrails": SAFETY_GUARDRAILS,
            "step_count": self.step_counter
        }

    def set_emergency_stop(self, stop: bool) -> Dict[str, Any]:
        """Trigger or release emergency kill switch."""
        self.emergency_stop_active = stop
        if stop:
            self.current_state["speed"] = 0.0
            self.current_state["efficiency"] = 0.0
            self.action_history.append({
                "id": len(self.action_history) + 1,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "trigger": "OPERATOR KILL SWITCH",
                "action": "EMERGENCY_HALT",
                "parameter": "speed",
                "old_val": 145.0,
                "new_val": 0.0,
                "rationale": "Safety interlock triggered: Assembly line immediately brought to zero velocity.",
                "status": "HALTED"
            })
        return self.get_status()

    def toggle_autonomous(self, enable: bool) -> Dict[str, Any]:
        """Toggle autonomous optimization loop on or off."""
        self.is_autonomous_enabled = enable
        return self.get_status()

    def manual_override(self, parameter: str, value: float) -> Dict[str, Any]:
        """Allow human operator to override any manufacturing parameter within physical limits."""
        if parameter in self.current_state:
            old_val = self.current_state[parameter]
            # Clip to absolute physical limits
            if parameter in SAFETY_GUARDRAILS:
                limits = SAFETY_GUARDRAILS[parameter]
                clipped_val = max(limits["min"], min(limits["max"], float(value)))
            else:
                clipped_val = float(value)

            self.current_state[parameter] = clipped_val
            self.action_history.append({
                "id": len(self.action_history) + 1,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "trigger": "HUMAN_OPERATOR_OVERRIDE",
                "action": "MANUAL_ADJUSTMENT",
                "parameter": parameter,
                "old_val": old_val,
                "new_val": clipped_val,
                "rationale": f"Manual engineer override applied to {parameter}.",
                "status": "Executed"
            })
            self._recalculate_efficiency()

        return self.get_status()

    def _recalculate_efficiency(self):
        """Estimate current efficiency based on manufacturing response curve."""
        t = self.current_state["temperature"]
        p = self.current_state["pressure"]
        s = self.current_state["speed"]
        v = self.current_state["vibration"]

        eff = 96.0 - (v * 16.0) - max(0.0, (t - 75.0) * 0.4) - max(0.0, (40.0 - p) * 0.3)
        eff = round(max(55.0, min(97.0, eff)), 2)

        self.current_state["efficiency"] = eff
        self.current_state["waste"] = round(max(0.5, (100.0 - eff) * 0.20), 2)
        self.current_state["failure_risk"] = round(max(0.2, (100.0 - eff) * 0.12), 2)

    def perceive_and_act(self, incoming_sensors: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Run one execution step of the Perception -> Reasoning -> Planning -> Action loop.
        """
        if self.emergency_stop_active:
            return {
                "decision": "BLOCKED",
                "reason": "Emergency stop is currently engaged. Clear stop before resuming optimization.",
                "status": self.get_status()
            }

        self.step_counter += 1

        # 1. PERCEPTION MODULE
        if incoming_sensors:
            for k, v in incoming_sensors.items():
                if k in self.current_state:
                    self.current_state[k] = float(v)

        temp = self.current_state["temperature"]
        pressure = self.current_state["pressure"]
        speed = self.current_state["speed"]
        vibration = self.current_state["vibration"]

        # 2. REASONING MODULE
        anomalies = []
        action_plan = []

        # Check Temperature
        if temp > SAFETY_GUARDRAILS["temperature"]["optimal"][1]:
            delta = temp - SAFETY_GUARDRAILS["temperature"]["optimal"][1]
            anomalies.append(f"Temperature high ({temp}°C > 78°C)")
            # Reduce speed to alleviate friction/thermal strain
            new_speed = max(SAFETY_GUARDRAILS["speed"]["min"], speed - round(delta * 1.5, 1))
            action_plan.append({
                "parameter": "speed",
                "target_value": new_speed,
                "current_value": speed,
                "action": "THROTTLE_DOWN",
                "rationale": f"Reduce assembly speed by {round(speed - new_speed, 1)} RPM to lower friction-induced heat."
            })
            # Also simulate cooling effect
            self.current_state["temperature"] = round(max(68.0, temp - 2.5), 1)

        elif temp < SAFETY_GUARDRAILS["temperature"]["optimal"][0]:
            anomalies.append(f"Temperature low ({temp}°C < 65°C)")
            new_speed = min(SAFETY_GUARDRAILS["speed"]["optimal"][1], speed + 5.0)
            action_plan.append({
                "parameter": "speed",
                "target_value": new_speed,
                "current_value": speed,
                "action": "ACCELERATE",
                "rationale": "Increase line speed toward optimal operating tempo."
            })

        # Check Vibration
        if vibration > 0.45:
            anomalies.append(f"Vibration elevated ({vibration} mm/s > 0.45 mm/s)")
            new_speed = max(SAFETY_GUARDRAILS["speed"]["min"], speed - 10.0)
            action_plan.append({
                "parameter": "speed",
                "target_value": new_speed,
                "current_value": speed,
                "action": "VIBRATION_DAMPENING",
                "rationale": f"Throttle speed to {new_speed} RPM to avoid harmonic resonance on degraded bearings."
            })
            self.current_state["vibration"] = round(max(0.25, vibration - 0.08), 3)

        # Check Pressure
        if pressure < SAFETY_GUARDRAILS["pressure"]["optimal"][0]:
            anomalies.append(f"Pneumatic pressure low ({pressure} bar < 38 bar)")
            new_pressure = min(SAFETY_GUARDRAILS["pressure"]["optimal"][1], pressure + 4.0)
            action_plan.append({
                "parameter": "pressure",
                "target_value": new_pressure,
                "current_value": pressure,
                "action": "BOOST_PRESSURE",
                "rationale": f"Increase pneumatic regulator from {pressure} to {new_pressure} bar to stabilize tool grip."
            })

        # 3. PLANNING & ACTION EXECUTION
        executed_actions = []
        if self.is_autonomous_enabled and action_plan:
            for plan_item in action_plan:
                param = plan_item["parameter"]
                val = plan_item["target_value"]
                old = self.current_state[param]
                self.current_state[param] = val

                action_record = {
                    "id": len(self.action_history) + 1,
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "trigger": plan_item["action"],
                    "parameter": param,
                    "old_val": old,
                    "new_val": val,
                    "rationale": plan_item["rationale"],
                    "status": "Executed Automatically"
                }
                self.action_history.append(action_record)
                executed_actions.append(action_record)

        self._recalculate_efficiency()

        return {
            "step": self.step_counter,
            "perception_anomalies": anomalies,
            "reasoning": f"Identified {len(anomalies)} process deviations. Formulated {len(action_plan)} corrective actions." if anomalies else "Process operating within optimal parameter corridor.",
            "plan": action_plan,
            "executed_actions": executed_actions,
            "new_state": self.current_state,
            "autonomous_mode": self.is_autonomous_enabled
        }


agent_brain = AgenticManufacturingBrain()
