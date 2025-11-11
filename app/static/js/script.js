// ---------------------------------------------------------------------
// Cosmetic ripple for CTA buttons
// ---------------------------------------------------------------------
document.addEventListener('click', e => {
    const t = e.target.closest('.btn-primary');
    if (!t) return;
    t.style.transform = 'translateY(1px) scale(.995)';
    setTimeout(() => (t.style.transform = ''), 90);
});

// ---------------------------------------------------------------------
// UNIVERSAL QR GENERATOR — WORKS FOR ALL QR TYPES
// ---------------------------------------------------------------------

function initQRGenerator(type = "text") {
    const preview      = document.getElementById("qr-preview");
    const textInput    = document.getElementById("qr-text");   // Only for text QR
    const colorInput   = document.getElementById("qr-color");
    const frameThumbs  = document.getElementById("frame-thumbs");
    const frameColor   = document.getElementById("frame-color");
    const formatSelect = document.getElementById("qr-format");
    const downloadBtn  = document.getElementById("downloadBtn");
    const shareBtn     = document.getElementById("shareBtn");
    window.scheduleQRUpdate = scheduleUpdate;


    let currentSvg        = null;  // Raw QR SVG
    let currentComposited = null;  // SVG + Frame -> PNG
    let currentFrame      = "none";
    let debounceTimer     = null;

    if (!preview) {
        console.warn("Missing preview element");
        return;
    }

    // -------------------------------------------------------------
    // Frame selection
    // -------------------------------------------------------------
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

    // -------------------------------------------------------------
    // Setup listeners
    // -------------------------------------------------------------
    function scheduleUpdate() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(updateQR, 250);
    }

    // Text QR uses <textarea id="qr-text">
    textInput?.addEventListener("input", scheduleUpdate);

    // Frame color change affects final composition
    frameColor?.addEventListener("input", composeFrame);

    // If page defines getQRInputData() → auto-bind all controls
    if (typeof window.getQRInputData === "function") {
        document.querySelectorAll("input,select,textarea")
            .forEach(el => el.addEventListener("input", scheduleUpdate));
    }

    // -------------------------------------------------------------
    // Main QR Generation Logic
    // -------------------------------------------------------------
    async function updateQR() {
        let dataPayload = null;

        if (type === "text") {
            const txt = textInput?.value.trim();
            if (!txt) {
                preview.innerHTML = `<p class="muted">Your QR will appear here</p>`;
                currentSvg = null;
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
                currentSvg = null;
                enableButtons(false);
                return;
            }
        }

        const payload = {
            type,
            data: dataPayload,
            settings: {
                color: frameColor?.value || "#000000",
                size: 512
            }
        };

        try {
            const res = await fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const result = await res.json();
            if (!result.success) throw new Error("API returned error");

            currentSvg = result.image;

            if (currentFrame === "none") {
                preview.innerHTML = `<img src="${currentSvg}" class="qr-big">`;
                currentComposited = currentSvg;
                enableButtons(true);
            } else {
                await composeFrame();
            }
        } catch (err) {
            console.error(err);
            preview.innerHTML = `<p style="color:red;">Error generating QR.</p>`;
            enableButtons(false);
        }
    }

    // -------------------------------------------------------------
    // Enable / Disable Action Buttons
    // -------------------------------------------------------------
    function enableButtons(v) {
        if (downloadBtn) downloadBtn.disabled = !v;
        if (shareBtn) shareBtn.disabled = !v;
    }

    // -------------------------------------------------------------
    // Compose QR + Frame (SVG injection)
    // -------------------------------------------------------------
    async function composeFrame() {
        if (!currentSvg) return;

        if (currentFrame === "none") {
            preview.innerHTML = `<img src="${currentSvg}" class="qr-big">`;
            currentComposited = currentSvg;
            enableButtons(true);
            return;
        }

        try {
            const framePath = `/static/images/frames/${currentFrame}.svg`;
            const resp = await fetch(framePath);
            let svg = await resp.text();

            const zone = svg.match(/<rect[^>]*id="QR_ZONE"[^>]*>/i);
            if (!zone) throw new Error("QR_ZONE not found in frame");

            const tag = zone[0];
            const get = (key) => {
                const match = tag.match(new RegExp(`${key}="([^"]+)"`));
                return match ? parseFloat(match[1]) : 0;
            };

            const x = get("x");
            const y = get("y");
            const w = get("width");
            const h = get("height");

            const frameColorValue = frameColor?.value || "#000";

            svg = svg.replace(/fill="#000000"/g, `fill="${frameColorValue}"`);
            svg = svg.replace(/stroke="#000000"/g, `stroke="${frameColorValue}"`);
            svg = svg.replace(/<g[^>]*id="qr-placeholder-index"[\s\S]*?<\/g>/i, "");

            const imgTag = `<image x="${x}" y="${y}" width="${w}" height="${h}" href="${currentSvg}" />`;
            svg = svg.replace(/<\/svg>\s*$/i, `${imgTag}</svg>`);

            preview.innerHTML = svg;

            currentComposited = await svgToPng(svg);
            enableButtons(true);

        } catch (err) {
            console.error("Frame composition error:", err);
            preview.innerHTML = `<img src="${currentSvg}" class="qr-big">`;
            currentComposited = currentSvg;
            enableButtons(true);
        }
    }

    // -------------------------------------------------------------
    // Convert SVG → PNG (for download/share)
    // -------------------------------------------------------------
    async function svgToPng(svgText) {
        const blob = new Blob([svgText], { type: "image/svg+xml" });
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

    // -------------------------------------------------------------
    // Download
    // -------------------------------------------------------------
    downloadBtn?.addEventListener("click", async () => {
        const rawSvg = preview.innerHTML;
        const format = formatSelect.value;

        if (format === "svg") {
            const blob = new Blob([rawSvg], { type: "image/svg+xml" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "qrwaver.svg";
            a.click();
            URL.revokeObjectURL(url);
            return;
        }

        const TARGET = 2400;
        const svgBlob = new Blob([rawSvg], { type: "image/svg+xml" });
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

    // -------------------------------------------------------------
    // Share
    // -------------------------------------------------------------
    shareBtn?.addEventListener("click", async () => {
        if (!currentComposited) return;

        const format = formatSelect.value;
        if (format === "svg") {
            alert("Sharing SVG is not widely supported.");
            return;
        }

        const dataUri = currentComposited;
        const blob = await (await fetch(dataUri)).blob();

        const file = new File([blob], `qrwaver.${format}`, { type: blob.type });

        if (navigator.share && navigator.canShare?.({ files: [file] })) {
            await navigator.share({ title: "QR Code", files: [file] });
        } else {
            alert("Sharing not supported on this device.");
        }
    });

    // INITIAL LOAD
    updateQR();
}
