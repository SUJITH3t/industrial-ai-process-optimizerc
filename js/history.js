const API_BASE = 'http://127.0.0.1:5001';
const tableBody = document.getElementById('historyTableBody');
const refreshButton = document.getElementById('refreshHistoryBtn');

async function loadSensorHistory() {
    try {
        const response = await fetch(`${API_BASE}/sensor-data`);

        if (!response.ok) {
            throw new Error('Failed to fetch sensor history');
        }

        const data = await response.json();

        if (!Array.isArray(data) || data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="9" class="empty-state">No sensor data found.</td></tr>';
            return;
        }

        tableBody.innerHTML = data.map(item => `
            <tr>
                <td>${item.id}</td>
                <td>${Number(item.temperature).toFixed(2)}</td>
                <td>${Number(item.pressure).toFixed(2)}</td>
                <td>${Number(item.humidity).toFixed(2)}</td>
                <td>${Number(item.speed).toFixed(2)}</td>
                <td>${Number(item.vibration).toFixed(2)}</td>
                <td>${Number(item.material).toFixed(2)}</td>
                <td>${Number(item.power).toFixed(2)}</td>
                <td>${new Date(item.created_at).toLocaleString()}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error(error);
        tableBody.innerHTML = '<tr><td colspan="9" class="empty-state">Unable to load sensor history.</td></tr>';
    }
}

refreshButton.addEventListener('click', loadSensorHistory);
loadSensorHistory();
