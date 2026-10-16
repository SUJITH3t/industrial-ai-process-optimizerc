// =============================================================================
// Smart Manufacturing Process Optimization - Frontend Controller
// =============================================================================

const API_BASE = "http://127.0.0.1:5001";

// Global Chart References
let efficiencyChart = null;
let sensorRadarChart = null;
let rocCurveChart = null;
let featureImportanceChart = null;
let dlHistoryChart = null;
let simulationChart = null;

// Preset sample logs cache
let cachedNlpSamples = [];

// =============================================================================
// Initialization & Tab Routing
// =============================================================================
document.addEventListener("DOMContentLoaded", () => {
    setupTabNavigation();
    setupEventListeners();
    initCharts();
    
    // Initial data fetch
    fetchMlDlMetrics();
    fetchNlpSamples();
    fetchAgentStatus();
    fetchRecommendations();
    loadOpenApiSpec();
    fetchFullHistory();
});

function setupTabNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");
    const topbarTitle = document.getElementById("topbarTitle");

    const titles = {
        "tab-telemetry": "Live Process Telemetry & Dual Inference",
        "tab-benchmarks": "ML (7 Algorithms) & DL ANN Model Benchmarks",
        "tab-nlp": "Natural Language Processing (NER & Maintenance Triage)",
        "tab-slm": "Small Language Model (SLM) Engineer Copilot",
        "tab-genai": "Generative AI Scenario Stress-Testing Simulator",
        "tab-agentic": "Autonomous Agentic AI Closed-Loop Control Room",
        "tab-lld": "Low-Level Design (LLD), C4 Diagrams & OpenAPI Docs",
        "tab-history": "Immutable Telemetry & Prediction Audit Database"
    };

    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const targetTab = item.getAttribute("data-tab");

            navItems.forEach(n => n.classList.remove("active"));
            tabContents.forEach(t => t.classList.remove("active"));

            item.classList.add("active");
            const activeTabEl = document.getElementById(targetTab);
            if (activeTabEl) activeTabEl.classList.add("active");

            if (topbarTitle && titles[targetTab]) {
                topbarTitle.innerText = titles[targetTab];
            }

            // Lazy trigger specific charts on tab activation
            if (targetTab === "tab-benchmarks") fetchMlDlMetrics();
            if (targetTab === "tab-agentic") fetchAgentStatus();
            if (targetTab === "tab-history") fetchFullHistory();
        });
    });
}

function setupEventListeners() {
    // Tab 1: Telemetry
    document.getElementById("mlBtn").addEventListener("click", () => runPrediction("ml"));
    document.getElementById("dlBtn").addEventListener("click", () => runPrediction("dl"));
    document.getElementById("saveReadingBtn").addEventListener("click", saveCurrentSensorData);

    // Tab 2: Benchmarks
    document.getElementById("refreshBenchmarksBtn").addEventListener("click", fetchMlDlMetrics);

    // Tab 3: NLP
    document.getElementById("analyzeNlpBtn").addEventListener("click", analyzeOperatorLog);
    document.getElementById("refreshNlpLogsBtn").addEventListener("click", fetchOperatorLogs);

    // Tab 4: SLM
    document.getElementById("generateSlmSummaryBtn").addEventListener("click", generateSlmSummary);
    document.getElementById("refreshRecommendationsBtn").addEventListener("click", fetchRecommendations);
    document.getElementById("chatSendBtn").addEventListener("click", sendChatMessage);
    document.getElementById("chatInput").addEventListener("keydown", (e) => {
        if (e.key === "Enter") sendChatMessage();
    });

    // Tab 5: Gen AI
    document.getElementById("runSimulationBtn").addEventListener("click", runGenerativeSimulation);

    // Tab 6: Agentic
    document.getElementById("triggerAgentStepBtn").addEventListener("click", stepAgenticLoop);
    document.getElementById("toggleAutoBtn").addEventListener("click", toggleAgentAuto);
    document.getElementById("killSwitchBtn").addEventListener("click", triggerKillSwitch);
    document.getElementById("refreshAgentLogsBtn").addEventListener("click", fetchAgentActionLogs);

    // Tab 7: LLD
    document.getElementById("fetchOpenApiBtn").addEventListener("click", loadOpenApiSpec);

    // Tab 8: History
    document.getElementById("refreshFullHistoryBtn").addEventListener("click", fetchFullHistory);
}

