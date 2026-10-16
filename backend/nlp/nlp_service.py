import re
from typing import Dict, Any, List

# Manufacturing domain dictionaries
DEFECT_KEYWORDS = {
    "Thermal": ["overheat", "temperature", "heat", "hot", "cooling", "coolant", "radiator", "thermal", "burner", "furnace"],
    "Mechanical": ["vibration", "bearing", "gear", "shaft", "belt", "jam", "friction", "rattling", "loose", "wear", "spindle"],
    "Pneumatic / Pressure": ["pressure", "leak", "valve", "compressor", "pneumatic", "cylinder", "psi", "bar", "burst", "pipe"],
    "Electrical": ["voltage", "power", "short", "breaker", "trip", "circuit", "fuse", "spike", "inverter", "current"],
    "Calibration & Speed": ["speed", "rpm", "feed rate", "tolerance", "drift", "offset", "misalignment", "dimension", "inaccurate"]
}

MACHINE_PATTERNS = [
    r"\b(CNC[-_ ]?\d+)\b",
    r"\b(LINE[-_ ]?[A-Z0-9]+)\b",
    r"\b(PRESS[-_ ]?\d+)\b",
    r"\b(ROBOT[-_ ]?ARM[-_ ]?\d+)\b",
    r"\b(FURNACE[-_ ]?\d+)\b",
    r"\b(LATHE[-_ ]?\d+)\b",
    r"\b(CONVEYOR[-_ ]?[A-Z0-9]+)\b",
    r"\b(STATION[-_ ]?\d+)\b"
]

COMPONENT_PATTERNS = [
    r"\b(spindle|bearing|gearbox|belt|cooling valve|coolant pump|hydraulic cylinder|motor|nozzle|filter|sensor|actuator|gasket)\b"
]

METRIC_PATTERNS = [
    r"\b(\d+(?:\.\d+)?\s*(?:°C|C|°F|F))\b",
    r"\b(\d+(?:\.\d+)?\s*(?:bar|psi|kPa))\b",
    r"\b(\d+(?:\.\d+)?\s*(?:mm/s|g|m/s2))\b",
    r"\b(\d+(?:\.\d+)?\s*(?:rpm|RPM))\b",
    r"\b(\d+(?:\.\d+)?\s*(?:kW|V|A|amps))\b"
]

ERROR_CODE_PATTERNS = [
    r"\b([A-Z]{2,4}[-_]?\d{2,4})\b",
    r"\b(E[-_]?STOP)\b",
    r"\b(ERR[-_]?\d+)\b",
    r"\b(WARN[-_]?\d+)\b",
    r"\b(FAULT[-_]?\d+)\b"
]

ACTION_WORDS = ["inspect", "lubricate", "replace", "recalibrate", "tighten", "shutdown", "throttle", "flush", "realign", "overhaul"]

NEGATIVE_SENTIMENT_WORDS = {
    "critical": -0.9, "danger": -0.9, "failure": -0.85, "broken": -0.8, "damage": -0.8,
    "smoke": -0.9, "leak": -0.7, "abnormal": -0.6, "severe": -0.8, "warning": -0.5,
    "delay": -0.4, "slow": -0.3, "high": -0.3, "spike": -0.5, "jam": -0.7, "wear": -0.5
}
POSITIVE_SENTIMENT_WORDS = {
    "optimal": 0.8, "smooth": 0.7, "stable": 0.75, "nominal": 0.7, "resolved": 0.8,
    "inspected": 0.5, "passed": 0.85, "efficient": 0.75, "calibrated": 0.7, "normal": 0.6
}


def preprocess_text(text: str) -> str:
    """Normalize text while retaining critical manufacturing tokens."""
    if not text:
        return ""
    cleaned = re.sub(r"[\r\n\t]+", " ", text.strip())
    return cleaned


def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """Extract domain-specific manufacturing entities."""
    entities = {
        "machines": [],
        "components": [],
        "metrics": [],
        "error_codes": [],
        "actions": []
    }

    # Extract Machines
    for pat in MACHINE_PATTERNS:
        matches = re.findall(pat, text, re.IGNORECASE)
        for m in matches:
            if m.upper() not in entities["machines"]:
                entities["machines"].append(m.upper())

    # Extract Components
    for pat in COMPONENT_PATTERNS:
        matches = re.findall(pat, text, re.IGNORECASE)
        for m in matches:
            m_clean = m.lower()
            if m_clean not in entities["components"]:
                entities["components"].append(m_clean)

    # Extract Metrics
    for pat in METRIC_PATTERNS:
        matches = re.findall(pat, text, re.IGNORECASE)
        for m in matches:
            if m not in entities["metrics"]:
                entities["metrics"].append(m)

    # Extract Error Codes
    for pat in ERROR_CODE_PATTERNS:
        matches = re.findall(pat, text, re.IGNORECASE)
        for m in matches:
            m_upper = m.upper()
            if m_upper not in entities["error_codes"] and not re.match(r"^(RPM|PSI|BAR)$", m_upper):
                entities["error_codes"].append(m_upper)

    # Extract Recommended Actions
    for word in ACTION_WORDS:
        if re.search(r"\b" + word + r"\b", text, re.IGNORECASE):
            if word not in entities["actions"]:
                entities["actions"].append(word)

    return entities


