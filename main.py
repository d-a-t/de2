"""Formicapunk OS — main Streamlit application."""
import copy
import html
import time
import yaml
import streamlit as st
import streamlit.components.v1 as components

from data import SAMPLE, art, generate_lorem_posts, get_posts
from local_player import player_html
from music import MUSIC_DIR, clear_cover_cache, load_library
from scroll_proto_player import scroll_proto_html
from sheets import SHEETS_DIR, load_sheets, save_sheet
from sonic_deck import sonic_deck_html
from spotify import has_keys
from styles import APP_CSS

st.set_page_config(page_title="Formicapunk OS", page_icon="✦", layout="wide")

tracks = load_library()
sheets = load_sheets()
S = st.session_state
S.setdefault("block", 1)
S.setdefault("saved", [])
S.setdefault("per", 3)
S.setdefault("spooling", False)
S.setdefault("player_mode", "CASSETTE DECK")
S.setdefault("force_svg_fallback", False)

if "posts" not in S:
    S.posts, S.live = get_posts()

posts, live = S.posts, S.live
SRC = {"API": "REDDIT API", "RSS": "REDDIT RSS", "JSON": "REDDIT JSON"}.get(posts[0].get("src", ""), "REDDIT") if live else ""
svg_count = sum(1 for p in posts if S.force_svg_fallback or not p.get("image"))

st.markdown(APP_CSS, unsafe_allow_html=True)

_AMBIENT_SUBS = {"ambientmusic", "slowliving", "slowweb", "typography", "fieldrecording", "audiophile"}
_CYBER_SUBS = {"jungle", "futurebeats", "chiptunes", "cyberdeck", "glitch_art"}

_DEFAULT_BARS_YAML = """- name: Bbmaj9
  bass: Bb1
  pad: [Bb2, D3, F3, A3, C4]
  keys: [F4, A4, Bb4, C5, D5]
  melody: [D5, null, C5, A4, null, F4, null, G4, A4, null, C5, null, D5, null, F5, null]
- name: Gm9
  bass: G1
  pad: [G2, Bb2, D3, F3, A3]
  keys: [D4, F4, G4, A4, Bb4]
  melody: [Bb4, null, A4, G4, null, D4, null, F4, G4, null, A4, null, Bb4, null, D5, null]
"""


def subreddit_atmosphere(sub):
    """Return (label, css_color, description) for a post's subreddit."""
    s = (sub or "").lower()
    if s in _AMBIENT_SUBS:
        return "AMBIENT CALM", "var(--cyan)", "WARM LOW-PASS FILTER // 68 BPM"
    if s in _CYBER_SUBS:
        return "BREAKBEAT CYBER", "var(--magenta)", "SYNCOPATED 16THS // 142 BPM"
    return "ANALOG TAPE", "var(--yellow)", "FLUTTER & CAPSTAN WOW // 88 BPM"


def render_comment_card(c):
    """Render a single comment box with author, karma score pill, timestamp, and body."""
    e = html.escape
    score = c.get("score", 0)
    cls = "high" if score >= 400 else ("neg" if score < 0 else "pos")
    return (
        f'<div class="cmt-card">'
        f'<div class="cmt-head">'
        f'<span class="cmt-user">u/{e(c.get("author", "anonymous"))}</span>'
        f'<div><span class="cmt-pts {cls}">▲ {score:+d} PTS</span>'
        f'<span class="cmt-time">· {e(c.get("time", "recent"))}</span></div>'
        f'</div>'
        f'<p class="cmt-msg">{e(c.get("body", ""))}</p>'
        f'</div>'
    )


def loading_spool_animation(active=False):
    g = "".join(
        f'<g class="reel"><circle cx="{x}" cy="22" r="16" fill="#e9e6f5"/>'
        f'<path d="M{x} 8v28M{x-14} 22h28M{x-10} 12l20 20M{x+10} 12l-20 20" stroke="#0c0c10" stroke-width="2.5"/></g>'
        for x in (45, 125)
    )
    return (
        f'<div class="spool{" go" if active else ""}"><div class="strip"><div class="tape-line"></div>'
        f'<div class="full-cassette"><div class="cass-lab"><span>SIDE B</span><span>LOADING</span></div>'
        f'<div class="cass-stripe"></div><div class="cass-win">'
        f'<svg viewBox="0 0 170 44" width="100%" role="img" aria-label="Full cassette rolling reels">'
        f'<rect width="170" height="44" rx="20" fill="#0c0c10"/>{g}'
        f'<path d="M65 22h40" stroke="#8b88a8" stroke-width="2.5" stroke-dasharray="2 3"/></svg></div></div></div></div>'
    )


