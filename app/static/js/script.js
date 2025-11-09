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
  const frameText   = document.getElementById("frame-text");
  const frameColor  = document.getElementById("frame-color");
  const frameFont   = document.getElementById("frame-font");

  let currentImageDataUri = null;     // plain QR PNG
  let currentComposited   = null;     // composited (with frame) data URL
  let currentFrame        = "none";
  let debounce            = null;

  if (!textInput || !preview) {
    console.warn("Missing expected elements for QR generator");
    return;
  }

  // Frame picker click handling
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

  // When text/Color/Size changes → regenerate QR
  function scheduleUpdate() {
    clearTimeout(debounce);
    debounce = setTimeout(updateQR, 250);
  }

  if (textInput)  textInput.addEventListener("input", scheduleUpdate);
  if (colorInput) colorInput.addEventListener("input", scheduleUpdate);
  if (sizeSelect) sizeSelect.addEventListener("change", scheduleUpdate);

  // Frame text/color/font changes → re-compose (no server call)
  [frameText, frameColor, frameFont].forEach(el => {
    if (!el) return;
    el.addEventListener("input", () => composeIfNeeded());
    el.addEventListener("change", () => composeIfNeeded());
  });

  async function updateQR() {
    const txt = (textInput.value || "").trim();
    if (!txt) {
      preview.innerHTML = `<p class="muted">Your QR will appear here</p>`;
      currentImageDataUri = null;
      currentComposited = null;
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
      if (!result.success) throw new Error("API returned error");

      currentImageDataUri = result.image;
      // If no frame → show raw PNG; else → compose
      if (currentFrame === "none") {
        preview.innerHTML = `<img src="${currentImageDataUri}" alt="QR" style="max-width:100%;height:auto">`;
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
      if (enable) btn.classList.add("enabled");
      else btn.classList.remove("enabled");
    });
  }

  async function composeIfNeeded() {
    if (!currentImageDataUri) return;

    if (currentFrame === "none") {
      preview.innerHTML = `<img src="${currentImageDataUri}" alt="QR" style="max-width:100%;height:auto">`;
      currentComposited = currentImageDataUri;
      toggleButtons(true);
      return;
    }

    // load frame SVG text
    const framePath = `/static/images/frames/${currentFrame}.svg`;
    let svgText = "";
    try {
      const resp = await fetch(framePath);
      svgText = await resp.text();
    } catch (e) {
      console.error("Failed to load frame SVG:", e);
      preview.innerHTML = `<img src="${currentImageDataUri}" alt="QR" style="max-width:100%;height:auto">`;
      currentComposited = currentImageDataUri;
      toggleButtons(true);
      return;
    }

    try {
      // 1) find white rect (QR area): x, y, width, height
      // The rect is the first with fill="#FFFFFF"
      const rectMatch = svgText.match(/<rect[^>]*fill="#FFFFFF"[^>]*>/i);
      if (!rectMatch) throw new Error("No white rect found in frame");

      const rectTag = rectMatch[0];
      const getNum = (name) => {
        const m = rectTag.match(new RegExp(`${name}\\s*=\\s*"(.*?)"`));
        return m ? parseFloat(m[1]) : 0;
        };
      const rx = getNum("x");
      const ry = getNum("y");
      const rw = getNum("width");
      const rh = getNum("height");

      // 2) Remove the placeholder group if present
      svgText = svgText.replace(/<g[^>]*id="qr-placeholder-index"[\s\S]*?<\/g>/i, "");

      // 3) Replace SCAN ME text (content + color + font)
      const txtVal   = (frameText && frameText.value) || "SCAN ME";
      const colorVal = (frameColor && frameColor.value) || "#FFFFFF";
      const fontVal  = (frameFont && frameFont.value) || "Arial, sans-serif";

      // change text content inside <text ...><tspan>...</tspan></text>
      svgText = svgText
        // fill on <text ... fill="...">
        .replace(/(<text[^>]*?)fill="[^"]*"/i, `$1 fill="${colorVal}"`)
        // or if <text> has no fill attribute, add it
        .replace(/<text([^>]*?)>/i, (m, attrs) => {
          return /fill="/i.test(attrs) ? `<text${attrs}>` : `<text${attrs} fill="${colorVal}">`;
        })
        // set font-family
        .replace(/(<text[^>]*?)font-family="[^"]*"/i, `$1 font-family="${fontVal}"`)
        .replace(/<tspan[^>]*>[\s\S]*?<\/tspan>/i, `<tspan>${escapeHtml(txtVal)}</tspan>`);

      // 4) Inject the QR image <image> into the rect area
      const imgTag = `<image x="${rx}" y="${ry}" width="${rw}" height="${rh}" href="${currentImageDataUri}" preserveAspectRatio="xMidYMid slice" />`;

      // Insert just before closing </svg>
      svgText = svgText.replace(/<\/svg>\s*$/i, `${imgTag}\n</svg>`);

      // 5) Render inline
      preview.innerHTML = svgText;
      // For download/share we’ll rasterize the SVG to PNG via a canvas
      currentComposited = await svgToPngDataUrl(svgText);
      toggleButtons(true);
    } catch (e) {
      console.error("Compose failed:", e);
      // fallback to raw QR
      preview.innerHTML = `<img src="${currentImageDataUri}" alt="QR" style="max-width:100%;height:auto">`;
      currentComposited = currentImageDataUri;
      toggleButtons(true);
    }
  }

  function escapeHtml(s){ return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

  async function svgToPngDataUrl(svgString) {
    const blob = new Blob([svgString], { type: "image/svg+xml" });
    const url  = URL.createObjectURL(blob);
    const img  = new Image();
    img.decoding = "async";
    img.src = url;
    await img.decode();

    // canvas sized to the SVG viewBox or image size
    const tmp = document.createElement("div");
    tmp.innerHTML = svgString;
    const svgEl = tmp.querySelector("svg");
    const vb = svgEl && svgEl.getAttribute("viewBox");
    let w = 1000, h = 1000;
    if (vb){
      const parts = vb.split(/\s+/).map(Number);
      if (parts.length === 4){ w = parts[2]; h = parts[3]; }
    }

    const canvas = document.createElement("canvas");
    canvas.width = Math.round(w);
    canvas.height = Math.round(h);
    const ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    URL.revokeObjectURL(url);
    return canvas.toDataURL("image/png");
  }

  // Download / Share use the composited data
  if (downloadBtn) {
    downloadBtn.addEventListener("click", () => {
      const data = currentComposited || currentImageDataUri;
      if (!data) return;
      const a = document.createElement("a");
      a.href = data;
      a.download = `qrwaver_${type}.png`;
      a.click();
    });
  }

  if (shareBtn) {
    shareBtn.addEventListener("click", async () => {
      const data = currentComposited || currentImageDataUri;
      if (!data) return;
      try {
        const blob = await (await fetch(data)).blob();
        const file = new File([blob], `qrwaver_${type}.png`, { type: "image/png" });
        if (navigator.share && navigator.canShare?.({ files: [file] })) {
          await navigator.share({ title: "My QR Code", text: "Made with QRWaver", files: [file] });
        } else {
          alert("Sharing not supported on this device.");
        }
      } catch (e) { console.error(e); }
    });
  }

  // initial
  scheduleUpdate();
}
