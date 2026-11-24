"""Early prototype dynamic music player (raw unthrottled scroll-to-tempo & meter Web Audio synth).
Serves as interactive evidence of early prototyping: raw scroll/wheel/layout-shift and UI interaction events
directly jump BPM and time signature without damping or bar-quantization."""
import json

TEMPLATE = r"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Space+Mono:wght@400;700&display=swap');
* { box-sizing: border-box; }
body {
    margin: 0;
    background: transparent;
    color: #f0f2f5;
    font-family: 'Space Mono', monospace;
}
.dev {
    background: #131722;
    border: 2px solid #ff007f;
    padding: 12px;
    clip-path: polygon(0 0, calc(100% - 26px) 0, 100% 26px, 100% 100%, 26px 100%, 0 calc(100% - 26px));
    position: relative;
    box-shadow: 4px 4px 0 #ffe600;
}
.dev::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 5;
    background: repeating-linear-gradient(0deg, transparent 0 2px, rgba(0, 0, 0, .24) 2px 3px);
}
.hz {
    height: 8px;
    background: repeating-linear-gradient(135deg, #ff007f 0 8px, #0b0e14 8px 16px);
    margin-bottom: 10px;
}
.top {
    display: flex;
    justify-content: space-between;
    font-size: 9px;
    letter-spacing: .16em;
    color: #8c95ad;
    margin-bottom: 8px;
}
.badge-proto {
    color: #ff007f;
    font-weight: 700;
}
.on .badge-proto {
    animation: bl 0.8s steps(2) infinite;
}
@keyframes bl { 50% { opacity: .25; } }

.lcd {
    background: #0b0e14;
    border: 2px solid #ff007f;
    padding: 10px;
    margin-bottom: 10px;
}
.bpm-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 8px;
}
.k {
    font-size: 9px;
    letter-spacing: .16em;
    color: #8c95ad;
}
.bpm-val {
    font: 400 40px/.95 Anton, sans-serif;
    color: #ffe600;
    text-shadow: 2px 0 #ff007f, -2px 0 #00f5ff;
}
.bpm-val.spike {
    color: #ff007f;
    text-shadow: 2px 0 #ffe600;
}
.bpm-unit {
    font-size: 11px;
    color: #00f5ff;
    margin-left: 4px;
}
.meta-col {
    text-align: right;
    font-size: 10px;
    line-height: 1.6;
    color: #b9c3d8;
}
.meta-col b { color: #00f5ff; }
.meta-col .warn { color: #ff6600; }

.scope-wrap {
    margin-top: 8px;
    border-top: 1px solid #2e364f;
    padding-top: 8px;
}
.scope-head {
    display: flex;
    justify-content: space-between;
    font-size: 9px;
    color: #8c95ad;
    margin-bottom: 4px;
}
canvas {
    width: 100%;
    height: 74px;
    display: block;
    background: #07090e;
    border: 1px solid #2e364f;
}

.panel {
    background: #1b2030;
    border: 1px solid #2e364f;
    padding: 10px;
    margin-bottom: 10px;
}
.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}
.stat-box {
    background: #0b0e14;
    border: 1px solid #2e364f;
    padding: 6px 8px;
}
.stat-box .v {
    font-size: 12px;
    font-weight: 700;
    color: #ffe600;
    margin-top: 2px;
}

.vol {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-top: 8px;
}
.vol input {
    flex: 1;
    accent-color: #ff007f;
}

.btns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 10px;
}
button {
    font: 400 15px Anton, sans-serif;
    letter-spacing: .08em;
    background: #0b0e14;
    color: #ffe600;
    border: 2px solid #ffe600;
    padding: 9px 8px;
    cursor: pointer;
    transform: skewX(-6deg);
}
button:hover, button[aria-pressed="true"] {
    background: #ffe600;
    color: #0b0e14;
}
button.alt {
    border-color: #00f5ff;
    color: #00f5ff;
}
button.alt:hover, button.alt[aria-pressed="true"] {
    background: #00f5ff;
    color: #0b0e14;
}
button.warn-btn {
    border-color: #ff6600;
    color: #ff6600;
    font-size: 13px;
}
button.warn-btn:hover {
    background: #ff6600;
    color: #0b0e14;
}
button.full {
    grid-column: 1 / -1;
}