def card(p, i, n):
    e = html.escape
    use_img = bool(p.get("image")) and not S.force_svg_fallback
    tag = "REDDIT IMG" if use_img else "GENERATED ART"
    img = f'<img alt="" referrerpolicy="no-referrer" loading="lazy" src="{e(p["image"])}">' if use_img else ""
    sc = "—" if p.get("score") is None else p["score"]
    comments = p.get("comments", [])
    cm = len(comments) if comments else (p.get("num_comments") or 0)
    top_score = max((c.get("score", 0) for c in comments), default=0) if comments else 0
    top_badge = f'<span class="cmt-badge">▲ TOP +{top_score}</span>' if comments else ""
    rendered = "".join(render_comment_card(c) for c in comments) or '<div class="cmt-card"><p class="cmt-msg">No transmission chatter on this frequency.</p></div>'

    drawer = (
        f'<details class="comments-drawer">'
        f'<summary class="comments-toggle">'
        f'<div class="cmt-toggle-left"><span>💬</span><span>COMMENTS // TRANSMISSIONS ({cm})</span></div>'
        f'<div class="cmt-toggle-right">{top_badge}<span class="cmt-action">PREVIEW IN-CARD ▾</span></div>'
        f'</summary>'
        f'<div class="comments-body">'
        f'<div class="comments-bar"><span>// ARCHIVED SIGNALS ({cm})</span><span>CLICK [COMMENTS WINDOW 💬] FOR FULL INTERACTION</span></div>'
        f'{rendered}'
        f'<div class="comments-footer">✦ FREQUENCY LOG END // USE [COMMENTS WINDOW] TO VOTE & REPLY</div>'
        f'</div></details>'
    )
    return (
        f'<div class="card" style="--i:{n}"><div class="pic"><img alt="" src="{art(p["title"], p["subreddit"])}">{img}'
        f'<span class="tg">IMG {i+1:02d} // {tag}</span><span class="rc">● REC</span></div><div class="bd">'
        f'<div class="l"><span>✦ r/{e(p["subreddit"])}</span><span>TRK {i+1:03d}</span></div>'
        f'<h3>{e(p["title"])}</h3><p>{e(p["selftext"])}</p>'
        f'<small>u/{e(p["author"])} · ▲ {sc} · 💬 {cm} · CLICK [COMMENTS WINDOW] FOR FULL THREAD ▾</small>'
        f'{drawer}</div></div>'
    )


@st.dialog("TRANSMISSION TERMINAL // COMMENTS WINDOW")
def open_comments_window(p, idx):
    e = html.escape
    sub = p.get("subreddit", "all")
    comments = p.get("comments", [])
    atm_type, atm_color, atm_desc = subreddit_atmosphere(sub)

    st.markdown(
        f'<div class="side-post-header" data-subreddit="{e(sub)}">'
        f'<div style="display:flex; justify-content:space-between; font-size:10px; color:var(--cyan); margin-bottom:4px;">'
        f'<span>✦ r/{e(sub)}</span><span>LOG #{idx+1:03d} · ▲ {p.get("score", 0)} PTS</span></div>'
        f'<h4>{e(p.get("title", ""))}</h4>'
        f'<p style="font-size:11px; color:#b9b6d4; line-height:1.5; margin:4px 0 6px;">{e(p.get("selftext", ""))}</p>'
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:4px;">'
        f'<span style="font-size:9px; color:var(--dim);">u/{e(p.get("author", "anonymous"))} · 💬 {len(comments)} SIGNALS</span>'
        f'<div class="side-genre-badge" style="border-color:{atm_color}; color:{atm_color};">⚡ AUDIO SYNC: {atm_type} [{atm_desc}]</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="cap">TRANSMISSION FREQUENCIES ({len(comments)}) »</div>', unsafe_allow_html=True)

    if not comments:
        st.markdown('<div class="plain">NO SIGNALS RECORDED ON THIS FREQUENCY YET.</div>', unsafe_allow_html=True)
    else:
        for c_i, c in enumerate(comments):
            st.markdown(render_comment_card(c), unsafe_allow_html=True)
            v1, v2 = st.columns(2, gap="small")
            with v1:
                if st.button("▲ UPVOTE (+1)", key=f"win_up_{idx}_{c_i}"):
                    c["score"] = c.get("score", 0) + 1
                    st.rerun()
            with v2:
                if st.button("▼ DOWNVOTE (-1)", key=f"win_dn_{idx}_{c_i}"):
                    c["score"] = c.get("score", 0) - 1
                    st.rerun()

    st.markdown('<div class="hazard" style="height:6px; margin:14px 0 10px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="cap">BROADCAST SIGNAL TO THREAD »</div>', unsafe_allow_html=True)
    with st.form(f"win_form_{idx}", clear_on_submit=True):
        r_body = st.text_area("SIGNAL MESSAGE", placeholder="Transmit your response...", label_visibility="collapsed", height=70)
        col_a, col_s = st.columns([1.2, 1.0])
        with col_a:
            r_author = st.text_input("CALLSIGN", value="guest_operator", label_visibility="collapsed")
        with col_s:
            if st.form_submit_button("BROADCAST ✦", use_container_width=True) and r_body.strip():
                p.setdefault("comments", []).append({
                    "author": r_author.strip() or "guest_operator",
                    "score": 1,
                    "time": "just now",
                    "body": r_body.strip(),
                })
                p["num_comments"] = len(p["comments"])
                st.rerun()


