import time
import html
import streamlit as st
import streamlit.components.v1 as components
from data import get_posts, art
from music import load_library, MUSIC_DIR, clear_cover_cache
from spotify import has_keys
from local_player import player_html

st.set_page_config(
    page_title="Formicapunk OS", 
    page_icon="✦", 
    layout="wide"
)

posts, live = get_posts()
tracks = load_library()
S = st.session_state
S.setdefault("block", 1)
S.setdefault("saved", [])
S.setdefault("per", 3)
S.setdefault("spooling", False)
S.setdefault("player_mode", "CASSETTE DECK")

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
    tag = "REDDIT IMG" if p.get("image") else "GENERATED ART"
    img = f'<img alt="" referrerpolicy="no-referrer" loading="lazy" src="{e(p["image"])}">' if p.get("image") else ""
    sc = "—" if p.get("score") is None else p["score"]
    cm = "—" if p.get("num_comments") is None else p["num_comments"]
    return (f'<div class="card" style="--i:{n}"><div class="pic"><img alt="" src="{art(p["title"], p["subreddit"])}">{img}'
            f'<span class="tg">IMG {i+1:02d} // {tag}</span><span class="rc">● REC</span></div><div class="bd">'
            f'<div class="l"><span>✦ r/{e(p["subreddit"])}</span><span>TRK {i+1:03d}</span></div><h3>{e(p["title"])}</h3><p>{e(p["selftext"])}</p>'
            f'<small>u/{e(p["author"])} · ▲ {sc} · 💬 {cm}</small></div></div>')

st.markdown(f"""<div class="top"><span class="badge">FORMICAPUNK®</span><span class="title">Feed <span class="os">✦ OS</span></span></div>
<div class="mini"><span>[ SLOW MODE ]</span><span class="pill">2026</span><span class="hex">NOVEMBER</span><span>TAPE: LOCAL CACHE // {len(tracks):02d} TRK</span><span class="live">● {('LIVE // ' + SRC) if live else 'OFFLINE // USING SAMPLE POSTS'}</span></div>""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1.2, 1.0, 3.4], gap="medium")

with c1:
    # Player Mode Switcher Tab
    player_choice = st.radio("AUDIO SOURCE", ["CASSETTE DECK", "SPOTIFY EMBED"], horizontal=True, label_visibility="collapsed", key="player_mode_select")
    S.player_mode = player_choice
    
    if S.player_mode == "CASSETTE DECK":
        components.html(player_html(tracks, MUSIC_DIR), height=830, scrolling=False)
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
        view = st.radio("Menu", ["FEED", "SETTINGS", "MEM. CARD", "NOTEPAD", "CREDITS"], label_visibility="collapsed")
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
                    if st.button("SAVED ✦" if done else "SAVE TO MEM.", key=f"s{i}"):
                        S.saved.remove(p["title"]) if done else S.saved.append(p["title"])
                        st.rerun()
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
        elif view == "SETTINGS":
            S.per = st.select_slider("POSTS PER SIDE", [2, 3, 4], value=S.per)
            #st.markdown(f'<div class="plain">MUSIC FOLDER: <b style="color:var(--yellow)">{html.escape(str(MUSIC_DIR))}</b><br>TRACKS FOUND: {len(tracks)}<br>COVER SEARCH: <b style="color:var(--yellow)">{"SPOTIFY ON" if has_keys() else "SPOTIFY OFF (add keys)"}</b><br>POSTS FROM: <b style="color:var(--yellow)">{SRC or "SAMPLE DATA"}</b><br>To search Spotify for covers, add <code>SPOTIFY_CLIENT_ID</code> and <code>SPOTIFY_CLIENT_SECRET</code> to <code>.streamlit/secrets.toml</code>. For the official Reddit API, add <code>REDDIT_CLIENT_ID</code> and <code>REDDIT_CLIENT_SECRET</code>. Restart after changing keys.</div>', unsafe_allow_html=True)
            if st.button("RE-SEARCH COVERS"): 
                clear_cover_cache()
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
                '<div class="plain">Visual direction: Inspired by <em>Zenless Zone Zero</em>\'s CRT-and-hazard-stripe interface and urban cassette futurism, alongside the Frutiger Aero, Nintendo, and Dreamcast aesthetics of <a href="https://www.youtube.com/watch?v=d3KfkKXRDzk" target="_blank">Sanctuary OS</a> by <strong>Dusqk</strong>. Music plays from a local cache of MP3 files or the Spotify Embed player tab. Album covers are looked up via Spotify search, with generated cover art as a fallback. Posts come from Reddit (official API when keys are set, otherwise the public RSS feed). Post images come from Reddit previews; posts without one get procedurally generated art.</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<iframe width="100%" height="400" src="https://www.youtube.com/embed/d3KfkKXRDzk" title="Sanctuary OS Showcase" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
                unsafe_allow_html=True,
            )

st.markdown('<div class="status"><span>WORLDWIDE (SX)</span><span>MODULAR PATTERN ▸</span><span>SIDE A ◂▸ SIDE B</span><span>01:45:51</span></div>', unsafe_allow_html=True)