// =============================================================================
// Preset Configurations
// =============================================================================
const PRESETS = {
    nominal: { temperature: 70, pressure: 40, humidity: 50, speed: 140, vibration: 0.28, material: 215, power: 365 },
    overheating: { temperature: 89, pressure: 33, humidity: 45, speed: 165, vibration: 0.65, material: 240, power: 450 },
    vibration: { temperature: 82, pressure: 39, humidity: 52, speed: 130, vibration: 0.82, material: 225, power: 420 },
    surge: { temperature: 84, pressure: 45, humidity: 48, speed: 185, vibration: 0.58, material: 260, power: 490 }
};

window.applyPreset = function(presetKey) {
    const data = PRESETS[presetKey];
    if (!data) return;

    for (let key in data) {
        const el = document.getElementById(key);
        if (el) el.value = data[key];
    }
    updateRadarChart(data);
};

function getSensorInputs() {
    return {
        temperature: parseFloat(document.getElementById("temperature").value) || 75.0,
        pressure: parseFloat(document.getElementById("pressure").value) || 40.0,
        humidity: parseFloat(document.getElementById("humidity").value) || 55.0,
        speed: parseFloat(document.getElementById("speed").value) || 140.0,
        vibration: parseFloat(document.getElementById("vibration").value) || 0.40,
        material: parseFloat(document.getElementById("material").value) || 220.0,
        power: parseFloat(document.getElementById("power").value) || 380.0
    };
}

// =============================================================================
// TAB 1: Live Inference & Telemetry
// =============================================================================
async function runPrediction(type) {
    const data = getSensorInputs();
    const endpoint = type === "ml" ? `${API_BASE}/predict/ml` : `${API_BASE}/predict/dl`;
    const banner = document.getElementById("predictionBanner");
    const titleEl = document.getElementById("predModelTitle");
    const textEl = document.getElementById("predDetailsText");
    const tagEl = document.getElementById("predStatusTag");

    titleEl.innerText = type === "ml" ? "Machine Learning Inference:" : "Deep Learning ANN Inference:";
    textEl.innerText = "Executing forward pass on factory telemetry...";

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
        const result = await response.json();

        // Update KPIs
        document.getElementById("efficiencyVal").innerText = `${result.efficiency}%`;
        document.getElementById("wasteVal").innerText = `${result.waste}%`;
        document.getElementById("failureVal").innerText = `${result.failure}%`;

        // Update Status Pill
        const statusPill = document.getElementById("globalStatusPill");
        const status = result.status || (result.efficiency >= 85 ? "Optimal" : (result.efficiency >= 80 ? "Warning" : "Critical"));
        
        statusPill.className = `status-pill status-${status.toLowerCase()}`;
        statusPill.innerHTML = `<i class="fa-solid fa-circle-check"></i> System ${status}`;

        document.getElementById("machineStatusVal").innerText = status.toUpperCase();
        document.getElementById("machineStatusVal").style.color = status === "Optimal" ? "var(--accent-emerald)" : (status === "Warning" ? "var(--accent-amber)" : "var(--accent-rose)");

        // Update Banner
        textEl.innerText = `${result.message} • Model Output Efficiency: ${result.efficiency}% | Waste: ${result.waste}% | Risk: ${result.failure}%`;
        tagEl.innerText = status;
        tagEl.className = `badge status-${status.toLowerCase()}`;

        // Update Charts
        updateEfficiencyChart(result.efficiency, result.waste, result.failure);
        updateRadarChart(data);

    } catch (err) {
        console.error("Prediction error:", err);
        textEl.innerText = `Inference failed: Ensure backend is running on :5001. (${err.message})`;
    }
}

async function saveCurrentSensorData() {
    const data = getSensorInputs();
    try {
        const res = await fetch(`${API_BASE}/sensor-data`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            alert("Current sensor reading successfully logged into smart_manufacturing.db!");
            fetchFullHistory();
        }
    } catch (e) {
        alert("Failed to save sensor reading: " + e.message);
    }
}

