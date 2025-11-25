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
            const shareUrl = qr.short_url || qr.url;
            const card = document.createElement("article");
            card.className = "qr-card";

            const created = qr.created_at
                ? new Date(qr.created_at).toLocaleString()
                : "";

            card.innerHTML = `
                <div class="qr-card-thumb">
                    <img src="${qr.url}" alt="QR code" />
                </div>
                <div class="qr-card-body">
                    <p class="qr-type">${qr.qr_type.toUpperCase()}</p>
                    <p class="qr-payload">${escapeHtml(shorten(qr.payload, 120))}</p>
                    <p class="qr-meta">
                        Created: ${created}<br>
                        Scans: ${qr.scan_count}
                    </p>
                    <div class="qr-card-actions">
                        <a href="${qr.url}" target="_blank" class="btn-secondary">Open</a>
                        <button class="btn-primary" data-url="${shareUrl}">Copy share link</button>
                        <button class="btn-danger" data-delete-id="${qr.id}">Delete</button>
                    </div>
                    ${qr.short_url ? `<p class="qr-meta">Short link: <a href="${qr.short_url}" target="_blank">${qr.short_url}</a></p>` : ""}
                </div>
            `;

            const copyBtn = card.querySelector("button[data-url]");
            copyBtn.addEventListener("click", async () => {
                try {
                    const toCopy = copyBtn.getAttribute("data-url") || qr.url;
                    await navigator.clipboard.writeText(toCopy);
                    copyBtn.textContent = "Copied!";
                    setTimeout(() => (copyBtn.textContent = "Copy share link"), 1500);
                } catch {
                    alert("Cannot copy link.");
                }
            });

            const deleteBtn = card.querySelector("button[data-delete-id]");
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
                    card.remove();
                    if (!listEl.querySelector('.qr-card')) {
                        listEl.innerHTML = "<p>You don't have any QR codes yet.</p>";
                    }
                } catch (e) {
                    console.error(e);
                    alert("Could not delete item. Please try again.");
                }
            });

            listEl.appendChild(card);
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
