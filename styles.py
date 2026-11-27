"""Formicapunk OS CSS stylesheet."""

APP_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Space+Mono:wght@400;700&display=swap');

:root {
    --bg: #0b0e14;
    --p1: #131722;
    --p2: #1b2030;
    --ln: #2e364f;
    --yellow: #ffe600;
    --cyan: #00f5ff;
    --magenta: #ff007f;
    --orange: #ff6600;
    --ink: #f0f2f5;
    --dim: #8c95ad;
}

.stApp {
    background: radial-gradient(circle at 15% 0%, #1a1e36, transparent 45%),
                radial-gradient(circle at 90% 95%, #102638, transparent 50%),
                var(--bg);
    font-family: 'Space Mono', monospace;
    color: var(--ink);
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background: radial-gradient(rgba(255,255,255,.05) 1px, transparent 1.3px) 0 0/6px 6px;
}

.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 99;
    opacity: .18;
    background: repeating-linear-gradient(0deg, transparent 0 2px, rgba(0,0,0,.4) 2px 3px);
    animation: fl 6s steps(60) infinite;
}

@keyframes fl { 50% { opacity: .12; } }

header[data-testid=stHeader] { background: transparent; }
[data-testid=stSidebar], footer { display: none; }
.block-container { max-width: 1520px; padding-top: 1.1rem; position: relative; z-index: 2; }

.top { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.badge { font: 400 15px Anton; letter-spacing: .1em; background: var(--yellow); color: var(--bg); padding: 6px 16px; transform: skewX(-10deg); }
.title { font: 400 clamp(40px, 7vw, 84px)/.95 Anton; text-transform: uppercase; font-style: italic; color: #fff; letter-spacing: .01em; text-shadow: 3px 0 var(--magenta), -3px 0 var(--cyan); }
.title .os { color: var(--yellow); text-shadow: 3px 0 var(--orange); }

.mini { font: 700 11px 'Space Mono'; color: var(--dim); letter-spacing: .14em; display: flex; gap: 12px; align-items: center; margin: 4px 0 14px; flex-wrap: wrap; }
.pill { border: 1.5px solid var(--cyan); color: var(--cyan); padding: 1px 10px; }
.hex { background: var(--orange); color: var(--bg); padding: 3px 9px; clip-path: polygon(25% 0, 75% 0, 100% 50%, 75% 100%, 25% 100%, 0 50%); }
.live { color: var(--magenta); }

.cap { font: 700 10px 'Space Mono'; letter-spacing: .16em; color: var(--dim); margin: 2px 0 8px; }

.st-key-menu, .st-key-stage { background: var(--p1); border: 2px solid var(--ln); padding: 16px; position: relative; }
.st-key-menu { clip-path: polygon(0 0, calc(100% - 22px) 0, 100% 22px, 100% 100%, 0 100%); }
.st-key-stage { clip-path: polygon(0 0, calc(100% - 46px) 0, 100% 46px, 100% 100%, 40px 100%, 0 calc(100% - 40px)); border-color: var(--yellow); }
.st-key-stage::before { content: ""; position: absolute; inset: 0; pointer-events: none; background: linear-gradient(150deg, transparent 49.7%, rgba(255,230,0,.2) 50%, transparent 50.3%); }

.hazard { height: 10px; margin: 12px 0 6px; background: repeating-linear-gradient(135deg, var(--yellow) 0 8px, var(--bg) 8px 16px); }

/* Menu radio buttons: single-line labels, no native radio circle */
.st-key-menu [role=radiogroup] { gap: 10px; display: flex; flex-direction: column; }
.st-key-menu label {
    background: var(--p2);
    border: 2px solid var(--ln);
    padding: 12px 12px 12px 34px;
    position: relative;
    cursor: pointer;
    transition: .15s;
    transform: skewX(-6deg);
    overflow: hidden;
}
.st-key-menu label > div:first-child,
.st-key-menu [data-baseweb="radio"] > div:first-child { display: none !important; }
.st-key-menu label p {
    font: 400 clamp(15px, 1.35vw, 19px) Anton !important;
    letter-spacing: .06em;
    color: var(--dim) !important;
    white-space: nowrap !important;
    margin: 0 !important;
}
.st-key-menu label::before { content: "✦"; position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--ln); font-size: 14px; }
.st-key-menu label:has(input:checked) { background: var(--yellow); border-color: var(--yellow); transform: translateX(6px) skewX(-6deg); box-shadow: 4px 4px 0 var(--magenta); }
.st-key-menu label:has(input:checked) p { color: var(--bg) !important; }
.st-key-menu label:has(input:checked)::before { color: var(--bg); }
.st-key-menu label:hover { border-color: var(--cyan); transform: translateX(3px) skewX(-6deg); }

.st-key-audiomode { margin-bottom: 10px; }
.st-key-audiomode [role=radiogroup] { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.st-key-audiomode label { background: var(--p2); border: 2px solid var(--ln); padding: 8px 6px; cursor: pointer; transform: skewX(-4deg); transition: .15s; margin: 0 !important; justify-content: center; }
.st-key-audiomode label > div:first-child,
.st-key-audiomode [data-baseweb="radio"] > div:first-child { display: none !important; }
.st-key-audiomode label p { font: 400 13px Anton !important; letter-spacing: .06em; color: var(--dim) !important; text-align: center; white-space: nowrap !important; }
.st-key-audiomode label:has(input:checked) { background: var(--yellow); border-color: var(--yellow); box-shadow: 3px 3px 0 var(--magenta); }
.st-key-audiomode label:has(input:checked) p { color: var(--bg) !important; }
.st-key-audiomode label:hover { border-color: var(--cyan); }

.stats { display: flex; gap: 10px; justify-content: flex-end; margin-bottom: 6px; }
.tile { border: 2px solid var(--ln); background: var(--p2); padding: 4px 14px; text-align: center; font: 700 9px 'Space Mono'; color: var(--dim); letter-spacing: .14em; }
.tile b { display: block; font: 400 24px Anton; color: var(--yellow); letter-spacing: .04em; }

.st-key-feedscroll { padding-right: 6px; }
.st-key-feedscroll *::-webkit-scrollbar { width: 8px; }
.st-key-feedscroll *::-webkit-scrollbar-thumb { background: var(--yellow); }

.card { background: var(--p2); border: 2px solid var(--ln); border-left: 6px solid var(--yellow); margin: 0 0 6px; position: relative; clip-path: polygon(0 0, calc(100% - 22px) 0, 100% 22px, 100% 100%, 0 100%); }
.pic { position: relative; aspect-ratio: 16/9; overflow: hidden; background: var(--bg); border-bottom: 3px solid var(--yellow); }
.pic img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform .6s; }
.card:hover .pic img { transform: scale(1.05); }
.pic::after { content: ""; position: absolute; inset: 0; pointer-events: none; background: radial-gradient(rgba(0,0,0,.35) 1px, transparent 1.4px) 0 0/4px 4px, repeating-linear-gradient(0deg, transparent 0 2px, rgba(0,0,0,.25) 2px 3px); }

.tg { position: absolute; left: 10px; bottom: 8px; z-index: 2; background: var(--bg); color: var(--yellow); font: 700 9px 'Space Mono'; letter-spacing: .14em; padding: 2px 8px; }
.rc { position: absolute; right: 30px; top: 8px; z-index: 2; color: var(--magenta); font: 700 10px 'Space Mono'; letter-spacing: .14em; animation: bl 1.2s steps(2) infinite; }
@keyframes bl { 50% { opacity: .2; } }

.bd { padding: 12px 16px; }
.bd .l { display: flex; justify-content: space-between; font: 700 10px 'Space Mono'; letter-spacing: .14em; color: var(--cyan); margin-bottom: 6px; }
.bd h3 { font: 400 clamp(18px, 2.4vw, 26px)/1.15 Anton; text-transform: uppercase; letter-spacing: .03em; margin: 0 0 6px; color: #fff; }
.bd p { color: #b9b6d4; font-size: 12px; line-height: 1.6; max-width: 100%; margin: 0 0 8px; }
.bd small { color: var(--dim); letter-spacing: .08em; }

@keyframes rise { from { opacity: 0; transform: translateY(46px) skewY(2deg); } to { opacity: 1; transform: none; } }
.card { animation: rise .7s cubic-bezier(.2, .8, .2, 1) both; animation-delay: calc(var(--i) * 120ms); }

.gap { height: 40px; background: repeating-linear-gradient(135deg, transparent 0 10px, rgba(255,230,0,.15) 10px 12px); margin: 6px 0; }

.stButton>button { border-radius: 0; border: 2px solid var(--yellow); font: 400 15px Anton; letter-spacing: .1em; color: var(--yellow); background: var(--bg); transform: skewX(-8deg); width: 100%; }
.stButton>button:hover { background: var(--yellow); color: var(--bg); border-color: var(--yellow); }
.stButton>button:disabled { opacity: .4; }

.spool { background: var(--p1); border: 2px solid var(--ln); padding: 14px 0 4px; overflow: hidden; margin-bottom: 8px; }
.strip { position: relative; height: 76px; }
.tape-line { position: absolute; left: 190px; right: 20px; top: 50%; height: 6px; margin-top: -3px; background: repeating-linear-gradient(90deg, var(--yellow) 0 10px, var(--magenta) 10px 20px); box-shadow: 0 0 8px var(--yellow); }
.full-cassette { position: absolute; left: 10px; top: 2px; width: 170px; background: #e9e6f5; border: 3px solid #0c0c10; outline: 2px solid #8b88a8; border-radius: 8px; padding: 6px; color: #0c0c10; }
.cass-lab { background: #fff; border: 2px solid #0c0c10; padding: 2px 6px; font: 400 11px Anton; display: flex; justify-content: space-between; letter-spacing: .06em; }
.cass-stripe { height: 6px; background: linear-gradient(90deg, #ff5b1f 0 33%, #d4ff1a 33% 66%, #34e6ff 66%); margin: 3px 0; }
.cass-win { background: #0c0c10; border-radius: 20px; margin: 2px 4px 0; display: flex; justify-content: space-around; padding: 2px; }

.reel { transform-box: fill-box; transform-origin: center; animation: sp 5s linear infinite; }
.spool.go .reel { animation-duration: .45s; }
.spool.go .full-cassette { animation: driveFull 3s linear forwards; }
.spool.go .tape-line { animation: eatFull 3s linear forwards, crawl .35s linear infinite; }

@keyframes driveFull { from { left: 10px; } to { left: calc(100% - 185px); } }
@keyframes eatFull { from { clip-path: inset(0 0 0 0); } to { clip-path: inset(0 0 0 100%); } }
@keyframes crawl { to { background-position: -20px 0; } }
@keyframes sp { to { transform: rotate(360deg); } }

.barcode { position: fixed; right: 8px; top: 22%; height: 38%; width: 20px; background: repeating-linear-gradient(0deg, var(--yellow) 0 2px, transparent 2px 4px, var(--yellow) 4px 5px, transparent 5px 9px); opacity: .7; z-index: 5; }

.sleepy-cat-corner {
    position: fixed; bottom: 24px; right: 24px; width: 130px;
    background: var(--p1); border: 2px solid var(--yellow); box-shadow: 4px 4px 0 var(--magenta);
    z-index: 100; padding: 6px; text-align: center;
    transition: bottom .25s ease;
    clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 0 100%);
}
.sleepy-cat-corner img { width: 100%; height: auto; display: block; border: 1px solid var(--ln); }
.sleepy-cat-corner span { display: block; font: 700 9px 'Space Mono'; color: var(--yellow); letter-spacing: .1em; margin-top: 4px; }

.status { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-top: 14px; background: var(--yellow); color: var(--bg); padding: 6px 16px; font: 700 10px 'Space Mono'; letter-spacing: .16em; }
.plain { background: var(--p2); border: 2px solid var(--ln); padding: 14px; color: #b9b6d4; font-size: 12px; line-height: 1.7; }

label, .stSelectSlider label p, [data-testid=stWidgetLabel] p { color: var(--ink)!important; font-family: 'Space Mono'!important; }
textarea { background: var(--p2)!important; color: var(--ink)!important; font-family: 'Space Mono'!important; }

/* In-Card Comments Drawer */
.comments-drawer { margin-top: 10px; border: 1px solid var(--ln); background: var(--p1); transition: all .2s ease; }
.comments-drawer[open] { border-color: var(--cyan); box-shadow: 0 0 10px rgba(0, 245, 255, 0.15); }
.comments-toggle {
    display: flex; justify-content: space-between; align-items: center; padding: 8px 12px;
    background: var(--p2); cursor: pointer; font: 700 10px 'Space Mono', monospace;
    letter-spacing: .08em; color: var(--cyan); user-select: none; list-style: none; border-left: 3px solid var(--cyan);
}
.comments-toggle::-webkit-details-marker { display: none; }
.comments-toggle:hover { background: #232c42; color: var(--yellow); border-left-color: var(--yellow); }
.comments-drawer[open] .comments-toggle { background: var(--p1); border-bottom: 1px solid var(--ln); border-left-color: var(--yellow); color: var(--yellow); }
.cmt-toggle-left, .cmt-toggle-right { display: flex; align-items: center; gap: 8px; }
.cmt-badge { background: rgba(0, 245, 255, 0.12); color: var(--cyan); border: 1px solid rgba(0, 245, 255, 0.4); padding: 2px 6px; font-size: 9px; font-weight: 700; }
.cmt-action { color: var(--dim); font-size: 9px; letter-spacing: .1em; }
.comments-drawer[open] .cmt-action { color: var(--magenta); }
.comments-body { padding: 10px; display: flex; flex-direction: column; gap: 8px; max-height: 360px; overflow-y: auto; background: rgba(11, 14, 20, 0.9); }
.comments-body::-webkit-scrollbar { width: 6px; }
.comments-body::-webkit-scrollbar-thumb { background: var(--cyan); }
.comments-bar { display: flex; justify-content: space-between; font-size: 9px; color: var(--dim); letter-spacing: .12em; padding-bottom: 4px; border-bottom: 1px dashed var(--ln); }
.comments-footer { text-align: center; font-size: 8px; color: var(--dim); letter-spacing: .15em; padding: 4px 0 2px; }

/* Shared Comment Card & Window Header */
.side-post-header { background: var(--p2); border: 1px solid var(--ln); border-left: 4px solid var(--yellow); padding: 10px 12px; margin-bottom: 10px; }
.side-post-header h4 { font: 400 18px/1.2 Anton, sans-serif; color: #fff; text-transform: uppercase; margin: 4px 0 6px; letter-spacing: .02em; }
.side-genre-badge { display: inline-block; background: rgba(0, 245, 255, 0.12); border: 1px solid var(--cyan); color: var(--cyan); font: 700 9px 'Space Mono', monospace; letter-spacing: .12em; padding: 2px 7px; margin-top: 4px; }

.cmt-card { background: var(--p1); border: 1px solid #283046; border-left: 3px solid var(--cyan); padding: 8px 10px; margin-bottom: 6px; font-family: 'Space Mono', monospace; transition: border-left-color .15s, background .15s; }
.cmt-card:hover { border-left-color: var(--yellow); background: #171d2c; }
.cmt-head { display: flex; justify-content: space-between; align-items: center; font-size: 10px; margin-bottom: 4px; flex-wrap: wrap; gap: 4px; }
.cmt-user { color: var(--yellow); font-weight: 700; }
.cmt-pts { font-weight: 700; padding: 1px 6px; font-size: 9px; display: inline-block; }
.cmt-pts.pos { background: rgba(0, 245, 255, 0.12); color: var(--cyan); border: 1px solid rgba(0, 245, 255, 0.3); }
.cmt-pts.high { background: rgba(255, 230, 0, 0.15); color: var(--yellow); border: 1px solid var(--yellow); }
.cmt-pts.neg { background: rgba(255, 0, 127, 0.15); color: var(--magenta); border: 1px solid var(--magenta); }
.cmt-time { color: var(--dim); font-size: 9px; margin-left: 4px; }
.cmt-msg { font-size: 11px; line-height: 1.5; color: #cbd2e1; margin: 0; white-space: pre-wrap; word-break: break-word; }

@media (prefers-reduced-motion: reduce) {
    .card, .reel, .rc, .tape-line, .full-cassette, .stApp::after { animation: none !important; }
}
</style>
<div class="barcode"></div>
<div class="sleepy-cat-corner"><img src="https://i.pinimg.com/originals/1a/5a/b6/1a5ab6b62dc1e65d28844539450f615c.gif" alt="Sleeping Cat"><span>Zzz... [IDLE]</span></div>
"""
