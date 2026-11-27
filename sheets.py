"""Music sheet sample loader for the dynamic Sonic Deck synthesizer.
Reads .yaml/.yml music sheets from ./music_sheets so users can add new sample musics
(chords, melodies, basslines, drum patterns, tempo, and mood tags) cleanly."""
import re
from pathlib import Path
import yaml

SHEETS_DIR = Path(__file__).parent / "music_sheets"

FALLBACK_SHEET = {
    "id": "sanctuary_dusk",
    "title": "Sanctuary Dusk",
    "artist": "Formicapunk Synth",
    "mood": "ambient",
    "subreddits": ["ambientmusic", "slowliving", "slowweb"],
    "bpm": 74,
    "meter": "4/4",
    "swing": 0.06,
    "cutoff": 820,
    "arp_mode": "up",
    "drums": {"kicks": [0, 6, 10], "snares": [4, 12], "hats": [0, 2, 4, 6, 8, 10, 12, 14]},
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
}

_DEFAULTS = {
    "artist": "Custom Sheet",
    "mood": "custom",
    "views": [],
    "subreddits": [],
    "bpm": 96,
    "meter": "4/4",
    "swing": 0.04,
    "cutoff": 950,
    "arp_mode": "up",
}


def load_sheets():
    """Load all valid .yaml/.yml music sheets from ./music_sheets, sorted by filename."""
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    paths = sorted(list(SHEETS_DIR.glob("*.yaml")) + list(SHEETS_DIR.glob("*.yml")))
    sheets = []
    for path in paths:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict) or not data.get("bars"):
            continue
        data.setdefault("id", path.stem)
        data.setdefault("title", path.stem.replace("_", " ").title())
        for key, val in _DEFAULTS.items():
            data.setdefault(key, list(val) if isinstance(val, list) else val)
        data["_file"] = path.name
        sheets.append(data)
    return sheets or [FALLBACK_SHEET]


def save_sheet(sheet_data):
    """Save a music sheet dictionary as YAML to ./music_sheets/<slug>.yaml."""
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    raw_id = sheet_data.get("id") or sheet_data.get("title") or "custom_sheet"
    slug = re.sub(r"[^a-z0-9_]+", "_", raw_id.lower()).strip("_") or "custom_sheet"
    sheet_data["id"] = slug
    direct = SHEETS_DIR / f"{slug}.yaml"
    if direct.exists():
        target = direct
    else:
        existing = list(SHEETS_DIR.glob("*.yaml")) + list(SHEETS_DIR.glob("*.yml"))
        target = SHEETS_DIR / f"{len(existing) + 1:02d}_{slug}.yaml"
    clean = {k: v for k, v in sheet_data.items() if not k.startswith("_")}
    target.write_text(yaml.safe_dump(clean, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return target
