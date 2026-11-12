"""Cassette player widget (HTML/JS) driven by Spotify's iFrame API."""
import json

TEMPLATE = r"""<!doctype html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Space+Mono:wght@400;700&display=swap');
*{box-sizing:border-box}body{margin:0;background:transparent;color:#ecebff;font-family:'Space Mono',monospace}
.dev{background:#17171e;border:2px solid #d4ff1a;padding:12px;clip-path:polygon(0 0,calc(100% - 26px) 0,100% 26px,100% 100%,26px 100%,0 calc(100% - 26px));position:relative}
.dev::before{content:"";position:absolute;inset:0;pointer-events:none;z-index:5;background:repeating-linear-gradient(0deg,transparent 0 2px,rgba(0,0,0,.22) 2px 3px)}
.hz{height:8px;background:repeating-linear-gradient(135deg,#d4ff1a 0 8px,#0c0c10 8px 16px);margin-bottom:10px}
.top{display:flex;justify-content:space-between;font-size:9px;letter-spacing:.18em;color:#8b88a8;margin-bottom:8px}
.rec{color:#ff3fa4;opacity:.25}.on .rec{opacity:1;animation:bl 1s steps(2) infinite}@keyframes bl{50%{opacity:.2}}
.row{display:flex;gap:10px}.cov{width:96px;height:96px;flex:none;border:2px solid #fff;position:relative;background:#0c0c10}
.cov img{width:100%;height:100%;object-fit:cover;display:block}
.cov::after{content:"";position:absolute;inset:-6px;border:2px solid #34e6ff;clip-path:polygon(0 0,18px 0,18px 2px,2px 2px,2px 18px,0 18px,0 0,100% 100%,calc(100% - 18px) 100%,calc(100% - 18px) calc(100% - 2px),calc(100% - 2px) calc(100% - 2px),calc(100% - 2px) calc(100% - 18px),100% calc(100% - 18px))}
.meta{min-width:0;flex:1;display:flex;flex-direction:column;justify-content:space-between}
.k{font-size:9px;letter-spacing:.18em;color:#8b88a8}.v{font-size:11px;color:#ecebff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nm{font:400 24px/1.1 Anton;text-transform:uppercase;color:#d4ff1a;white-space:nowrap;overflow:hidden;text-shadow:2px 0 #ff3fa4,-2px 0 #34e6ff}
.nm span{display:inline-block}.nm.mq span{padding-left:100%;animation:mq 12s linear infinite}@keyframes mq{to{transform:translateX(-100%)}}
.tape{margin:14px 0;background:#e9e6f5;border:3px solid #0c0c10;outline:2px solid #8b88a8;border-radius:10px;padding:8px;color:#0c0c10}
.lab{background:#fff;border:2px solid #0c0c10;padding:3px 8px;font:400 13px Anton;display:flex;justify-content:space-between;letter-spacing:.06em}
.stripe{height:9px;background:linear-gradient(90deg,#ff5b1f 0 33%,#d4ff1a 33% 66%,#34e6ff 66%)}
.win{background:#0c0c10;border-radius:34px;margin:8px 14px 0;display:flex;justify-content:space-around;padding:4px}
.reel{transform-box:fill-box;transform-origin:center}.on .reel{animation:sp 2.2s linear infinite}@keyframes sp{to{transform:rotate(360deg)}}
.lcd{background:#0c0c10;border:2px solid #34e6ff;padding:8px 10px}
.tm{display:flex;justify-content:space-between;align-items:baseline;font:700 24px 'Space Mono';color:#d4ff1a;text-shadow:0 0 8px #d4ff1a88}.tm small{font-size:11px;color:#8b88a8;text-shadow:none}
.bar{height:12px;border:2px solid #8b88a8;margin:6px 0;cursor:pointer;background:#0c0c10}.bar i{display:block;height:100%;width:0;background:repeating-linear-gradient(90deg,#d4ff1a 0 4px,#8aa80e 4px 6px)}
.vu{display:flex;gap:3px;align-items:end;height:22px}.vu b{flex:1;height:4px;background:#ff5b1f}.on .vu b{animation:vu .9s ease-in-out infinite}
.vu b:nth-child(3n){animation-delay:.15s}.vu b:nth-child(3n+1){animation-delay:.4s}.vu b:nth-child(5n){background:#d4ff1a;animation-delay:.6s}@keyframes vu{50%{height:22px}}
.btns{display:grid;grid-template-columns:1fr 1.5fr 1fr;gap:8px;margin:10px 0}
button{font:400 18px Anton;letter-spacing:.08em;background:#0c0c10;color:#d4ff1a;border:2px solid #d4ff1a;padding:8px;cursor:pointer;transform:skewX(-8deg)}
button:hover{background:#d4ff1a;color:#0c0c10}button:focus-visible{outline:3px solid #34e6ff}
.tray{border:2px dashed #8b88a8;padding:6px;margin-bottom:10px}.tray iframe{display:block;border-radius:0}
.list{max-height:150px;overflow:auto;border-top:2px solid #34344a}
.r{display:flex;gap:8px;font-size:11px;padding:5px 6px;border-bottom:1px solid #2a2a38;cursor:pointer;color:#bdbad6}.r:hover{background:#1f1f29}
.r.a{background:#d4ff1a;color:#0c0c10;font-weight:700}.r span:nth-child(2){flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.note{font-size:9px;color:#8b88a8;letter-spacing:.08em;line-height:1.5;margin-top:6px}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
</style></head><body><div class="dev" id="dev"><div class="hz"></div>
<div class="top"><span>CASSETTE DECK // SANCTUARY-01</span><span class="rec">&#9679; REC</span></div>
<div class="row"><div class="cov"><img id="cover" alt="Album cover" src=""></div><div class="meta">
<div><div class="k">TITLE</div><div class="nm" id="nm"><span id="tt">INSERT TAPE</span></div></div>
<div><div class="k">ARTIST</div><div class="v" id="ar">-</div></div><div><div class="k">ALBUM</div><div class="v" id="al">-</div></div></div></div>
<div class="tape"><div class="lab"><span id="lt">SIDE A</span><span id="ln">TRK --</span></div><div class="stripe"></div>
<div class="win"><svg viewBox="0 0 220 60" width="100%" height="56" aria-hidden="true">
<g class="reel"><circle cx="55" cy="30" r="22" fill="#e9e6f5"/><path d="M55 10v40M35 30h40M41 16l28 28M69 16l-28 28" stroke="#0c0c10" stroke-width="3"/></g>
<g class="reel"><circle cx="165" cy="30" r="22" fill="#e9e6f5"/><path d="M165 10v40M145 30h40M151 16l28 28M179 16l-28 28" stroke="#0c0c10" stroke-width="3"/></g>
<path d="M77 30h66" stroke="#8b88a8" stroke-width="3" stroke-dasharray="3 4"/></svg></div></div>
<div class="lcd"><div class="tm"><span id="cur">--:--</span><small>/ <span id="tot">--:--</span></small></div><div class="bar" id="bar"><i id="fill"></i></div>
<div class="vu"><b></b><b></b><b></b><b></b><b></b><b></b><b></b><b></b><b></b><b></b><b></b><b></b><b></b><b></b></div></div>
<div class="btns"><button id="pv" aria-label="Previous track">&#9664;&#9664;</button><button id="pp" aria-label="Play or pause">&#9654; PLAY</button><button id="nx" aria-label="Next track">&#9654;&#9654;</button></div>
<div class="tray"><div class="k" style="margin-bottom:4px">SOURCE TRAY // SPOTIFY</div><div id="embed"></div></div>
<div class="list" id="list"></div><div class="note" id="note"></div></div>
<script>
const D=__DATA__,$=i=>document.getElementById(i),M={};let C=null,idx=0,playing=false,dur=0,pos=0,curU="";
const fmt=ms=>{const s=Math.floor((ms||0)/1000);return String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0")};
function show(t){$("tt").textContent=t.name||"UNKNOWN";$("nm").className="nm"+((t.name||"").length>16?" mq":"");$("ar").textContent=t.artist||("PLAYLIST // "+D.playlist.name);
$("al").textContent=t.album||("by "+D.playlist.owner);if(t.cover)$("cover").src=t.cover;$("ln").textContent="TRK "+String(Math.max(idx,0)+1).padStart(2,"0");
document.querySelectorAll(".r").forEach((r,i)=>r.classList.toggle("a",i===idx&&D.tracks.length>0));if(t.dur&&!dur)$("tot").textContent=fmt(t.dur)}
function render(){const d=dur||(D.tracks[idx]||{}).dur||0;$("cur").textContent=fmt(pos);$("tot").textContent=d?fmt(d):"--:--";$("fill").style.width=d?Math.min(100,pos/d*100)+"%":"0";
$("dev").classList.toggle("on",playing);$("pp").innerHTML=playing?"&#10074;&#10074; PAUSE":"&#9654; PLAY"}
async function meta(u){if(M[u]!==undefined)return M[u];try{const r=await fetch("https://open.spotify.com/oembed?url="+encodeURIComponent("https://open.spotify.com/track/"+u.split(":").pop()));const j=await r.json();M[u]={name:j.title,cover:j.thumbnail_url}}catch(e){M[u]=null}return M[u]}
function go(i){if(!C||!D.tracks.length)return;idx=(i+D.tracks.length)%D.tracks.length;curU=D.tracks[idx].uri;dur=0;pos=0;C.loadUri(curU);C.play();show(D.tracks[idx]);render()}
D.tracks.forEach((t,i)=>{const r=document.createElement("div");r.className="r";r.innerHTML="<span>"+String(i+1).padStart(2,"0")+"</span><span></span><span>"+fmt(t.dur)+"</span>";r.children[1].textContent=t.name+" // "+t.artist;r.onclick=()=>go(i);$("list").appendChild(r)});
$("note").textContent=D.tracks.length?"FULL METADATA MODE // WEB API":"EMBED MODE // ADD SPOTIFY KEYS FOR TRACK LIST. USE SOURCE TRAY TO SKIP. LOGGED-IN SPOTIFY = FULL SONGS, OTHERWISE 30S PREVIEWS.";
if(!D.tracks.length)$("list").style.display="none";
show(D.tracks[0]||{name:D.playlist.name,cover:D.playlist.cover,album:"by "+D.playlist.owner+" // "+D.playlist.count+" TRACKS"});render();
$("pp").onclick=()=>C&&C.togglePlay();$("pv").onclick=()=>go(idx-1);$("nx").onclick=()=>go(idx+1);
$("bar").onclick=e=>{if(C&&dur){const b=$("bar").getBoundingClientRect();C.seek(Math.floor((e.clientX-b.left)/b.width*dur/1000))}};
window.onSpotifyIframeApiReady=API=>{API.createController($("embed"),{uri:D.tracks.length?D.tracks[0].uri:"spotify:playlist:"+D.playlist.id,width:"100%",height:80},c=>{C=c;
c.addListener("playback_update",async e=>{const d=e.data;dur=d.duration||0;pos=d.position||0;playing=!d.isPaused&&!d.isBuffering;render();const u=d.playingURI;
if(u&&u!==curU){curU=u;let k=D.tracks.findIndex(x=>x.uri===u);if(k>=0){idx=k;show(D.tracks[k])}else{const m=await meta(u);if(m)show(m)}}})})};
const s=document.createElement("script");s.src="https://open.spotify.com/embed/iframe-api/v1";s.async=true;document.body.appendChild(s);
</script></body></html>"""

def player_html(playlist, tracks):
    data = json.dumps({"playlist": playlist, "tracks": tracks}).replace("</", "<\\/")
    return TEMPLATE.replace("__DATA__", data)