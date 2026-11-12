"""Spotify playlist helper. Official Web API needs a free app's client id/secret (client-credentials flow).
Put them in .streamlit/secrets.toml as SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET, or in environment variables.
Without keys the player falls back to Spotify's embed + iFrame API (no track list)."""
import os, requests, streamlit as st

PLAYLIST = {"id": "2FoWNDK09Fps21vZiNjhu7", "name": "Chill ZZZ BGM", "owner": "SCBoo", "count": 110,
            "cover": "https://image-cdn-fa.spotifycdn.com/image/ab67706c0000da84a5d4020ef4b97bf79f2a855a"}

def _keys():
    try: return st.secrets["SPOTIFY_CLIENT_ID"], st.secrets["SPOTIFY_CLIENT_SECRET"]
    except Exception: return os.environ.get("SPOTIFY_CLIENT_ID"), os.environ.get("SPOTIFY_CLIENT_SECRET")

def has_keys():
    a, b = _keys(); return bool(a and b)

@st.cache_data(ttl=3600, show_spinner=False)
def get_tracks():
    """List of {name, artist, album, cover, dur (ms), uri}. Empty list if no keys or request fails."""
    cid, sec = _keys()
    if not (cid and sec): return []
    try:
        tok = requests.post("https://accounts.spotify.com/api/token", data={"grant_type": "client_credentials"}, auth=(cid, sec), timeout=8).json()["access_token"]
        url, out = f"https://api.spotify.com/v1/playlists/{PLAYLIST['id']}/tracks?limit=100", []
        while url and len(out) < 200:
            j = requests.get(url, headers={"Authorization": f"Bearer {tok}"}, timeout=8).json()
            for it in j.get("items", []):
                t = it.get("track")
                if not t or not t.get("uri"): continue
                imgs = t["album"].get("images") or []
                out.append({"name": t["name"], "artist": ", ".join(a["name"] for a in t["artists"]), "album": t["album"]["name"],
                            "cover": (imgs[1] if len(imgs) > 1 else imgs[0])["url"] if imgs else "", "dur": t["duration_ms"], "uri": t["uri"]})
            url = j.get("next")
        return out
    except Exception:
        return []