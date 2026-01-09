/**
 * dashboard.js
 * Rapid Maternal Emergency Dashboard
 */

const API_BASE = "http://127.0.0.1:8000";

/* =========================
   Fetch Summary
========================= */
async function fetchSummary() {
    try {
        const res = await fetch(`${API_BASE}/emergencies/summary`);
        if (!res.ok) throw new Error("Failed to fetch summary");

        const data = await res.json();

        document.getElementById("total").innerText = data.total ?? 0;
        document.getElementById("active").innerText = data.active ?? 0;
        document.getElementById("escalated").innerText = data.escalated ?? 0;

        updateLastUpdated();
    } catch (err) {
        console.error("Summary fetch failed:", err);
    }
}

/* =========================
   Fetch Emergencies
========================= */
async function fetchEmergencies() {
    try {
        const res = await fetch(`${API_BASE}/emergencies/`);
        if (!res.ok) throw new Error("Failed to fetch emergencies");

        const emergencies = await res.json();

        const tbody = document.querySelector("#emergencies tbody");
        if (!tbody) return;

        tbody.innerHTML = "";

        emergencies.forEach(e => {
            const tr = document.createElement("tr");

            // 🔥 Highlight escalated emergencies
            if (e.status === "Escalated" || e.escalation_level > 0) {
                tr.classList.add("escalated-row");
            }

            tr.innerHTML = `
                <td>${e.id ?? "-"}</td>

                <td>
                    <span class="facility">
                        ${
                            e.facility_name ??
                            e.facility?.name ??
                            e.facility ??
                            e.facility_id ??
                            "-"
                        }
                    </span>
                </td>

                <td>${e.emergency_type ?? "-"}</td>

                <td>
                    <span class="status ${e.status ? e.status.toLowerCase() : ""}">
                             ${e.status ? e.status.charAt(0).toUpperCase() + e.status.slice(1) : "-"}
                     </span>

                </td>

                <td>${e.acknowledged_by ?? "-"}</td>

                <td>
                    ${
                        e.escalation_level > 0
                            ? "⚠️ Level " + e.escalation_level
                            : "-"
                    }
                </td>
            `;

            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Emergency fetch failed:", err);
    }
}

/* =========================
   Last Updated Indicator
========================= */
function updateLastUpdated() {
    const el = document.getElementById("last-time");
    if (!el) return;

    el.innerText = new Date().toLocaleTimeString();
}

/* =========================
   Load Dashboard
========================= */
async function loadDashboard() {
    await fetchSummary();
    await fetchEmergencies();
    console.log("Dashboard refreshed");
}

/* =========================
   Auto Refresh (15s)
========================= */
loadDashboard();
setInterval(loadDashboard, 15000);

/* =========================
   Role-based UI (optional)
========================= */
if (typeof userRole !== "undefined" && userRole !== "SUBDISTRICT_ADMIN") {
    const btn = document.getElementById("acknowledgeBtn");
    if (btn) btn.style.display = "none";
}

/* =========================
   Load Dashboard (SAFE)
========================= */
document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();

    // ✅ Only ONE interval
    window.dashboardInterval && clearInterval(window.dashboardInterval);

    window.dashboardInterval = setInterval(loadDashboard, 15000);
});