// =============================================================================
// Charts Initialization
// =============================================================================
function initCharts() {
    // 1. Efficiency Bar Chart
    const effCtx = document.getElementById("efficiencyChart").getContext("2d");
    efficiencyChart = new Chart(effCtx, {
        type: "bar",
        data: {
            labels: ["Production Efficiency", "Material Waste", "Failure Risk"],
            datasets: [{
                label: "Percentage Metric (%)",
                data: [92.4, 1.52, 0.91],
                backgroundColor: [
                    "rgba(6, 182, 212, 0.7)",
                    "rgba(245, 158, 11, 0.7)",
                    "rgba(244, 63, 94, 0.7)"
                ],
                borderColor: ["#06b6d4", "#f59e0b", "#f43f5e"],
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 100, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
                x: { grid: { display: false }, ticks: { color: "#94a3b8" } }
            },
            plugins: { legend: { display: false } }
        }
    });

    // 2. Sensor Radar Chart
    const radarCtx = document.getElementById("sensorRadarChart").getContext("2d");
    sensorRadarChart = new Chart(radarCtx, {
        type: "radar",
        data: {
            labels: ["Temp (°C)", "Pressure (bar)", "Humidity (%)", "Speed (RPM/2)", "Vibration (x100)", "Power (kW/5)"],
            datasets: [
                {
                    label: "Current Telemetry",
                    data: [75, 40, 55, 70, 40, 76],
                    borderColor: "#06b6d4",
                    backgroundColor: "rgba(6, 182, 212, 0.2)",
                    borderWidth: 2
                },
                {
                    label: "Nominal Envelope",
                    data: [70, 40, 50, 70, 28, 73],
                    borderColor: "#10b981",
                    backgroundColor: "rgba(16, 185, 129, 0.1)",
                    borderWidth: 1.5,
                    borderDash: [4, 4]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: "rgba(255,255,255,0.08)" },
                    grid: { color: "rgba(255,255,255,0.08)" },
                    pointLabels: { color: "#94a3b8", font: { size: 10 } },
                    ticks: { display: false }
                }
            },
            plugins: { legend: { labels: { color: "#94a3b8", boxWidth: 12 } } }
        }
    });
}

function updateEfficiencyChart(eff, waste, failure) {
    if (!efficiencyChart) return;
    efficiencyChart.data.datasets[0].data = [eff, waste, failure];
    efficiencyChart.update();
}

function updateRadarChart(data) {
    if (!sensorRadarChart) return;
    sensorRadarChart.data.datasets[0].data = [
        data.temperature || 75,
        data.pressure || 40,
        data.humidity || 55,
        (data.speed || 140) / 2.0,
        (data.vibration || 0.40) * 100,
        (data.power || 380) / 5.0
    ];
    sensorRadarChart.update();
}

// =============================================================================
// TAB 2: ML & DL Model Benchmarking
// =============================================================================
async function fetchMlDlMetrics() {
    try {
        const [mlRes, dlRes] = await Promise.all([
            fetch(`${API_BASE}/ml/metrics`),
            fetch(`${API_BASE}/dl/metrics`)
        ]);

        if (mlRes.ok) {
            const mlData = await mlRes.json();
            renderBenchmarkTable(mlData.models, mlData.best_model);
            renderFeatureImportance(mlData.feature_importance);
            renderRocCurve(mlData.roc_data);
        }

        if (dlRes.ok) {
            const dlData = await dlRes.json();
            renderDlCurves(dlData.history);
        }
    } catch (err) {
        console.warn("Could not fetch metrics:", err);
    }
}

