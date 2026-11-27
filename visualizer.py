"""Shared bottom-of-screen Web Audio frequency visualizer bridge.
Injected into dynamic synth players (Sonic Deck & Scroll Synth) so that when
dynamic audio plays, live spectrum bars and modulation readouts render across
the bottom of the parent viewport."""

VIZ_BRIDGE_JS = r"""
    const vizState = { analyser: null, data: null, raf: 0, active: false, left: "", right: "" };

    function ensureParentVisualizer(audioCtx, sourceNode) {
        try {
            const pDoc = window.parent.document;
            if (!pDoc || !pDoc.body) return;
            let wrap = pDoc.getElementById("formica-bottom-viz");
            if (!wrap) {
                wrap = pDoc.createElement("div");
                wrap.id = "formica-bottom-viz";
                wrap.style.cssText = [
                    "position:fixed", "left:0", "right:0", "bottom:0", "height:86px",
                    "pointer-events:none", "z-index:90", "opacity:0",
                    "transition:opacity .25s ease",
                    "background:linear-gradient(180deg, transparent 0%, rgba(11,14,20,0.82) 38%, rgba(11,14,20,0.96) 100%)"
                ].join(";");
                wrap.innerHTML =
                    '<div id="formica-viz-hud" style="display:flex;justify-content:space-between;align-items:center;padding:2px 18px;font:700 9px \'Space Mono\',monospace;letter-spacing:.12em;color:#00f5ff;text-shadow:0 0 6px rgba(0,245,255,0.45);">' +
                    '<span id="formica-viz-left">⚡ DYNAMIC AUDIO // SPECTRUM</span>' +
                    '<span id="formica-viz-right" style="color:#ffe600;">STANDBY</span>' +
                    '</div>' +
                    '<canvas id="formica-viz-canvas" style="width:100%;height:64px;display:block;"></canvas>';
                pDoc.body.appendChild(wrap);
            }
            if (audioCtx && sourceNode && !vizState.analyser) {
                const analyser = audioCtx.createAnalyser();
                analyser.fftSize = 128;
                analyser.smoothingTimeConstant = 0.78;
                sourceNode.connect(analyser);
                vizState.analyser = analyser;
                vizState.data = new Uint8Array(analyser.frequencyBinCount);
            }
            if (!vizState.raf) {
                const peaks = new Float32Array(64);
                const draw = () => {
                    vizState.raf = window.requestAnimationFrame(draw);
                    const el = pDoc.getElementById("formica-bottom-viz");
                    const canvas = pDoc.getElementById("formica-viz-canvas");
                    if (!el || !canvas) return;
                    el.style.opacity = vizState.active ? "1" : "0";
                    if (!vizState.active || !vizState.analyser) return;

                    const dpr = window.parent.devicePixelRatio || 1;
                    const w = canvas.clientWidth;
                    const h = canvas.clientHeight;
                    if (w <= 0 || h <= 0) return;
                    if (canvas.width !== Math.floor(w * dpr) || canvas.height !== Math.floor(h * dpr)) {
                        canvas.width = Math.floor(w * dpr);
                        canvas.height = Math.floor(h * dpr);
                    }
                    const c2d = canvas.getContext("2d");
                    c2d.setTransform(dpr, 0, 0, dpr, 0, 0);
                    c2d.clearRect(0, 0, w, h);

                    vizState.analyser.getByteFrequencyData(vizState.data);
                    const bars = 64;
                    const gap = 3;
                    const barW = Math.max(2, (w - gap * (bars - 1)) / bars);

                    for (let i = 0; i < bars; i++) {
                        const bin = Math.min(vizState.data.length - 1, Math.floor(i * vizState.data.length / bars));
                        const norm = vizState.data[bin] / 255;
                        const bh = Math.max(2, norm * (h - 8));
                        const x = i * (barW + gap);
                        const y = h - bh;

                        if (norm > peaks[i]) peaks[i] = norm;
                        else peaks[i] = Math.max(0, peaks[i] - 0.014);

                        const grad = c2d.createLinearGradient(0, h, 0, y);
                        grad.addColorStop(0, "rgba(0, 245, 255, 0.78)");
                        grad.addColorStop(0.55, "rgba(255, 230, 0, 0.9)");
                        grad.addColorStop(1, "rgba(255, 0, 127, 0.98)");
                        c2d.fillStyle = grad;
                        c2d.fillRect(x, y, barW, bh);

                        const peakY = h - Math.max(3, peaks[i] * (h - 8)) - 2;
                        c2d.fillStyle = peaks[i] > 0.68 ? "#ff007f" : "#ffe600";
                        c2d.fillRect(x, peakY, barW, 2);
                    }
                };
                draw();
            }
        } catch (e) {}
    }

    function updateParentVisualizer(isActive, leftText, rightText) {
        vizState.active = Boolean(isActive);
        try {
            const pDoc = window.parent.document;
            const l = pDoc.getElementById("formica-viz-left");
            const r = pDoc.getElementById("formica-viz-right");
            if (l && leftText) l.textContent = leftText;
            if (r && rightText) r.textContent = rightText;
            const el = pDoc.getElementById("formica-bottom-viz");
            if (el) el.style.opacity = vizState.active ? "1" : "0";
            const cat = pDoc.querySelector(".sleepy-cat-corner");
            if (cat) cat.style.bottom = vizState.active ? "96px" : "24px";
        } catch (e) {}
    }
"""
