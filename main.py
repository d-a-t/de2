import time
import json
import html
import streamlit as st
import streamlit.components.v1 as components
from data import get_posts, art
from music import load_library, MUSIC_DIR, clear_cover_cache
from sheets import load_sheets, save_sheet, SHEETS_DIR
from spotify import has_keys
from local_player import player_html
from scroll_proto_player import scroll_proto_html
from sonic_deck import sonic_deck_html

st.set_page_config(
    page_title="Formicapunk OS", 
    page_icon="✦", 
    layout="wide"
)

tracks = load_library()
sheets = load_sheets()
S = st.session_state
S.setdefault("block", 1)
S.setdefault("saved", [])
S.setdefault("per", 3)
S.setdefault("spooling", False)
S.setdefault("player_mode", "CASSETTE DECK")
S.setdefault("force_svg_fallback", False)
S.setdefault("side_post_idx", None)

if "posts" not in S:
    p_init, live_init = get_posts()
    S.posts = p_init
    S.live = live_init

posts = S.posts
live = S.live

SRC = {"API": "REDDIT API", "RSS": "REDDIT RSS", "JSON": "REDDIT JSON"}.get(posts[0].get("src", ""), "REDDIT") if live else ""

st.markdown("""<style>
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

.st-key-menu [role=radiogroup] { gap: 10px; display: flex; flex-direction: column; }
.st-key-menu label { background: var(--p2); border: 2px solid var(--ln); padding: 14px 16px 14px 40px; position: relative; cursor: pointer; transition: .15s; transform: skewX(-6deg); }
.st-key-menu label>div:first-child { display: none; }
.st-key-menu label p { font: 400 22px Anton !important; letter-spacing: .08em; color: var(--dim) !important; }
.st-key-menu label::before { content: "✦"; position: absolute; left: 14px; top: 50%; transform: translateY(-50%); color: var(--ln); font-size: 16px; }
.st-key-menu label:has(input:checked) { background: var(--yellow); border-color: var(--yellow); transform: translateX(8px) skewX(-6deg); box-shadow: 4px 4px 0 var(--magenta); }
.st-key-menu label:has(input:checked) p { color: var(--bg) !important; }
.st-key-menu label:has(input:checked)::before { color: var(--bg); }
.st-key-menu label:hover { border-color: var(--cyan); transform: translateX(4px) skewX(-6deg); }

.st-key-audiomode { margin-bottom: 10px; }
.st-key-audiomode [role=radiogroup] { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.st-key-audiomode label { background: var(--p2); border: 2px solid var(--ln); padding: 8px 6px; cursor: pointer; transform: skewX(-4deg); transition: .15s; margin: 0 !important; justify-content: center; }
.st-key-audiomode label>div:first-child { display: none; }
.st-key-audiomode label p { font: 400 13px Anton !important; letter-spacing: .06em; color: var(--dim) !important; text-align: center; }
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

/* Full Detailed Cassette Styling matching the player deck */
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
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 130px;
    background: var(--p1);
    border: 2px solid var(--yellow);
    box-shadow: 4px 4px 0 var(--magenta);
    z-index: 100;
    padding: 6px;
    text-align: center;
    clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 0 100%);
}
.sleepy-cat-corner img { width: 100%; height: auto; display: block; border: 1px solid var(--ln); }
.sleepy-cat-corner span { display: block; font: 700 9px 'Space Mono'; color: var(--yellow); letter-spacing: .1em; margin-top: 4px; }

.status { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-top: 14px; background: var(--yellow); color: var(--bg); padding: 6px 16px; font: 700 10px 'Space Mono'; letter-spacing: .16em; }
.plain { background: var(--p2); border: 2px solid var(--ln); padding: 14px; color: #b9b6d4; font-size: 12px; line-height: 1.7; }

label, .stSelectSlider label p, [data-testid=stWidgetLabel] p { color: var(--ink)!important; font-family: 'Space Mono'!important; }
textarea { background: var(--p2)!important; color: var(--ink)!important; font-family: 'Space Mono'!important; }

/* In-Card Comments Section */
.comments-drawer {
    margin-top: 10px;
    border: 1px solid var(--ln);
    background: var(--p1);
    transition: all .2s ease;
}
.comments-drawer[open] {
    border-color: var(--cyan);
    box-shadow: 0 0 10px rgba(0, 245, 255, 0.15);
}
.comments-toggle {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: var(--p2);
    cursor: pointer;
    font: 700 10px 'Space Mono', monospace;
    letter-spacing: .08em;
    color: var(--cyan);
    user-select: none;
    transition: background .15s, color .15s, border-color .15s;
    list-style: none;
    border-left: 3px solid var(--cyan);
}
.comments-toggle::-webkit-details-marker { display: none; }
.comments-toggle:hover {
    background: #232c42;
    color: var(--yellow);
    border-left-color: var(--yellow);
}
.comments-drawer[open] .comments-toggle {
    background: var(--p1);
    border-bottom: 1px solid var(--ln);
    border-left-color: var(--yellow);
    color: var(--yellow);
}
.cmt-toggle-left {
    display: flex;
    align-items: center;
    gap: 8px;
}
.cmt-toggle-right {
    display: flex;
    align-items: center;
    gap: 8px;
}
.cmt-badge {
    background: rgba(0, 245, 255, 0.12);
    color: var(--cyan);
    border: 1px solid rgba(0, 245, 255, 0.4);
    padding: 2px 6px;
    font-size: 9px;
    font-weight: 700;
}
.cmt-action {
    color: var(--dim);
    font-size: 9px;
    letter-spacing: .1em;
}
.comments-drawer[open] .cmt-action {
    color: var(--magenta);
}
.comments-body {
    padding: 10px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 360px;
    overflow-y: auto;
    background: rgba(11, 14, 20, 0.9);
}
.comments-body::-webkit-scrollbar {
    width: 6px;
}
.comments-body::-webkit-scrollbar-thumb {
    background: var(--cyan);
}
.comments-bar {
    display: flex;
    justify-content: space-between;
    font-size: 9px;
    color: var(--dim);
    letter-spacing: .12em;
    padding-bottom: 4px;
    border-bottom: 1px dashed var(--ln);
}
.comment-card {
    background: var(--p1);
    border: 1px solid #23293d;
    border-left: 3px solid var(--cyan);
    padding: 8px 10px;
    font-family: 'Space Mono', monospace;
    transition: border-left-color .15s, background .15s;
}
.comment-card:hover {
    border-left-color: var(--yellow);
    background: #171d2c;
}
.comment-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 10px;
    margin-bottom: 4px;
    flex-wrap: wrap;
    gap: 4px;
}
.comment-user {
    color: var(--yellow);
    font-weight: 700;
    font-size: 10px;
}
.comment-pts {
    font-weight: 700;
    padding: 1px 6px;
    font-size: 9px;
    display: inline-block;
}
.comment-pts.pos {
    background: rgba(0, 245, 255, 0.12);
    color: var(--cyan);
    border: 1px solid rgba(0, 245, 255, 0.3);
}
.comment-pts.high {
    background: rgba(255, 230, 0, 0.15);
    color: var(--yellow);
    border: 1px solid var(--yellow);
}
.comment-pts.neg {
    background: rgba(255, 0, 127, 0.15);
    color: var(--magenta);
    border: 1px solid var(--magenta);
}
.comment-time {
    color: var(--dim);
    font-size: 9px;
    margin-left: 4px;
}
.comment-msg {
    font-size: 11px;
    line-height: 1.5;
    color: #cbd2e1;
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
}
.comments-footer {
    text-align: center;
    font-size: 8px;
    color: var(--dim);
    letter-spacing: .15em;
    padding: 4px 0 2px;
}

/* Side Comments Dock */
.side-post-header {
    background: var(--p2);
    border: 1px solid var(--ln);
    border-left: 4px solid var(--yellow);
    padding: 10px 12px;
    margin-bottom: 10px;
}
.side-post-header h4 {
    font: 400 18px/1.2 Anton, sans-serif;
    color: #fff;
    text-transform: uppercase;
    margin: 4px 0 6px;
    letter-spacing: .02em;
}
.side-genre-badge {
    display: inline-block;
    background: rgba(0, 245, 255, 0.12);
    border: 1px solid var(--cyan);
    color: var(--cyan);
    font: 700 9px 'Space Mono', monospace;
    letter-spacing: .12em;
    padding: 2px 7px;
    margin-top: 4px;
}
.side-comment-card {
    background: var(--p1);
    border: 1px solid #283046;
    border-left: 3px solid var(--cyan);
    padding: 8px 10px;
    margin-bottom: 6px;
    font-family: 'Space Mono', monospace;
    transition: all .15s ease;
}
.side-comment-card:hover {
    border-left-color: var(--yellow);
    background: #171d2c;
}
.side-comment-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 10px;
    margin-bottom: 4px;
    flex-wrap: wrap;
    gap: 4px;
}
.side-comment-user {
    color: var(--yellow);
    font-weight: 700;
}
.side-comment-score {
    font-weight: 700;
    padding: 1px 6px;
    font-size: 9px;
    display: inline-block;
}
.side-comment-score.pos {
    background: rgba(0, 245, 255, 0.12);
    color: var(--cyan);
    border: 1px solid rgba(0, 245, 255, 0.3);
}
.side-comment-score.high {
    background: rgba(255, 230, 0, 0.15);
    color: var(--yellow);
    border: 1px solid var(--yellow);
}
.side-comment-score.neg {
    background: rgba(255, 0, 127, 0.15);
    color: var(--magenta);
    border: 1px solid var(--magenta);
}
.side-comment-text {
    font-size: 11px;
    line-height: 1.5;
    color: #cbd2e1;
    margin: 0;
    word-break: break-word;
}
.card.card-docked {
    border-color: var(--cyan) !important;
    border-left: 6px solid var(--cyan) !important;
    box-shadow: 0 0 16px rgba(0, 245, 255, 0.35) !important;
}
.card.card-docked .rc {
    color: var(--cyan) !important;
    animation: bl .5s steps(2) infinite !important;
}
.st-key-sidescroll *::-webkit-scrollbar { width: 6px; }
.st-key-sidescroll *::-webkit-scrollbar-thumb { background: var(--cyan); }

@media (prefers-reduced-motion: reduce) {
    .card, .reel, .rc, .tape-line, .full-cassette, .stApp::after { animation: none !important; }
}
</style>
<div class="barcode"></div>
<div class="sleepy-cat-corner"><img src="https://i.pinimg.com/originals/1a/5a/b6/1a5ab6b62dc1e65d28844539450f615c.gif" alt="Sleeping Cat"><span>Zzz... [IDLE]</span></div>
""", unsafe_allow_html=True)