function renderBenchmarkTable(models, bestModelName) {
    const tbody = document.getElementById("benchmarkTableBody");
    if (!tbody || !models) return;

    tbody.innerHTML = models.map(m => {
        const isBest = m.name === bestModelName;
        return `
            <tr style="${isBest ? 'background: rgba(6, 182, 212, 0.08); font-weight:600;' : ''}">
                <td>${isBest ? '⭐ ' : ''}${m.name}</td>
                <td>${(m.accuracy * 100).toFixed(2)}%</td>
                <td>${(m.precision * 100).toFixed(2)}%</td>
                <td>${(m.recall * 100).toFixed(2)}%</td>
                <td>${(m.f1 * 100).toFixed(2)}%</td>
                <td>${(m.roc_auc * 100).toFixed(2)}%</td>
                <td>${m.train_time.toFixed(3)}s</td>
                <td>${m.predict_time.toFixed(4)}s</td>
                <td><span class="badge ${isBest ? 'status-optimal' : 'badge-machine'}">${isBest ? 'BEST MODEL' : 'Trained'}</span></td>
            </tr>
        `;
    }).join("");
}

function renderFeatureImportance(featImp) {
    const ctx = document.getElementById("featureImportanceChart");
    if (!ctx || !featImp) return;

    const labels = Object.keys(featImp);
    const values = Object.values(featImp).map(v => v * 100);

    if (featureImportanceChart) featureImportanceChart.destroy();

    featureImportanceChart = new Chart(ctx.getContext("2d"), {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Relative Importance (%)",
                data: values,
                backgroundColor: "rgba(59, 130, 246, 0.7)",
                borderColor: "#3b82f6",
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { beginAtZero: true, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
                y: { ticks: { color: "#94a3b8" }, grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function renderRocCurve(rocData) {
    const ctx = document.getElementById("rocCurveChart");
    if (!ctx || !rocData) return;

    const points = rocData.fpr.map((fpr, i) => ({ x: fpr, y: rocData.tpr[i] }));

    if (rocCurveChart) rocCurveChart.destroy();

    rocCurveChart = new Chart(ctx.getContext("2d"), {
        type: "line",
        data: {
            datasets: [
                {
                    label: "Best Model (ROC AUC = 1.00)",
                    data: points,
                    borderColor: "#06b6d4",
                    backgroundColor: "rgba(6, 182, 212, 0.15)",
                    fill: true,
                    tension: 0.1
                },
                {
                    label: "Random Chance (AUC = 0.50)",
                    data: [{x:0, y:0}, {x:1, y:1}],
                    borderColor: "rgba(255,255,255,0.2)",
                    borderDash: [5, 5],
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { type: "linear", min: 0, max: 1, title: { display: true, text: "False Positive Rate (FPR)", color: "#94a3b8" }, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
                y: { min: 0, max: 1, title: { display: true, text: "True Positive Rate (TPR)", color: "#94a3b8" }, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
            },
            plugins: { legend: { labels: { color: "#94a3b8" } } }
        }
    });
}

function renderDlCurves(history) {
    const ctx = document.getElementById("dlHistoryChart");
    if (!ctx || !history) return;

    const epochs = history.loss.map((_, i) => i + 1);

    if (dlHistoryChart) dlHistoryChart.destroy();

    dlHistoryChart = new Chart(ctx.getContext("2d"), {
        type: "line",
        data: {
            labels: epochs,
            datasets: [
                {
                    label: "Training Loss (Binary Crossentropy)",
                    data: history.loss,
                    borderColor: "#f43f5e",
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    tension: 0.2
                },
                {
                    label: "Training Accuracy",
                    data: history.accuracy,
                    borderColor: "#10b981",
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: "Epoch", color: "#94a3b8" }, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
                y: { beginAtZero: true, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
            },
            plugins: { legend: { labels: { color: "#94a3b8" } } }
        }
    });
}

// =============================================================================
// TAB 3: NLP Log Triage & Named Entity Recognition (NER)
// =============================================================================
async function fetchNlpSamples() {
    try {
        const res = await fetch(`${API_BASE}/nlp/samples`);
        if (res.ok) {
            cachedNlpSamples = await res.json();
            if (cachedNlpSamples.length > 0) {
                loadNlpSample(0);
            }
        }
        fetchOperatorLogs();
    } catch (e) {
        console.warn("Could not fetch NLP samples:", e);
    }
}

window.loadNlpSample = function(idx) {
    if (cachedNlpSamples[idx]) {
        document.getElementById("nlpInputText").value = cachedNlpSamples[idx].text;
    }
};

async function analyzeOperatorLog() {
    const text = document.getElementById("nlpInputText").value.trim();
    if (!text) {
        alert("Please enter or select an operator log.");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/nlp/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });
        if (!res.ok) throw new Error("NLP analysis failed");
        const data = await res.json();

        // Render NLP results
        document.getElementById("nlpResultsBox").style.display = "block";

        const urgencyBadge = document.getElementById("nlpUrgencyBadge");
        urgencyBadge.innerText = data.urgency;
        urgencyBadge.className = `badge status-${data.urgency === 'Critical' ? 'critical' : (data.urgency === 'High' ? 'warning' : 'optimal')}`;

        document.getElementById("nlpCategoryText").innerText = data.category;
        document.getElementById("nlpSentimentScore").innerText = `${data.sentiment_score} (${data.sentiment_label})`;
        
        // Sentiment Bar (mapped from -1..1 to 0..100%)
        const pct = ((data.sentiment_score + 1) / 2) * 100;
        document.getElementById("nlpSentimentBar").style.width = `${pct}%`;
        document.getElementById("nlpSentimentBar").style.backgroundColor = data.sentiment_score < 0 ? 'var(--accent-rose)' : 'var(--accent-emerald)';

        document.getElementById("nlpSummaryText").innerText = data.summary;

        // Render NER badges
        renderEntityBadges("nerMachines", data.entities.machines, "badge-machine");
        renderEntityBadges("nerComponents", data.entities.components, "badge-component");
        renderEntityBadges("nerMetrics", data.entities.metrics, "badge-metric");
        renderEntityBadges("nerErrors", data.entities.error_codes, "badge-error");
        renderEntityBadges("nerActions", data.entities.actions, "badge-action");

        fetchOperatorLogs();
    } catch (err) {
        alert("NLP extraction error: " + err.message);
    }
}

function renderEntityBadges(elementId, items, badgeClass) {
    const el = document.getElementById(elementId);
    if (!el) return;
    if (!items || items.length === 0) {
        el.innerHTML = `<span style="color:var(--text-muted); font-size:0.8rem;">None detected</span>`;
        return;
    }
    el.innerHTML = items.map(item => `<span class="badge ${badgeClass}" style="margin-right:4px;">${item}</span>`).join("");
}

async function fetchOperatorLogs() {
    try {
        const res = await fetch(`${API_BASE}/nlp/logs`);
        if (!res.ok) return;
        const logs = await res.json();
        const tbody = document.getElementById("operatorLogsBody");
        if (!tbody) return;

        if (logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No operator logs recorded yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = logs.map(l => {
            const ents = l.entities || {};
            const pills = [
                ...(ents.machines || []).map(m => `<span class="badge badge-machine">${m}</span>`),
                ...(ents.components || []).map(c => `<span class="badge badge-component">${c}</span>`),
                ...(ents.error_codes || []).map(e => `<span class="badge badge-error">${e}</span>`)
            ].slice(0, 4).join(" ");

            return `
                <tr>
                    <td>${new Date(l.created_at).toLocaleTimeString()}</td>
                    <td><span class="badge status-${l.urgency === 'Critical' ? 'critical' : (l.urgency === 'High' ? 'warning' : 'optimal')}">${l.urgency}</span></td>
                    <td>${l.category}</td>
                    <td>${pills || '-'}</td>
                    <td style="max-width:320px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${l.text}</td>
                </tr>
            `;
        }).join("");
    } catch (e) {
        console.warn("Could not fetch operator logs:", e);
    }
}

// =============================================================================
// TAB 4: SLM Process Copilot
// =============================================================================
async function generateSlmSummary() {
    const box = document.getElementById("slmSummaryBox");
    box.innerHTML = `<span style="color:var(--accent-cyan);">Synthesizing multi-shift operational logs with Edge-SLM-1.1B...</span>`;

    try {
        const res = await fetch(`${API_BASE}/slm/summarize`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({})
        });
        if (!res.ok) throw new Error("SLM service error");
        const data = await res.json();

        box.innerHTML = `
            <div style="font-size:0.9rem; line-height:1.6; color:#fff;">
                ${data.summary.replace(/\n/g, '<br>')}
            </div>
            <div style="margin-top:12px; font-size:0.78rem; color:var(--text-muted); display:flex; gap:16px;">
                <span>Quantization: <strong>${data.quantization}</strong></span>
                <span>Inference Latency: <strong>${data.latency_ms}</strong></span>
                <span>Compression: <strong>${data.compression_ratio}</strong></span>
            </div>
        `;

        document.getElementById("rouge1Val").innerText = `${data.rouge_metrics.rouge_1}%`;
        document.getElementById("rouge2Val").innerText = `${data.rouge_metrics.rouge_2}%`;
        document.getElementById("rougeLVal").innerText = `${data.rouge_metrics.rouge_l}%`;

    } catch (e) {
        box.innerHTML = `<span style="color:var(--accent-rose);">Failed to generate SLM briefing: ${e.message}</span>`;
    }
}

async function fetchRecommendations() {
    const container = document.getElementById("recommendationsList");
    const data = getSensorInputs();

    try {
        const res = await fetch(`${API_BASE}/slm/recommend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Recommendation service error");
        const recs = await res.json();

        container.innerHTML = recs.recommendations.map(r => `
            <div style="background: rgba(255,255,255,0.03); border-left: 3px solid ${r.priority === 'CRITICAL' ? 'var(--accent-rose)' : (r.priority === 'HIGH' ? 'var(--accent-amber)' : 'var(--accent-cyan)')}; padding: 12px 16px; border-radius: var(--radius-sm);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
                    <strong style="color: #fff; font-size:0.9rem;">${r.component}</strong>
                    <span class="badge ${r.priority === 'CRITICAL' ? 'status-critical' : (r.priority === 'HIGH' ? 'status-warning' : 'status-optimal')}">${r.priority}</span>
                </div>
                <p style="font-size:0.86rem; color:var(--text-secondary); margin-bottom: 6px;">${r.action}</p>
                <small style="color:var(--accent-emerald);"><i class="fa-solid fa-arrow-trend-up"></i> ${r.expected_gain}</small>
            </div>
        `).join("");

    } catch (e) {
        container.innerHTML = `<em style="color:var(--text-muted);">Could not evaluate recommendations: ${e.message}</em>`;
    }
}

async function sendChatMessage() {
    const input = document.getElementById("chatInput");
    const query = input.value.trim();
    if (!query) return;

    const chatMessages = document.getElementById("chatMessages");
    chatMessages.innerHTML += `<div class="chat-bubble bubble-user">${query}</div>`;
    input.value = "";
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const res = await fetch(`${API_BASE}/slm/ask`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });
        const data = await res.json();

        chatMessages.innerHTML += `
            <div class="chat-bubble bubble-bot">
                ${data.answer}
                <div style="font-size:0.72rem; color:var(--text-muted); margin-top:4px;">${data.model} • ${data.latency_ms}</div>
            </div>
        `;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (e) {
        chatMessages.innerHTML += `<div class="chat-bubble bubble-bot" style="color:var(--accent-rose);">Error communicating with SLM copilot.</div>`;
    }
}

// =============================================================================
// TAB 5: Generative AI Scenario Simulator
// =============================================================================
async function runGenerativeSimulation() {
    const scenario = document.getElementById("scenarioSelect").value;
    const steps = parseInt(document.getElementById("scenarioSteps").value) || 40;

    try {
        const res = await fetch(`${API_BASE}/genai/simulate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ scenario, steps })
        });
        if (!res.ok) throw new Error("Simulation failed");
        const simData = await res.json();

        // Update score cards
        document.getElementById("fidelityScoreVal").innerText = `${simData.fidelity_score}%`;
        document.getElementById("simMttfVal").innerText = simData.contingency_plan.predicted_mttf;
        document.getElementById("simScrapVal").innerText = simData.contingency_plan.projected_yield_impact;

        // Render Waveform Chart
        renderSimulationWaveform(simData.records);

        // Render Contingency Actions
        const actionsBox = document.getElementById("contingencyActionsBox");
        actionsBox.innerHTML = `
            <div style="margin-bottom: 8px;">
                <strong style="color:#fff;">Contingency Response for ${simData.title}:</strong>
            </div>
            <ul style="padding-left: 20px; margin-bottom: 8px;">
                ${simData.contingency_plan.recommended_actions.map(a => `<li>${a}</li>`).join("")}
            </ul>
        `;

    } catch (e) {
        alert("Simulation failed: " + e.message);
    }
}

function renderSimulationWaveform(records) {
    const ctx = document.getElementById("simulationChart");
    if (!ctx || !records) return;

    const steps = records.map(r => `T+${r.step}`);
    const speeds = records.map(r => r.speed);
    const temps = records.map(r => r.temperature);
    const vibs = records.map(r => r.vibration * 100);
    const effs = records.map(r => r.efficiency);

    if (simulationChart) simulationChart.destroy();

    simulationChart = new Chart(ctx.getContext("2d"), {
        type: "line",
        data: {
            labels: steps,
            datasets: [
                { label: "Assembly Speed (RPM)", data: speeds, borderColor: "#3b82f6", borderWidth: 2, tension: 0.2 },
                { label: "Spindle Temp (°C)", data: temps, borderColor: "#f59e0b", borderWidth: 2, tension: 0.2 },
                { label: "Vibration Harmonics (x100)", data: vibs, borderColor: "#f43f5e", borderWidth: 2, tension: 0.2 },
                { label: "Predicted Efficiency (%)", data: effs, borderColor: "#10b981", borderWidth: 2.5, tension: 0.2 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
                y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
            },
            plugins: { legend: { labels: { color: "#94a3b8" } } }
        }
    });
}

// =============================================================================
// TAB 6: Agentic AI Closed-Loop Controller
// =============================================================================
async function fetchAgentStatus() {
    try {
        const res = await fetch(`${API_BASE}/agent/status`);
        if (!res.ok) return;
        const status = await res.json();

        // Update toggle button
        const autoBtn = document.getElementById("toggleAutoBtn");
        const autoText = document.getElementById("autoBtnText");
        if (status.autonomous_mode) {
            autoBtn.className = "btn btn-emerald";
            autoText.innerText = "Auto-Pilot: ACTIVE";
        } else {
            autoBtn.className = "btn btn-secondary";
            autoText.innerText = "Auto-Pilot: MANUAL";
        }

        // Update override inputs
        document.getElementById("overrideSpeed").value = status.current_state.speed;
        document.getElementById("overridePressure").value = status.current_state.pressure;

        fetchAgentActionLogs();
    } catch (e) {
        console.warn("Could not fetch agent status:", e);
    }
}

async function stepAgenticLoop() {
    const currentSensors = getSensorInputs();
    try {
        const res = await fetch(`${API_BASE}/agent/step`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sensors: currentSensors })
        });
        const data = await res.json();

        // Update cycle text
        const anomalies = data.perception_anomalies || [];
        document.getElementById("agentPerceptionText").innerText = anomalies.length ? `Deviations Detected: ${anomalies.join(" • ")}` : "All telemetry channels within standard ISO tolerance.";
        document.getElementById("agentReasoningText").innerText = data.reasoning;
        
        const plan = data.plan || [];
        document.getElementById("agentPlanText").innerText = plan.length ? plan.map(p => `${p.action}: ${p.rationale}`).join(" | ") : "Zero corrective actions required (steady-state production).";

        fetchAgentStatus();
    } catch (e) {
        alert("Agent step failed: " + e.message);
    }
}

async function toggleAgentAuto() {
    const autoBtnText = document.getElementById("autoBtnText");
    const willEnable = autoBtnText.innerText.includes("MANUAL");

    try {
        await fetch(`${API_BASE}/agent/toggle-auto`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ enabled: willEnable })
        });
        fetchAgentStatus();
    } catch (e) {
        alert("Toggle auto-pilot failed: " + e.message);
    }
}

