"""Shared data loader: live Reddit JSON when online, bundled sample posts otherwise."""
import requests, streamlit as st

SAMPLE = [
 {"subreddit":"ambientmusic","title":"Long-form pieces that sound like a quiet room at dusk","author":"slowtide","score":1840,"num_comments":212,"selftext":"Collecting albums with no hurry in them. Recommendations welcome."},
 {"subreddit":"digitalminimalism","title":"I turned off every badge for a month. Here is what I noticed","author":"greylight","score":3120,"num_comments":405,"selftext":"My thumb kept reaching for the phone anyway. The habit outlasted the notifications."},
 {"subreddit":"Frutiger_Aero","title":"Early 2000s menu screens deserve a proper archive","author":"glassbutton","score":2275,"num_comments":96,"selftext":"Translucent panels, soft gradients, a calm idle loop."},
 {"subreddit":"jungle","title":"Why does breakbeat music feel so settling at low volume?","author":"ghostsnare","score":970,"num_comments":134,"selftext":"Fast drums, slow pads. The two speeds seem to cancel out."},
 {"subreddit":"slowliving","title":"A reading chair, one lamp, and a rule about phones","author":"lowlamp","score":1502,"num_comments":61,"selftext":"Twenty minutes a night. The phone lives in another room."},
 {"subreddit":"web_design","title":"Designing a feed that ends: what happens to time-on-page?","author":"finitescroll","score":688,"num_comments":77,"selftext":"Sessions got shorter and people reported feeling better afterwards."},
 {"subreddit":"VaporwaveAesthetics","title":"Console menus as comfort objects","author":"memcard","score":1210,"num_comments":58,"selftext":"Idling on a title screen was its own kind of rest."},
 {"subreddit":"Atlanta","title":"Small record shops are still where scenes get archived","author":"southsidecrate","score":2044,"num_comments":143,"selftext":"Flyers on the wall, mixtapes in a bin, someone who remembers everything."},
 {"subreddit":"mildlyinteresting","title":"This library kept its card catalog next to the new touchscreens","author":"dewey_decimal","score":4310,"num_comments":320,"selftext":"People use both. The drawers get more browsing than the screens."},
]

@st.cache_data(ttl=600, show_spinner=False)
def get_posts(subs="ambientmusic+digitalminimalism+Frutiger_Aero+jungle", limit=18):
    """Returns (posts, is_live)."""
    try:
        r = requests.get(f"https://www.reddit.com/r/{subs}/hot.json", params={"limit": limit},
                         headers={"User-Agent": "sanctuary-feed-class-project/0.1"}, timeout=6)
        r.raise_for_status()
        out = [{"subreddit":d["subreddit"],"title":d["title"],"author":d["author"],"score":d["score"],
                "num_comments":d["num_comments"],"selftext":(d.get("selftext") or "")[:220]}
               for d in (c["data"] for c in r.json()["data"]["children"]) if not d.get("over_18")]
        return (out, True) if out else (SAMPLE, False)
    except Exception:
        return SAMPLE, False