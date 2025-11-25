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
                    <p class="qr-meta">Created: ${created}</p>
                    <div class="qr-row-actions">
                        <a href="${qr.url}" target="_blank" class="btn-secondary">Open</a>
                        <button class="btn-danger" data-delete-id="${qr.id}">Delete</button>
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

document.addEventListener("DOMContentLoaded", loadUserQRCodes);
