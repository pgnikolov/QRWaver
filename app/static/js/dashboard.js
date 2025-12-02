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

// (UTM builder removed — UTMs are now defined at creation time only)

async function loadAnalytics(qrId, panelEl) {
    try {
        const res = await fetch(`/api/v1/qr/${qrId}/stats`, { credentials: "include" });
        const json = await res.json();
        if (!json.success) throw new Error(json.error || "Failed to load stats");
        panelEl.dataset.loaded = "1";
        panelEl.innerHTML = renderStats(qrId, json);
    } catch (e) {
        console.error(e);
        panelEl.innerHTML = `<p style="color:red;">Could not load analytics.</p>`;
    }
}

function renderStats(qrId, data) {
    const totals = data.totals || { scans: 0 };
    const uniques = data.uniques || { all_time: 0 };
    const series = data.series || [];
    const seriesUnique = data.series_unique || [];
    const byCountry = data.by_country || [];
    const byDevice = data.by_device || [];
    const byBrowser = data.by_browser || [];
    const utm = data.utm || {};

    // Sheet-like layout: compact summary + sortable, exportable tables
    const dailyTableId = `daily-${qrId}`;
    const dailyUniqueTableId = `daily-unique-${qrId}`;
    const countriesTableId = `countries-${qrId}`;
    const devicesTableId = `devices-${qrId}`;
    const browsersTableId = `browsers-${qrId}`;
    const utmTableId = `utm-${qrId}`;

    return `
      <div class="analytics-sheet">
        <div class="sheet-summary">
          <span class="muted">Total scans</span>
          <span class="sheet-total">${totals.scans ?? 0}</span>
          <span class="muted" style="margin-left:12px;">Unique (by IP)</span>
          <span class="sheet-total">${uniques.all_time ?? 0}</span>
        </div>

        <div class="sheet-row">
          <div class="sheet-card">
            <div class="sheet-title">Daily</div>
            <div class="sheet-actions">
              <button class="btn-secondary btn-xs" onclick="exportTableCSV('${dailyTableId}', 'qr_${qrId}_daily.csv')">Export CSV</button>
            </div>
            ${renderTable(dailyTableId, ["Date","Count"], series.map(s => [s.date, s.count]), ["str","num"]) }
          </div>
          <div class="sheet-card">
            <div class="sheet-title">Daily unique (by IP)</div>
            <div class="sheet-actions">
              <button class="btn-secondary btn-xs" onclick="exportTableCSV('${dailyUniqueTableId}', 'qr_${qrId}_daily_unique.csv')">Export CSV</button>
            </div>
            ${renderTable(dailyUniqueTableId, ["Date","Unique"], seriesUnique.map(s => [s.date, s.count]), ["str","num"]) }
          </div>
        </div>

        <div class="sheet-row">
          <div class="sheet-card">
            <div class="sheet-title">Top countries</div>
            <div class="sheet-actions">
              <button class="btn-secondary btn-xs" onclick="exportTableCSV('${countriesTableId}', 'qr_${qrId}_countries.csv')">Export CSV</button>
            </div>
            ${renderTable(countriesTableId, ["Country","Count"], byCountry.map(c => [c.country ?? '(unknown)', c.count]), ["str","num"]) }
          </div>
          <div class="sheet-card">
            <div class="sheet-title">Devices</div>
            <div class="sheet-actions">
              <button class="btn-secondary btn-xs" onclick="exportTableCSV('${devicesTableId}', 'qr_${qrId}_devices.csv')">Export CSV</button>
            </div>
            ${renderTable(devicesTableId, ["Device","Count"], byDevice.map(d => [d.device_type ?? '(unknown)', d.count]), ["str","num"]) }
          </div>
        </div>

        <div class="sheet-row">
          <div class="sheet-card">
            <div class="sheet-title">Browsers</div>
            <div class="sheet-actions">
              <button class="btn-secondary btn-xs" onclick="exportTableCSV('${browsersTableId}', 'qr_${qrId}_browsers.csv')">Export CSV</button>
            </div>
            ${renderTable(browsersTableId, ["Browser","Count"], byBrowser.map(b => [b.browser ?? '(unknown)', b.count]), ["str","num"]) }
          </div>
          <div class="sheet-card">
            <div class="sheet-title">UTM breakdown</div>
            <div class="sheet-actions">
              <button class="btn-secondary btn-xs" onclick="exportTableCSV('${utmTableId}', 'qr_${qrId}_utm.csv')">Export CSV</button>
            </div>
            ${renderUtmTable(utmTableId, utm)}
          </div>
        </div>
      </div>
    `;
}

// Generic simple table with sortable headers
function renderTable(tableId, headers, rows, types) {
    if (!rows || !rows.length) {
        return `<div class="muted">No data</div>`;
    }
    const thead = `
      <thead>
        <tr>
          ${headers.map((h, idx) => `<th onclick="sortTable('${tableId}', ${idx}, '${types[idx] || 'str'}')">${escapeHtml(h)} <span class="sort-hint">⇅</span></th>`).join('')}
        </tr>
      </thead>`;
    const tbody = `
      <tbody>
        ${rows.map(r => `<tr>${r.map(c => `<td>${escapeHtml(String(c))}</td>`).join('')}</tr>`).join('')}
      </tbody>`;
    return `<div class="sheet-table-wrap"><table class="sheet-table" id="${tableId}">${thead}${tbody}</table></div>`;
}

function renderUtmTable(tableId, utm) {
    const keys = ["utm_source","utm_medium","utm_campaign","utm_term","utm_content"];
    // Flatten into rows: dimension, value, count
    const rows = [];
    keys.forEach(k => {
        const arr = (utm && utm[k]) || [];
        if (!arr.length) {
            rows.push([k, '(none)', 0]);
        } else {
            arr.forEach(x => rows.push([k, String(x[k] ?? '(unknown)'), x.count]));
        }
    });
    return renderTable(tableId, ["Dimension","Value","Count"], rows, ["str","str","num"]);
}

// Sorting and CSV export helpers (exposed globally via window)
window.sortTable = function(tableId, colIndex, type) {
    const table = document.getElementById(tableId);
    if (!table) return;
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const getVal = (td) => td.textContent.trim();
    const cmp = (a, b) => {
        const av = getVal(a.children[colIndex]);
        const bv = getVal(b.children[colIndex]);
        if (type === 'num') {
            return (parseFloat(av) || 0) - (parseFloat(bv) || 0);
        }
        return av.localeCompare(bv);
    };
    // Toggle asc/desc
    const current = table.getAttribute('data-sort') || '';
    const key = `${colIndex}`;
    const desc = current === key ? true : false;
    const sorted = rows.sort((r1, r2) => desc ? -cmp(r1, r2) : cmp(r1, r2));
    // Update marker
    table.setAttribute('data-sort', desc ? `-${key}` : key);
    // Re-append
    sorted.forEach(tr => tbody.appendChild(tr));
};

window.exportTableCSV = function(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    const rows = [];
    const esc = (v) => {
        const s = String(v).replaceAll('"', '""');
        return /[",\n]/.test(s) ? `"${s}"` : s;
    };
    // headers
    const headers = Array.from(table.tHead?.rows[0]?.cells || []).map(th => th.textContent.replace('⇅','').trim());
    if (headers.length) rows.push(headers.map(esc).join(','));
    // body
    Array.from(table.tBodies[0].rows).forEach(tr => {
        const cols = Array.from(tr.cells).map(td => td.textContent.trim());
        rows.push(cols.map(esc).join(','));
    });
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'export.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

document.addEventListener("DOMContentLoaded", loadUserQRCodes);
