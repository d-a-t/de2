"""DE3 Sonic Deck (Tuner): dampened tempo controller, bar-quantized time signatures,
and explicit synth layer controls shaped by how the user navigates and interacts with the app."""

SONIC_DECK_HTML = r"""<!doctype html>
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
    font: 11px 'Space Mono', 'Courier New', monospace;
}
.deck {
    border: 2px solid #00f5ff;
    background: linear-gradient(145deg, #171d2b, #10131d);
    padding: 12px;
    box-shadow: 4px 4px 0 #ff007f;
    clip-path: polygon(0 0, calc(100% - 26px) 0, 100% 26px, 100% 100%, 26px 100%, 0 calc(100% - 26px));
    position: relative;
}
.deck::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 5;
    background: repeating-linear-gradient(0deg, transparent 0 2px, rgba(0, 0, 0, .20) 2px 3px);
}
.hz {
    height: 8px;
    background: repeating-linear-gradient(135deg, #00f5ff 0 8px, #0b0e14 8px 16px);
    margin-bottom: 8px;
}
.eyebrow, .caption {
    color: #00f5ff;
    font-weight: 700;
    letter-spacing: .14em;
    font-size: 9px;
}
.eyebrow {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    flex-wrap: wrap;
    padding-bottom: 6px;
    border-bottom: 1px solid #343d55;
}
.display {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 10px;
    padding: 8px 0 6px;
}
.display strong {
    display: block;
    color: #ffe600;
    font: 400 36px/.95 Anton, 'Courier New', monospace;
    text-shadow: 2px 0 #00f5ff, -2px 0 #ff007f;
}
.display small {
    color: #8c95ad;
    font-size: 9px;
    letter-spacing: .12em;
}
.readout {
    text-align: right;
    line-height: 1.55;
    color: #b9c3d8;
    font-size: 10px;
}
.readout b { color: #ffe600; }

.meter-wrap {
    margin-bottom: 7px;
}
.meter-head {
    display: flex;
    justify-content: space-between;
    font-size: 9px;
    color: #8c95ad;
    margin-bottom: 3px;
}
.meter-bar {
    height: 7px;
    background: #0b0e14;
    border: 1px solid #343d55;
    position: relative;
}
.meter-target {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 3px;
    background: #ff007f;
    left: 0%;
}
.meter-smooth {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #00f5ff, #ffe600);
}

.control {
    padding: 6px 0;
    border-top: 1px solid #2e364f;
}
.control-head {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 3px;
    font-size: 10px;
}
.control-head span:last-child { color: #ffe600; font-weight: 700; }
input[type=range] {
    width: 100%;
    accent-color: #ffe600;
    margin: 0;
}
.row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.link {
    color: #b9c3d8;
    line-height: 1.35;
    font-size: 10px;
    cursor: pointer;
}
.link input {
    accent-color: #ff007f;
    vertical-align: middle;
}
.buttons {
    display: flex;
    gap: 8px;
    margin-top: 8px;
}
button {
    cursor: pointer;
    border: 2px solid #ffe600;
    background: #0b0e14;
    color: #ffe600;
    padding: 7px;
    font: 400 14px Anton, 'Courier New', monospace;
    letter-spacing: .08em;
    transform: skewX(-6deg);
}
button:hover, button[aria-pressed=true] {
    background: #ffe600;
    color: #0b0e14;
}
button:focus-visible, input:focus-visible {
    outline: 2px solid #00f5ff;
    outline-offset: 2px;
}
.buttons button { flex: 1; }

.sig-row {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 4px;
    margin-top: 5px;
}
.sig-row button {
    border: 1px solid #343d55;
    color: #b9c3d8;
    font: 700 9px 'Space Mono', monospace;
    padding: 5px 2px;
    transform: none;
    text-align: center;
}
.sig-row button[aria-pressed=true] {
    border-color: #ff007f;
    background: #ff007f;
    color: #fff;
}

.layers {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 4px;
    margin-top: 5px;
}
.layers button {
    border: 1px solid #343d55;
    color: #b9c3d8;
    text-align: left;
    font: 700 9px 'Space Mono', 'Courier New', monospace;
    padding: 5px 6px;
    transform: none;
}
.layers button[aria-pressed=true] {
    border-color: #00f5ff;
    background: #00f5ff;
    color: #0b0e14;
}
.sheet-row {
    display: flex;
    gap: 5px;
    align-items: center;
    margin-top: 4px;
}
.sheet-select {
    flex: 1;
    background: #0b0e14;
    color: #ffe600;
    border: 1px solid #343d55;
    padding: 4px 6px;
    font: 700 10px 'Space Mono', monospace;
    outline: none;
}
.sheet-select:focus {
    border-color: #00f5ff;
}
.sheet-next {
    border: 1px solid #00f5ff;
    color: #00f5ff;
    background: #0b0e14;
    padding: 4px 8px;
    font: 700 9px 'Space Mono', monospace;
    transform: none;
}
.sheet-next:hover {
    background: #00f5ff;
    color: #0b0e14;
}
.sheet-meta {
    display: flex;
    justify-content: space-between;
    font-size: 9px;
    color: #8c95ad;
    margin-top: 4px;
}
.sheet-meta b { color: #00f5ff; }
.status {
    min-height: 28px;
    margin-top: 8px;
    padding-top: 6px;
    border-top: 1px solid #2e364f;
    color: #8c95ad;
    font-size: 9px;
    line-height: 1.45;
    letter-spacing: .04em;
}
.status b { color: #ff007f; }
@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; }
}
</style>
</head>
<body>
<div class="deck">
  <div class="hz"></div>
  <div class="eyebrow"><span>DE3 // SONIC DECK TUNER</span><span id="chord-lbl">AM9 // 4/4</span></div>
  <div class="display">
    <div><small>DAMPED TEMPO</small><strong><span id="bpm">076</span><small> BPM</small></strong></div>
    <div class="readout">
      <div>METER <b id="meter-lbl">4/4 · 1/8</b></div>
      <div>TARGET <b id="target-bpm">076</b> · <b id="pace">IDLE</b></div>
      <div>SESSION <b id="timer">00:00</b> · <b id="view-lbl">FEED</b></div>
    </div>
  </div>
  <div class="meter-wrap">
    <div class="meter-head"><span>SMOOTHED CURVE vs TARGET</span><span id="shifts-ignored">SHIFTS FILTERED: 0</span></div>
    <div class="meter-bar"><div class="meter-smooth" id="meter-smooth"></div><div class="meter-target" id="meter-target"></div></div>
  </div>
  <div class="control">
    <div class="control-head"><label for="manual">BASE TEMPO</label><span><output id="manual-value">76</output> BPM</span></div>
    <input id="manual" type="range" min="55" max="165" value="76" aria-label="Base tempo in beats per minute">
  </div>
  <div class="control">
    <div class="row">
      <label class="link"><input id="scroll-link" type="checkbox" checked> LINK SCROLL TO TEMPO</label>
      <label class="link"><input id="interact-sfx" type="checkbox" checked> UI / FEED SFX</label>
    </div>
  </div>
  <div class="control">
    <div class="control-head"><span class="caption">MUSIC SHEET SAMPLE</span><label class="link" style="font-size:9px"><input id="auto-sample" type="checkbox" checked> AUTO-SAMPLE</label></div>
    <div class="sheet-row">
      <select id="sheet-select" class="sheet-select" aria-label="Select music sheet sample"></select>
      <button id="next-sheet" class="sheet-next" type="button">NEXT &#9656;</button>
    </div>
    <div class="sheet-meta"><span id="sheet-mood">MOOD: AMBIENT</span><span id="sheet-arp">ARP: <b id="arp-lbl">UP</b></span></div>
  </div>
  <div class="control">
    <div class="control-head"><span class="caption">TIME SIGNATURE</span><span id="meter-mode-lbl" style="color:#ff007f;font-size:9px">AUTO (USAGE)</span></div>
    <div class="sig-row">
      <button type="button" data-sig="AUTO" aria-pressed="true">AUTO</button>
      <button type="button" data-sig="4/4" aria-pressed="false">4/4</button>
      <button type="button" data-sig="3/4" aria-pressed="false">3/4</button>
      <button type="button" data-sig="6/8" aria-pressed="false">6/8</button>
      <button type="button" data-sig="5/4" aria-pressed="false">5/4</button>
      <button type="button" data-sig="7/8" aria-pressed="false">7/8</button>
    </div>
  </div>
  <div class="control">
    <div class="control-head"><label for="threshold">FAST-SCROLL THRESHOLD</label><span><output id="threshold-value">700</output> px/s</span></div>
    <input id="threshold" type="range" min="200" max="1600" step="50" value="700" aria-label="Fast scroll threshold in pixels per second">
    <div class="control-head" style="margin:5px 0 3px"><label for="lift">SCROLL TEMPO LIFT</label><span>+<output id="lift-value">24</output> BPM</span></div>
    <input id="lift" type="range" min="0" max="40" step="1" value="24" aria-label="Maximum tempo increase from scrolling">
  </div>
  <div class="control">
    <div class="control-head"><label for="smoothing">TEMPO DAMPING</label><span><output id="smoothing-value">2.5</output> sec</span></div>
    <input id="smoothing" type="range" min="0.5" max="6" step="0.5" value="2.5" aria-label="Tempo smoothing duration in seconds">
    <div class="control-head" style="margin:5px 0 3px"><label for="vol">MASTER GAIN</label><span><output id="vol-value">70</output>%</span></div>
    <input id="vol" type="range" min="0" max="100" step="1" value="70" aria-label="Master volume">
  </div>
  <div class="control">
    <div class="caption">SYNTH LAYERS</div>
    <div class="layers">
      <button type="button" data-layer="pad" aria-pressed="true">&#10022; PAD</button>
      <button type="button" data-layer="bass" aria-pressed="true">&#9644; BASS</button>
      <button type="button" data-layer="beat" aria-pressed="true">&#9673; BEAT</button>
      <button type="button" data-layer="keys" aria-pressed="true">&#9834; KEYS</button>
      <button type="button" data-layer="melody" aria-pressed="true">&#9835; MELODY</button>
    </div>
  </div>
  <div class="buttons">
    <button id="power" type="button">&#9654; START SESSION</button>
    <button id="reset" type="button">&#8634; END / RESET</button>
  </div>
  <div class="status"><div id="state">READY // BAR-SYNCED METER &amp; DAMPENED TEMPO</div><div id="sensor">FEED + SELECT* LINKED // SHIFT-GUARDED</div></div>
</div>
<script>
(() => {
    const $ = id => document.getElementById(id);
    const ctxState = { context: null, master: null, layers: {}, padOscs: [], padFilter: null, padLfo: null, running: false };
    const layerOn = { pad: true, bass: true, beat: true, keys: true, melody: true };

    const NOTE_OFFSETS = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
    function noteToHz(n) {
        if (typeof n === "number") return n;
        if (!n || typeof n !== "string") return null;
        const m = n.trim().match(/^([A-Ga-g])([#b]?)(-?\d)$/);
        if (!m) return 220;
        let semi = NOTE_OFFSETS[m[1].toUpperCase()];
        if (m[2] === "#") semi += 1;
        if (m[2] === "b") semi -= 1;
        const oct = parseInt(m[3], 10);
        const midi = (oct + 1) * 12 + semi;
        return 440 * Math.pow(2, (midi - 69) / 12);
    }

    const RAW_SHEETS = __SHEETS_DATA__;
    const SHEETS = RAW_SHEETS.map(s => ({
        id: s.id || "sheet",
        title: s.title || "Untitled",
        artist: s.artist || "Custom",
        mood: (s.mood || "ambient").toUpperCase(),
        subreddits: (s.subreddits || []).map(x => x.toLowerCase()),
        bpm: Number(s.bpm || 88),
        meter: s.meter || "4/4",
        swing: Number(s.swing || 0.04),
        cutoff: Number(s.cutoff || 950),
        arpMode: (s.arp_mode || "up").toLowerCase(),
        drums: s.drums || { kicks: [0, 8], snares: [4, 12], hats: [0, 2, 4, 6, 8, 10, 12, 14] },
        bars: (s.bars || []).map(b => ({
            name: b.name || "CHORD",
            bass: noteToHz(b.bass) || 65.41,
            pad: (b.pad || ["A3", "C#4", "E4", "G#4"]).map(noteToHz).filter(Boolean),
            keys: (b.keys || ["E4", "G#4", "B4", "C#5"]).map(noteToHz).filter(Boolean),
            melody: (b.melody || []).map(n => n ? noteToHz(n) : null)
        }))
    }));

    let activeSheetIdx = 0;
    let PROGRESSION = SHEETS[0].bars;

    const METERS = {
        "4/4": { steps: 16, kicks: [0, 6, 10], snares: [4, 12], hats: [0, 2, 4, 6, 8, 10, 12, 14], accent: [0, 8] },
        "3/4": { steps: 12, kicks: [0, 6], snares: [4, 8], hats: [0, 2, 4, 6, 8, 10], accent: [0, 4] },
        "6/8": { steps: 12, kicks: [0, 6], snares: [3, 9], hats: [0, 2, 4, 6, 8, 10], accent: [0, 6] },
        "5/4": { steps: 10, kicks: [0, 6], snares: [3, 8], hats: [0, 2, 3, 5, 6, 8, 9], accent: [0, 3, 6] },
        "7/8": { steps: 14, kicks: [0, 4, 8, 11], snares: [6, 12], hats: [0, 2, 4, 6, 8, 10, 12], accent: [0, 4, 8] }
    };

    let baseBpm = SHEETS[0].bpm || 76;
    let smoothBpm = baseBpm;
    let scrollVelocity = 0;
    let lastScrollAt = 0;
    let lastInputAt = 0;
    let lastTickAt = performance.now();
    let nextBeatAt = 0;
    let stepInBar = 0;
    let barCount = 0;
    let sigSetting = "AUTO";
    let activeMeter = SHEETS[0].meter || "4/4";
    let pendingMeter = activeMeter;
    let activeView = "FEED";
    let elapsed = 0;
    let startedAt = 0;
    let sensorAttached = false;
    let feedEl = null;
    let lastScrollTop = 0;
    let lastScrollHeight = 0;
    let shiftsFiltered = 0;
    let interactCount = 0;
    let lastKeyAt = 0;

    function populateSheetSelect() {
        const sel = $("sheet-select");
        if (!sel) return;
        sel.innerHTML = "";
        SHEETS.forEach((sh, i) => {
            const opt = document.createElement("option");
            opt.value = String(i);
            opt.textContent = (i + 1) + ". " + sh.title + " (" + sh.bpm + " BPM)";
            sel.appendChild(opt);
        });
        sel.value = String(activeSheetIdx);
    }

    function selectSheet(idx, reason) {
        if (!SHEETS.length) return;
        activeSheetIdx = ((idx % SHEETS.length) + SHEETS.length) % SHEETS.length;
        const sh = SHEETS[activeSheetIdx];
        PROGRESSION = sh.bars;
        baseBpm = sh.bpm;
        $("manual").value = Math.round(baseBpm);
        $("manual-value").textContent = String(Math.round(baseBpm));
        if (sigSetting === "AUTO") {
            pendingMeter = sh.meter || "4/4";
        }
        if ($("sheet-select")) $("sheet-select").value = String(activeSheetIdx);
        if ($("sheet-mood")) $("sheet-mood").textContent = "MOOD: " + sh.mood + " // " + sh.artist.toUpperCase();
        if ($("arp-lbl")) $("arp-lbl").textContent = sh.arpMode.toUpperCase();
        if (ctxState.padFilter && ctxState.context) {
            ctxState.padFilter.frequency.setTargetAtTime(sh.cutoff || 950, ctxState.context.currentTime, 0.25);
        }
        if (reason) {
            $("state").textContent = "SHEET: " + sh.title.toUpperCase() + " (" + reason + ")";
        }
    }

    function setLayerGain(name, value) {
        const gain = ctxState.layers[name];
        if (gain && ctxState.context) {
            gain.gain.setTargetAtTime(value, ctxState.context.currentTime, 0.08);
        }
    }

    function initializeAudio() {
        if (ctxState.context) return;
        let AudioContextClass = null;
        try { AudioContextClass = window.parent.AudioContext || window.parent.webkitAudioContext; } catch (e) {}
        AudioContextClass = AudioContextClass || window.AudioContext || window.webkitAudioContext;
        if (!AudioContextClass) {
            $("state").textContent = "WEB AUDIO UNAVAILABLE IN THIS BROWSER";
            return;
        }
        const context = new AudioContextClass();
        const master = context.createGain();
        const compressor = context.createDynamicsCompressor();
        master.gain.value = (Number($("vol").value) / 100) * 0.28;
        master.connect(compressor);
        compressor.connect(context.destination);
        ctxState.context = context;
        ctxState.master = master;

        ["pad", "bass", "beat", "keys", "melody"].forEach(name => {
            const gain = context.createGain();
            gain.gain.value = layerOn[name] ? (name === "melody" ? 0.36 : 0.45) : 0;
            gain.connect(master);
            ctxState.layers[name] = gain;
        });

        const padFilter = context.createBiquadFilter();
        padFilter.type = "lowpass";
        padFilter.frequency.value = SHEETS[activeSheetIdx].cutoff || 820;
        padFilter.Q.value = 1.6;
        padFilter.connect(ctxState.layers.pad);
        ctxState.padFilter = padFilter;

        // Subtle breathing LFO on the pad low-pass filter
        const lfo = context.createOscillator();
        const lfoGain = context.createGain();
        lfo.frequency.value = 0.14;
        lfoGain.gain.value = 180;
        lfo.connect(lfoGain);
        lfoGain.connect(padFilter.frequency);
        lfo.start();
        ctxState.padLfo = lfo;

        const padNotes = PROGRESSION[0].pad;
        for (let index = 0; index < 5; index++) {
            const freq = padNotes[index % padNotes.length];
            const oscillator = context.createOscillator();
            const gain = context.createGain();
            oscillator.type = index % 2 ? "triangle" : "sine";
            oscillator.frequency.value = freq;
            gain.gain.value = index === 0 ? 0.14 : 0.065;
            oscillator.connect(gain);
            gain.connect(padFilter);
            oscillator.start();
            ctxState.padOscs.push(oscillator);
        }
    }

    function tone(frequency, at, duration, volume, type, destination, endFrequency) {
        const context = ctxState.context;
        const oscillator = context.createOscillator();
        const gain = context.createGain();
        oscillator.type = type;
        oscillator.frequency.setValueAtTime(frequency, at);
        if (endFrequency) oscillator.frequency.exponentialRampToValueAtTime(endFrequency, at + duration);
        gain.gain.setValueAtTime(volume, at);
        gain.gain.exponentialRampToValueAtTime(0.001, at + duration);
        oscillator.connect(gain);
        gain.connect(destination);
        oscillator.start(at);
        oscillator.stop(at + duration + 0.01);
    }

    function noise(at, duration, volume, destination, frequency) {
        const context = ctxState.context;
        const buffer = context.createBuffer(1, Math.max(1, Math.ceil(context.sampleRate * duration)), context.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
        const source = context.createBufferSource();
        const filter = context.createBiquadFilter();
        const gain = context.createGain();
        source.buffer = buffer;
        filter.type = "highpass";
        filter.frequency.value = frequency;
        gain.gain.setValueAtTime(volume, at);
        gain.gain.exponentialRampToValueAtTime(0.001, at + duration);
        source.connect(filter);
        filter.connect(gain);
        gain.connect(destination);
        source.start(at);
        source.stop(at + duration);
    }

    function desiredAutoMeter(activeVelocity, threshold) {
        if (activeView === "MEM. CARD") return "3/4";
        if (activeView === "NOTEPAD") return "6/8";
        if (activeView === "SETTINGS") return "5/4";
        if (activeView === "CREDITS") return "4/4";
        if (activeVelocity >= threshold) return "7/8";
        if (activeVelocity >= threshold * 0.45) return "5/4";
        return SHEETS[activeSheetIdx].meter || "4/4";
    }

    function pickArpNote(keys, step, mode) {
        if (!keys || !keys.length) return 440;
        const n = keys.length;
        if (mode === "down") return keys[(n - 1 - (step % n))];
        if (mode === "pingpong") {
            const cycle = Math.max(1, n * 2 - 2);
            const p = step % cycle;
            return keys[p < n ? p : cycle - p];
        }
        if (mode === "random") return keys[(step * 7 + barCount * 3) % n];
        return keys[step % n];
    }

    function playStep(at) {
        const sh = SHEETS[activeSheetIdx];
        let spec = METERS[activeMeter] || METERS["4/4"];
        if (stepInBar >= spec.steps) {
            stepInBar = 0;
            barCount++;
            // Quantize time-signature transitions cleanly to bar downbeat
            if (pendingMeter !== activeMeter) {
                activeMeter = pendingMeter;
                spec = METERS[activeMeter] || METERS["4/4"];
            }
            // Auto-sample evolution: every 8 bars when no comments window is open, evolve to another sheet
            if ($("auto-sample") && $("auto-sample").checked && barCount > 0 && barCount % 8 === 0 && !lastDetectedAtm && SHEETS.length > 1) {
                selectSheet((activeSheetIdx + 1) % SHEETS.length, "AUTO-EVOLVE BAR " + barCount);
            }
        }
        const s = stepInBar;
        const chord = PROGRESSION[barCount % PROGRESSION.length];
        const isDownbeat = s === 0;
        const isAccent = spec.accent.includes(s);
        const drums = (sh.drums && sh.drums.kicks) ? sh.drums : spec;

        if (isDownbeat) {
            ctxState.padOscs.forEach((osc, i) => {
                osc.frequency.setTargetAtTime(chord.pad[i % chord.pad.length], at, 0.14);
            });
            $("chord-lbl").textContent = chord.name.toUpperCase() + " // " + activeMeter;
        }

        if (layerOn.bass && (drums.kicks.includes(s) || (isAccent && s % 4 === 0))) {
            const bassFreq = isDownbeat ? chord.bass : (s % 8 === 6 ? chord.bass * 2 : chord.bass * 1.5);
            tone(bassFreq, at, 0.28, isDownbeat ? 0.44 : 0.28, "sine", ctxState.layers.bass);
        }

        if (layerOn.beat) {
            if (drums.kicks.includes(s)) {
                tone(isDownbeat ? 112 : 95, at, 0.16, isDownbeat ? 0.36 : 0.24, "sine", ctxState.layers.beat, 46);
            }
            if (drums.snares.includes(s)) {
                noise(at, 0.10, 0.08, ctxState.layers.beat, 2100);
                tone(175, at, 0.05, 0.08, "triangle", ctxState.layers.beat, 110);
            }
            if (drums.hats.includes(s)) {
                const vel = isAccent ? 0.042 : (s % 2 === 0 ? 0.024 : 0.014);
                noise(at, 0.03, vel, ctxState.layers.beat, 6500);
            }
        }

        const isWindowOpen = !!(window.parent && window.parent.document.querySelector("[data-testid='stDialog'], [role='dialog']"));
        if (layerOn.keys && (isDownbeat || isAccent || s % 2 === 0 || isWindowOpen)) {
            const note = pickArpNote(chord.keys, s + barCount, sh.arpMode);
            const dur = isDownbeat ? 0.32 : 0.16;
            tone(note, at, dur, isDownbeat ? 0.16 : 0.10, "triangle", ctxState.layers.keys);
            if (isWindowOpen) tone(note * 2, at, dur * 0.5, 0.035, "sine", ctxState.layers.keys);
        }

        if (layerOn.melody && chord.melody && chord.melody.length) {
            const melFreq = chord.melody[s % chord.melody.length];
            if (melFreq) {
                const melDur = 0.28;
                tone(melFreq, at, melDur, 0.15, "triangle", ctxState.layers.melody);
                tone(melFreq * 1.003, at, melDur * 0.9, 0.06, "sine", ctxState.layers.melody);
            }
        }

        $("meter-lbl").textContent = activeMeter + " · " + (s + 1) + "/" + spec.steps;
        stepInBar++;
    }

    function playTunedInteraction(kind, label) {
        if (!$("interact-sfx").checked) return;
        interactCount++;
        $("state").textContent = "ACTION #" + interactCount + ": " + label;
        try {
            initializeAudio();
            const ctx = ctxState.context;
            if (!ctx) return;
            if (ctx.state === "suspended") ctx.resume().catch(() => {});
            if (ctx.state !== "running") {
                $("state").textContent = "PRESS START SESSION TO UNLOCK INTERACTION AUDIO";
                return;
            }
            const t = ctx.currentTime + 0.01;
            const out = ctxState.master;
            const chord = PROGRESSION[barCount % PROGRESSION.length];
            if (kind === "save") {
                tone(chord.keys[2], t, 0.18, 0.20, "triangle", out);
                tone(chord.keys[4], t + 0.07, 0.26, 0.22, "sine", out);
            } else if (kind === "unsave") {
                tone(chord.keys[3], t, 0.14, 0.15, "triangle", out);
                tone(chord.keys[0], t + 0.06, 0.20, 0.15, "sine", out);
            } else if (kind === "select") {
                tone(chord.keys[1], t, 0.14, 0.16, "triangle", out);
                tone(chord.keys[3], t + 0.06, 0.20, 0.14, "sine", out);
            } else if (kind === "load") {
                tone(chord.bass * 2, t, 0.24, 0.26, "sine", out, chord.bass);
                tone(chord.keys[0], t + 0.04, 0.30, 0.14, "triangle", out);
                tone(chord.keys[2], t + 0.08, 0.30, 0.12, "sine", out);
                noise(t, 0.14, 0.05, out, 2200);
            } else if (kind === "dock") {
                tone(chord.bass * 2, t, 0.28, 0.28, "triangle", out);
                tone(chord.keys[1], t + 0.06, 0.26, 0.22, "sine", out);
                tone(chord.keys[3 % chord.keys.length] * 2, t + 0.12, 0.36, 0.25, "sine", out);
                noise(t + 0.08, 0.10, 0.035, out, 3200);
                if (ctxState.padFilter && ctxState.context) {
                    ctxState.padFilter.frequency.setValueAtTime(1400, t);
                }
            } else if (kind === "undock") {
                tone(chord.keys[3 % chord.keys.length] * 2, t, 0.18, 0.20, "sine", out);
                tone(chord.keys[1], t + 0.06, 0.20, 0.16, "triangle", out);
                tone(chord.bass * 2, t + 0.12, 0.26, 0.22, "sine", out);
                if (ctxState.padFilter && ctxState.context) {
                    ctxState.padFilter.frequency.setValueAtTime(820, t);
                }
            } else if (kind === "upvote") {
                tone(chord.keys[0] * 2, t, 0.12, 0.24, "triangle", out);
                tone(chord.keys[2 % chord.keys.length] * 2, t + 0.04, 0.15, 0.26, "sine", out);
                tone(chord.keys[4 % chord.keys.length] * 2, t + 0.08, 0.24, 0.28, "sine", out);
                if (ctxState.padFilter && ctxState.context) {
                    const cur = ctxState.padFilter.frequency.value || 900;
                    ctxState.padFilter.frequency.setValueAtTime(Math.min(3800, cur + 600), t);
                    ctxState.padFilter.frequency.exponentialRampToValueAtTime(cur, t + 0.7);
                }
            } else if (kind === "downvote") {
                tone(chord.bass * 1.5, t, 0.20, 0.32, "sawtooth", out, chord.bass * 0.7);
                noise(t, 0.08, 0.05, out, 850);
            } else if (kind === "transmit") {
                for (let k = 0; k < 4; k++) {
                    const f = chord.keys[k % chord.keys.length] * 1.5;
                    tone(f, t + k * 0.045, 0.16, 0.22, "triangle", out);
                }
                tone(chord.bass, t + 0.18, 0.25, 0.36, "sine", out, chord.bass * 0.6);
                noise(t + 0.18, 0.12, 0.06, out, 4500);
            } else {
                const freq = chord.keys[interactCount % chord.keys.length];
                tone(freq, t, 0.13, 0.13, kind === "key" ? "sine" : "triangle", out);
            }
            if ($("scroll-link").checked && sensorAttached) {
                const nudge = kind === "transmit" ? 360 : kind === "dock" ? 280 : kind === "upvote" ? 220 : kind === "load" ? 320 : kind === "save" ? 210 : 120;
                scrollVelocity = Math.min(1600, scrollVelocity * 0.7 + nudge * 0.3);
                lastScrollAt = performance.now();
            }
        } catch (e) {}
    }

    function detectActiveView() {
        try {
            const checked = window.parent.document.querySelector(".st-key-menu input:checked");
            if (checked) {
                const lbl = checked.closest("label");
                const txt = (lbl ? lbl.innerText : "").trim().toUpperCase();
                if (txt) {
                    activeView = txt;
                    $("view-lbl").textContent = activeView;
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
        } catch (error) {
            return null;
        }
    }

    function connectFeedSensor() {
        detectActiveView();
        if (feedEl && feedEl.isConnected) return true;
        try {
            const feed = findScrollableElement();
            if (!feed) {
                sensorAttached = false;
                return false;
            }
            feedEl = feed;
            lastScrollTop = feed.scrollTop;
            lastScrollHeight = feed.scrollHeight;

            const recordPace = amount => {
                const now = performance.now();
                const interval = Math.max(24, now - (lastInputAt || now - 100));
                const instant = Math.min(2400, Math.abs(amount) * 1000 / interval);
                scrollVelocity = scrollVelocity * 0.62 + instant * 0.38;
                lastInputAt = now;
                lastScrollAt = now;
            };

            feed.addEventListener("scroll", () => {
                const h = feed.scrollHeight;
                if (Math.abs(h - lastScrollHeight) > 24) {
                    lastScrollHeight = h;
                    lastScrollTop = feed.scrollTop;
                    shiftsFiltered++;
                    $("shifts-ignored").textContent = "SHIFTS FILTERED: " + shiftsFiltered;
                    return;
                }
                const dy = Math.abs(feed.scrollTop - lastScrollTop);
                lastScrollTop = feed.scrollTop;
                if (dy > 0) recordPace(dy);
            }, { passive: true });

            feed.addEventListener("wheel", event => recordPace(event.deltaY), { passive: true });
            let touchY = null;
            feed.addEventListener("touchstart", event => {
                touchY = event.touches.length ? event.touches[0].clientY : null;
            }, { passive: true });
            feed.addEventListener("touchmove", event => {
                if (touchY !== null && event.touches.length) {
                    const nextY = event.touches[0].clientY;
                    recordPace(touchY - nextY);
                    touchY = nextY;
                }
            }, { passive: true });

            sensorAttached = true;
            $("sensor").textContent = "FEED + SELECT* LINKED // BAR-SYNCED + SHIFT-GUARDED";
            return true;
        } catch (error) {
            sensorAttached = false;
            $("sensor").textContent = "FEED SENSOR BLOCKED // MANUAL TUNER ACTIVE";
            return false;
        }
    }

    function refreshControls() {
        const threshold = Number($("threshold").value);
        const lift = Number($("lift").value);
        const damping = Number($("smoothing").value);
        const timeSinceInput = performance.now() - lastScrollAt;
        const activeVelocity = timeSinceInput < 2200
            ? scrollVelocity * Math.exp(-Math.max(0, timeSinceInput - 180) / 650)
            : 0;
        const linkedTempo = $("scroll-link").checked && sensorAttached
            ? Math.min(lift, activeVelocity / threshold * lift)
            : 0;
        const target = baseBpm + linkedTempo;
        const now = performance.now();
        const delta = Math.min(0.2, Math.max(0.001, (now - lastTickAt) / 1000));
        lastTickAt = now;
        const blend = 1 - Math.exp(-delta / damping);
        smoothBpm += (target - smoothBpm) * blend;

        pendingMeter = sigSetting === "AUTO" ? desiredAutoMeter(activeVelocity, threshold) : sigSetting;
        if (!ctxState.running) activeMeter = pendingMeter;

        $("bpm").textContent = String(Math.round(smoothBpm)).padStart(3, "0");
        $("target-bpm").textContent = String(Math.round(target)).padStart(3, "0");
        $("pace").textContent = activeVelocity < 80 ? "IDLE" : activeVelocity >= threshold ? "FAST" : "ACTIVE";
        $("manual-value").textContent = String(baseBpm);
        $("threshold-value").textContent = String(threshold);
        $("lift-value").textContent = String(lift);
        $("smoothing-value").textContent = damping.toFixed(1);
        $("vol-value").textContent = String($("vol").value);
        const spec = METERS[activeMeter] || METERS["4/4"];
        $("meter-lbl").textContent = activeMeter + " · " + ((stepInBar % spec.steps) + 1) + "/" + spec.steps;
        $("meter-mode-lbl").textContent = sigSetting === "AUTO" ? ("AUTO -> " + pendingMeter) : ("LOCKED " + sigSetting);

        const normSmooth = Math.max(0, Math.min(100, (smoothBpm - 55) / (180 - 55) * 100));
        const normTarget = Math.max(0, Math.min(100, (target - 55) / (180 - 55) * 100));
        $("meter-smooth").style.width = normSmooth + "%";
        $("meter-target").style.left = "calc(" + normTarget + "% - 2px)";

        if (ctxState.running && ctxState.context && ctxState.context.state === "running") {
            const horizon = ctxState.context.currentTime + 0.12;
            const swing = SHEETS[activeSheetIdx].swing || 0;
            while (nextBeatAt < horizon) {
                playStep(nextBeatAt);
                const baseStep = 15 / smoothBpm; // 16th-note groove pulse
                const swingOffset = (stepInBar % 2 === 1 ? 1 : -1) * swing * baseStep;
                nextBeatAt += Math.max(0.04, baseStep + swingOffset);
            }
        }
        const total = elapsed + (ctxState.running ? (Date.now() - startedAt) : 0);
        const seconds = Math.floor(total / 1000);
        $("timer").textContent = String(Math.floor(seconds / 60)).padStart(2, "0") + ":" + String(seconds % 60).padStart(2, "0");
    }

    populateSheetSelect();
    selectSheet(0, null);
    if ($("sheet-select")) {
        $("sheet-select").addEventListener("change", e => {
            selectSheet(Number(e.target.value), "MANUAL PICK");
        });
    }
    if ($("next-sheet")) {
        $("next-sheet").addEventListener("click", () => {
            selectSheet((activeSheetIdx + 1) % SHEETS.length, "NEXT SHEET");
        });
    }

    $("manual").addEventListener("input", event => { baseBpm = Number(event.target.value); });
    $("threshold").addEventListener("input", refreshControls);
    $("lift").addEventListener("input", refreshControls);
    $("smoothing").addEventListener("input", refreshControls);
    $("vol").addEventListener("input", event => {
        if (ctxState.master) ctxState.master.gain.value = (Number(event.target.value) / 100) * 0.28;
        refreshControls();
    });
    $("scroll-link").addEventListener("change", () => {
        if (!sensorAttached) $("sensor").textContent = "FEED SENSOR UNAVAILABLE // MANUAL TEMPO ACTIVE";
    });

    document.querySelectorAll("[data-sig]").forEach(button => {
        button.addEventListener("click", () => {
            sigSetting = button.dataset.sig;
            document.querySelectorAll("[data-sig]").forEach(b => b.setAttribute("aria-pressed", String(b === button)));
            $("state").textContent = sigSetting === "AUTO" ? "METER: AUTO BY APP USAGE" : "METER LOCKED TO " + sigSetting + " (NEXT BAR)";
        });
    });

    document.querySelectorAll("[data-layer]").forEach(button => {
        button.addEventListener("click", () => {
            const name = button.dataset.layer;
            layerOn[name] = !layerOn[name];
            button.setAttribute("aria-pressed", String(layerOn[name]));
            setLayerGain(name, layerOn[name] ? (name === "melody" ? 0.36 : 0.45) : 0);
        });
    });

    $("power").addEventListener("click", async () => {
        initializeAudio();
        if (!ctxState.context) return;
        if (ctxState.running) {
            elapsed += Date.now() - startedAt;
            ctxState.running = false;
            await ctxState.context.suspend();
            $("power").innerHTML = "&#9654; RESUME SESSION";
            $("state").textContent = "PAUSED // YOUR TEMPO, YOUR CALL";
        } else {
            await ctxState.context.resume();
            ctxState.running = true;
            startedAt = Date.now();
            nextBeatAt = ctxState.context.currentTime + 0.05;
            $("power").innerHTML = "&#10074;&#10074; PAUSE SESSION";
            $("state").textContent = "SESSION LIVE // TUNE METER & LAYERS";
        }
    });

    $("reset").addEventListener("click", async () => {
        if (ctxState.context) await ctxState.context.suspend();
        elapsed = 0;
        ctxState.running = false;
        scrollVelocity = 0;
        lastScrollAt = 0;
        baseBpm = Number($("manual").value);
        smoothBpm = baseBpm;
        stepInBar = 0;
        barCount = 0;
        $("power").innerHTML = "&#9654; START SESSION";
        $("state").textContent = "SESSION ENDED // READY WHEN YOU ARE";
    });

    let lastDetectedAtm = null;
    function checkSubredditAtmosphere() {
        try {
            const sideEl = window.parent.document.querySelector(".side-post-header[data-subreddit]");
            if (sideEl) {
                const sub = (sideEl.getAttribute("data-subreddit") || "").toLowerCase();
                if (sub && sub !== lastDetectedAtm) {
                    lastDetectedAtm = sub;
                    if ($("auto-sample") && $("auto-sample").checked) {
                        const matchIdx = SHEETS.findIndex(sh => sh.subreddits.includes(sub));
                        if (matchIdx !== -1) {
                            selectSheet(matchIdx, "SYNC r/" + sub.toUpperCase());
                            return;
                        }
                    }
                    if (["ambientmusic", "slowliving", "slowweb", "typography", "fieldrecording", "audiophile"].includes(sub)) {
                        baseBpm = 68;
                        if (ctxState.padFilter && ctxState.context) {
                            ctxState.padFilter.frequency.setTargetAtTime(520, ctxState.context.currentTime, 0.25);
                        }
                        $("state").textContent = "ATMOSPHERE: r/" + sub.toUpperCase() + " // AMBIENT FOCUS [68 BPM]";
                    } else if (["jungle", "futurebeats", "chiptunes", "cyberdeck", "glitch_art"].includes(sub)) {
                        baseBpm = 142;
                        if (ctxState.padFilter && ctxState.context) {
                            ctxState.padFilter.frequency.setTargetAtTime(2600, ctxState.context.currentTime, 0.25);
                        }
                        $("state").textContent = "ATMOSPHERE: r/" + sub.toUpperCase() + " // BREAKBEAT CYBER [142 BPM]";
                    } else {
                        baseBpm = 88;
                        if (ctxState.padFilter && ctxState.context) {
                            ctxState.padFilter.frequency.setTargetAtTime(1100, ctxState.context.currentTime, 0.25);
                        }
                        $("state").textContent = "ATMOSPHERE: r/" + sub.toUpperCase() + " // ANALOG SATURATION [88 BPM]";
                    }
                    $("manual").value = Math.round(baseBpm);
                }
            } else if (lastDetectedAtm) {
                lastDetectedAtm = null;
                const sh = SHEETS[activeSheetIdx];
                baseBpm = sh.bpm || 96;
                $("manual").value = Math.round(baseBpm);
                if (ctxState.padFilter && ctxState.context) {
                    ctxState.padFilter.frequency.setTargetAtTime(sh.cutoff || 820, ctxState.context.currentTime, 0.25);
                }
                $("state").textContent = "SHEET: " + sh.title.toUpperCase() + " [" + Math.round(baseBpm) + " BPM]";
            }
        } catch (e) {}
    }

    let sideSensorAttached = false;
    function connectSideScrollSensor() {
        try {
            const side = window.parent.document.querySelector("[data-testid='stDialog'], [role='dialog'], .st-key-sidescroll");
            if (!side) {
                sideSensorAttached = false;
                return;
            }
            if (sideSensorAttached && side.isConnected) return;
            sideSensorAttached = true;
            let lastSideTop = side.scrollTop;
            
            side.addEventListener("scroll", () => {
                const dy = Math.abs(side.scrollTop - lastSideTop);
                lastSideTop = side.scrollTop;
                if (dy > 0) {
                    recordPace(dy * 1.5);
                    if (ctxState.context && ctxState.padFilter) {
                        const maxScroll = Math.max(1, side.scrollHeight - side.clientHeight);
                        const frac = Math.min(1, side.scrollTop / maxScroll);
                        const sweep = 550 + frac * 2200;
                        ctxState.padFilter.frequency.setTargetAtTime(sweep, ctxState.context.currentTime, 0.08);
                    }
                }
            }, { passive: true });
            
            side.addEventListener("wheel", e => recordPace(e.deltaY * 1.5), { passive: true });
        } catch (e) {}
    }

    setInterval(() => {
        if (!connectFeedSensor() && !sensorAttached) {
            $("sensor").textContent = activeView + " VIEW // SELECT* & MANUAL TUNER ACTIVE";
        }
        connectSideScrollSensor();
        checkSubredditAtmosphere();
    }, 450);
    setInterval(refreshControls, 25);

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
                    $("view-lbl").textContent = activeView;
                    playTunedInteraction("select", "SELECT* -> " + txt);
                }
                return;
            }

            if (!target.closest(".st-key-feedscroll, .st-key-sidescroll, .st-key-stage, [data-testid='stDialog'], [role='dialog']")) return;

            const btn = target.closest("button");
            if (btn) {
                const txt = (btn.innerText || btn.textContent || "").trim().toUpperCase();
                if (txt.includes("SAVE TO MEM")) {
                    playTunedInteraction("save", "SAVE TO MEM.");
                } else if (txt.includes("SAVED")) {
                    playTunedInteraction("unsave", "REMOVED FROM MEM.");
                } else if (txt.includes("LOAD NEXT SIDE")) {
                    playTunedInteraction("load", "LOAD NEXT SIDE");
                } else if (txt.includes("COMMENTS WINDOW") || txt.includes("SIDE COMMENTS") || txt.includes("OPEN TO SIDE")) {
                    playTunedInteraction("dock", "OPEN COMMENTS WINDOW");
                } else if (txt.includes("CLOSE DOCK") || txt.includes("CLOSE")) {
                    playTunedInteraction("undock", "CLOSE WINDOW");
                } else if (txt.includes("▲") || txt.includes("+1") || txt.includes("UPVOTE")) {
                    playTunedInteraction("upvote", "COMMENT ▲ UPVOTE (+1)");
                } else if (txt.includes("▼") || txt.includes("-1") || txt.includes("DOWNVOTE")) {
                    playTunedInteraction("downvote", "COMMENT ▼ DOWNVOTE (-1)");
                } else if (txt.includes("BROADCAST") || txt.includes("TRANSMIT")) {
                    playTunedInteraction("transmit", "SIGNAL BROADCAST");
                } else {
                    playTunedInteraction("btn", txt.slice(0, 16) || "BUTTON PRESS");
                }
                return;
            }
            if (target.closest(".side-comment-card, .comment-card")) {
                playTunedInteraction("select", "COMMENT FREQUENCY TOUCH");
                return;
            }
            if (target.closest(".card")) {
                playTunedInteraction("card", "CARD CLICK");
            } else {
                playTunedInteraction("click", "STAGE INTERACTION");
            }
        };

        const onParentKeyDown = e => {
            const target = e.target;
            if (!target || !target.closest) return;
            if (!target.closest(".st-key-menu, .st-key-feedscroll, .st-key-stage")) return;
            const now = performance.now();
            if (now - lastKeyAt < 75) return;
            lastKeyAt = now;
            playTunedInteraction("key", "KEY " + e.key.toUpperCase());
        };

        pDoc.addEventListener("pointerdown", onParentPointerDown, { capture: true, passive: true });
        pDoc.addEventListener("keydown", onParentKeyDown, { capture: true, passive: true });
        window.addEventListener("pagehide", () => {
            pDoc.removeEventListener("pointerdown", onParentPointerDown, { capture: true });
            pDoc.removeEventListener("keydown", onParentKeyDown, { capture: true });
            if (ctxState.context && ctxState.context.state !== "closed") ctxState.context.close().catch(() => {});
        });
    } catch (e) {}
})();
</script>
</body>
</html>
"""


def sonic_deck_html(sheets=None):
    import json
    from sheets import load_sheets
    data = sheets if sheets is not None else load_sheets()
    payload = json.dumps(data).replace("</", "<\\/")
    return SONIC_DECK_HTML.replace("__SHEETS_DATA__", payload)
