"""Music sheet sample loader for the dynamic Sonic Deck synthesizer.
Reads .json music sheets from ./music_sheets so users can add new sample musics
(chords, melodies, basslines, drum patterns, tempo, and mood tags) to make the
dynamic music richer and more complex."""
import json
import re
from pathlib import Path

SHEETS_DIR = Path(__file__).parent / "music_sheets"

FALLBACK_SHEET = {
    "id": "sanctuary_dusk",
    "title": "Sanctuary Dusk",
    "artist": "Formicapunk Synth",
    "mood": "ambient",
    "subreddits": ["ambientmusic", "slowliving", "SlowWeb"],
    "bpm": 74,
    "meter": "4/4",
    "swing": 0.06,
    "cutoff": 820,
    "arp_mode": "up",
    "bars": [
        {
            "name": "Amaj9",
            "bass": "A1",
            "pad": ["A3", "C#4", "E4", "G#4", "B4"],
            "keys": ["E4", "G#4", "B4", "C#5", "E5"],
            "melody": ["E5", None, "C#5", None, "B4", "G#4", None, "E4", None, "A4", "B4", None, "C#5", None, "B4", None],
        },
        {
            "name": "F#m9",
            "bass": "F#1",
            "pad": ["F#3", "A3", "C#4", "E4", "G#4"],
            "keys": ["C#4", "E4", "G#4", "A4", "C#5"],
            "melody": ["C#5", None, "A4", None, "G#4", "E4", None, "C#4", None, "F#4", "G#4", None, "A4", None, "E4", None],
        },
    ],
    "drums": {
        "kicks": [0, 6, 10],
        "snares": [4, 12],
        "hats": [0, 2, 4, 6, 8, 10, 12, 14],
    },
}


def load_sheets():
    """Load all valid .json music sheets from ./music_sheets, sorted by filename."""
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    sheets = []
    for path in sorted(SHEETS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("bars"):
                data.setdefault("id", path.stem)
                data.setdefault("title", path.stem.replace("_", " ").title())
                data.setdefault("artist", "Custom Sheet")
                data.setdefault("mood", "custom")
                data.setdefault("subreddits", [])
                data.setdefault("bpm", 96)
                data.setdefault("meter", "4/4")
                data.setdefault("swing", 0.04)
                data.setdefault("cutoff", 950)
                data.setdefault("arp_mode", "up")
                data["_file"] = path.name
                sheets.append(data)
        except Exception:
            continue
    return sheets or [FALLBACK_SHEET]


def save_sheet(sheet_data):
    """Save a new music sheet dictionary to ./music_sheets/<slug>.json and return its Path."""
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    raw_id = sheet_data.get("id") or sheet_data.get("title") or "custom_sheet"
    slug = re.sub(r"[^a-z0-9_]+", "_", raw_id.lower()).strip("_") or "custom_sheet"
    sheet_data["id"] = slug
    existing = list(SHEETS_DIR.glob("*.json"))
    prefix = f"{len(existing) + 1:02d}_"
    target = SHEETS_DIR / f"{prefix}{slug}.json"
    if (SHEETS_DIR / f"{slug}.json").exists():
        target = SHEETS_DIR / f"{slug}.json"
    clean = {k: v for k, v in sheet_data.items() if not k.startswith("_")}
    target.write_text(json.dumps(clean, indent=2), encoding="utf-8")
    return target
