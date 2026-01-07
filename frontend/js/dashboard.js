const API_BASE = "http://127.0.0.1:8000";

/* =========================
   Fetch Summary
========================= */
async function fetchSummary() {
    try {
        const res = await fetch(`${API_BASE}/emergencies/summary`);
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
        const emergencies = await res.json();

        const tbody = document.querySelector("#emergencies tbody");
        tbody.innerHTML = "";

        emergencies.forEach(e => {
            const tr = document.createElement("tr");

            // 🔥 Flash escalated rows
            if (e.status === "Escalated" || e.escalation_level > 0) {
                tr.classList.add("escalated-row");
            }

            tr.innerHTML = `
                <td>${e.id}</td>

                <!-- ✅ FACILITY AS ENTERED -->
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



                <td>${e.emergency_type}</td>

                <td>
                    <span class="status ${e.status?.toLowerCase()}">
                        ${e.status}
                    </span>
                </td>

                <td>${e.acknowledged_by || "-"}</td>

                <td>
                    ${e.escalation_level > 0
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
   Last Updated Time
========================= */
function updateLastUpdated() {
    const el = document.getElementById("lastUpdated");
    if (!el) return;

    el.innerText = new Date().toLocaleTimeString();
}

/* =========================
   Load Dashboard
========================= */
async function loadDashboard() {
    await fetchSummary();
    await fetchEmergencies();
}

/* =========================
   Auto Refresh
========================= */
loadDashboard();
setInterval(loadDashboard, 15000);

/* =========================
   Role-based UI
========================= */
if (typeof userRole !== "undefined" && userRole !== "SUBDISTRICT_ADMIN") {
    const btn = document.getElementById("acknowledgeBtn");
    if (btn) btn.style.display = "none";
}