def render_spotify_deck():
    st.markdown(
        '<div style="background:#17171e; border:2px solid #00f5ff; padding:12px; '
        'clip-path:polygon(0 0,calc(100% - 26px) 0,100% 26px,100% 100%,26px 100%,0 calc(100% - 26px)); position:relative;">'
        '<div style="height:8px; background:repeating-linear-gradient(135deg,#00f5ff 0 8px,#0c0c10 8px 16px); margin-bottom:10px;"></div>'
        '<div style="display:flex; justify-content:space-between; font-size:9px; letter-spacing:.18em; color:#8b88a8; margin-bottom:8px;">'
        '<span>SPOTIFY DECK // STREAM</span><span style="color:#ff3fa4">&#9679; LINKED</span></div>',
        unsafe_allow_html=True,
    )
    spotify_uri = st.text_input("Spotify Playlist / Track URI or URL", value="https://open.spotify.com/album/0ErRTuEFNp7E7Yp8iWLSkw")
    try:
        if "open.spotify.com" in spotify_uri:
            parts = spotify_uri.split("?")[0].split("/")
            item_type, item_id = parts[-2], parts[-1]
        else:
            item_type, item_id = spotify_uri.split(":")[-2:]
        embed_url = f"https://open.spotify.com/embed/{item_type}/{item_id}?utm_source=generator&theme=0"
        components.iframe(embed_url, height=380, scrolling=False)
    except Exception:
        components.iframe("https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M?utm_source=generator&theme=0", height=380, scrolling=False)
    st.markdown('<div class="note" style="margin-top:10px; font-size:9px; color:#8b88a8; letter-spacing:.08em;">DIRECT EMBED STREAM // CLIPPED VIA SPOTIFY API.</div></div>', unsafe_allow_html=True)


def render_feed_view(per):
    with st.container(height=700, key="feedscroll", border=False):
        needed = S.block * per
        if needed > len(posts):
            posts.extend(generate_lorem_posts(needed - len(posts), start_idx=len(posts)))
        shown = posts[:needed]
        for i, p in enumerate(shown):
            st.markdown(card(p, i, i % per), unsafe_allow_html=True)
            done = p["title"] in S.saved
            c_save, c_win = st.columns(2, gap="small")
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

        beyond_base = len(shown) >= len(SAMPLE)
        if beyond_base:
            st.markdown(
                '<div class="plain" style="text-align:center; margin-bottom:8px;">'
                'BEYOND END OF TAPE // DYNAMIC LOREM IPSUM GENERATOR ACTIVE'
                '</div>',
                unsafe_allow_html=True,
            )
        st.markdown(loading_spool_animation(active=S.spooling), unsafe_allow_html=True)
        msg = st.empty()
        btn_label = "▶ GENERATE MORE (LOREM TAPE)" if beyond_base else "▶ LOAD NEXT SIDE"
        if st.button(btn_label, use_container_width=True, disabled=S.spooling):
            S.spooling = True
            st.rerun()
        if S.spooling:
            for sec in range(3, 0, -1):
                msg.markdown(f"<p class='cap' style='text-align:center'>ROLLING UP TAPE ... {sec}</p>", unsafe_allow_html=True)
                time.sleep(1)
            S.spooling = False
            S.block += 1
            if S.block * per > len(posts):
                posts.extend(generate_lorem_posts(S.block * per - len(posts), start_idx=len(posts)))
            st.rerun()