def loading_spool_animation(active=False):
    g = "".join(f'<g class="reel"><circle cx="{x}" cy="22" r="16" fill="#e9e6f5"/><path d="M{x} 8v28M{x-14} 22h28M{x-10} 12l20 20M{x+10} 12l-20 20" stroke="#0c0c10" stroke-width="2.5"/></g>' for x in (45, 125))
    return (f'<div class="spool{" go" if active else ""}"><div class="strip"><div class="tape-line"></div><div class="full-cassette">'
            f'<div class="cass-lab"><span>SIDE B</span><span>LOADING</span></div>'
            f'<div class="cass-stripe"></div>'
            f'<div class="cass-win"><svg viewBox="0 0 170 44" width="100%" role="img" aria-label="Full cassette rolling reels">'
            f'<rect width="170" height="44" rx="20" fill="#0c0c10"/>'
            f'{g}'
            f'<path d="M65 22h40" stroke="#8b88a8" stroke-width="2.5" stroke-dasharray="2 3"/>'
            f'</svg></div></div></div></div>')

def card(p, i, n):
    e = html.escape
    use_img = bool(p.get("image")) and not S.force_svg_fallback
    tag = "REDDIT IMG" if use_img else "GENERATED ART"
    img = f'<img alt="" referrerpolicy="no-referrer" loading="lazy" src="{e(p["image"])}">' if use_img else ""
    sc = "—" if p.get("score") is None else p["score"]
    
    comments = p.get("comments", [])
    cm = len(comments) if comments else (p.get("num_comments") or 0)
    top_score = max((c.get("score", 0) for c in comments), default=0) if comments else 0
    top_badge = f'<span class="cmt-badge">▲ TOP +{top_score}</span>' if comments else ''
    
    c_cards = []
    for c in comments:
        c_score = c.get("score", 0)
        c_cls = "high" if c_score >= 400 else ("neg" if c_score < 0 else "pos")
        c_author = e(c.get("author", "anonymous"))
        c_time = e(c.get("time", "recent"))
        c_body = e(c.get("body", ""))
        c_cards.append(
            f'<div class="comment-card">'
            f'  <div class="comment-head">'
            f'    <span class="comment-user">u/{c_author}</span>'
            f'    <div>'
            f'      <span class="comment-pts {c_cls}">▲ {c_score:+d} PTS</span>'
            f'      <span class="comment-time">· {c_time}</span>'
            f'    </div>'
            f'  </div>'
            f'  <p class="comment-msg">{c_body}</p>'
            f'</div>'
        )
    rendered_comments = "".join(c_cards) if c_cards else '<div class="comment-card"><p class="comment-msg">No transmission chatter on this frequency.</p></div>'
    
    comments_drawer = (
        f'<details class="comments-drawer">'
        f'  <summary class="comments-toggle">'
        f'    <div class="cmt-toggle-left">'
        f'      <span class="cmt-icon">💬</span>'
        f'      <span class="cmt-title">COMMENTS // TRANSMISSIONS ({cm})</span>'
        f'    </div>'
        f'    <div class="cmt-toggle-right">'
        f'      {top_badge}'
        f'      <span class="cmt-action">PREVIEW IN-CARD ▾</span>'
        f'    </div>'
        f'  </summary>'
        f'  <div class="comments-body">'
        f'    <div class="comments-bar"><span>// ARCHIVED SIGNALS ({cm})</span><span>CLICK [COMMENTS WINDOW 💬] FOR FULL INTERACTION</span></div>'
        f'    {rendered_comments}'
        f'    <div class="comments-footer">✦ FREQUENCY LOG END // USE [COMMENTS WINDOW] TO VOTE & REPLY</div>'
        f'  </div>'
        f'</details>'
    )
    
    return (f'<div class="card" style="--i:{n}"><div class="pic"><img alt="" src="{art(p["title"], p["subreddit"])}">{img}'
            f'<span class="tg">IMG {i+1:02d} // {tag}</span><span class="rc">● REC</span></div><div class="bd">'
            f'<div class="l"><span>✦ r/{e(p["subreddit"])}</span><span>TRK {i+1:03d}</span></div><h3>{e(p["title"])}</h3><p>{e(p["selftext"])}</p>'
            f'<small>u/{e(p["author"])} · ▲ {sc} · 💬 {cm} · CLICK [COMMENTS WINDOW] FOR FULL THREAD ▾</small>'
            f'{comments_drawer}'
            f'</div></div>')

