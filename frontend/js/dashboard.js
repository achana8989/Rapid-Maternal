async function fetchSummary() {
    const res = await fetch('http://127.0.0.1:8000/emergencies/summary');
    const data = await res.json();
    document.getElementById('total').innerText = data.total_emergencies;
    document.getElementById('active').innerText = data.active;
    document.getElementById('escalated').innerText = data.escalated;
}

async function fetchEmergencies() {
    const res = await fetch('http://127.0.0.1:8000/emergencies/');
    const emergencies = await res.json();
    const tbody = document.querySelector('#emergencies tbody');
    tbody.innerHTML = '';
    emergencies.forEach(e => {
        const row = `<tr>
            <td>${e.id}</td>
            <td>${e.facility_id}</td>
            <td>${e.emergency_type}</td>
            <td>${e.status}</td>
            <td>${e.acknowledged_by || '-'}</td>
            <td>${e.is_escalated ? '⚠️ Level ' + e.escalation_level : '-'}</td>
        </tr>`;
        tbody.innerHTML += row;
    });
}

async function loadDashboard() {
    await fetchSummary();
    await fetchEmergencies();
}

// Auto-refresh every 15 seconds
loadDashboard();
setInterval(loadDashboard, 15000);