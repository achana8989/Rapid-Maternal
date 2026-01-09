/* =========================
   Dashboard WebSocket
========================= */

// ⚠️ Make sure you have a "sounds/alert.mp3" file in your frontend folder
const alertSound = new Audio("/sounds/alert.mp3");

// Summary elements
const totalEl = document.getElementById("total");
const activeEl = document.getElementById("active");
const escalatedEl = document.getElementById("escalated");
const lastUpdatedEl = document.getElementById("last-time");

// Table body
const tbody = document.querySelector("#emergencies tbody");

// Store the current emergency IDs to detect new ones
let currentEmergencies = new Map();

/* =========================
   WebSocket Setup
========================= */
const WS_URL = "ws://127.0.0.1:8000/ws/emergencies"; // Make sure backend has a /ws/emergencies endpoint
const ws = new WebSocket(WS_URL);

ws.onopen = () => {
  console.log("✅ WebSocket connected");
};

ws.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);

    if (!data || !data.emergencies) return;

    updateSummary(data.summary);
    updateEmergencies(data.emergencies);
    updateLastUpdated();
  } catch (err) {
    console.error("WebSocket message error:", err);
  }
};

ws.onclose = () => {
  console.warn("⚠️ WebSocket closed. Reconnecting in 5s...");
  setTimeout(() => {
    location.reload(); // simple reconnect strategy
  }, 5000);
};

/* =========================
   Update Summary Cards
========================= */
function updateSummary(summary) {
  if (!summary) return;
  totalEl.innerText = summary.total ?? 0;
  activeEl.innerText = summary.active ?? 0;
  escalatedEl.innerText = summary.escalated ?? 0;
}

/* =========================
   Update Emergency Table
========================= */
function updateEmergencies(emergencies) {
  if (!emergencies) return;

  tbody.innerHTML = ""; // clear table

  emergencies.forEach(e => {
    const tr = document.createElement("tr");

    // Highlight escalated rows
    if (e.status === "Escalated" || e.escalation_level > 0) {
      tr.classList.add("escalated-row");
    }

    tr.innerHTML = `
      <td>${e.id}</td>
      <td>
        <span class="facility">
          ${e.facility_name ?? e.facility?.name ?? e.facility ?? e.facility_id ?? "-"}
        </span>
      </td>
      <td>${e.emergency_type}</td>
      <td>
        <span class="status ${e.status?.toLowerCase()}">
          ${e.status}
        </span>
      </td>
      <td>${e.acknowledged_by || "-"}</td>
      <td>${e.escalation_level > 0 ? "⚠️ Level " + e.escalation_level : "-"}</td>
    `;

    tbody.appendChild(tr);

    // 🔔 Sound alert for new or escalated emergencies
    if (!currentEmergencies.has(e.id) || e.escalation_level > currentEmergencies.get(e.id)) {
      alertSound.play().catch(() => {});
    }

    // Update current emergencies map
    currentEmergencies.set(e.id, e.escalation_level);
  });

  // Remove old emergencies that no longer exist
  currentEmergencies.forEach((_, id) => {
    if (!emergencies.find(e => e.id === id)) {
      currentEmergencies.delete(id);
    }
  });
}

/* =========================
   Last Updated Time
========================= */
function updateLastUpdated() {
  if (!lastUpdatedEl) return;
  lastUpdatedEl.innerText = new Date().toLocaleTimeString();
}

/* =========================
   Role-based UI
========================= */
if (typeof userRole !== "undefined" && userRole !== "SUBDISTRICT_ADMIN") {
  const btn = document.getElementById("acknowledgeBtn");
  if (btn) btn.style.display = "none";
}
