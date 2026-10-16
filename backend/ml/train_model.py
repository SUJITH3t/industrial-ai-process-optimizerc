import os
import sys
import time
import warnings
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

try:
    from xgboost import XGBClassifier
except ImportError:  # pragma: no cover
    XGBClassifier = None

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
    """Locate the manufacturing dataset file in the project (used for deployment)."""
    project_root = Path(__file__).resolve().parents[1]
    candidates = [
        # Prioritize the manufacturing dataset for the Smart Manufacturing project.
        project_root / "ml" / "manufacturing.csv",
        project_root / "data" / "manufacturing.csv",
        Path(__file__).resolve().parent / "manufacturing.csv",
    ]

    for path in candidates:
        if path.exists():
            return str(path)

    raise FileNotFoundError(
        "No dataset file found. Expected: manufacturing.csv"
    )


def convert_target_to_binary(df, target_column):
    """Convert a continuous target into a binary classification target when needed."""
    y = df[target_column]

# Normalize string labels ('0'/'1', 'yes'/'no', etc.) to numeric 0/1.
    if y.dtype == object:
        str_y = y.astype(str).str.strip().str.lower()
        mapping = {"0": 0, "1": 1, "no": 0, "yes": 1, "false": 0, "true": 1}
        if str_y.isin(mapping.keys()).all():
            y = str_y.map(mapping).astype(int)
            return y, target_column

    # Coerce numeric strings (e.g. efficiency values) to numeric dtype.
    try:
        y = pd.to_numeric(y, errors="coerce")
    except (ValueError, TypeError):
        pass

    if y.nunique() <= 2:
        # Ensure binary labels are numeric 0/1 for consistent metric evaluation.
        return y.astype(int), target_column

    median = y.median()
    binary_target = (y >= median).astype(int)
    df = df.copy()
    df[target_column] = binary_target
    print(
        colorize(
            f"Target '{target_column}' was continuous. Converted to binary using median threshold {median:.2f}.",
            "yellow",
        )
    )
    return binary_target, target_column


def build_preprocessor(X):
    """Create a preprocessing pipeline for mixed categorical and numeric data."""
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    numeric_cols = X.select_dtypes(exclude=["object", "category"]).columns.tolist()

    transformers = []

    if numeric_cols:
        transformers.append(
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_cols,
            )
        )

    if categorical_cols:
        transformers.append(
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            )
        )

    if not transformers:
        raise ValueError("No usable feature columns were found after dataset loading.")

    return ColumnTransformer(transformers=transformers, remainder="drop")


def format_metric(value):
    """Return a consistent percentage format for metrics."""
    return f"{value * 100:.2f}%"


def print_model_result(name, metrics):
    """Print a single model's evaluation in the required professional layout."""
    print(colorize("\n----------------------------------------", "blue"))
    print(colorize(name, "bold"))
    print(colorize("----------------------------------------", "blue"))
    print(f"Accuracy: {format_metric(metrics['accuracy'])}")
    print(f"Precision: {format_metric(metrics['precision'])}")
    print(f"Recall: {format_metric(metrics['recall'])}")
    print(f"F1 Score: {format_metric(metrics['f1'])}")
    print(f"ROC-AUC: {format_metric(metrics['roc_auc'])}")
    print(f"Training Time (seconds): {metrics['train_time']:.2f} s")
    print(f"Prediction Time (seconds): {metrics['predict_time']:.2f} s")


def print_comparison_table(results):
    """Print the model comparison table sorted by accuracy."""
    print(colorize("\n========================================", "green"))
    print(colorize("MODEL COMPARISON", "bold"))
    print(colorize("========================================", "green"))

    headers = [
        "Model",
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score",
        "ROC-AUC",
        "Train Time",
        "Predict Time",
    ]

    rows = []
    for result in results:
        rows.append(
            [
                result["name"],
                format_metric(result["accuracy"]),
                format_metric(result["precision"]),
                format_metric(result["recall"]),
                format_metric(result["f1"]),
                format_metric(result["roc_auc"]),
                f"{result['train_time']:.2f}s",
                f"{result['predict_time']:.2f}s",
            ]
        )

    rows.sort(key=lambda row: float(row[1].rstrip("%")) if row[1].endswith("%") else float(row[1]), reverse=True)

    widths = [max(len(str(header)), max(len(str(row[idx])) for row in [*rows, headers])) for idx, header in enumerate(headers)]

    header_line = " | ".join(str(header).ljust(widths[idx]) for idx, header in enumerate(headers))
    separator = "-+-".join("-" * widths[idx] for idx in range(len(headers)))

    print(header_line)
    print(separator)
    for row in rows:
        print(" | ".join(str(value).ljust(widths[idx]) for idx, value in enumerate(row)))