def render_sheets_view():
    st.markdown(
        f'<div class="plain" style="margin-bottom:10px;">'
        f'MUSIC SHEETS FOLDER: <b style="color:var(--yellow)">{html.escape(str(SHEETS_DIR))}</b> ({len(sheets)} YAML SHEETS LOADED)<br>'
        f'Drop <code>.yaml</code> music sheet files into this folder or create one below. The <b>SONIC DECK</b> dynamically samples chords, basslines, melodies, drums, and swing from these sheets.'
        f'</div>',
        unsafe_allow_html=True,
    )
    if st.button("↻ RELOAD SHEETS FROM DISK"):
        st.rerun()
    with st.container(height=340, border=False):
        for idx_s, sh in enumerate(sheets):
            chords = " → ".join(b.get("name", "?") for b in sh.get("bars", []))
            subs = ", ".join(f"r/{s}" for s in sh.get("subreddits", [])) or "ALL"
            mel = " ".join(str(n) if n else "·" for n in (sh.get("bars", [{}])[0].get("melody", [])[:12]))
            st.markdown(
                f'<div class="cmt-card" style="border-left-color:var(--yellow); margin-bottom:8px;">'
                f'<div class="cmt-head"><span class="cmt-user">{idx_s+1:02d}. {html.escape(sh.get("title", "Untitled"))} — {html.escape(sh.get("artist", ""))}</span>'
                f'<div><span class="cmt-pts high">{sh.get("bpm", 90)} BPM · {html.escape(sh.get("meter", "4/4"))}</span>'
                f'<span class="cmt-pts pos" style="margin-left:4px;">{html.escape(str(sh.get("mood", "custom")).upper())} · ARP:{html.escape(str(sh.get("arp_mode", "up")).upper())}</span></div></div>'
                f'<p class="cmt-msg"><b>CHORDS:</b> {html.escape(chords)}<br>'
                f'<b>MELODY BAR 1:</b> <code>{html.escape(mel)}</code><br>'
                f'<b>SYNC SUBS:</b> <span style="color:var(--cyan)">{html.escape(subs)}</span> · <b>SWING:</b> {sh.get("swing", 0)}</p></div>',
                unsafe_allow_html=True,
            )
    st.markdown('<div class="hazard" style="height:6px; margin:10px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="cap">ADD NEW SAMPLE MUSIC SHEET (YAML) »</div>', unsafe_allow_html=True)
    with st.form("new_sheet_form", clear_on_submit=False):
        sc1, sc2, sc3 = st.columns([1.4, 1.0, 0.8])
        with sc1:
            s_title = st.text_input("SHEET TITLE", value="Midnight Neon Drift")
        with sc2:
            s_artist = st.text_input("ARTIST / SOURCE", value="Custom Synth")
        with sc3:
            s_mood = st.selectbox("MOOD", ["ambient", "cyber", "dreamy", "breakbeat", "lofi", "experimental"])
        sc4, sc5, sc6, sc7 = st.columns(4)
        with sc4:
            s_bpm = st.number_input("BPM", min_value=55, max_value=170, value=94)
        with sc5:
            s_meter = st.selectbox("METER", ["4/4", "3/4", "6/8", "5/4", "7/8"])
        with sc6:
            s_arp = st.selectbox("ARP MODE", ["up", "down", "pingpong", "random"])
        with sc7:
            s_swing = st.slider("SWING", 0.0, 0.25, 0.06, 0.01)
        s_subs = st.text_input("SYNC SUBREDDITS (comma-separated)", value="VaporwaveAesthetics, CozyPlaces")
        s_bars_yaml = st.text_area("CHORDS & MELODY BARS (YAML)", value=_DEFAULT_BARS_YAML, height=150)
        if st.form_submit_button("SAVE YAML SHEET TO LIBRARY ✦", use_container_width=True):
            try:
                parsed_bars = yaml.safe_load(s_bars_yaml)
                if not isinstance(parsed_bars, list) or not parsed_bars:
                    raise ValueError("Bars must be a non-empty YAML list.")
                saved_path = save_sheet({
                    "title": s_title.strip() or "Custom Sheet",
                    "artist": s_artist.strip() or "Custom Synth",
                    "mood": s_mood,
                    "subreddits": [x.strip() for x in s_subs.split(",") if x.strip()],
                    "bpm": int(s_bpm),
                    "meter": s_meter,
                    "swing": float(s_swing),
                    "cutoff": 1150,
                    "arp_mode": s_arp,
                    "drums": {"kicks": [0, 6, 10], "snares": [4, 12], "hats": [0, 2, 4, 6, 8, 10, 12, 14]},
                    "bars": parsed_bars,
                })
                st.success(f"Saved YAML sheet: {saved_path.name}")
                time.sleep(0.4)
                st.rerun()
            except Exception as ex:
                st.error(f"Invalid sheet YAML: {ex}")


