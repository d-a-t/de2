"""CHECKPOINT 3 - Sanctuary Feed. Pacing + glass/Frutiger Aero styling + menu + ambient audio.
Run: streamlit run v3_checkpoint_sanctuary.py"""
import time, streamlit as st, streamlit.components.v1 as components
from data import get_posts

st.set_page_config(page_title="Sanctuary Feed", page_icon="✨", layout="wide")
posts, live = get_posts()
S = st.session_state
S.setdefault("block", 1); S.setdefault("saved", []); S.setdefault("per", 3)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@500;800&family=Nunito:wght@500;700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #d9cffc, #bfe3f7);
        font-family: 'Nunito', sans-serif;
        color: #4b3f7a;
    }

    [data-testid="stSidebar"] {
        background: rgba(247, 244, 255, 0.75);
        backdrop-filter: blur(14px);
        border-right: 1.5px solid #a79bdc;
    }

    h1, h2, h3 {
        font-family: 'Unbounded', sans-serif !important;
        color: #4b3f7a !important;
        letter-spacing: -0.02em;
    }

    .title {
        font: 800 clamp(28px, 5vw, 48px) 'Unbounded', sans-serif;
        margin: 0 0 4px;
    }

    .title span {
        color: #7fc4e8;
        font-weight: 500;
    }

    .card {
        background: rgba(247, 244, 255, 0.74);
        border: 1.5px solid #a79bdc;
        border-radius: 26px;
        padding: 22px 26px;
        backdrop-filter: blur(14px);
        box-shadow: 0 10px 30px rgba(111, 91, 211, 0.18);
        margin-bottom: 6px;
    }

    .card .l {
        font: 800 11px 'Unbounded', sans-serif;
        color: #6f5bd3;
        margin-bottom: 8px;
    }

    .card h3 {
        font-size: 19px;
        margin: 0 0 8px;
    }

    .card p {
        color: #8478b8;
        max-width: 62ch;
        line-height: 1.55;
    }

    .card small {
        color: #8478b8;
    }

    .gap {
        height: 48px;
    }

    .orb {
        width: 84px;
        height: 84px;
        margin: 10px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, #fff, #7fc4e8 60%, #6f5bd3);
        animation: br 8s ease-in-out infinite;
    }

    @keyframes br {
        0%, 100% {
            transform: scale(0.7);
            opacity: 0.7;
        }
        50% {
            transform: scale(1.15);
            opacity: 1;
        }
    }

    .stButton > button {
        border-radius: 99px;
        border: 2px solid #a79bdc;
        font-family: 'Unbounded', sans-serif;
        font-weight: 800;
        font-size: 12px;
        color: #6f5bd3;
        background: rgba(255, 255, 255, 0.6);
    }

    .stButton > button:hover {
        background: #6f5bd3;
        color: #fff;
        border-color: #6f5bd3;
    }

    [data-testid="stRadio"] label p {
        color: #333333 !important;
        font-family: 'Nunito', sans-serif !important;
    }

    @media (prefers-reduced-motion: reduce) {
        .orb {
            animation: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### ✦ SANCTUARY")
    view = st.radio("Menu", ["Feed", "Settings", "Mem. Card", "Notepad", "Credits"], label_visibility="collapsed")
    components.html(
        """
        <div style="font: 700 13px 'Nunito', sans-serif; color: #8478b8;">
            ambient loop (generated live)<br>
            <button
                id="b"
                style="
                    margin-top: 8px;
                    width: 42px;
                    height: 42px;
                    border-radius: 50%;
                    border: 2px solid #a79bdc;
                    background: #fff8;
                    color: #6f5bd3;
                    cursor: pointer;
                "
            >▶</button>
            <input
                id="v"
                type="range"
                min="0"
                max="100"
                value="40"
                style="vertical-align: middle; accent-color: #6f5bd3;"
            >
        </div>

        <script>
            let c, m, on = 0, t, s = 0, o = [];
            const CH = [
                [261.6, 329.6, 392, 493.9],
                [220, 277.2, 329.6, 415.3],
                [174.6, 220, 261.6, 329.6],
                [196, 246.9, 293.7, 392]
            ];

            function hit(k, w) {
                const g = c.createGain();
                g.connect(m);

                if (k === 'k') {
                    const x = c.createOscillator();
                    x.frequency.setValueAtTime(110, w);
                    x.frequency.exponentialRampToValueAtTime(40, w + 0.15);

                    g.gain.setValueAtTime(0.5, w);
                    g.gain.exponentialRampToValueAtTime(0.001, w + 0.2);

                    x.connect(g);
                    x.start(w);
                    x.stop(w + 0.22);
                } else {
                    const n = c.createBuffer(1, c.sampleRate * 0.2, c.sampleRate);
                    const d = n.getChannelData(0);
                    for (let i = 0; i < d.length; i++) {
                        d[i] = Math.random() * 2 - 1;
                    }

                    const r = c.createBufferSource();
                    r.buffer = n;

                    const f = c.createBiquadFilter();
                    f.type = 'bandpass';
                    f.frequency.value = k === 's' ? 1800 : 7000;

                    g.gain.setValueAtTime(k === 's' ? 0.16 : 0.04, w);
                    g.gain.exponentialRampToValueAtTime(0.001, w + (k === 's' ? 0.14 : 0.04));

                    r.connect(f);
                    f.connect(g);
                    r.start(w);
                }
            }

            b.onclick = () => {
                if (on) {
                    clearInterval(t);
                    c.suspend();
                    on = 0;
                    b.textContent = '▶';
                    return;
                }

                if (!c) {
                    c = new AudioContext();
                    m = c.createGain();
                    m.gain.value = (v.value / 100) * 0.6;
                    m.connect(c.destination);

                    const lp = c.createBiquadFilter();
                    lp.frequency.value = 900;
                    lp.connect(m);

                    CH[0].forEach((f, i) => {
                        const x = c.createOscillator();
                        const g = c.createGain();
                        x.type = i % 2 ? 'triangle' : 'sine';
                        x.frequency.value = f;
                        g.gain.value = 0.12;
                        x.connect(g);
                        g.connect(lp);
                        x.start();
                        o.push(x);
                    });
                }

                c.resume();
                on = 1;
                b.textContent = '❚❚';

                t = setInterval(() => {
                    const w = c.currentTime + 0.05;
                    const q = s % 16;

                    if (q === 0 || q === 10) hit('k', w);
                    if (q === 4 || q === 12) hit('s', w);
                    if (q % 2 === 0) hit('h', w);

                    if (s % 128 === 0) {
                        const h = CH[(s / 128) % 4];
                        o.forEach((x, i) => x.frequency.setTargetAtTime(h[i], w, 2.5));
                    }
                    s++;
                }, 93.75);
            };

            v.oninput = () => {
                if (m) {
                    m.gain.value = (v.value / 100) * 0.6;
                }
            };
        </script>
        """,
        height=110,
    )
    st.caption("Live from Reddit" if live else "Sample posts (offline)")

st.markdown('<div class="title">Sanctuary<span> ✦ Feed</span></div>', unsafe_allow_html=True)

if view == "Feed":
    per = S.per
    shown = posts[: S.block * per]
    for i, p in enumerate(shown):
        st.markdown(f'<div class="card"><div class="l">✦ r/{p["subreddit"]}</div><h3>{p["title"]}</h3><p>{p["selftext"]}</p>'
                    f'<small>u/{p["author"]} · ▲ {p["score"]} · 💬 {p["num_comments"]}</small></div>', unsafe_allow_html=True)
        is_saved = p["title"] in S.saved
        if st.button("Saved ✦" if is_saved else "Save", key=f"s{i}"):
            S.saved.remove(p["title"]) if is_saved else S.saved.append(p["title"]); st.rerun()
        if (i + 1) % per == 0: st.markdown('<div class="gap"></div>', unsafe_allow_html=True)
    if len(shown) < len(posts):
        st.markdown('<div class="card" style="text-align:center"><div class="orb"></div></div>', unsafe_allow_html=True)
        if st.button("Breathe, then next block ✦", use_container_width=True):
            ph = st.empty()
            for sec in range(6, 0, -1):
                ph.markdown(f"<p style='text-align:center;color:#8478b8'>{'Breathe in...' if sec > 3 else 'Breathe out...'} {sec}</p>", unsafe_allow_html=True)
                time.sleep(1)
            S.block += 1; st.rerun()
    else:
        st.markdown('<div class="card" style="text-align:center"><div class="orb"></div><p>That is everything for now. The timeline ends here on purpose.</p></div>', unsafe_allow_html=True)
elif view == "Settings":
    S.per = st.select_slider("Posts per block", [2, 3, 4], value=S.per)
    st.caption("Fewer posts per block means a slower, quieter timeline.")
elif view == "Mem. Card":
    st.write("Nothing saved yet." if not S.saved else "")
    for t_ in S.saved: st.markdown(f"✦ {t_}")
elif view == "Notepad":
    st.text_area("Write what you noticed while reading.", key="note", height=220)
else:
    st.markdown("Visual direction inspired by dusqk's *Sanctuary OS* menu screens. Audio is a generated ambient loop, not the original recording. "
                "DRL: Contextual Awareness, Purposeful Innovation. OI: S (Sequence, Spacing), A (Aesthetics, Agency, Accessibility).")