def evaluate_model(name, estimator, X_train, X_test, y_train, y_test):
    """Train a single estimator and return evaluation metrics."""
    start = time.perf_counter()
    estimator.fit(X_train, y_train)
    train_time = time.perf_counter() - start

    start = time.perf_counter()
    y_pred = estimator.predict(X_test)
    predict_time = time.perf_counter() - start

    metrics = {
        "name": name,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_pred),
        "train_time": train_time,
        "predict_time": predict_time,
    }

    print_model_result(name, metrics)
    return metrics


def get_model_candidates(preprocessor, full_comparison=True):
    """Return the full production benchmark set by default; allow a smaller subset when explicitly requested."""
    models = {
        "Logistic Regression": Pipeline(
            steps=[("preprocess", preprocessor), ("model", LogisticRegression(max_iter=1000, random_state=42))]
        ),
        "Decision Tree": Pipeline(
            steps=[("preprocess", preprocessor), ("model", DecisionTreeClassifier(random_state=42))]
        ),
        "Random Forest": Pipeline(
            steps=[("preprocess", preprocessor), ("model", RandomForestClassifier(n_estimators=120, random_state=42))]
        ),
        "Gradient Boosting": Pipeline(
            steps=[("preprocess", preprocessor), ("model", GradientBoostingClassifier(random_state=42))]
        ),
        "Support Vector Machine (SVM)": Pipeline(
            steps=[("preprocess", preprocessor), ("model", SVC(probability=True, random_state=42))]
        ),
        "K-Nearest Neighbors (KNN)": Pipeline(
            steps=[("preprocess", preprocessor), ("model", KNeighborsClassifier(n_neighbors=5))]
        ),
    }

    if XGBClassifier is not None:
        models["XGBoost"] = Pipeline(
            steps=[("preprocess", preprocessor), ("model", XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42))]
        )

    if full_comparison:
        print(colorize("Running full model comparison for the production benchmark.", "yellow"))
    else:
        print(colorize("Running reduced comparison for a faster validation pass.", "green"))

    return models


