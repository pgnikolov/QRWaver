// ---------------------------------------------------------------------
// Cosmetic ripple for CTA buttons
// ---------------------------------------------------------------------
document.addEventListener('click', e => {
    const t = e.target.closest('.btn-primary');
    if (!t) return;
    t.style.transform = 'translateY(1px) scale(.995)';
    setTimeout(() => (t.style.transform = ''), 90);
});

// (Removed) Theme toggle logic

// ---------------------------------------------------------------------
// Mobile navigation toggle
// ---------------------------------------------------------------------
(function(){
    document.addEventListener('DOMContentLoaded', () => {
        const toggle = document.getElementById('mobile-menu-toggle');
        const nav = document.getElementById('primary-nav');
        if (!toggle || !nav) return;

        const closeOnOutside = (ev) => {
            if (!nav.classList.contains('open')) return;
            if (ev.target.closest('#primary-nav') || ev.target.closest('#mobile-menu-toggle')) return;
            nav.classList.remove('open');
            toggle.setAttribute('aria-expanded', 'false');
        };

        toggle.addEventListener('click', () => {
            const isOpen = nav.classList.toggle('open');
            toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        document.addEventListener('click', closeOnOutside);
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 960 && nav.classList.contains('open')) {
                nav.classList.remove('open');
                toggle.setAttribute('aria-expanded', 'false');
            }
        });
    });
})();

// ---------------------------------------------------------------------
// UNIVERSAL QR GENERATOR – talks to /api/qr/create (JWT COOKIE REQUIRED)
// ---------------------------------------------------------------------

