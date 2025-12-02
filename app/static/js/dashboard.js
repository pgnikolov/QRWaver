async function loadUserQRCodes() {
    const listEl = document.getElementById("qr-list");
    if (!listEl) return;

    listEl.innerHTML = "<p>Loading...</p>";

    try {
        const res = await fetch("/api/v1/qr", {
            method: "GET",
            credentials: "include",
        });

        const json = await res.json();
        if (!json.success) throw new Error(json.error || "Failed to load");

        const items = json.items || [];
        if (!items.length) {
            listEl.innerHTML = "<p>You don't have any QR codes yet.</p>";
            return;
        }

        listEl.innerHTML = "";

        items.forEach(qr => {
            const row = document.createElement("article");
            row.className = "qr-row";

            const created = qr.created_at
                ? new Date(qr.created_at).toLocaleString()
                : "";

            row.innerHTML = `
                <div class="qr-row-thumb">
                    <img src="${qr.url}" alt="QR code" loading="lazy" width="160" height="160" />
                </div>
                <div class="qr-row-body">
                    <div class="qr-row-header">
                        <span class="qr-type">${qr.qr_type.toUpperCase()}</span>
                        <span class="qr-scans">Scans: ${qr.scan_count}</span>
                    </div>
                    <p class="qr-payload" title="${escapeHtml(qr.payload)}">${escapeHtml(shorten(qr.payload, 160))}</p>
                    <p class="qr-meta">Created: ${created}${qr.short_url ? ` • Short: <a href="${qr.short_url}" target="_blank">${qr.short_url}</a>` : ""}</p>
                    <div class="qr-row-actions">
                        <a href="${qr.url}" target="_blank" class="btn-secondary">Open</a>
                        <button class="btn-secondary" data-analytics-id="${qr.id}">Analytics</button>
                        <button class="btn-danger" data-delete-id="${qr.id}">Delete</button>
                    </div>
                    <div class="qr-analytics" id="analytics-${qr.id}" style="display:none; margin-top: 12px;">
                        <div class="analytics-loading">Loading analytics…</div>
                    </div>
                </div>
            `;

            const deleteBtn = row.querySelector("button[data-delete-id]");
            deleteBtn.addEventListener("click", async () => {
                if (!confirm("Delete this QR from your dashboard? This will remove stats and the short link, but will not delete the file from storage.")) return;
                try {
                    const delRes = await fetch(`/api/v1/qr/${qr.id}`, {
                        method: "DELETE",
                        credentials: "include",
                    });
                    if (delRes.status === 404) {
                        alert("Item not found or already deleted.");
                        return;
                    }
                    const out = await delRes.json();
                    if (!out.success) throw new Error(out.error || "Delete failed");
                    row.remove();
                    if (!listEl.querySelector('.qr-row')) {
                        listEl.innerHTML = "<p>You don't have any QR codes yet.</p>";
                    }
                } catch (e) {
                    console.error(e);
                    alert("Could not delete item. Please try again.");
                }
            });

            // Analytics toggle
            const analyticsBtn = row.querySelector("button[data-analytics-id]");
            analyticsBtn.addEventListener("click", async () => {
                const panel = document.getElementById(`analytics-${qr.id}`);
                if (!panel) return;
                const isHidden = panel.style.display === "none";
                if (isHidden) {
                    panel.style.display = "block";
                    // If not loaded yet, fetch stats
                    if (!panel.dataset.loaded) {
                        await loadAnalytics(qr.id, panel);
                    }
                } else {
                    panel.style.display = "none";
                }
            });

            listEl.appendChild(row);
        });

    } catch (err) {
        console.error(err);
        listEl.innerHTML = "<p style='color:red;'>Failed to load QR codes.</p>";
    }
}

// ---------------------------------------------
// Helpers
// ---------------------------------------------

function shorten(str, max) {
    if (!str) return "";
    if (str.length <= max) return str;
    return str.slice(0, max - 1) + "…";
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

async function loadAnalytics(qrId, panelEl) {
    try {
        const res = await fetch(`/api/v1/qr/${qrId}/stats`, { credentials: "include" });
        const json = await res.json();
        if (!json.success) throw new Error(json.error || "Failed to load stats");
        panelEl.dataset.loaded = "1";
        panelEl.innerHTML = renderStats(json);
    } catch (e) {
        console.error(e);
        panelEl.innerHTML = `<p style="color:red;">Could not load analytics.</p>`;
    }
}

function renderStats(data) {
    const totals = data.totals || { scans: 0 };
    const series = data.series || [];
    const byCountry = data.by_country || [];
    const byDevice = data.by_device || [];
    const byBrowser = data.by_browser || [];
    const byReferrer = data.by_referrer || [];
    const utm = data.utm || {};

    return `
      <div class="analytics-grid">
        <div class="analytics-card">
          <div class="analytics-title">Totals</div>
          <div>Scans: <strong>${totals.scans ?? 0}</strong></div>
        </div>
        <div class="analytics-card">
          <div class="analytics-title">Daily</div>
          <div class="analytics-series">${renderSeries(series)}</div>
        </div>
        <div class="analytics-card">
          <div class="analytics-title">Top countries</div>
          ${renderList(byCountry, 'country')}
        </div>
        <div class="analytics-card">
          <div class="analytics-title">Devices</div>
          ${renderList(byDevice, 'device_type')}
        </div>
        <div class="analytics-card">
          <div class="analytics-title">Browsers</div>
          ${renderList(byBrowser, 'browser')}
        </div>
        <div class="analytics-card">
          <div class="analytics-title">Referrers</div>
          ${renderList(byReferrer, 'referrer')}
        </div>
        <div class="analytics-card">
          <div class="analytics-title">UTM</div>
          ${renderUtm(utm)}
        </div>
      </div>
    `;
}

function renderSeries(series) {
    if (!series.length) return `<div class="muted">No scans yet</div>`;
    return `
      <ul class="list-plain">
        ${series.map(s => `<li>${s.date}: <strong>${s.count}</strong></li>`).join("")}
      </ul>
    `;
}

function renderList(items, key) {
    if (!items || !items.length) return `<div class="muted">No data</div>`;
    return `
      <ul class="list-plain">
        ${items.map(x => `<li>${escapeHtml(String(x[key] ?? '(unknown)'))}: <strong>${x.count}</strong></li>`).join("")}
      </ul>
    `;
}

function renderUtm(utm) {
    const keys = ["utm_source","utm_medium","utm_campaign","utm_term","utm_content"];
    return `
      <ul class="list-plain">
        ${keys.map(k => {
            const arr = (utm && utm[k]) || [];
            if (!arr.length) return `<li>${k}: <span class="muted">(none)</span></li>`;
            return `<li>${k}: ${arr.map(x => `${escapeHtml(String(x[k] ?? '(unknown)'))} <strong>${x.count}</strong>`).join(', ')}</li>`;
        }).join('')}
      </ul>
    `;
}

document.addEventListener("DOMContentLoaded", loadUserQRCodes);