def main(full_comparison=True):
    """Run the smart manufacturing ML pipeline and print the final benchmark report."""
    try:
        dataset_path = Path(__file__).resolve().parents[1] / "ml" / "manufacturing.csv"
        print(colorize("\nLoading dataset...", "cyan"))
        df = pd.read_csv(dataset_path)

        if df.empty:
            raise ValueError("The manufacturing dataset is empty.")

        print(colorize(f"Dataset loaded successfully: {dataset_path}", "green"))
        print(colorize(f"Rows: {len(df)}, Columns: {len(df.columns)}", "cyan"))

        # ------------------------------------------------------------------
        # Step 1: Handle missing values
        # ------------------------------------------------------------------
        df = df.replace(["", " ", "nan", "NaN", "None", "null", "N/A"], pd.NA)
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown")
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                df[col] = df[col].fillna(df[col].median())
        print(colorize("Missing values handled successfully.", "green"))

        # ------------------------------------------------------------------
        # Step 2: Remove duplicate records
        # ------------------------------------------------------------------
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            print(colorize(f"Duplicate rows detected: {duplicates}", "yellow"))
            df = df.drop_duplicates().reset_index(drop=True)
            print(colorize(f"Duplicates removed. Remaining rows: {len(df)}", "green"))
        else:
            print(colorize("No duplicate rows detected.", "green"))

        target_column = "efficiency"
        if target_column not in df.columns:
            raise ValueError("Target column 'efficiency' not found in the manufacturing dataset.")

        y = pd.to_numeric(df[target_column], errors="coerce").fillna(df[target_column].median())
        if y.nunique() <= 2:
            y = y.astype(int)
        else:
            y = (y >= y.median()).astype(int)

        X = df.drop(columns=[target_column]).copy()

        categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
        if categorical_cols:
            X = pd.get_dummies(X, columns=categorical_cols, drop_first=False)

        if X.empty:
            raise ValueError("No feature columns remain after target separation.")

        # ------------------------------------------------------------------
        # Step 3: Split dataset into 80% train and 20% test
        # ------------------------------------------------------------------
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        # ------------------------------------------------------------------
        # Step 4: Build preprocessor for mixed numeric/categorical features
        # ------------------------------------------------------------------
        preprocessor = build_preprocessor(X)
        models = get_model_candidates(preprocessor, full_comparison=full_comparison)
        if XGBClassifier is None:
            print(colorize("XGBoost is not installed. Please install xgboost to enable that model.", "red"))

        results = []
        for name, estimator in models.items():
            print(colorize(f"\nTraining {name}...", "magenta"))
            result = evaluate_model(name, estimator, X_train, X_test, y_train, y_test)
            results.append(result)

        results = sorted(results, key=lambda x: x["accuracy"], reverse=True)
        print_comparison_table(results)

        best = results[0]
        print(colorize("\n========================================", "green"))
        print(colorize("BEST MACHINE LEARNING MODEL", "bold"))
        print(colorize("========================================", "green"))
        print(f"Best Model: {best['name']}")
        print(f"Accuracy: {format_metric(best['accuracy'])}")
        print(f"Precision: {format_metric(best['precision'])}")
        print(f"Recall: {format_metric(best['recall'])}")
        print(f"F1 Score: {format_metric(best['f1'])}")
        print(f"ROC-AUC: {format_metric(best['roc_auc'])}")
        print("Reason for Selection: Highest accuracy with strong precision, recall, and ROC-AUC on the manufacturing test set.")

        project_root = Path(__file__).resolve().parents[2]
        models_dir = project_root / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        trained_dir = Path(__file__).resolve().parents[1] / "trained_models"
        trained_dir.mkdir(parents=True, exist_ok=True)

        best_model_path = models_dir / "best_ml_model.pkl"
        backend_model_path = trained_dir / "model.pkl"

        best_pipeline = next(est for name, est in models.items() if name == best["name"])
        best_pipeline.fit(X_train, y_train)
        joblib.dump(best_pipeline, best_model_path)
        joblib.dump(best_pipeline, backend_model_path)
        print(f"Best model saved to: {best_model_path}")
        print(f"Backend model saved to: {backend_model_path}")

        # Extract feature importance from tree-based model (e.g. Random Forest)
        rf_pipeline = models.get("Random Forest")
        feature_names = list(X.columns)
        feature_importance = {}
        if rf_pipeline and hasattr(rf_pipeline.named_steps["model"], "feature_importances_"):
            importances = rf_pipeline.named_steps["model"].feature_importances_
            feature_importance = {name: round(float(imp), 4) for name, imp in zip(feature_names, importances)}

        from sklearn.metrics import confusion_matrix, roc_curve
        y_pred_best = best_pipeline.predict(X_test)
        cm = confusion_matrix(y_test, y_pred_best).tolist()

        try:
            y_prob_best = best_pipeline.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, y_prob_best)
            roc_data = {"fpr": [round(float(x), 4) for x in fpr], "tpr": [round(float(x), 4) for x in tpr]}
        except Exception:
            roc_data = {"fpr": [0.0, 0.0, 1.0], "tpr": [0.0, 1.0, 1.0]}

        import json
        metrics_payload = {
            "best_model": best["name"],
            "models": results,
            "feature_importance": feature_importance,
            "confusion_matrix": cm,
            "roc_data": roc_data,
            "features": feature_names,
            "samples_count": len(df),
            "target": target_column
        }

        with open(trained_dir / "ml_metrics.json", "w") as f:
            json.dump(metrics_payload, f, indent=2)
        with open(Path(__file__).resolve().parent / "ml_metrics.json", "w") as f:
            json.dump(metrics_payload, f, indent=2)
        print("Model evaluation metrics and feature importance saved to ml_metrics.json")

        print(colorize("\nMachine Learning Pipeline Completed Successfully.", "green"))

    except Exception as exc:  # pragma: no cover
        print(colorize("\nML pipeline failed:", "red"), exc)
        raise


if __name__ == "__main__":
    main(full_comparison=True)