function initQRGenerator(type = "text") {
    const preview = document.getElementById("qr-preview");
    const textInput = document.getElementById("qr-text");
    const frameThumbs = document.getElementById("frame-thumbs");
    const frameColor = document.getElementById("frame-color");
    const formatSelect = document.getElementById("qr-format");
    const downloadBtn = document.getElementById("downloadBtn");
    const saveBtn = document.getElementById("saveBtn");
    const shareBtn = document.getElementById("shareBtn");

    window.scheduleQRUpdate = scheduleUpdate;

    let currentImageUrl = null;
    let currentComposited = null;
    let currentFrame = "none";
    let debounceTimer = null;
    let isSaved = false;
    let savedRecordId = null;
    let savedShortUrl = null;

    if (!preview) {
        console.warn("Missing #qr-preview");
        return;
    }

    // ---------------------------------------------------------------------
    // FRAME SELECTION
    // ---------------------------------------------------------------------
    if (frameThumbs) {
        frameThumbs.addEventListener("click", (e) => {
            const btn = e.target.closest("button.thumb");
            if (!btn) return;

            [...frameThumbs.querySelectorAll(".thumb")]
                .forEach(b => b.classList.remove("selected"));

            btn.classList.add("selected");
            currentFrame = btn.dataset.frame || "none";
            composeFrame();
        });
    }

    // ---------------------------------------------------------------------
    // DEBOUNCE INPUT
    // ---------------------------------------------------------------------
    function scheduleUpdate() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(updateQR, 250);
    }

    textInput?.addEventListener("input", scheduleUpdate);
    frameColor?.addEventListener("input", composeFrame);

    if (typeof window.getQRInputData === "function") {
        document.querySelectorAll("input,select,textarea")
            .forEach(el => el.addEventListener("input", scheduleUpdate));
    }

    // ---------------------------------------------------------------------
    // MAIN QR PREVIEW CALL → /api/v1/qr/preview (no auth, no persistence)
    // ---------------------------------------------------------------------
    async function updateQR() {
        let dataPayload = null;

        if (type === "text") {
            const txt = textInput?.value.trim();
            if (!txt) {
                preview.innerHTML = `<p class="muted">Your QR will appear here</p>`;
                currentImageUrl = null;
                enableButtons(false);
                return;
            }
            dataPayload = txt;
        } else {
            if (typeof window.getQRInputData === "function") {
                dataPayload = window.getQRInputData();
            }
            if (!dataPayload) {
                preview.innerHTML = `<p class="muted">Your QR will appear here</p>`;
                currentImageUrl = null;
                enableButtons(false);
                return;
            }
        }

        try {
            const res = await fetch("/api/v1/qr/preview", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    type: type,
                    data: dataPayload,
                    settings: {
                        color: frameColor?.value || "#000000",
                        size: 1024
                    }
                }),
            });

            const result = await res.json();
            if (!result.success) throw new Error(result.error || "API error");

            currentImageUrl = result.image; // data URI for preview

            if (currentFrame === "none") {
                preview.innerHTML = `<img src="${currentImageUrl}" class="qr-big">`;
                currentComposited = currentImageUrl;
                enableButtons(true);
                isSaved = false; // content changed → mark unsaved
            } else {
                await composeFrame();
            }

        } catch (err) {
            console.error(err);
            preview.innerHTML = `<p style="color:red;">Error generating QR.</p>`;
            enableButtons(false);
        }
    }

    function enableButtons(v) {
        if (downloadBtn) downloadBtn.disabled = !v;
        if (shareBtn) shareBtn.disabled = !v;
    }

    // ---------------------------------------------------------------------
    // RENDER FRAME (inject QR inside SVG frame)
    // ---------------------------------------------------------------------
    async function composeFrame() {
        if (!currentImageUrl) return;

        if (currentFrame === "none") {
            preview.innerHTML = `<img src="${currentImageUrl}" class="qr-big">`;
            currentComposited = currentImageUrl;
            enableButtons(true);
            // frame change → unsaved
            isSaved = false;
            return;
        }

        try {
            const framePath = `/static/images/frames/${currentFrame}.svg`;
            const resp = await fetch(framePath);
            let svg = await resp.text();

            const zone = svg.match(/<rect[^>]*id="QR_ZONE"[^>]*>/i);
            if (!zone) throw new Error("QR_ZONE not found in frame SVG");

            const tag = zone[0];
            const get = (key) => {
                const m = tag.match(new RegExp(`${key}="([^"]+)"`));
                return m ? parseFloat(m[1]) : 0;
            };

            const x = get("x");
            const y = get("y");
            const w = get("width");
            const h = get("height");

            const colorValue = frameColor?.value || "#000";
            svg = svg.replace(/fill="#000000"/g, `fill="${colorValue}"`);
            svg = svg.replace(/stroke="#000000"/g, `stroke="${colorValue}"`);
            svg = svg.replace(/<g[^>]*id="qr-placeholder-index"[\s\S]*?<\/g>/i, "");

            const imgTag = `<image x="${x}" y="${y}" width="${w}" height="${h}" href="${currentImageUrl}" />`;
            svg = svg.replace(/<\/svg>\s*$/i, `${imgTag}</svg>`);

            preview.innerHTML = svg;

            currentComposited = await svgToPng(svg);
            enableButtons(true);

        } catch (err) {
            console.error("Frame composition error:", err);
            preview.innerHTML = `<img src="${currentImageUrl}" class="qr-big">`;
            currentComposited = currentImageUrl;
            enableButtons(true);
            isSaved = false;
        }
    }

    // ---------------------------------------------------------------------
    // Convert frame+QR SVG → PNG
    // ---------------------------------------------------------------------
    async function svgToPng(svgText) {
        const blob = new Blob([svgText], {type: "image/svg+xml"});
        const url = URL.createObjectURL(blob);

        const img = new Image();
        img.src = url;
        await img.decode();

        const canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;

        const ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(img, 0, 0);

        URL.revokeObjectURL(url);
        return canvas.toDataURL("image/png");
    }

    // ---------------------------------------------------------------------
    // DOWNLOAD
    // ---------------------------------------------------------------------
    function toast(msg, type = "info") {
        let el = document.createElement("div");
        el.className = `toast toast-${type}`;
        el.textContent = msg;
        document.body.appendChild(el);
        requestAnimationFrame(() => (el.style.opacity = "1"));
        setTimeout(() => {
            el.style.opacity = "0";
            setTimeout(() => el.remove(), 300);
        }, 2500);
    }

    async function persistIfNeeded() {
        if (isSaved) return true;

        // Build the same payload used for preview
        let dataPayload = null;
        if (type === "text") {
            const txt = textInput?.value.trim();
            if (!txt) return false;
            dataPayload = txt;
        } else if (typeof window.getQRInputData === "function") {
            dataPayload = window.getQRInputData();
        }
        if (!dataPayload) return false;

        try {
            const res = await fetch("/api/v1/qr/create", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                credentials: "include",
                body: JSON.stringify({
                    type: type,
                    data: dataPayload,
                    settings: { size: 1024, format: (formatSelect?.value || "png") },
                    frame: currentFrame,
                    utm: (typeof window.getUTMFields === "function" ? window.getUTMFields() : undefined)
                })
            });
            if (res.status === 401) {
                toast("Not logged in — downloading without saving.", "info");
                return false; // allow download to proceed
            }
            if (res.status === 403) {
                toast("Free limit reached (5). Delete older QRs to save new ones.", "error");
                return false;
            }
            const out = await res.json();
            if (out && out.success) {
                isSaved = true;
                savedRecordId = out.record_id;
                savedShortUrl = out.short_url;
                toast("Saved to dashboard.", "success");
                return true;
            }
        } catch (e) {
            console.error("Auto-save error", e);
            toast("Couldn’t auto-save — downloading anyway.", "error");
        }
        return false;
    }

    downloadBtn?.addEventListener("click", async () => {
        if (!currentImageUrl) return;

        const format = formatSelect?.value || "png";

        // Try auto-save if user is logged in and not saved yet
        await persistIfNeeded();

        if (format === "svg" && currentFrame === "none") {
            const a = document.createElement("a");
            a.href = currentImageUrl;
            a.download = "qrwaver.svg";
            a.click();
            return;
        }

        const rawSvg = preview.innerHTML;
        const TARGET = 2400;

        const svgBlob = new Blob([rawSvg], {type: "image/svg+xml"});
        const url = URL.createObjectURL(svgBlob);

        const img = new Image();
        img.src = url;
        await img.decode();

        const scale = TARGET / Math.max(img.width, img.height);
        const canvas = document.createElement("canvas");

        canvas.width = img.width * scale;
        canvas.height = img.height * scale;

        const ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        URL.revokeObjectURL(url);

        const mime = format === "jpeg" ? "image/jpeg" : "image/png";
        const out = canvas.toDataURL(mime, 0.98);

        const a = document.createElement("a");
        a.href = out;
        a.download = `qrwaver.${format}`;
        a.click();
    });

    // ---------------------------------------------------------------------
    // SHARE API
    // ---------------------------------------------------------------------
    shareBtn?.addEventListener("click", async () => {
        if (!currentComposited) return;

        const format = formatSelect?.value || "png";
        if (format === "svg") {
            alert("Sharing SVG not supported");
            return;
        }

        const blob = await (await fetch(currentComposited)).blob();
        const file = new File([blob], `qrwaver.${format}`, {type: blob.type});

        if (navigator.share && navigator.canShare?.({files: [file]})) {
            await navigator.share({title: "QR Code", files: [file]});
        } else {
            alert("Sharing not supported.");
        }
    });

    // ---------------------------------------------------------------------
    // SAVE (persist to account) — optional button with id="saveBtn"
    // ---------------------------------------------------------------------
    saveBtn?.addEventListener("click", async () => {
        // Gather the same payload used for preview
        let dataPayload = null;
        if (type === "text") {
            const txt = textInput?.value.trim();
            if (!txt) return alert("Nothing to save yet.");
            dataPayload = txt;
        } else {
            if (typeof window.getQRInputData === "function") {
                dataPayload = window.getQRInputData();
            }
            if (!dataPayload) return alert("Nothing to save yet.");
        }

        try {
            const res = await fetch("/api/v1/qr/create", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                credentials: "include", // requires login
                body: JSON.stringify({
                    type: type,
                    data: dataPayload,
                    settings: { size: 1024, format: (formatSelect?.value || "png") },
                    frame: currentFrame,
                    utm: (typeof window.getUTMFields === "function" ? window.getUTMFields() : undefined)
                })
            });
            if (res.status === 401) {
                alert("Please log in to save your QR.");
                return;
            }
            const out = await res.json();
            if (!out.success) throw new Error(out.error || "Save failed");
            isSaved = true;
            savedRecordId = out.record_id;
            savedShortUrl = out.short_url;
            if (typeof toast === 'function') {
                toast("Saved to dashboard.", "success");
            } else {
                alert("Saved! You can find it in your dashboard.");
            }
        } catch (e) {
            console.error("Save error", e);
            alert("Could not save QR. Please try again.");
        }
    });

    // ---------------------------------------------------------------------
    // INITIAL LOAD
    // ---------------------------------------------------------------------
    updateQR();
}

// Global site JS
document.addEventListener("DOMContentLoaded", () => {
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      try {
        logoutBtn.disabled = true;
        logoutBtn.textContent = "Logging out...";
        const res = await fetch("/auth/logout", {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
        });
        // Regardless of JSON body, if 200, redirect to home
        if (res.ok) {
          window.location.href = "/";
          return;
        }
      } catch (e) {
        console.error("Logout failed", e);
      } finally {
        logoutBtn.disabled = false;
        logoutBtn.textContent = "Logout";
      }
      alert("Could not log out. Please try again.");
    });
  }
  // (Removed) UTM help toggle handler — now handled inline via onclick on the button
});
