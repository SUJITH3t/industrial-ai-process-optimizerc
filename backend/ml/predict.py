import os

import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
MODEL_PATH = os.path.join(PROJECT_ROOT, "trained_models", "model.pkl")

# Load Model
model = joblib.load(MODEL_PATH)

# Sample Input
sample = pd.DataFrame([{
    "temperature": 75,
    "pressure": 40,
    "humidity": 55,
    "speed": 140,
    "vibration": 0.40,
    "material": 220,
    "power": 380
}])

prediction = model.predict(sample)

print("--------------------------------")
print("Predicted Efficiency:")
print(round(prediction[0], 2), "%")
print("--------------------------------")