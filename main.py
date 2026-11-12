import streamlit as st
from data import get_posts
 
st.set_page_config(page_title="Feed (pacing)", layout="centered")
posts, live = get_posts()
BLOCK = 3
st.session_state.setdefault("block", 1)
st.title("Slow feed")
st.caption("Live from Reddit" if live else "Sample posts (offline)")
 
shown = posts[: st.session_state.block * BLOCK]
for k in range(0, len(shown), BLOCK):
    for p in shown[k:k + BLOCK]:
        with st.container(border=True):
            st.caption(f"r/{p['subreddit']}")
            st.subheader(p["title"])
            st.write(p["selftext"])
            st.caption(f"u/{p['author']} · ▲ {p['score']} · 💬 {p['num_comments']}")
    st.write(""); st.write("")                      # intentional negative space between blocks
 
if len(shown) < len(posts):
    if st.button("Take a breath, then continue"):
        bar = st.progress(0, text="Breathe in...")
        for i in range(60):
            time.sleep(0.1)
            bar.progress((i + 1) / 60, text="Breathe in..." if i < 30 else "Breathe out...")
        st.session_state.block += 1; st.rerun()
else:
    st.info("That is everything for now. The timeline ends here on purpose.")
