import streamlit as st
from data import get_posts
 
st.set_page_config(page_title="Feed (baseline)", layout="centered")
posts, live = get_posts()
st.markdown("""<style>
.stApp{background:#dae0e6}
.p{background:#fff;border:1px solid #ccc;border-radius:4px;padding:10px 12px;margin-bottom:6px}
.p b{font-size:16px}.hot{color:#ff4500;font-weight:700}
.badge{background:#ff4500;color:#fff;border-radius:99px;padding:2px 9px;font-weight:700;animation:blink 1s infinite}
@keyframes blink{50%{opacity:.25}}
</style>""", unsafe_allow_html=True)
st.markdown('<h2>Home <span class="badge">17 new</span> <span class="badge">3 mentions</span></h2>', unsafe_allow_html=True)
st.caption("Live from Reddit" if live else "Sample posts (offline)")
if "n" not in st.session_state: st.session_state.n = 12
for i in range(st.session_state.n):                 # everything at once, no pause
    p = posts[i % len(posts)]
    st.markdown(f'<div class="p"><span class="hot">▲ {p["score"]}</span> r/{p["subreddit"]}<br><b>{p["title"]}</b><br>'
                f'<small>💬 {p["num_comments"]} · u/{p["author"]} · TRENDING NOW</small></div>', unsafe_allow_html=True)
if st.button("Load more", type="primary", use_container_width=True):   # infinite scroll stand-in
    st.session_state.n += 12; st.rerun()
 
