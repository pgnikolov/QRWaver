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
function initQRGenerator(type = "text") {
  const textInput   = document.getElementById("qr-text");
  const colorInput  = document.getElementById("qr-color");
  const sizeSelect  = document.getElementById("qr-size");
  const preview     = document.getElementById("qr-preview");
  const downloadBtn = document.getElementById("downloadBtn");
  const shareBtn    = document.getElementById("shareBtn");

  const frameThumbs = document.getElementById("frame-thumbs");
  const frameColor  = document.getElementById("frame-color");

  let currentImageDataUri = null;
  let currentComposited   = null;
  let currentFrame        = "none";
  let debounce            = null;

  if (!textInput || !preview) {
    console.warn("Missing expected elements for QR generator");
    return;
  }

  // Frame picker
  if (frameThumbs) {
    frameThumbs.addEventListener("click", (e) => {
      const btn = e.target.closest("button.thumb");
      if (!btn) return;

      [...frameThumbs.querySelectorAll(".thumb")].forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");

      currentFrame = btn.dataset.frame || "none";
      frameThumbs.dataset.selected = currentFrame;
      composeIfNeeded();
    });
  }

  // Re-generate QR when input changes
  function scheduleUpdate() {
    clearTimeout(debounce);
    debounce = setTimeout(updateQR, 250);
  }

  textInput?.addEventListener("input", scheduleUpdate);
  colorInput?.addEventListener("input", scheduleUpdate);
  sizeSelect?.addEventListener("change", scheduleUpdate);

  // Frame color change only recomposes
  frameColor?.addEventListener("input", composeIfNeeded);

  async function updateQR() {
    const txt = (textInput.value || "").trim();

    if (!txt) {
      preview.innerHTML = `<p class="muted">Your QR will appear here</p>`;
      currentImageDataUri = null;
      toggleButtons(false);
      return;
    }

    const payload = {
      type,
      data: txt,
      settings: {
        color: colorInput ? colorInput.value : "#2563EB",
        size: sizeSelect ? parseInt(sizeSelect.value, 10) : 512
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

      currentImageDataUri = result.image;

      if (currentFrame === "none") {
        preview.innerHTML = `<img src="${currentImageDataUri}" class="qr-big">`;
        currentComposited = currentImageDataUri;
        toggleButtons(true);
      } else {
        await composeIfNeeded();
      }

    } catch (err) {
      console.error(err);
      preview.innerHTML = `<p style="color:red;">Error generating QR.</p>`;
      toggleButtons(false);
    }
  }

  function toggleButtons(enable) {
    [downloadBtn, shareBtn].forEach((btn) => {
      if (!btn) return;
      btn.disabled = !enable;
    });
  }

  // ✅ Compose frame (SVG overlay)
  async function composeIfNeeded() {
    if (!currentImageDataUri) return;

    if (currentFrame === "none") {
      preview.innerHTML = `<img src="${currentImageDataUri}" class="qr-big">`;
      currentComposited = currentImageDataUri;
      toggleButtons(true);
      return;
    }

    const framePath = `/static/images/frames/${currentFrame}.svg`;
    let svgText = "";

    try {
      const resp = await fetch(framePath);
      svgText = await resp.text();
    } catch {
      preview.innerHTML = `<img src="${currentImageDataUri}" class="qr-big">`;
      currentComposited = currentImageDataUri;
      return;
    }

    try {
      // ✅ QR ZONE detection using id="QR_ZONE"
      const zone = svgText.match(/<rect[^>]*id="QR_ZONE"[^>]*>/i);
      if (!zone) throw new Error("QR_ZONE not found");

      const rectTag = zone[0];

      const getNum = (name) => {
        const m = rectTag.match(new RegExp(`${name}="([^"]+)"`));
        return m ? parseFloat(m[1]) : 0;
      };

      const rx = getNum("x");
      const ry = getNum("y");
      const rw = getNum("width");
      const rh = getNum("height");

      // Remove placeholder QR group
      svgText = svgText.replace(/<g[^>]*id="qr-placeholder-index"[\s\S]*?<\/g>/i, "");

      // Apply frame color
      const col = frameColor ? frameColor.value : "#000000";
      svgText = svgText.replace(/stroke="#000000"/g, `stroke="${col}"`);
      svgText = svgText.replace(/fill="#000000"/g, `fill="${col}"`);

      // Insert QR image inside QR_ZONE
      const imgTag = `<image x="${rx}" y="${ry}" width="${rw}" height="${rh}" href="${currentImageDataUri}" />`;
      svgText = svgText.replace(/<\/svg>\s*$/i, `${imgTag}</svg>`);

      // Render in preview
      preview.innerHTML = svgText;

      // Convert SVG to PNG
      currentComposited = await svgToPngDataUrl(svgText);
      toggleButtons(true);

    } catch (err) {
      console.error(err);
      preview.innerHTML = `<img src="${currentImageDataUri}" class="qr-big">`;
      currentComposited = currentImageDataUri;
      toggleButtons(true);
    }
  }

  async function svgToPngDataUrl(svgString) {
    const blob = new Blob([svgString], { type: "image/svg+xml" });
    const url  = URL.createObjectURL(blob);
    const img  = new Image();
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

  // Download
  downloadBtn?.addEventListener("click", () => {
    const data = currentComposited || currentImageDataUri;
    if (!data) return;

    const a = document.createElement("a");
    a.href = data;
    a.download = `qrwaver_${type}.png`;
    a.click();
  });

  // Share
  shareBtn?.addEventListener("click", async () => {
    const data = currentComposited || currentImageDataUri;
    if (!data) return;

    const blob = await (await fetch(data)).blob();
    const file = new File([blob], "qr.png", { type: "image/png" });

    if (navigator.share && navigator.canShare?.({ files: [file] })) {
      await navigator.share({ files: [file], title: "QR Code" });
    } else {
      alert("Sharing not supported.");
    }
  });

  scheduleUpdate();
}
