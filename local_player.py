"""Cassette player widget driven by an HTML5 <audio> element and the local music cache."""
import json
from spotify_player import TEMPLATE as _T

_head = _T.split("<script>")[0]
_head = _head.replace(
    '<div class="tray"><div class="k" style="margin-bottom:4px">SOURCE TRAY // SPOTIFY</div><div id="embed"></div></div>',
    '<audio id="au" preload="metadata"></audio><div class="vol"><span class="k">VOL</span><input id="vol" type="range" min="0" max="100" value="70"></div>'
)
# Updated accent-color to match the ZZZ electric yellow (#ffe600) and cyan links (#00f5ff)
_head = _head.replace(
    "</style>",
    ".vol{display:flex;gap:10px;align-items:center;margin-bottom:10px}.vol input{flex:1;accent-color:#ffe600}a{color:#00f5ff}</style>"
)

_JS = r"""<script>
const D = __DATA__;
const $ = i => document.getElementById(i);
const au = $("au");
const N = D.tracks.length;
let idx = 0;

const fmt = s => {
    s = Math.floor(s || 0);
    return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
};

function show() {
    const t = D.tracks[idx];
    $("tt").textContent = t.name;
    $("nm").className = "nm" + (t.name.length > 16 ? " mq" : "");
    $("ar").textContent = t.artist;
    $("al").textContent = t.album || "LOCAL CACHE";
    
    const c = $("cover");
    c.onerror = () => {
        c.onerror = null;
        c.src = t.fallback;
    };
    c.src = t.cover;
    $("ln").textContent = "TRK " + String(idx + 1).padStart(2, "0") + "/" + String(N).padStart(2, "0");
    
    $("note").innerHTML = "COVER: " + t.src + 
        (t.match ? " // " + t.match.replace(/</g, "&lt;") : "") + 
        (t.spotify ? ' // <a href="' + t.spotify + '" target="_blank" rel="noopener">OPEN ON SPOTIFY</a>' : "");
    
    document.querySelectorAll(".r").forEach((r, i) => r.classList.toggle("a", i === idx));
}

function render() {
    const d = au.duration || (D.tracks[idx].dur || 0) / 1000;
    $("cur").textContent = fmt(au.currentTime);
    $("tot").textContent = d ? fmt(d) : "--:--";
    $("fill").style.width = d ? Math.min(100, au.currentTime / d * 100) + "%" : "0";
    
    const p = !au.paused;
    $("dev").classList.toggle("on", p);
    $("pp").innerHTML = p ? "&#10074;&#10074; PAUSE" : "&#9654; PLAY";
}

function load(i, play) {
    idx = (i + N) % N;
    au.src = D.tracks[idx].url;
    show();
    render();
    if (play) {
        au.play().catch(() => {
            $("note").textContent = "CANNOT PLAY FILE // CHECK THE MUSIC FOLDER";
            $("note").style.color = "#ff4b4b";
        });
    }
}

if (!N) {
    $("tt").textContent = "NO TAPES";
    $("ar").textContent = "Put .mp3 files in: " + D.dir;
    $("note").textContent = "FILE NAMES: Title - Artist.mp3";
    ["pp", "pv", "nx"].forEach(i => $(i).disabled = true);
} else {
    D.tracks.forEach((t, i) => {
        const r = document.createElement("div");
        r.className = "r";
        r.innerHTML = "<span>" + String(i + 1).padStart(2, "0") + "</span><span></span><span>" + (t.dur ? fmt(t.dur / 1000) : "--:--") + "</span>";
        r.children[1].textContent = t.name + " // " + t.artist;
        r.onclick = () => load(i, true);
        $("list").appendChild(r);
    });

    au.volume = .7;
    load(0, false);

    $("pp").onclick = () => au.paused ? au.play() : au.pause();
    $("pv").onclick = () => au.currentTime > 3 ? (au.currentTime = 0) : load(idx - 1, true);
    $("nx").onclick = () => load(idx + 1, true);
    $("vol").oninput = e => au.volume = e.target.value / 100;
    
    $("bar").onclick = e => {
        if (au.duration) {
            const b = $("bar").getBoundingClientRect();
            au.currentTime = (e.clientX - b.left) / b.width * au.duration;
        }
    };

    ["timeupdate", "play", "pause", "loadedmetadata"].forEach(ev => au.addEventListener(ev, render));
    
    au.addEventListener("loadedmetadata", () => {
        const r = document.querySelectorAll(".r")[idx];
        if (r) r.children[2].textContent = fmt(au.duration);
    });
    
    au.addEventListener("ended", () => load(idx + 1, true));
    au.addEventListener("error", () => {
        $("note").textContent = "CANNOT LOAD FILE // IS THE LOCAL SERVER RUNNING?";
        $("note").style.color = "#ff4b4b";
    });
}
</script></body></html>"""

def player_html(tracks, music_dir=""):
    data = json.dumps({"tracks": tracks, "dir": str(music_dir)}).replace("</", "<\\/")
    return _head + _JS.replace("__DATA__", data)