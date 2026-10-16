import os
import joblib
import numpy as np
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
MODEL_PATH = os.path.join(PROJECT_ROOT, "trained_models", "dl_model.keras")
SCALER_PATH = os.path.join(PROJECT_ROOT, "trained_models", "dl_scaler.pkl")

# Cache loaded artifacts
_model = None
_scaler = None


def get_model_and_scaler():
    global _model, _scaler
    if _model is None and os.path.exists(MODEL_PATH):
        _model = tf.keras.models.load_model(MODEL_PATH)
    if _scaler is None and os.path.exists(SCALER_PATH):
        _scaler = joblib.load(SCALER_PATH)
    return _model, _scaler


def predict_from_sample(sample_data):
    model, scaler = get_model_and_scaler()
    if model is None:
        raise FileNotFoundError(
            "DL model not found. Train it first with: python backend/dl/train_model.py"
        )

    raw_values = np.array([sample_data], dtype=float)
    if scaler is not None:
        scaled_values = scaler.transform(raw_values)
    else:
        scaled_values = raw_values

    predicted_prob = float(model.predict(scaled_values, verbose=0)[0][0])
    # Map probability to manufacturing efficiency range [74%, 96%]
    efficiency = round(74.0 + (predicted_prob * (96.0 - 74.0)), 2)
    waste = round(max(0.5, (100.0 - efficiency) * 0.20), 2)
    failure = round(max(0.2, (100.0 - efficiency) * 0.12), 2)

    return {
        "model": "Deep Learning (ANN)",
        "probability": round(predicted_prob, 4),
        "efficiency": efficiency,
        "waste": waste,
        "failure": failure,
        "status": "Optimal" if efficiency >= 85 else ("Warning" if efficiency >= 80 else "Critical"),
        "message": "Deep Learning ANN Prediction Completed Successfully",
    }


if __name__ == "__main__":
    sample = [75, 40, 55, 140, 0.40, 220, 380]
    result = predict_from_sample(sample)
    print(result)
