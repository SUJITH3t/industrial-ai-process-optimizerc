# 🏭 Smart Manufacturing Process Optimization

An end-to-end industrial AI platform designed to optimize manufacturing processes (assembly line speed, material usage, thermal dynamics, and pneumatic pressure) to maximize production efficiency and reduce waste. 

This platform implements a 7-stage evolution: from **Classical Machine Learning** baselines and **Deep Learning (ANN)** to **NLP Maintenance Triage**, **Edge Small Language Models (SLM)**, **Generative AI Scenario Stress-Testing**, and an **Autonomous Agentic AI Closed-Loop Control System**.

---

## 🌟 Key Features

* **Multi-Model ML Benchmark**: Evaluates 7 algorithms (Logistic Regression, Random Forest, Gradient Boosting, SVM, Decision Tree, KNN, XGBoost) with confusion matrices, ROC curves, and feature importance rankings.
* **Deep Learning (ANN)**: 3-layer neural network with standard input scaling for continuous efficiency calibration and failure risk estimation.
* **NLP Maintenance Triage & NER**: Ingests unstructured operator shift logs and extracts machine entities (`CNC-04`, `LINE-A`), components (`spindle`, `bearing`), sensor readings, error codes (`ERR-304`, `E-STOP`), and urgency classifications.
* **SLM Process Copilot**: Edge-quantized Small Language Model (`EdgeManufacturing-SLM-1.1B`) providing automated shift summaries (evaluated via ROUGE-1/2/L), prioritized parameter recommendations, and interactive Q&A.
* **Generative AI Scenario Simulator**: Synthesizes multivariate sensor runs across 5 stress conditions (*Thermal Runaway*, *Bearing Spalling*, *Pressure Loss*, *Surge Overclocking*) with distribution fidelity scoring and automated contingency plans.
* **Autonomous Agentic AI Control Room**: Closed-loop cognitive cycle (Perception $\to$ Working Memory $\to$ Reasoning $\to$ Planning $\to$ Action) with hard ISO safety guardrails, emergency kill switch, and human-in-the-loop manual overrides.
* **Executive Dark Glassmorphism Dashboard**: Real-time Chart.js telemetry waveforms, radar operating profiles, interactive OpenAPI 3.0 explorer, and full audit logs.

---

## 🏗️ Architecture & Tech Stack

* **Backend**: Python 3, Flask, SQLAlchemy ORM, SQLite / PostgreSQL
* **AI & Machine Learning**: Scikit-Learn, TensorFlow / Keras, XGBoost, NumPy, Pandas
* **NLP & SLM**: Domain NER Extraction Engine, ROUGE evaluation metrics
* **Frontend**: Vanilla JavaScript (ES6+), HTML5, Custom Industrial Dark Glassmorphism CSS, Chart.js, FontAwesome
* **Specifications**: OpenAPI 3.0, C4 Architecture Models (Context, Container, Component)

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-manufacturing-process-optimization.git
cd smart-manufacturing-process-optimization
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Run the Platform
Launch both the Flask AI backend (:5001) and web dashboard (:8000) with a single command:
```bash
python3 run.py
```

* **Dashboard**: [http://127.0.0.1:8000/dashboard.html](http://127.0.0.1:8000/dashboard.html)
* **Login Portal**: [http://127.0.0.1:8000/index.html](http://127.0.0.1:8000/index.html) *(Default: `admin` / `admin123`)*
* **Backend API**: [http://127.0.0.1:5001](http://127.0.0.1:5001)
* **OpenAPI 3.0 Docs**: [http://127.0.0.1:5001/lld/spec](http://127.0.0.1:5001/lld/spec)

---

## 📊 Model Training

* To train the 7 ML models and save benchmark metrics:
  ```bash
  python3 backend/ml/train_model.py
  ```
* To train the Deep Learning ANN:
  ```bash
  python3 backend/dl/train_model.py
  ```

---

## 📜 License
MIT License. Open source for academic, industrial research, and educational use.
