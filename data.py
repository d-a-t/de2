"""Shared data loader: live Reddit JSON when online, bundled sample posts otherwise.
Each post may carry an 'image' URL (Reddit preview/thumbnail). art() builds a generated fallback image."""
import html, hashlib, requests, streamlit as st
import xml.etree.ElementTree as ET
from urllib.parse import quote

SAMPLE = [
    {
        "subreddit": "ambientmusic",
        "title": "Long-form pieces that sound like a quiet room at dusk",
        "author": "slowtide",
        "score": 1840,
        "num_comments": 212,
        "selftext": "Collecting albums with no hurry in them. Recommendations welcome.",
        "image": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=800&q=80"
    },
    {
        "subreddit": "digitalminimalism",
        "title": "I turned off every badge for a month. Here is what I noticed",
        "author": "greylight",
        "score": 3120,
        "num_comments": 405,
        "selftext": "My thumb kept reaching for the phone anyway. The habit outlasted the notifications.",
        "image": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "subreddit": "Frutiger_Aero",
        "title": "Early 2000s menu screens deserve a proper archive",
        "author": "glassbutton",
        "score": 2275,
        "num_comments": 96,
        "selftext": "Translucent panels, soft gradients, a calm idle loop.",
        "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80"
    },
    {
        "subreddit": "jungle",
        "title": "Why does breakbeat music feel so settling at low volume?",
        "author": "ghostsnare",
        "score": 970,
        "num_comments": 134,
        "selftext": "Fast drums, slow pads. The two speeds seem to cancel out.",
        "image": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80"
    },
    {
        "subreddit": "slowliving",
        "title": "A reading chair, one lamp, and a rule about phones",
        "author": "lowlamp",
        "score": 1502,
        "num_comments": 61,
        "selftext": "Twenty minutes a night. The phone lives in another room.",
        "image": "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?auto=format&fit=crop&w=800&q=80"
    },
    {
        "subreddit": "web_design",
        "title": "Designing a feed that ends: what happens to time-on-page?",
        "author": "finitescroll",
        "score": 688,
        "num_comments": 77,
        "selftext": "Sessions got shorter and people reported feeling better afterwards.",
        "image": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80"
    },
    {
        "subreddit": "VaporwaveAesthetics",
        "title": "Console menus as comfort objects",
        "author": "memcard",
        "score": 1210,
        "num_comments": 58,
        "selftext": "Idling on a title screen was its own kind of rest.",
        "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80"
    },
    {
        "subreddit": "Atlanta",
        "title": "Small record shops are still where scenes get archived",
        "author": "southsidecrate",
        "score": 2044,
        "num_comments": 143,
        "selftext": "Flyers on the wall, mixtapes in a bin, someone who remembers everything.",
        "image": "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=800&q=80"
    },
    {
        "subreddit": "mildlyinteresting",
        "title": "This library kept its card catalog next to the new touchscreens",
        "author": "dewey_decimal",
        "score": 4310,
        "num_comments": 320,
        "selftext": "People use both. The drawers get more browsing than the screens.",
        "image": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=800&q=80"
    },
    {
        "subreddit": "cassetteculture",
        "title": "Found an old Walkman in my parent's attic. The belt was melted, but the magic is intact.",
        "author": "magnetic_tape",
        "score": 1420,
        "num_comments": 88,
        "selftext": "Spent an hour cleaning the capstan with isopropyl alcohol. Worth every second.",
        "image": "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=800&q=80"
    },
    {
        "subreddit": "CozyPlaces",
        "title": "Rain on the skylight while testing out a new CRT monitor setup",
        "author": "scanline_dream",
        "score": 2950,
        "num_comments": 164,
        "selftext": "Amber phosphors make late-night coding feel completely different.",
        "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80"
    }
]

def _image(d):
    try:
        u = d["preview"]["images"][0]["source"]["url"]
        if u: return html.unescape(u)
    except Exception: pass
    u = d.get("url_overridden_by_dest") or ""
    if u.lower().split("?")[0].endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")): return u
    t = d.get("thumbnail") or ""
    return t if t.startswith("http") else None

@st.cache_data(ttl=600, show_spinner=False)
def get_posts():
    # Using Reddit's public RSS feed which rarely triggers 403 bot blocks
    url = "https://www.reddit.com/r/all/.rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("--- [LOG] Attempting to fetch live Reddit RSS feed ---")
    try:
        response = requests.get(url, headers=headers, timeout=8)
        print(f"--- [LOG] Reddit RSS HTTP Status Code: {response.status_code} ---")
        
        if response.status_code == 200:
            # Parse XML RSS feed
            root = ET.fromstring(response.content)
            posts = []
            
            # Namespace mapping for Atom feed
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry')[:50]:
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                author_elem = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
                link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
                content_elem = entry.find('{http://www.w3.org/2005/Atom}content')
                
                title = title_elem.text if title_elem is not None else "Untitled"
                author = author_elem.text if author_elem is not None else "unknown"
                
                posts.append({
                    "title": title,
                    "selftext": "Live transmission pulled via RSS stream.",
                    "author": author.replace("/u/", ""),
                    "subreddit": "all",
                    "score": 42,
                    "num_comments": 0,
                    "image": None
                })
            
            if posts:
                print("--- [LOG] Returning LIVE RSS posts successfully ---")
                return posts, True
    except Exception as e:
        print(f"--- [LOG] Exception occurred during RSS fetch: {e} ---")
        
    print("--- [LOG] Falling back to offline sample posts ---")
    return SAMPLE, False

def art(seed, label):
    """Procedural 16:9 'tape frame' image, unique per post. Used when a post has no image."""
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    a, b, c = [("#d4ff1a","#1b1030","#ff5b1f"),("#34e6ff","#101827","#ff3fa4"),("#b7a6ff","#14141a","#d4ff1a"),("#ff5b1f","#0f1a1f","#34e6ff")][h % 4]
    cx, cy, r = 60 + (h >> 4) % 200, 50 + (h >> 12) % 60, 30 + (h >> 20) % 30
    bars = "".join(f"<rect x='{14+i*13}' y='{150-((h>>(i*2))%7+2)*8}' width='9' height='{((h>>(i*2))%7+2)*8}' fill='{a}' opacity='.85'/>" for i in range(23))
    lab = html.escape(label)[:22]
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 320 180'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='{b}'/><stop offset='1' stop-color='#0c0c10'/></linearGradient>"
           f"<pattern id='p' width='20' height='20' patternUnits='userSpaceOnUse'><path d='M20 0H0V20' fill='none' stroke='{a}' stroke-opacity='.15'/></pattern></defs>"
           f"<rect width='320' height='180' fill='url(#g)'/><rect width='320' height='180' fill='url(#p)'/><circle cx='{cx}' cy='{cy}' r='{r}' fill='{c}'/><circle cx='{cx}' cy='{cy}' r='{r+10}' fill='none' stroke='{c}' stroke-dasharray='4 5'/>"
           f"{bars}<rect x='0' y='0' width='320' height='10' fill='{a}'/><text x='12' y='30' font-family='monospace' font-size='12' font-weight='bold' fill='{a}'>r/{lab}</text></svg>")
    return "data:image/svg+xml;utf8," + quote(svg)