def render_settings_view():
    S.per = st.select_slider("POSTS PER SIDE", list(range(2, 31)), value=S.per)
    st.toggle("PREVIEW SVG FALLBACK ART (OFFLINE)", key="force_svg_fallback")
    st.markdown(
        f'<div class="plain" style="margin-bottom:10px;">'
        f'MUSIC FOLDER: <b style="color:var(--yellow)">{html.escape(str(MUSIC_DIR))}</b> ({len(tracks)} TRACKS)<br>'
        f'MUSIC SHEETS: <b style="color:var(--yellow)">{html.escape(str(SHEETS_DIR))}</b> ({len(sheets)} YAML SHEETS)<br>'
        f'COVER SEARCH: <b style="color:var(--yellow)">{"SPOTIFY ON" if has_keys() else "SPOTIFY OFF"}</b><br>'
        f'FEED SOURCE: <b style="color:var(--cyan)">{html.escape(SRC or "SAMPLE PLACEHOLDER DATA")}</b><br>'
        f'SVG FALLBACK CARDS: <b style="color:var(--magenta)">{svg_count} / {len(posts)}</b></div>',
        unsafe_allow_html=True,
    )
    if st.button("RE-SEARCH COVERS"):
        clear_cover_cache()
        st.rerun()
    if st.button("RELOAD DEFAULT SAMPLE POSTS"):
        S.posts = copy.deepcopy(SAMPLE)
        S.live = False
        st.rerun()


# --- Main Header & Layout ---
st.markdown(
    f'<div class="top"><span class="badge">FORMICAPUNK®</span><span class="title">Feed <span class="os">✦ OS</span></span></div>'
    f'<div class="mini"><span>[ SLOW MODE ]</span><span class="pill">2026</span><span class="hex">NOVEMBER</span>'
    f'<span>TAPE: LOCAL CACHE // {len(tracks):02d} TRK</span>'
    f'<span class="live">● {("LIVE // " + SRC) if live else "OFFLINE // SAMPLE + SVG FALLBACK"}</span></div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns([1.3, 1.05, 3.25], gap="medium")

with c1:
    with st.container(key="audiomode"):
        S.player_mode = st.radio(
            "AUDIO SOURCE",
            ["CASSETTE DECK", "SPOTIFY EMBED", "SCROLL SYNTH", "SONIC DECK"],
            horizontal=True,
            label_visibility="collapsed",
            key="player_mode_select",
        )
    if S.player_mode == "CASSETTE DECK":
        components.html(player_html(tracks, MUSIC_DIR), height=830, scrolling=False)
    elif S.player_mode == "SCROLL SYNTH":
        components.html(scroll_proto_html(live_feed=live, feed_source=SRC or "SAMPLE", svg_count=svg_count, total_posts=len(posts)), height=830, scrolling=False)
    elif S.player_mode == "SONIC DECK":
        components.html(sonic_deck_html(sheets=sheets), height=830, scrolling=False)
    else:
        render_spotify_deck()

with c2:
    with st.container(key="menu"):
        st.markdown('<div class="cap">SELECT* »</div>', unsafe_allow_html=True)
        view = st.radio("Menu", ["FEED", "SHEETS", "SETTINGS", "MEM. CARD", "NOTEPAD", "CREDITS"], label_visibility="collapsed")
        st.markdown('<div class="hazard"></div><div class="cap">MODULAR PATTERN ▸</div>', unsafe_allow_html=True)

with c3:
    with st.container(key="stage"):
        per = S.per
        total = -(-len(posts) // per)
        if view == "FEED":
            st.markdown(f'<div class="stats"><div class="tile">SIDE<b>{min(S.block, total):02d}/{total:02d}</b></div><div class="tile">SAVED<b>{len(S.saved):02d}</b></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="cap">{view} »</div>', unsafe_allow_html=True)
        if view == "FEED":
            render_feed_view(per)
        elif view == "SHEETS":
            render_sheets_view()
        elif view == "SETTINGS":
            render_settings_view()
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
                '&bull; <b>SONIC DECK (DE3 Tuner):</b> Dampened tempo controller with YAML music sheet sampling, 5-layer synth, LFO filter, and interactive comment resonance.'
                '</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<iframe width="100%" height="400" src="https://www.youtube.com/embed/d3KfkKXRDzk" title="Sanctuary OS Showcase" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', unsafe_allow_html=True)

st.markdown('<div class="status"><span>WORLDWIDE (SX)</span><span>MODULAR PATTERN ▸</span><span>SIDE A ◂▸ SIDE B</span><span>01:45:51</span></div>', unsafe_allow_html=True)