@st.dialog("TRANSMISSION TERMINAL // COMMENTS WINDOW")
def open_comments_window(p, idx):
    e = html.escape
    sub = p.get("subreddit", "all")
    title = p.get("title", "")
    author = p.get("author", "anonymous")
    score = p.get("score", 0)
    comments = p.get("comments", [])
    
    sub_lower = sub.lower()
    if sub_lower in ["ambientmusic", "slowliving", "slowweb", "typography", "fieldrecording", "audiophile"]:
        atm_type = "AMBIENT CALM"
        atm_color = "var(--cyan)"
        atm_desc = "WARM LOW-PASS FILTER // 68 BPM"
    elif sub_lower in ["jungle", "futurebeats", "chiptunes", "cyberdeck", "glitch_art"]:
        atm_type = "BREAKBEAT CYBER"
        atm_color = "var(--magenta)"
        atm_desc = "SYNCOPATED 16THS // 142 BPM"
    else:
        atm_type = "ANALOG TAPE"
        atm_color = "var(--yellow)"
        atm_desc = "FLUTTER & CAPSTAN WOW // 88 BPM"

    st.markdown(
        f'<div class="side-post-header" data-subreddit="{e(sub)}">'
        f'<div style="display:flex; justify-content:space-between; font-size:10px; color:var(--cyan); margin-bottom:4px;">'
        f'<span>✦ r/{e(sub)}</span><span>LOG #{idx+1:03d} · ▲ {score} PTS</span>'
        f'</div>'
        f'<h4>{e(title)}</h4>'
        f'<p style="font-size:11px; color:#b9b6d4; line-height:1.5; margin:4px 0 6px;">{e(p.get("selftext", ""))}</p>'
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:4px;">'
        f'<span style="font-size:9px; color:var(--dim);">u/{e(author)} · 💬 {len(comments)} SIGNALS</span>'
        f'<div class="side-genre-badge" style="border-color:{atm_color}; color:{atm_color};">'
        f'⚡ AUDIO SYNC: {atm_type} [{atm_desc}]'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(f'<div class="cap">TRANSMISSION FREQUENCIES ({len(comments)}) »</div>', unsafe_allow_html=True)

    if not comments:
        st.markdown('<div class="plain">NO SIGNALS RECORDED ON THIS FREQUENCY YET.</div>', unsafe_allow_html=True)
    else:
        for c_i, c in enumerate(comments):
            c_score = c.get("score", 0)
            c_cls = "high" if c_score >= 400 else ("neg" if c_score < 0 else "pos")
            st.markdown(
                f'<div class="side-comment-card">'
                f'<div class="side-comment-top">'
                f'<span class="side-comment-user">u/{e(c.get("author", "anon"))}</span>'
                f'<div>'
                f'<span class="side-comment-score {c_cls}">▲ {c_score:+d} PTS</span>'
                f'<span style="color:var(--dim); font-size:9px; margin-left:4px;">· {e(c.get("time", "recent"))}</span>'
                f'</div>'
                f'</div>'
                f'<p class="side-comment-text">{e(c.get("body", ""))}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
            col_v1, col_v2 = st.columns([1, 1], gap="small")
            with col_v1:
                if st.button("▲ UPVOTE (+1)", key=f"win_up_{idx}_{c_i}", help="Upvote transmission"):
                    c["score"] = c.get("score", 0) + 1
                    st.rerun()
            with col_v2:
                if st.button("▼ DOWNVOTE (-1)", key=f"win_dn_{idx}_{c_i}", help="Downvote transmission"):
                    c["score"] = c.get("score", 0) - 1
                    st.rerun()

    st.markdown('<div class="hazard" style="height:6px; margin:14px 0 10px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="cap">BROADCAST SIGNAL TO THREAD »</div>', unsafe_allow_html=True)
    with st.form(f"win_form_{idx}", clear_on_submit=True):
        r_body = st.text_area("SIGNAL MESSAGE", placeholder="Transmit your response...", label_visibility="collapsed", height=70)
        col_author, col_send = st.columns([1.2, 1.0])
        with col_author:
            r_author = st.text_input("CALLSIGN", value="guest_operator", label_visibility="collapsed")
        with col_send:
            sub_click = st.form_submit_button("BROADCAST ✦", use_container_width=True)
        if sub_click and r_body.strip():
            new_entry = {
                "author": r_author.strip() or "guest_operator",
                "score": 1,
                "time": "just now",
                "body": r_body.strip()
            }
            if "comments" not in p:
                p["comments"] = []
            p["comments"].append(new_entry)
            p["num_comments"] = len(p["comments"])
            st.rerun()

svg_count = sum(1 for p in posts if S.force_svg_fallback or not p.get("image"))

st.markdown(f"""<div class="top"><span class="badge">FORMICAPUNK®</span><span class="title">Feed <span class="os">✦ OS</span></span></div>
<div class="mini"><span>[ SLOW MODE ]</span><span class="pill">2026</span><span class="hex">NOVEMBER</span><span>TAPE: LOCAL CACHE // {len(tracks):02d} TRK</span><span class="live">● {('LIVE // ' + SRC) if live else 'OFFLINE // SAMPLE + SVG FALLBACK'}</span></div>""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1.2, 1.0, 3.4], gap="medium")

with c1:
    # 4-Deck Audio Source Switcher: DE2 static decks + Early Raw Scroll Prototype + DE3 Dampened Tuner
    with st.container(key="audiomode"):
        player_choice = st.radio(
            "AUDIO SOURCE",
            ["CASSETTE DECK", "SPOTIFY EMBED", "SCROLL SYNTH", "SONIC DECK"],
            horizontal=True,
            label_visibility="collapsed",
            key="player_mode_select",
        )
    S.player_mode = player_choice

    if S.player_mode == "CASSETTE DECK":
        components.html(player_html(tracks, MUSIC_DIR), height=830, scrolling=False)
    elif S.player_mode == "SCROLL SYNTH":
        components.html(
            scroll_proto_html(
                live_feed=live,
                feed_source=SRC or "SAMPLE",
                svg_count=svg_count,
                total_posts=len(posts),
            ),
            height=830,
            scrolling=False,
        )
    elif S.player_mode == "SONIC DECK":
        components.html(sonic_deck_html(sheets=sheets), height=830, scrolling=False)
    else:
            # Styled ZZZ OS Container matching the cassette deck aesthetics
            st.markdown('''
            <div style="background:#17171e; border:2px solid #00f5ff; padding:12px; clip-path:polygon(0 0,calc(100% - 26px) 0,100% 26px,100% 100%,26px 100%,0 calc(100% - 26px)); position:relative;">
                <div style="height:8px; background:repeating-linear-gradient(135deg,#00f5ff 0 8px,#0c0c10 8px 16px); margin-bottom:10px;"></div>
                <div style="display:flex; justify-content:space-between; font-size:9px; letter-spacing:.18em; color:#8b88a8; margin-bottom:8px;">
                    <span>SPOTIFY DECK // STREAM</span><span style="color:#ff3fa4">&#9679; LINKED</span>
                </div>
            ''', unsafe_allow_html=True)
            
            spotify_uri = st.text_input("Spotify Playlist / Track URI or URL", value="https://open.spotify.com/album/0ErRTuEFNp7E7Yp8iWLSkw") # sanctuary os
            try:
                if "open.spotify.com" in spotify_uri:
                    parts = spotify_uri.split("?")[0].split("/")
                    item_type = parts[-2]
                    item_id = parts[-1]
                    embed_url = f"https://open.spotify.com/embed/{item_type}/{item_id}?utm_source=generator&theme=0"
                else:
                    p_type, p_id = spotify_uri.split(":")[-2:]
                    embed_url = f"https://open.spotify.com/embed/{p_type}/{p_id}?utm_source=generator&theme=0"
                
                components.iframe(embed_url, height=380, scrolling=False)
            except Exception:
                components.iframe("https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M?utm_source=generator&theme=0", height=380, scrolling=False)
            
            st.markdown('<div class="note" style="margin-top:10px; font-size:9px; color:#8b88a8; letter-spacing:.08em;">DIRECT EMBED STREAM // CLIPPED VIA SPOTIFY API.</div></div>', unsafe_allow_html=True)

with c2:
    with st.container(key="menu"):
        st.markdown('<div class="cap">SELECT* »</div>', unsafe_allow_html=True)
        view = st.radio("Menu", ["FEED", "SHEETS", "SETTINGS", "MEM. CARD", "NOTEPAD", "CREDITS"], label_visibility="collapsed")
        st.markdown('<div class="hazard"></div><div class="cap">MODULAR PATTERN ▸</div>', unsafe_allow_html=True)

with c3:
    with st.container(key="stage"):
        per = S.per; total = -(-len(posts) // per)
        if view == "FEED":
            st.markdown(f'<div class="stats"><div class="tile">SIDE<b>{min(S.block,total):02d}/{total:02d}</b></div><div class="tile">SAVED<b>{len(S.saved):02d}</b></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="cap">{view} »</div>', unsafe_allow_html=True)
        if view == "FEED":
            with st.container(height=700, key="feedscroll", border=False):
                shown = posts[: S.block * per]
                for i, p in enumerate(shown):
                    st.markdown(card(p, i, i % per), unsafe_allow_html=True)
                    done = p["title"] in S.saved
                    c_save, c_win = st.columns([1, 1], gap="small")
                    with c_save:
                        if st.button("SAVED ✦" if done else "SAVE TO MEM.", key=f"s{i}"):
                            S.saved.remove(p["title"]) if done else S.saved.append(p["title"])
                            st.rerun()
                    with c_win:
                        cm_cnt = len(p.get("comments", []))
                        if st.button(f"COMMENTS WINDOW 💬 ({cm_cnt})", key=f"w{i}"):
                            open_comments_window(p, i)
                    if (i + 1) % per == 0: 
                        st.markdown('<div class="gap"></div>', unsafe_allow_html=True)
                if len(shown) < len(posts):
                    st.markdown(loading_spool_animation(active=S.spooling), unsafe_allow_html=True)
                    msg = st.empty()
                    if st.button("▶ LOAD NEXT SIDE", use_container_width=True, disabled=S.spooling):
                        S.spooling = True
                        st.rerun()
                    if S.spooling:
                        for sec in range(3, 0, -1):
                            msg.markdown(f"<p class='cap' style='text-align:center'>ROLLING UP TAPE ... {sec}</p>", unsafe_allow_html=True)
                            time.sleep(1)
                        S.spooling = False
                        S.block += 1
                        st.rerun()
                else:
                    st.markdown('<div class="plain" style="text-align:center">END OF TAPE. The timeline stops here on purpose.</div>', unsafe_allow_html=True)
        elif view == "SHEETS":
            st.markdown(
                f'<div class="plain" style="margin-bottom:10px;">'
                f'MUSIC SHEETS FOLDER: <b style="color:var(--yellow)">{html.escape(str(SHEETS_DIR))}</b> ({len(sheets)} SHEETS LOADED)<br>'
                f'Drop <code>.json</code> music sheet files into this folder or create one below. The <b>SONIC DECK</b> dynamically samples chords, basslines, melodies, drums, and swing from these sheets.'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("↻ RELOAD SHEETS FROM DISK"):
                st.rerun()
            with st.container(height=360, border=False):
                for idx_s, sh in enumerate(sheets):
                    chords_str = " → ".join(b.get("name", "?") for b in sh.get("bars", []))
                    subs_str = ", ".join(f"r/{s}" for s in sh.get("subreddits", [])) or "ALL"
                    mel_preview = " ".join(n or "·" for n in (sh.get("bars", [{}])[0].get("melody", [])[:12]))
                    st.markdown(
                        f'<div class="side-comment-card" style="border-left-color:var(--yellow); margin-bottom:8px;">'
                        f'<div class="side-comment-top">'
                        f'<span class="side-comment-user">{idx_s+1:02d}. {html.escape(sh.get("title", "Untitled"))} — {html.escape(sh.get("artist", ""))}</span>'
                        f'<div>'
                        f'<span class="side-comment-score high">{sh.get("bpm", 90)} BPM · {html.escape(sh.get("meter", "4/4"))}</span>'
                        f'<span class="side-comment-score pos" style="margin-left:4px;">{html.escape(str(sh.get("mood", "custom")).upper())} · ARP:{html.escape(str(sh.get("arp_mode", "up")).upper())}</span>'
                        f'</div>'
                        f'</div>'
                        f'<p class="side-comment-text">'
                        f'<b>CHORDS:</b> {html.escape(chords_str)}<br>'
                        f'<b>MELODY BAR 1:</b> <code>{html.escape(mel_preview)}</code><br>'
                        f'<b>SYNC SUBS:</b> <span style="color:var(--cyan)">{html.escape(subs_str)}</span> · <b>SWING:</b> {sh.get("swing", 0)}'
                        f'</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            st.markdown('<div class="hazard" style="height:6px; margin:10px 0;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="cap">ADD NEW SAMPLE MUSIC SHEET »</div>', unsafe_allow_html=True)
            default_bars = json.dumps([
                {
                    "name": "Bbmaj9",
                    "bass": "Bb1",
                    "pad": ["Bb2", "D3", "F3", "A3", "C4"],
                    "keys": ["F4", "A4", "Bb4", "C5", "D5"],
                    "melody": ["D5", None, "C5", "A4", None, "F4", None, "G4", "A4", None, "C5", None, "D5", None, "F5", None],
                },
                {
                    "name": "Gm9",
                    "bass": "G1",
                    "pad": ["G2", "Bb2", "D3", "F3", "A3"],
                    "keys": ["D4", "F4", "G4", "A4", "Bb4"],
                    "melody": ["Bb4", None, "A4", "G4", None, "D4", None, "F4", "G4", None, "A4", None, "Bb4", None, "D5", None],
                },
            ], indent=2)
            with st.form("new_sheet_form", clear_on_submit=False):
                sc1, sc2, sc3 = st.columns([1.4, 1.0, 0.8])
                with sc1:
                    s_title = st.text_input("SHEET TITLE", value="Midnight Neon Drift")
                with sc2:
                    s_artist = st.text_input("ARTIST / SOURCE", value="Custom Synth")
                with sc3:
                    s_mood = st.selectbox("MOOD", ["ambient", "cyber", "dreamy", "breakbeat", "lofi", "experimental"])
                sc4, sc5, sc6, sc7 = st.columns([1, 1, 1, 1])
                with sc4:
                    s_bpm = st.number_input("BPM", min_value=55, max_value=170, value=94)
                with sc5:
                    s_meter = st.selectbox("METER", ["4/4", "3/4", "6/8", "5/4", "7/8"])
                with sc6:
                    s_arp = st.selectbox("ARP MODE", ["up", "down", "pingpong", "random"])
                with sc7:
                    s_swing = st.slider("SWING", 0.0, 0.25, 0.06, 0.01)
                s_subs = st.text_input("SYNC SUBREDDITS (comma-separated)", value="VaporwaveAesthetics, CozyPlaces")
                s_bars_json = st.text_area("CHORDS & MELODY BARS (JSON)", value=default_bars, height=150)
                if st.form_submit_button("SAVE MUSIC SHEET TO LIBRARY ✦", use_container_width=True):
                    try:
                        parsed_bars = json.loads(s_bars_json)
                        if not isinstance(parsed_bars, list) or not parsed_bars:
                            raise ValueError("Bars must be a non-empty JSON list.")
                        new_sheet = {
                            "title": s_title.strip() or "Custom Sheet",
                            "artist": s_artist.strip() or "Custom Synth",
                            "mood": s_mood,
                            "subreddits": [x.strip() for x in s_subs.split(",") if x.strip()],
                            "bpm": int(s_bpm),
                            "meter": s_meter,
                            "swing": float(s_swing),
                            "cutoff": 1150,
                            "arp_mode": s_arp,
                            "bars": parsed_bars,
                            "drums": {"kicks": [0, 6, 10], "snares": [4, 12], "hats": [0, 2, 4, 6, 8, 10, 12, 14]},
                        }
                        saved_path = save_sheet(new_sheet)
                        st.success(f"Saved sample music sheet: {saved_path.name}")
                        time.sleep(0.4)
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Invalid sheet JSON: {ex}")
        elif view == "SETTINGS":
            S.per = st.select_slider("POSTS PER SIDE", [2, 3, 4], value=S.per)
            st.toggle("PREVIEW SVG FALLBACK ART (OFFLINE)", key="force_svg_fallback")
            st.markdown(
                f'<div class="plain" style="margin-bottom:10px;">'
                f'MUSIC FOLDER: <b style="color:var(--yellow)">{html.escape(str(MUSIC_DIR))}</b> ({len(tracks)} TRACKS)<br>'
                f'COVER SEARCH: <b style="color:var(--yellow)">{"SPOTIFY ON" if has_keys() else "SPOTIFY OFF"}</b><br>'
                f'FEED SOURCE: <b style="color:var(--cyan)">{html.escape(SRC or "SAMPLE PLACEHOLDER DATA")}</b><br>'
                f'SVG FALLBACK CARDS: <b style="color:var(--magenta)">{svg_count} / {len(posts)}</b>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("RE-SEARCH COVERS"): 
                clear_cover_cache()
                st.rerun()
            if st.button("RELOAD DEFAULT SAMPLE POSTS"):
                import copy
                from data import SAMPLE
                S.posts = copy.deepcopy(SAMPLE)
                S.live = False
                st.rerun()
        elif view == "MEM. CARD":
            if not S.saved: 
                st.markdown('<div class="plain">NO DATA ON CARD.</div>', unsafe_allow_html=True)
            for t_ in S.saved: 
                st.markdown(f'<div class="plain" style="margin-bottom:8px">✦ {html.escape(t_)}</div>', unsafe_allow_html=True)
        elif view == "NOTEPAD":
            st.text_area("Write whatever you want here.", key="note", height=260)
        else:
            st.markdown(
                '<div class="plain">'
                'Visual direction: Inspired by <em>Zenless Zone Zero</em>\'s CRT-and-hazard-stripe interface and urban cassette futurism, alongside the Frutiger Aero, Nintendo, and Dreamcast aesthetics of <a href="https://www.youtube.com/watch?v=d3KfkKXRDzk" target="_blank">Sanctuary OS</a> by <strong>Dusqk</strong>.<br><br>'
                '<strong>Audio Evolution (DE2 &rarr; Prototype &rarr; DE3):</strong><br>'
                '&bull; <b>CASSETTE DECK &amp; SPOTIFY EMBED (DE2):</b> Static pacing via local MP3 cache or Spotify iframe.<br>'
                '&bull; <b>SCROLL SYNTH (Early Prototype):</b> Unthrottled scroll-velocity-to-tempo synthesis demonstrating erratic BPM spikes during auto-scroll and RSS/SVG fallback layout height shifts.<br>'
                '&bull; <b>SONIC DECK (DE3 Tuner):</b> Dampened tempo controller with layout-shift filtering, fast-scroll thresholds, and interactive synth layer controls for intentional user agency.'
                '</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<iframe width="100%" height="400" src="https://www.youtube.com/embed/d3KfkKXRDzk" title="Sanctuary OS Showcase" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
                unsafe_allow_html=True,
            )

st.markdown('<div class="status"><span>WORLDWIDE (SX)</span><span>MODULAR PATTERN ▸</span><span>SIDE A ◂▸ SIDE B</span><span>01:45:51</span></div>', unsafe_allow_html=True)