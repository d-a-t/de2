"""Local music cache for the cassette deck.
- Reads audio files from ./music (or $SANCTUARY_MUSIC_DIR). Song name/artist come from the filename: "Title - Artist.mp3".
- Serves them to the browser through a tiny local HTTP server (with Range support so seeking works).
- Album cover: 1) Spotify search (needs SPOTIFY_CLIENT_ID/SECRET) -> 2) cover embedded in the MP3 (needs mutagen) -> 3) generated cassette art.
- Spotify matches are cached in ./cache/covers.json so each song is searched once."""
import os
import re
import json
import hashlib
import html
import base64
import threading
import mimetypes
import unicodedata
import http.server
import requests
import streamlit as st
from pathlib import Path
from urllib.parse import quote
from spotify import _keys, has_keys

MUSIC_DIR = Path(os.environ.get("SANCTUARY_MUSIC_DIR") or Path(__file__).parent / "music")
CACHE = Path(__file__).parent / "cache" / "covers.json"
EXT = {".mp3", ".m4a", ".wav", ".ogg", ".flac"}
PAL = [
    ("#ffe600", "#131722", "#ff6600"),
    ("#00f5ff", "#101827", "#ff007f"),
    ("#b7a6ff", "#14141a", "#ffe600"),
    ("#ff6600", "#0f1a1f", "#00f5ff")
]

class _Limited:
    def __init__(self, f, n):
        self.f = f
        self.n = n

    def read(self, k=-1):
        k = self.n if k is None or k < 0 else min(k, self.n)
        d = self.f.read(k)
        self.n -= len(d)
        return d

    def close(self):
        self.f.close()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(MUSIC_DIR), **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def send_head(self):
        rng = self.headers.get("Range")
        m = re.match(r"bytes=(\d*)-(\d*)", rng or "")
        if not m:
            return super().send_head()
        path = self.translate_path(self.path)
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404)
            return None
        size = os.fstat(f.fileno()).st_size
        a = int(m[1]) if m[1] else 0
        b = min(int(m[2]) if m[2] else size - 1, size - 1)
        f.seek(a)
        self.send_response(206)
        self.send_header("Content-Type", mimetypes.guess_type(path)[0] or "audio/mpeg")
        self.send_header("Content-Range", f"bytes {a}-{b}/{size}")
        self.send_header("Content-Length", str(b - a + 1))
        self.end_headers()
        return _Limited(f, b - a + 1)

    def copyfile(self, source, outputfile):
        """Suppress benign client disconnect errors when seeking or skipping tracks."""
        try:
            super().copyfile(source, outputfile)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass
        finally:
            if hasattr(source, "close"):
                source.close()

@st.cache_resource
def start_server():
    srv = None
    for port in (8765, 0):
        try:
            srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv.server_address[1]

def parse(stem):
    """'Time To Play - Sān-Z' -> ('Time To Play', 'Sān-Z')"""
    if " - " in stem:
        t, a = stem.rsplit(" - ", 1)
        return t.strip(), a.strip()
    return stem.strip(), "Unknown artist"

def _norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", s.lower())

def _ascii(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()

@st.cache_data(ttl=3000, show_spinner=False)
def _token():
    cid, sec = _keys()
    try:
        r = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(cid, sec),
            timeout=8
        )
        return r.json()["access_token"]
    except Exception:
        return ""

def spotify_search(title, artist):
    """Search Spotify for the song; accept a result only if its artist matches. Returns dict or None."""
    tok = _token()
    if not tok:
        return None
    for q in (f'track:"{title}" artist:"{artist}"', f"{title} {artist}", f"{_ascii(title)} {_ascii(artist)}"):
        try:
            r = requests.get(
                "https://api.spotify.com/v1/search",
                params={"q": q, "type": "track", "limit": 5},
                headers={"Authorization": f"Bearer {tok}"},
                timeout=8
            )
            if r.status_code != 200:
                continue
            for it in r.json()["tracks"]["items"]:
                names = " ".join(x["name"] for x in it["artists"])
                imgs = it["album"].get("images") or []
                if imgs and _norm(artist) and _norm(artist) in _norm(names):
                    chosen_img = (imgs[1] if len(imgs) > 1 else imgs[0])["url"]
                    return {
                        "cover": chosen_img,
                        "album": it["album"]["name"],
                        "url": it["external_urls"]["spotify"],
                        "match": f'{it["name"]} // {names}'
                    }
        except Exception:
            continue
    return None

def _embedded(p):
    try:
        from mutagen.id3 import ID3
        pics = ID3(str(p)).getall("APIC")
        if pics:
            return f"data:{pics[0].mime or 'image/jpeg'};base64," + base64.b64encode(pics[0].data).decode()
    except Exception:
        pass
    return None

def _dur(p):
    try:
        from mutagen import File
        return int(File(str(p)).info.length * 1000)
    except Exception:
        return 0

def gen_cover(title, artist):
    """Square generated cassette art, used when no cover can be found."""
    a, b, c = PAL[int(hashlib.md5((title + artist).encode()).hexdigest(), 16) % 4]
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='{b}'/><stop offset='1' stop-color='#0b0e14'/></linearGradient></defs>"
           f"<rect width='200' height='200' fill='url(#g)'/><rect width='200' height='12' fill='{a}'/><rect x='20' y='50' width='160' height='100' rx='10' fill='#e9e6f5'/><rect x='30' y='60' width='140' height='34' fill='#fff'/><rect x='30' y='84' width='140' height='8' fill='{c}'/>"
           f"<circle cx='70' cy='122' r='16' fill='#0b0e14'/><circle cx='130' cy='122' r='16' fill='#0b0e14'/><circle cx='70' cy='122' r='7' fill='{a}'/><circle cx='130' cy='122' r='7' fill='{a}'/>"
           f"<text x='36' y='78' font-family='monospace' font-size='12' font-weight='bold' fill='#0b0e14'>{html.escape(title[:14])}</text>"
           f"<text x='100' y='180' text-anchor='middle' font-family='monospace' font-size='11' fill='{a}'>NO COVER FOUND</text></svg>")
    return "data:image/svg+xml;utf8," + quote(svg)

def _read_cache():
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def clear_cover_cache():
    try:
        CACHE.unlink()
    except OSError:
        pass
    load_library.clear()

@st.cache_data(ttl=60, show_spinner=False)
def load_library():
    """List of track dicts for the player. Empty list if the music folder is missing/empty."""
    if not MUSIC_DIR.exists():
        return []
    port, covers, dirty, out = start_server(), _read_cache(), False, []
    for p in sorted(MUSIC_DIR.iterdir(), key=lambda x: x.name.lower()):
        if p.suffix.lower() not in EXT:
            continue
        title, artist = parse(p.stem)
        c = covers.get(p.name)
        if c is None and has_keys():
            c = spotify_search(title, artist) or {"miss": True}
            covers[p.name] = c
            dirty = True
        fb = gen_cover(title, artist)
        cover, album, sp, src, match = fb, "", "", "GENERATED", ""
        if c and not c.get("miss"):
            cover, album, sp, src, match = c["cover"], c["album"], c["url"], "SPOTIFY", c.get("match", "")
        else:
            emb = _embedded(p)
            if emb:
                cover, src = emb, "EMBEDDED"
        out.append({
            "name": title, "artist": artist, "album": album, "cover": cover,
            "fallback": fb, "dur": _dur(p), "url": f"http://127.0.0.1:{port}/{quote(p.name)}",
            "spotify": sp, "src": src, "match": match
        })
    if dirty:
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(covers, ensure_ascii=False, indent=1), encoding="utf-8")
    return out