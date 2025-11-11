// Subtle hover ripple for CTA (cosmetic)
document.addEventListener('click', e => {
  const t = e.target.closest('.btn-primary');
  if(!t) return;
  t.style.transform = 'translateY(1px) scale(.995)';
  setTimeout(()=> (t.style.transform=''), 90);
});

/**
 * Universal QR Generator with SVG overlay frames
 */
// -----------------------------------------
// QRWaver — Clean Professional Frontend JS
// -----------------------------------------

function initQRGenerator(type = "text") {
    const textInput    = document.getElementById("qr-text");
    const colorInput   = document.getElementById("qr-color");
    const frameThumbs  = document.getElementById("frame-thumbs");
    const frameColor   = document.getElementById("frame-color");
    const preview      = document.getElementById("qr-preview");
    const formatSelect = document.getElementById("qr-format");

    const downloadBtn  = document.getElementById("downloadBtn");
    const shareBtn     = document.getElementById("shareBtn");

    let currentSvg        = null;   // чистия QR (SVG)
    let currentComposited = null;   // SVG + frame -> PNG
    let currentFrame      = "none";
    let debounceTimer     = null;

    if (!textInput || !preview) {
        console.warn("Missing main QR elements");
        return;
    }

    //------------------------------------------
    // Frame selection UI
    //------------------------------------------
    if (frameThumbs) {
        frameThumbs.addEventListener("click", (e) => {
            const btn = e.target.closest("button.thumb");
            if (!btn) return;

            [...frameThumbs.querySelectorAll(".thumb")].forEach(b => b.classList.remove("selected"));
            btn.classList.add("selected");

            currentFrame = btn.dataset.frame || "none";
            composeFrame();
        });
    }

    //------------------------------------------
    // Live updates
    //------------------------------------------
    function scheduleUpdate() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(updateQR, 250);
    }

    textInput?.addEventListener("input", scheduleUpdate);
    colorInput?.addEventListener("input", scheduleUpdate);
    frameColor?.addEventListener("input", composeFrame);

    //------------------------------------------
    // Generate fresh SVG QR
    //------------------------------------------
    async function updateQR() {
        const txt = (textInput.value || "").trim();

        if (!txt) {
            preview.innerHTML = `<p class="muted">Your QR will appear here</p>`;
            currentSvg = null;
            currentComposited = null;
            enableButtons(false);
            return;
        }

        const payload = {
            type,
            data: txt,
            settings: {
                color: colorInput?.value || "#000000",
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
            if (!result.success) throw new Error("API error");

            // -> това е SVG в base64 data-uri
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

    //------------------------------------------
    function enableButtons(v) {
        [downloadBtn, shareBtn].forEach(btn => btn && (btn.disabled = !v));
    }

    //------------------------------------------
    // Insert QR into SVG frame (overlay)
    //------------------------------------------
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

            // Find QR_ZONE
            const zone = svg.match(/<rect[^>]*id="QR_ZONE"[^>]*>/i);
            if (!zone) throw new Error("QR_ZONE not found");

            const tag = zone[0];

            const get = (k) => {
                const m = tag.match(new RegExp(`${k}="([^"]+)"`));
                return m ? parseFloat(m[1]) : 0;
            };

            const x = get("x");
            const y = get("y");
            const w = get("width");
            const h = get("height");

            const color = frameColor?.value || "#000";

            svg = svg.replace(/fill="#000000"/g, `fill="${color}"`);
            svg = svg.replace(/stroke="#000000"/g, `stroke="${color}"`);
            svg = svg.replace(/<g[^>]*id="qr-placeholder-index"[\s\S]*?<\/g>/i, "");

            // Insert QR image in SVG
            const imgTag = `<image x="${x}" y="${y}" width="${w}" height="${h}" href="${currentSvg}" />`;
            svg = svg.replace(/<\/svg>\s*$/i, `${imgTag}</svg>`);

            preview.innerHTML = svg;

            currentComposited = await svgToPng(svg);
            enableButtons(true);

        } catch (err) {
            console.error("Frame error:", err);
            preview.innerHTML = `<img src="${currentSvg}" class="qr-big">`;
            currentComposited = currentSvg;
            enableButtons(true);
        }
    }

    //------------------------------------------
    // Convert full SVG to PNG for preview + export
    //------------------------------------------
    async function svgToPng(svgText) {
        const blob = new Blob([svgText], { type: "image/svg+xml" });
        const url  = URL.createObjectURL(blob);

        const img = new Image();
        img.src = url;
        await img.decode();

        const canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);

        URL.revokeObjectURL(url);
        return canvas.toDataURL("image/png");
    }

    //------------------------------------------
    // DOWNLOAD
    //------------------------------------------
downloadBtn?.addEventListener("click", async () => {
    const format = formatSelect.value;
    const rawSvg = preview.innerHTML;

    // SVG директно
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

    // PNG / JPEG — рендърваме SVG директно в голяма резолюция (НЕ през малък PNG)
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

    // ВАЖНО — за остри ръбове
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

    //------------------------------------------
    // SHARE
    //------------------------------------------
    shareBtn?.addEventListener("click", async () => {
        if (!currentComposited) return;

        const format = formatSelect.value;
        if (format === "svg") {
            alert("Sharing SVG not supported on most devices.");
            return;
        }

        const dataUri = currentComposited;
        const blob = await (await fetch(dataUri)).blob();

        const file = new File([blob], `qrwaver.${format}`, { type: blob.type });

        if (navigator.share && navigator.canShare?.({ files: [file] })) {
            await navigator.share({ files: [file], title: "QR Code" });
        } else {
            alert("Sharing not supported.");
        }
    });

    //------------------------------------------
    updateQR();
}