async function triggerKillSwitch() {
    if (!confirm("⚠️ WARNING: Confirm Emergency Kill Switch invocation? This will immediately halt line assembly speed to 0 RPM.")) {
        return;
    }

    try {
        await fetch(`${API_BASE}/agent/kill-switch`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ active: true })
        });
        alert("EMERGENCY KILL SWITCH ENGAGED: Assembly line set to 0 RPM. Safety interlock logged.");
        fetchAgentStatus();
    } catch (e) {
        alert("Kill switch error: " + e.message);
    }
}

window.applyOverride = async function(param, inputId) {
    const val = parseFloat(document.getElementById(inputId).value);
    try {
        const res = await fetch(`${API_BASE}/agent/override`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ parameter: param, value: val })
        });
        if (res.ok) {
            alert(`Manual parameter override applied: ${param} set to ${val}`);
            fetchAgentStatus();
        }
    } catch (e) {
        alert("Override failed: " + e.message);
    }
};

async function fetchAgentActionLogs() {
    try {
        const res = await fetch(`${API_BASE}/agent/actions`);
        if (!res.ok) return;
        const actions = await res.json();
        const tbody = document.getElementById("agentActionsBody");
        if (!tbody) return;

        if (actions.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">No autonomous actions logged yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = actions.map(a => `
            <tr>
                <td>${new Date(a.created_at).toLocaleTimeString()}</td>
                <td><span class="badge ${a.trigger_reason.includes('EMERGENCY') ? 'status-critical' : 'badge-action'}">${a.trigger_reason}</span></td>
                <td>${a.parameter_name}</td>
                <td>${a.old_value} → <strong style="color:var(--accent-cyan);">${a.new_value}</strong></td>
                <td>${a.rationale}</td>
                <td><span class="badge status-optimal">${a.status}</span></td>
            </tr>
        `).join("");
    } catch (e) {
        console.warn("Could not fetch agent actions:", e);
    }
}

// =============================================================================
// TAB 7: LLD Architecture & OpenAPI Spec
// =============================================================================
async function loadOpenApiSpec() {
    const box = document.getElementById("openApiJsonBox");
    if (!box) return;

    try {
        const res = await fetch(`${API_BASE}/lld/spec`);
        if (res.ok) {
            const spec = await res.json();
            box.innerText = JSON.stringify(spec, null, 2);
        }
    } catch (e) {
        box.innerText = "Error loading OpenAPI contract: " + e.message;
    }
}

// =============================================================================
// TAB 8: Telemetry History Database
// =============================================================================
async function fetchFullHistory() {
    try {
        const [sensRes, predRes] = await Promise.all([
            fetch(`${API_BASE}/sensor-data`),
            fetch(`${API_BASE}/predictions`)
        ]);

        if (sensRes.ok) {
            const sens = await sensRes.json();
            const tbody = document.getElementById("fullSensorHistoryBody");
            if (tbody) {
                if (sens.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;">No sensor records in database.</td></tr>`;
                } else {
                    tbody.innerHTML = sens.map(s => `
                        <tr>
                            <td>#${s.id}</td>
                            <td>${new Date(s.created_at).toLocaleTimeString()}</td>
                            <td>${s.temperature}</td>
                            <td>${s.pressure}</td>
                            <td>${s.humidity}</td>
                            <td>${s.speed}</td>
                            <td>${s.vibration}</td>
                            <td>${s.material}</td>
                            <td>${s.power}</td>
                        </tr>
                    `).join("");
                }
            }
        }

        if (predRes.ok) {
            const preds = await predRes.json();
            const tbody = document.getElementById("predictionHistoryBody");
            if (tbody) {
                if (preds.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;">No model predictions recorded.</td></tr>`;
                } else {
                    tbody.innerHTML = preds.map(p => `
                        <tr>
                            <td>#${p.id}</td>
                            <td>${new Date(p.created_at).toLocaleTimeString()}</td>
                            <td><span class="badge ${p.model_name.includes('Deep') ? 'badge-component' : 'badge-machine'}">${p.model_name}</span></td>
                            <td><strong>${p.efficiency}%</strong></td>
                            <td>${p.waste}%</td>
                            <td>${p.failure}%</td>
                            <td>${p.message}</td>
                        </tr>
                    `).join("");
                }
            }
        }
    } catch (e) {
        console.warn("Could not fetch full history:", e);
    }
}
