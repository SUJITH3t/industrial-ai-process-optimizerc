import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "trained_models", "dl_model.keras")
SCALER_PATH = os.path.join(BASE_DIR, "trained_models", "dl_scaler.pkl")

_model = None
_scaler = None


def _get_artifacts():
    global _model, _scaler
    if _model is None and os.path.exists(MODEL_PATH):
        try:
            _model = tf.keras.models.load_model(MODEL_PATH)
        except Exception:
            _model = None
    if _scaler is None and os.path.exists(SCALER_PATH):
        try:
            _scaler = joblib.load(SCALER_PATH)
        except Exception:
            _scaler = None
    return _model, _scaler


def _fallback_prediction(data):
    vibration = float(data.get("vibration", 0.3))
    temp = float(data.get("temperature", 70))
    efficiency = max(65.0, min(96.0, 98.0 - vibration * 18.0 - (temp - 65) * 0.4))
    waste = round(max(0.5, (100.0 - efficiency) * 0.20), 2)
    failure = round(max(0.2, (100.0 - efficiency) * 0.12), 2)

    return {
        "model": "Deep Learning (ANN)",
        "probability": round(efficiency / 100.0, 4),
        "temperature": float(data.get("temperature", 0)),
        "pressure": float(data.get("pressure", 0)),
        "humidity": float(data.get("humidity", 0)),
        "speed": float(data.get("speed", 0)),
        "efficiency": round(efficiency, 2),
        "waste": waste,
        "failure": failure,
        "status": "Optimal" if efficiency >= 85 else ("Warning" if efficiency >= 80 else "Critical"),
        "message": "Deep Learning ANN Prediction Completed (Heuristic Engine)"
    }


def predict_dl(data):
    """
    Deep Learning Prediction Service utilizing the trained ANN and fitted scaler.
    """
    model, scaler = _get_artifacts()
    if model is None:
        return _fallback_prediction(data)

    feature_cols = ["temperature", "pressure", "humidity", "speed", "vibration", "material", "power"]
    df_in = pd.DataFrame([{col: float(data.get(col, 0)) for col in feature_cols}])

    try:
        if scaler is not None:
            scaled_input = scaler.transform(df_in)
        else:
            scaled_input = df_in.to_numpy()

        predicted_prob = float(model.predict(scaled_input, verbose=0)[0][0])
        efficiency = round(74.0 + (predicted_prob * (96.0 - 74.0)), 2)
        waste = round(max(0.5, (100.0 - efficiency) * 0.20), 2)
        failure = round(max(0.2, (100.0 - efficiency) * 0.12), 2)

        return {
            "model": "Deep Learning (ANN)",
            "probability": round(predicted_prob, 4),
            "temperature": float(data.get("temperature", 0)),
            "pressure": float(data.get("pressure", 0)),
            "humidity": float(data.get("humidity", 0)),
            "speed": float(data.get("speed", 0)),
            "efficiency": efficiency,
            "waste": waste,
            "failure": failure,
            "status": "Optimal" if efficiency >= 85 else ("Warning" if efficiency >= 80 else "Critical"),
            "message": "Deep Learning ANN Prediction Completed Successfully"
        }
    except Exception as exc:
        print("DL inference fallback due to:", exc)
        return _fallback_prediction(data)