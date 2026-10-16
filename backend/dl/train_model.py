import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.datasets import make_classification
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Input

warnings.filterwarnings("ignore")


def colorize(text, color="cyan"):
    """Return ANSI-colored text when terminal output supports it."""
    colors = {
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "magenta": "\033[95m",
        "blue": "\033[94m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }
    if sys.stdout.isatty() and os.name != "nt":
        return f"{colors.get(color, '')}{text}{colors['reset']}"
    return text


def find_dataset_path():
    """Return the manufacturing dataset path for the deep learning model."""
    project_root = Path(__file__).resolve().parents[1]
    dataset_path = project_root / "ml" / "manufacturing.csv"
    if dataset_path.exists():
        return str(dataset_path)
    raise FileNotFoundError("Manufacturing dataset not found at backend/ml/manufacturing.csv")


def prepare_dl_data(df):
    """Clean the manufacturing dataset and convert the target to a binary classification problem."""
    df = df.drop_duplicates().reset_index(drop=True)

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown")
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].fillna(df[col].median())

    target_column = "efficiency"
    if target_column not in df.columns:
        raise ValueError("Target column 'efficiency' not found in manufacturing dataset.")

    y = df[target_column].copy()
    y = pd.to_numeric(y, errors="coerce")
    threshold = y.median()
    y_binary = (y >= threshold).astype(int)

    X = df.drop(columns=[target_column])
    X = pd.get_dummies(X, drop_first=False)
    X = X.astype(float)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, y_binary.to_numpy(), scaler, list(X.columns)


def format_metric(value):
    """Return a consistent percentage format for metrics."""
    return f"{value * 100:.2f}%"


def train_model():
    """Train a production-style ANN for manufacturing performance classification."""
    try:
        import json
        import joblib
        project_root = Path(__file__).resolve().parents[1]
        model_dir = project_root / "trained_models"
        model_dir.mkdir(parents=True, exist_ok=True)

        dataset_path = find_dataset_path()
        print(colorize("\nLoading manufacturing dataset for deep learning...", "cyan"))
        df = pd.read_csv(dataset_path)

        if df.empty:
            raise ValueError("Manufacturing dataset is empty.")

        X, y, scaler, feature_names = prepare_dl_data(df)
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        model = Sequential(
            [
                Input(shape=(X_train.shape[1],)),
                Dense(64, activation="relu", kernel_initializer="he_normal"),
                Dense(32, activation="relu", kernel_initializer="he_normal"),
                Dense(1, activation="sigmoid"),
            ]
        )

        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

        start = time.perf_counter()
        history = model.fit(
            X_train,
            y_train,
            validation_split=0.2,
            epochs=80,
            batch_size=8,
            verbose=0,
            shuffle=True,
        )
        train_time = time.perf_counter() - start

        start = time.perf_counter()
        y_prob = model.predict(X_test, verbose=0).ravel()
        predict_time = time.perf_counter() - start

        y_pred = (y_prob >= 0.5).astype(int)
        loss_value = history.history["loss"][-1]

        metrics = {
            "model": "Deep Learning (ANN)",
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1": f1_score(y_test, y_pred, zero_division=0),
            "roc_auc": roc_auc_score(y_test, y_prob),
            "loss": float(loss_value),
            "train_time": float(train_time),
            "predict_time": float(predict_time),
            "history": {
                "loss": [float(x) for x in history.history["loss"]],
                "accuracy": [float(x) for x in history.history.get("accuracy", [])],
                "val_loss": [float(x) for x in history.history.get("val_loss", [])],
                "val_accuracy": [float(x) for x in history.history.get("val_accuracy", [])],
            },
            "features": feature_names
        }

        print(colorize("\n----------------------------------------", "blue"))
        print(colorize("Deep Learning (ANN)", "bold"))
        print(colorize("----------------------------------------", "blue"))
        print(f"Accuracy: {format_metric(metrics['accuracy'])}")
        print(f"Precision: {format_metric(metrics['precision'])}")
        print(f"Recall: {format_metric(metrics['recall'])}")
        print(f"F1 Score: {format_metric(metrics['f1'])}")
        print(f"ROC-AUC: {format_metric(metrics['roc_auc'])}")
        print(f"Loss: {metrics['loss']:.4f}")
        print(f"Training Time: {metrics['train_time']:.2f} s")
        print(f"Prediction Time: {metrics['predict_time']:.2f} s")

        model_path = model_dir / "dl_model.keras"
        scaler_path = model_dir / "dl_scaler.pkl"
        metrics_path = model_dir / "dl_metrics.json"

        model.save(model_path)
        joblib.dump(scaler, scaler_path)
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)

        print(f"Deep learning model saved to: {model_path}")
        print(f"Deep learning scaler saved to: {scaler_path}")
        print(f"Deep learning metrics saved to: {metrics_path}")

    except Exception as exc:  # pragma: no cover
        print(colorize("\nDL pipeline failed:", "red"), exc)
        raise


if __name__ == "__main__":
    train_model()
    print(colorize("\n========================================", "green"))
    print(colorize("PIPELINE COMPLETED", "bold"))
    print(colorize("========================================", "green"))
    print("Machine Learning Pipeline Completed Successfully.")
    print("Deep Learning Pipeline Completed Successfully.")