.log-box {
    background: #0b0e14;
    border: 1px solid #2e364f;
    padding: 8px;
    font-size: 9px;
    line-height: 1.55;
    color: #8c95ad;
    max-height: 112px;
    overflow-y: auto;
}
.log-box div {
    border-bottom: 1px dashed #1b2030;
    padding: 2px 0;
}
.log-box .ev-spike { color: #ff007f; }
.log-box .ev-shift { color: #ff6600; }
.log-box .ev-info { color: #00f5ff; }

.note {
    font-size: 9px;
    color: #8c95ad;
    letter-spacing: .06em;
    line-height: 1.5;
    margin-top: 8px;
}
@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; }
}
</style>
</head>
<body>
<div class="dev" id="dev">
  <div class="hz"></div>
  <div class="top">
    <span>PROTO v0.1 // RAW SCROLL SYNTH</span>
    <span class="badge-proto" id="status-tag">&#9679; IDLE</span>
  </div>

  <div class="lcd">
    <div class="bpm-row">
      <div>
        <div class="k">UNSMOOTHED TEMPO &amp; METER</div>
        <div class="bpm-val" id="bpm">064<span class="bpm-unit">BPM</span></div>
      </div>
      <div class="meta-col">
        <div>METER <b id="meter-lbl">3/4 · 1/6</b></div>
        <div>RAW VEL <b id="vel-lbl">0 px/s</b></div>
        <div>SHIFTS <b class="warn" id="shift-lbl">0</b> · ACT <b id="interact-lbl">0</b></div>
      </div>
    </div>
    <div class="scope-wrap">
      <div class="scope-head">
        <span>RAW BPM TRACE (UNQUANTIZED METER JUMPS)</span>
        <span id="delta-lbl">ΔBPM: +0</span>
      </div>
      <canvas id="scope" width="320" height="74"></canvas>
    </div>
  </div>

  <div class="panel">
    <div class="stat-grid">
      <div class="stat-box">
        <div class="k">FEED SOURCE</div>
        <div class="v" id="feed-src">--</div>
      </div>
      <div class="stat-box">
        <div class="k">SVG FALLBACK ART</div>
        <div class="v" id="svg-stat">--</div>
      </div>
      <div class="stat-box">
        <div class="k">SCROLL + SELECT*</div>
        <div class="v" id="sensor-stat">LINKED</div>
      </div>
      <div class="stat-box">
        <div class="k">ACTIVE VIEW</div>
        <div class="v" id="view-stat" style="color:#00f5ff">FEED</div>
      </div>
    </div>
    <div class="vol">
      <span class="k">VOL</span>
      <input id="vol" type="range" min="0" max="100" value="60" aria-label="Prototype synth volume">
    </div>
  </div>

  <div class="btns">
    <button id="power" class="full" type="button">&#9654; START RAW SCROLL AUDIO</button>
    <button id="autoscroll" class="alt" type="button" aria-pressed="false">&#8693; AUTO-SCROLL TEST</button>
    <button id="simshift" class="warn-btn" type="button">&#9889; SIMULATE RSS SHIFT</button>
  </div>

  <div class="k" style="margin-bottom:4px">EVENT LOG</div>
  <div class="log-box" id="log"></div>

  <div class="note">
    EARLY PROTOTYPE: Unthrottled scroll, SELECT* view switches, and RSS layout shifts snap both BPM (64-185) and time signature (3/4 &rarr; 4/4 &rarr; 5/4 &rarr; 7/8) mid-bar.
  </div>
</div>

<script>
(() => {
    const D = __DATA__;
    const $ = id => document.getElementById(id);

    $("feed-src").textContent = D.live ? ("LIVE " + D.source) : "PLACEHOLDER";
    $("svg-stat").textContent = D.svgCount + " / " + D.totalPosts + " CARDS";

    // Musical chords (A minor / C major palette)
    const PROGRESSION = [
        { name: "Am9", pad: [110, 164.81, 246.94, 261.63], bass: 55, arp: [220, 261.63, 329.63, 392, 493.88] },
        { name: "Fmaj9", pad: [87.31, 164.81, 220, 261.63], bass: 87.31, arp: [174.61, 220, 261.63, 329.63, 392] },
        { name: "Dm9", pad: [146.83, 174.61, 220, 329.63], bass: 73.42, arp: [146.83, 220, 261.63, 329.63, 440] },
        { name: "G6", pad: [98.0, 164.81, 246.94, 293.66], bass: 98.0, arp: [196.0, 246.94, 293.66, 392, 493.88] }
    ];

    // Time signature patterns in eighth-note steps
    const METERS = {
        "3/4": { steps: 6, kicks: [0], snares: [2, 4], hats: [0, 1, 2, 3, 4, 5], accent: [0] },
        "4/4": { steps: 8, kicks: [0, 4], snares: [2, 6], hats: [0, 1, 2, 3, 4, 5, 6, 7], accent: [0, 4] },
        "6/8": { steps: 6, kicks: [0], snares: [3], hats: [0, 1, 2, 3, 4, 5], accent: [0, 3] },
        "5/4": { steps: 10, kicks: [0, 6], snares: [3, 8], hats: [0, 2, 3, 5, 6, 8, 9], accent: [0, 3, 6] },
        "7/8": { steps: 7, kicks: [0, 4], snares: [2, 5], hats: [0, 1, 2, 3, 4, 5, 6], accent: [0, 2, 4] }
    };

    const MIN_BPM = 64;
    const MAX_BPM = 185;
    let ctx = null;
    let master = null;
    let padOscs = [];
    let padFilter = null;
    let running = false;
    let rawBpm = MIN_BPM;
    let prevBpm = MIN_BPM;
    let rawVelocity = 0;
    let currentMeter = "3/4";
    let activeView = "FEED";
    let lastEventAt = performance.now();
    let nextStepAt = 0;
    let stepInBar = 0;
    let barCount = 0;
    let heightShifts = 0;
    let interactions = 0;
    let autoScrolling = false;
    let autoDir = 1;
    let feedEl = null;
    let lastScrollTop = 0;
    let lastScrollHeight = 0;
    let resizeObs = null;
    let mutObs = null;
    let warnedUnlock = false;
    let lastKeySoundAt = 0;
    const history = new Array(64).fill(MIN_BPM);

    function addLog(text, cls) {
        const box = $("log");
        const row = document.createElement("div");
        if (cls) row.className = cls;
        const ts = new Date().toLocaleTimeString([], { hour12: false, minute: "2-digit", second: "2-digit" });
        row.textContent = "[" + ts + "] " + text;
        box.prepend(row);
        while (box.children.length > 25) box.removeChild(box.lastChild);
    }

    function initAudio() {
        if (ctx) return;
        let AC = null;
        try { AC = window.parent.AudioContext || window.parent.webkitAudioContext; } catch (e) {}
        AC = AC || window.AudioContext || window.webkitAudioContext;
        if (!AC) {
            addLog("Web Audio API unsupported in this browser.", "ev-shift");
            return;
        }
        ctx = new AC();
        master = ctx.createGain();
        master.gain.value = ($("vol").value / 100) * 0.30;
        master.connect(ctx.destination);

        padFilter = ctx.createBiquadFilter();
        padFilter.type = "lowpass";
        padFilter.frequency.value = 650;
        padFilter.connect(master);

        PROGRESSION[0].pad.forEach((freq, i) => {
            const osc = ctx.createOscillator();
            const g = ctx.createGain();
            osc.type = i % 2 ? "triangle" : "sine";
            osc.frequency.value = freq;
            g.gain.value = i === 0 ? 0.16 : 0.075;
            osc.connect(g);
            g.connect(padFilter);
            osc.start();
            padOscs.push(osc);
        });
    }

    function playNote(freq, at, dur, vol, type, endFreq) {
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, at);
        if (endFreq) osc.frequency.exponentialRampToValueAtTime(endFreq, at + dur);
        g.gain.setValueAtTime(vol, at);
        g.gain.exponentialRampToValueAtTime(0.001, at + dur);
        osc.connect(g);
        g.connect(master);
        osc.start(at);
        osc.stop(at + dur + 0.01);
    }

    function playNoise(at, dur, vol, hpFreq) {
        const buf = ctx.createBuffer(1, Math.max(1, Math.floor(ctx.sampleRate * dur)), ctx.sampleRate);
        const data = buf.getChannelData(0);
        for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
        const src = ctx.createBufferSource();
        const flt = ctx.createBiquadFilter();
        const g = ctx.createGain();
        src.buffer = buf;
        flt.type = "highpass";
        flt.frequency.value = hpFreq;
        g.gain.setValueAtTime(vol, at);
        g.gain.exponentialRampToValueAtTime(0.001, at + dur);
        src.connect(flt);
        flt.connect(g);
        g.connect(master);
        src.start(at);
        src.stop(at + dur);
    }

    function chooseRawMeter() {
        // Usage + unsmoothed BPM abruptly snap time signature mid-bar
        if (rawBpm >= 132) return "7/8";
        if (rawBpm >= 102) return "5/4";
        if (activeView === "NOTEPAD") return "6/8";
        if (activeView === "SETTINGS") return "5/4";
        if (activeView === "MEM. CARD") return "3/4";
        return rawBpm >= 78 ? "4/4" : "3/4";
    }

    function scheduleStep(at) {
        const spec = METERS[currentMeter] || METERS["4/4"];
        if (stepInBar >= spec.steps) {
            stepInBar = 0;
            barCount++;
        }
        const s = stepInBar;
        const chord = PROGRESSION[barCount % PROGRESSION.length];
        const energy = Math.min(1, (rawBpm - MIN_BPM) / (MAX_BPM - MIN_BPM));

        if (s === 0) {
            padOscs.forEach((osc, i) => {
                osc.frequency.setTargetAtTime(chord.pad[i], at, 0.09);
            });
        }
        if (padFilter) {
            padFilter.frequency.setValueAtTime(520 + energy * 2400, at);
        }

        const isDownbeat = s === 0;
        const isAccent = spec.accent.includes(s);

        if (spec.kicks.includes(s)) {
            playNote(isDownbeat ? 115 : 98, at, 0.16, isDownbeat ? 0.48 : 0.34, "sine", 42);
            playNote(chord.bass * (isDownbeat ? 1 : 1.5), at, 0.24, 0.28, "triangle");
        }
        if (spec.snares.includes(s) && (energy > 0.12 || currentMeter !== "3/4")) {
            playNoise(at, 0.08, 0.11 + energy * 0.09, 1900);
            playNote(185, at, 0.05, 0.10, "triangle", 110);
        }
        if (spec.hats.includes(s)) {
            playNoise(at, 0.03, isAccent ? 0.065 : 0.03 + energy * 0.03, 6400);
        }

        // Melodic phrase outlining the meter
        if (isDownbeat || (isAccent && energy > 0.18) || energy > 0.45) {
            const note = chord.arp[(s + barCount) % chord.arp.length] * (energy > 0.65 && s % 2 ? 2 : 1);
            const toneType = energy > 0.65 ? "sawtooth" : "triangle";
            playNote(note, at, isAccent ? 0.22 : 0.11, isAccent ? 0.16 : 0.10, toneType);
        }

        $("meter-lbl").textContent = currentMeter + " · " + (s + 1) + "/" + spec.steps;
        stepInBar++;
    }

    function pushRawSpike(pxDelta, reason) {
        const now = performance.now();
        const dt = Math.max(8, now - lastEventAt);
        lastEventAt = now;
        const instantVel = Math.min(4800, Math.abs(pxDelta) * 1000 / dt);
        rawVelocity = instantVel;

        const nextBpm = Math.round(Math.min(MAX_BPM, MIN_BPM + (instantVel / 1800) * (MAX_BPM - MIN_BPM)));
        const jump = nextBpm - rawBpm;
        rawBpm = nextBpm;

        const nextMeter = chooseRawMeter();
        if (nextMeter !== currentMeter) {
            currentMeter = nextMeter;
            addLog(reason + " -> METER SNAPPED TO " + currentMeter + " (" + rawBpm + " BPM)", "ev-spike");
        } else if (Math.abs(jump) >= 22) {
            addLog(reason + " -> BPM jumped " + (jump > 0 ? "+" : "") + jump + " (" + rawBpm + " BPM)", reason.includes("SHIFT") ? "ev-shift" : "ev-spike");
        }
    }

    function playRawInteractionSfx(kind) {
        try {
            if (!ctx) initAudio();
            if (!ctx) return;
            if (ctx.state === "suspended") ctx.resume().catch(() => {});
            if (ctx.state !== "running") {
                if (!warnedUnlock) {
                    warnedUnlock = true;
                    addLog("Click START RAW SCROLL AUDIO once to unlock browser audio.", "ev-shift");
                }
                return;
            }
            const t = ctx.currentTime + 0.005;
            const chord = PROGRESSION[barCount % PROGRESSION.length];
            if (kind === "save") {
                playNote(chord.arp[2], t, 0.08, 0.22, "square", chord.arp[4]);
                playNote(chord.arp[4], t + 0.07, 0.11, 0.20, "sawtooth");
            } else if (kind === "unsave") {
                playNote(chord.arp[3], t, 0.08, 0.18, "square", chord.arp[0]);
            } else if (kind === "select") {
                playNote(chord.arp[1], t, 0.07, 0.20, "triangle", chord.arp[3]);
                playNote(chord.arp[3], t + 0.05, 0.10, 0.16, "square");
            } else if (kind === "load") {
                playNoise(t, 0.16, 0.22, 1200);
                playNote(chord.bass * 2, t, 0.18, 0.28, "sawtooth", chord.arp[4]);
            } else if (kind === "key") {
                playNote(chord.arp[interactions % chord.arp.length], t, 0.05, 0.13, "triangle");
            } else {
                playNote(chord.arp[(interactions + 1) % chord.arp.length], t, 0.06, 0.16, "sawtooth", chord.arp[0]);
            }
        } catch (e) {}
    }

    function handleFeedInteraction(kind, label, spikePx) {
        interactions++;
        $("interact-lbl").textContent = String(interactions);
        pushRawSpike(spikePx, label);
        playRawInteractionSfx(kind);
    }

    function detectActiveView() {
        try {
            const checked = window.parent.document.querySelector(".st-key-menu input:checked");
            if (checked) {
                const lbl = checked.closest("label");
                const txt = (lbl ? lbl.innerText : "").trim().toUpperCase();
                if (txt) {
                    activeView = txt;
                    $("view-stat").textContent = activeView;
                }
            }
        } catch (e) {}
    }

    function findScrollableElement() {
        try {
            const root = window.parent.document.querySelector(".st-key-feedscroll");
            if (!root) return null;
            if (root.scrollHeight > root.clientHeight + 4) return root;
            const nested = Array.from(root.querySelectorAll("div")).find(el => {
                const st = window.parent.getComputedStyle(el);
                return (st.overflowY === "auto" || st.overflowY === "scroll") && el.scrollHeight > el.clientHeight + 4;
            });
            return nested || root;
        } catch (e) {
            return null;
        }
    }

    function attachFeedSensor() {
        detectActiveView();
        if (feedEl && feedEl.isConnected) return true;
        const el = findScrollableElement();
        if (!el) return false;
        feedEl = el;
        lastScrollTop = el.scrollTop;
        lastScrollHeight = el.scrollHeight;

        el.addEventListener("scroll", () => {
            const dy = Math.abs(el.scrollTop - lastScrollTop);
            lastScrollTop = el.scrollTop;
            if (dy > 0) pushRawSpike(dy, "SCROLL");
        }, { passive: true });

        el.addEventListener("wheel", e => {
            pushRawSpike(e.deltaY, "WHEEL");
        }, { passive: true });

        let touchY = null;
        el.addEventListener("touchstart", e => {
            touchY = e.touches.length ? e.touches[0].clientY : null;
        }, { passive: true });
        el.addEventListener("touchmove", e => {
            if (touchY !== null && e.touches.length) {
                const y = e.touches[0].clientY;
                pushRawSpike(touchY - y, "TOUCH");
                touchY = y;
            }
        }, { passive: true });

        const checkHeightShift = () => {
            if (!feedEl || !feedEl.isConnected) return;
            const h = feedEl.scrollHeight;
            if (Math.abs(h - lastScrollHeight) > 24) {
                const diff = Math.abs(h - lastScrollHeight);
                lastScrollHeight = h;
                heightShifts++;
                $("shift-lbl").textContent = String(heightShifts);
                pushRawSpike(Math.min(900, diff), "LAYOUT SHIFT (" + diff + "px)");
            }
        };

        if (resizeObs) resizeObs.disconnect();
        if (window.parent.ResizeObserver) {
            resizeObs = new window.parent.ResizeObserver(checkHeightShift);
            resizeObs.observe(el);
        }
        if (mutObs) mutObs.disconnect();
        mutObs = new window.parent.MutationObserver(checkHeightShift);
        mutObs.observe(el, { childList: true, subtree: true });

        $("sensor-stat").textContent = "RAW LINKED";
        addLog("Attached unthrottled listener to feed & SELECT*.", "ev-info");
        return true;
    }

    function drawScope() {
        const c = $("scope");
        const g = c.getContext("2d");
        g.clearRect(0, 0, c.width, c.height);

        g.strokeStyle = "#1b2030";
        g.lineWidth = 1;
        [18, 37, 56].forEach(y => {
            g.beginPath(); g.moveTo(0, y); g.lineTo(c.width, y); g.stroke();
        });

        g.strokeStyle = "#ff007f";
        g.lineWidth = 2;
        g.beginPath();
        history.forEach((val, idx) => {
            const x = (idx / (history.length - 1)) * c.width;
            const norm = (val - MIN_BPM) / (MAX_BPM - MIN_BPM);
            const y = c.height - 6 - norm * (c.height - 14);
            if (idx === 0) g.moveTo(x, y);
            else g.lineTo(x, y);
        });
        g.stroke();
    }

    function tick() {
        const now = performance.now();
        if (now - lastEventAt > 240) {
            rawVelocity = Math.max(0, rawVelocity * 0.72);
            rawBpm = Math.max(MIN_BPM, Math.round(rawBpm - (rawBpm - MIN_BPM) * 0.25));
            currentMeter = chooseRawMeter();
        }

        if (autoScrolling && feedEl && feedEl.isConnected) {
            const maxTop = Math.max(0, feedEl.scrollHeight - feedEl.clientHeight);
            if (maxTop > 10) {
                const stepPx = (14 + Math.random() * 24) * autoDir;
                feedEl.scrollTop = Math.max(0, Math.min(maxTop, feedEl.scrollTop + stepPx));
                if (feedEl.scrollTop >= maxTop - 2) autoDir = -1;
                else if (feedEl.scrollTop <= 2) autoDir = 1;
            }
        }

        const delta = rawBpm - prevBpm;
        prevBpm = rawBpm;

        const bpmEl = $("bpm");
        bpmEl.innerHTML = String(rawBpm).padStart(3, "0") + '<span class="bpm-unit">BPM</span>';
        bpmEl.classList.toggle("spike", Math.abs(delta) >= 12 || rawBpm >= 135);
        $("vel-lbl").textContent = Math.round(rawVelocity) + " px/s";
        $("delta-lbl").textContent = "ΔBPM: " + (delta >= 0 ? "+" : "") + delta;
        const spec = METERS[currentMeter] || METERS["4/4"];
        $("meter-lbl").textContent = currentMeter + " · " + ((stepInBar % spec.steps) + 1) + "/" + spec.steps;

        history.push(rawBpm);
        if (history.length > 64) history.shift();
        drawScope();

        if (running && ctx && ctx.state === "running") {
            const horizon = ctx.currentTime + 0.1;
            while (nextStepAt < horizon) {
                scheduleStep(nextStepAt);
                nextStepAt += 30 / rawBpm; // eighth-note musical step
            }
        }
    }

    $("power").addEventListener("click", async () => {
        initAudio();
        if (!ctx) return;
        if (running) {
            running = false;
            await ctx.suspend();
            $("dev").classList.remove("on");
            $("status-tag").innerHTML = "&#9679; PAUSED";
            $("power").innerHTML = "&#9654; START RAW SCROLL AUDIO";
            addLog("Audio paused.", "ev-info");
        } else {
            await ctx.resume();
            running = true;
            nextStepAt = ctx.currentTime + 0.04;
            $("dev").classList.add("on");
            $("status-tag").innerHTML = "&#9679; LIVE RAW";
            $("power").innerHTML = "&#10074;&#10074; PAUSE RAW AUDIO";
            addLog("Raw scroll & meter synth armed.", "ev-info");
        }
    });

    $("autoscroll").addEventListener("click", () => {
        autoScrolling = !autoScrolling;
        $("autoscroll").setAttribute("aria-pressed", String(autoScrolling));
        $("autoscroll").innerHTML = autoScrolling ? "&#9632; STOP AUTO-SCROLL" : "&#8693; AUTO-SCROLL TEST";
        if (autoScrolling) {
            if (!attachFeedSensor()) addLog("Select FEED in SELECT* to auto-scroll posts.", "ev-shift");
            else addLog("Auto-scroll active (erratic BPM & meter jumps).", "ev-spike");
        } else {
            addLog("Auto-scroll stopped.", "ev-info");
        }
    });

    $("simshift").addEventListener("click", () => {
        heightShifts++;
        $("shift-lbl").textContent = String(heightShifts);
        pushRawSpike(1150, "SIMULATED RSS LAYOUT SHIFT");
    });

    $("vol").addEventListener("input", e => {
        if (master) master.gain.value = (e.target.value / 100) * 0.30;
    });

    setInterval(() => {
        if (!attachFeedSensor() && (!feedEl || !feedEl.isConnected)) {
            $("sensor-stat").textContent = activeView + " VIEW";
        }
    }, 500);

    addLog("Proto ready. Use SELECT*, feed scroll, cards, or SAVE TO MEM.", "ev-info");
    setInterval(tick, 45);

    try {
        const pDoc = window.parent.document;
        const onParentPointerDown = e => {
            const target = e.target;
            if (!target || !target.closest) return;

            const inMenu = target.closest(".st-key-menu");
            if (inMenu) {
                const lbl = target.closest("label");
                const txt = (lbl ? (lbl.innerText || lbl.textContent) : "").trim().toUpperCase();
                if (txt) {
                    activeView = txt;
                    $("view-stat").textContent = activeView;
                    handleFeedInteraction("select", "SELECT*: " + txt, 740);
                }
                return;
            }

            const inFeed = target.closest(".st-key-feedscroll, .st-key-stage");
            if (!inFeed) return;

            const btn = target.closest("button");
            if (btn) {
                const txt = (btn.innerText || btn.textContent || "").trim().toUpperCase();
                if (txt.includes("SAVE TO MEM")) {
                    handleFeedInteraction("save", "BTN: SAVE TO MEM.", 820);
                } else if (txt.includes("SAVED")) {
                    handleFeedInteraction("unsave", "BTN: UNSAVE MEM.", 640);
                } else if (txt.includes("LOAD NEXT SIDE")) {
                    handleFeedInteraction("load", "BTN: LOAD NEXT SIDE", 1100);
                } else {
                    handleFeedInteraction("btn", "BTN: " + (txt.slice(0, 14) || "ACTION"), 680);
                }
                return;
            }
            if (target.closest(".card")) {
                handleFeedInteraction("card", "CARD CLICK", 520);
            } else {
                handleFeedInteraction("click", "STAGE CLICK", 420);
            }
        };

        const onParentKeyDown = e => {
            const target = e.target;
            if (!target || !target.closest) return;
            if (!target.closest(".st-key-menu, .st-key-feedscroll, .st-key-stage")) return;
            const now = performance.now();
            if (now - lastKeySoundAt < 75) return;
            lastKeySoundAt = now;
            const nav = ["ArrowDown", "ArrowUp", "PageDown", "PageUp", " ", "Enter"].includes(e.key);
            handleFeedInteraction("key", "KEY: " + e.key.toUpperCase(), nav ? 660 : 320);
        };

        pDoc.addEventListener("pointerdown", onParentPointerDown, { capture: true, passive: true });
        pDoc.addEventListener("keydown", onParentKeyDown, { capture: true, passive: true });
        window.addEventListener("pagehide", () => {
            pDoc.removeEventListener("pointerdown", onParentPointerDown, { capture: true });
            pDoc.removeEventListener("keydown", onParentKeyDown, { capture: true });
            if (ctx && ctx.state !== "closed") ctx.close().catch(() => {});
        });
    } catch (e) {}
})();
</script>
</body>
</html>
"""


def scroll_proto_html(live_feed=False, feed_source="SAMPLE", svg_count=0, total_posts=0):
    data = json.dumps({
        "live": bool(live_feed),
        "source": feed_source or "SAMPLE",
        "svgCount": int(svg_count),
        "totalPosts": int(total_posts),
    }).replace("</", "<\\/")
    return TEMPLATE.replace("__DATA__", data)