def classify_log(text: str) -> Dict[str, Any]:
    """Classify failure category, urgency, and operational risk."""
    text_lower = text.lower()

    # Category scoring
    scores = {}
    for cat, kws in DEFECT_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in text_lower)
        scores[cat] = score

    top_cat = max(scores, key=scores.get)
    if scores[top_cat] == 0:
        top_cat = "General Operational"

    # Urgency determination
    critical_terms = ["e-stop", "smoke", "fire", "burst", "emergency", "fatal", "blown", "err-99", "danger"]
    high_terms = ["overheat", "spike", "severe", "leak", "crack", "critical", "heavy vibration", "stop line"]
    medium_terms = ["warning", "noise", "drift", "friction", "elevated", "inspect", "intermittent"]

    if any(term in text_lower for term in critical_terms):
        urgency = "Critical"
        urgency_score = 95
    elif any(term in text_lower for term in high_terms):
        urgency = "High"
        urgency_score = 75
    elif any(term in text_lower for term in medium_terms):
        urgency = "Medium"
        urgency_score = 50
    else:
        urgency = "Low"
        urgency_score = 25

    # Sentiment calculation
    sentiment_val = 0.0
    words = re.findall(r"\w+", text_lower)
    match_count = 0
    for w in words:
        if w in NEGATIVE_SENTIMENT_WORDS:
            sentiment_val += NEGATIVE_SENTIMENT_WORDS[w]
            match_count += 1
        elif w in POSITIVE_SENTIMENT_WORDS:
            sentiment_val += POSITIVE_SENTIMENT_WORDS[w]
            match_count += 1

    final_sentiment = round(sentiment_val / max(1, match_count), 2) if match_count else 0.0

    return {
        "category": top_cat,
        "category_scores": scores,
        "urgency": urgency,
        "urgency_score": urgency_score,
        "sentiment_score": final_sentiment,
        "sentiment_label": "Negative / Alarm" if final_sentiment < -0.2 else ("Positive / Stable" if final_sentiment > 0.2 else "Neutral")
    }


def extract_keywords(text: str, top_k: int = 5) -> List[str]:
    """Extract significant keywords representing bottlenecks or components."""
    stopwords = {"the", "is", "at", "which", "on", "and", "a", "an", "in", "to", "for", "with", "by", "from", "of", "was", "were", "has", "have", "been"}
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9_-]{3,}", text) if w.lower() not in stopwords]
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w[0] for w in sorted_words[:top_k]]


def analyze_log(text: str) -> Dict[str, Any]:
    """Full NLP pipeline analyzing an operator log or maintenance report."""
    cleaned = preprocess_text(text)
    classification = classify_log(cleaned)
    entities = extract_named_entities(cleaned)
    keywords = extract_keywords(cleaned)

    # Concise one-sentence summary
    machine_str = ", ".join(entities["machines"]) if entities["machines"] else "Equipment"
    component_str = ", ".join(entities["components"]) if entities["components"] else "subsystems"
    summary = f"[{classification['urgency']}] {machine_str} report regarding {classification['category'].lower()} on {component_str}."

    return {
        "original_text": text,
        "cleaned_text": cleaned,
        "urgency": classification["urgency"],
        "urgency_score": classification["urgency_score"],
        "category": classification["category"],
        "category_scores": classification["category_scores"],
        "sentiment_score": classification["sentiment_score"],
        "sentiment_label": classification["sentiment_label"],
        "entities": entities,
        "keywords": keywords,
        "summary": summary
    }


# Preset realistic samples for UI demonstration
SAMPLE_LOGS = [
    {
        "id": "sample-1",
        "title": "CNC Spindle Overheating Incident",
        "text": "CNC-04 spindle temperature spiked to 92°C during high speed milling. Heavy vibration (0.85 mm/s) recorded. Operator initiated warning protocol. ERR-304 detected. Immediate lubrication and speed reduction recommended."
    },
    {
        "id": "sample-2",
        "title": "Pneumatic Pressure Drop on Assembly Line",
        "text": "LINE-A conveyor pneumatic regulator pressure dropped to 32 psi due to air line micro-leak at cooling valve. Speed throttled to 110 RPM to prevent defective stamping. Gasket replacement required."
    },
    {
        "id": "sample-3",
        "title": "Routine Bearing Inspection",
        "text": "PRESS-2 main drive bearing inspected during planned shift handover. Operating temperature stable at 68°C, vibration nominal at 0.22 mm/s. All tolerance checks passed smoothly."
    },
    {
        "id": "sample-4",
        "title": "Emergency Stop Triggered on Robot Arm",
        "text": "E-STOP triggered on ROBOT-ARM-7 after gearbox current overload (480 kW spike). FLT-09 tripped main circuit breaker. Operator smells burning insulation. Maintenance overhaul urgently dispatched."
    }
]
