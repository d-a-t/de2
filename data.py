"""Shared data loader: live Reddit JSON when online, bundled sample posts otherwise.
Each post may carry an 'image' URL (Reddit preview/thumbnail). art() builds a generated fallback image."""
import html, hashlib, random, requests, streamlit as st
import xml.etree.ElementTree as ET
from urllib.parse import quote

def generate_default_comments(title, subreddit):
    """Generates thematic fallback comments with scores if a post has no comments."""
    return [
        {
            "author": "signal_pilot",
            "score": 142,
            "time": "2h ago",
            "body": f"Fascinating perspective on r/{subreddit}. The signal clarity on this broadcast is remarkably high."
        },
        {
            "author": "cache_walker",
            "score": 68,
            "time": "1h ago",
            "body": "Logged this transmission onto memory tape. Adding to my weekly offline reading archive."
        },
        {
            "author": "ambient_core",
            "score": 24,
            "time": "30m ago",
            "body": "Subscribed to this frequency for updates. Looking forward to where this thread leads."
        }
    ]

SAMPLE = [
    {
        "subreddit": "ambientmusic",
        "title": "Long-form pieces that sound like a quiet room at dusk",
        "author": "slowtide",
        "score": 1840,
        "num_comments": 4,
        "selftext": "Collecting albums with no hurry in them. Recommendations welcome.",
        "image": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "drift_signal",
                "score": 428,
                "time": "4h ago",
                "body": "Hiroshi Yoshimura's 'Green' and Brian Eno's 'Thursday Afternoon'. 61 uninterrupted minutes of warm sunlight slowly moving across floorboards."
            },
            {
                "author": "reverb_dusk",
                "score": 215,
                "time": "3h ago",
                "body": "Chihei Hatakeyama's entire catalog fits this. Especially 'Minima Moralia'—warm tape hiss, submerged guitars, and gentle decay."
            },
            {
                "author": "analog_zen",
                "score": 87,
                "time": "1h ago",
                "body": "Stars of the Lid - 'And Their Refinement of the Decline'. Put it on at twilight; by the time it finishes, the room is completely pitch black."
            },
            {
                "author": "quiet_loops",
                "score": 34,
                "time": "45m ago",
                "body": "Warm vintage synth pads combined with rain on glass is the ultimate antidote to staring at spreadsheets all day."
            }
        ]
    },
    {
        "subreddit": "digitalminimalism",
        "title": "I turned off every badge for a month. Here is what I noticed",
        "author": "greylight",
        "score": 3120,
        "num_comments": 4,
        "selftext": "My thumb kept reaching for the phone anyway. The habit outlasted the notifications.",
        "image": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "phantom_buzz",
                "score": 680,
                "time": "6h ago",
                "body": "The phantom vibration syndrome takes at least two weeks to fade. You never realize how conditioned you are until you stop the pings."
            },
            {
                "author": "monochrome_soul",
                "score": 342,
                "time": "4h ago",
                "body": "Setting screen display to grayscale did even more for me. Instagram in black and white looks like a sad 1950s newspaper. Completely killed the dopamine loop."
            },
            {
                "author": "focus_state",
                "score": 129,
                "time": "2h ago",
                "body": "Did you find yourself opening email on desktop more often to compensate, or did total screen time actually drop?"
            },
            {
                "author": "greylight",
                "score": 95,
                "time": "1h ago",
                "body": "OP here: desktop time went up about 10% the first week, then cratered. I read two full paperbacks instead."
            }
        ]
    },
    {
        "subreddit": "Frutiger_Aero",
        "title": "Early 2000s menu screens deserve a proper archive",
        "author": "glassbutton",
        "score": 2275,
        "num_comments": 4,
        "selftext": "Translucent panels, soft gradients, a calm idle loop.",
        "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "aqua_gloss",
                "score": 512,
                "time": "8h ago",
                "body": "The PS3 XrossMediaBar (XMB) with dynamic waves was peak user interface design. Pure liquid crystal optimism."
            },
            {
                "author": "skeuo_dream",
                "score": 284,
                "time": "5h ago",
                "body": "Windows Vista Media Center had that low-frequency ambient hum and floating blue bubbles. It felt like living inside a luxury submarine."
            },
            {
                "author": "render_farm",
                "score": 110,
                "time": "3h ago",
                "body": "Everything today is flat gray rectangles. We traded gloss, water droplets, and depth for corporate efficiency."
            },
            {
                "author": "wii_sports_champ",
                "score": 43,
                "time": "1h ago",
                "body": "The Wii system menu music alone should be preserved in the Library of Congress."
            }
        ]
    },
    {
        "subreddit": "jungle",
        "title": "Why does breakbeat music feel so settling at low volume?",
        "author": "ghostsnare",
        "score": 970,
        "num_comments": 3,
        "selftext": "Fast drums, slow pads. The two speeds seem to cancel out.",
        "image": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "amen_brother",
                "score": 310,
                "time": "5h ago",
                "body": "It's the polyrhythm. The 160-170 BPM drums occupy the analytical part of your brain, while the 80 BPM half-time sub bass lulls the nervous system."
            },
            {
                "author": "timestretch94",
                "score": 145,
                "time": "3h ago",
                "body": "LTJ Bukem's 'Logical Progression' series at 3 AM with headphones on is basically a guided meditation."
            },
            {
                "author": "sub_frequency",
                "score": 62,
                "time": "1h ago",
                "body": "Old Akai S950 timestretching artifacts add this fuzzy warmth that clean digital DAWs can never quite replicate."
            }
        ]
    },
    {
        "subreddit": "slowliving",
        "title": "A reading chair, one lamp, and a rule about phones",
        "author": "lowlamp",
        "score": 1502,
        "num_comments": 3,
        "selftext": "Twenty minutes a night. The phone lives in another room.",
        "image": "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "linen_pages",
                "score": 389,
                "time": "7h ago",
                "body": "What wattage is the lamp bulb? I switched to a 2200K warm amber filament bulb and my sleep latency went down dramatically."
            },
            {
                "author": "lowlamp",
                "score": 178,
                "time": "5h ago",
                "body": "OP: 40W equivalent warm incandescent. Just enough to illuminate the page without bleeding into the corners of the room."
            },
            {
                "author": "cedar_tea",
                "score": 94,
                "time": "2h ago",
                "body": "Leaving the phone in the hallway charger felt like cutting an umbilical cord the first few nights. Now it's the most peaceful sanctuary in the house."
            }
        ]
    },
    {
        "subreddit": "web_design",
        "title": "Designing a feed that ends: what happens to time-on-page?",
        "author": "finitescroll",
        "score": 688,
        "num_comments": 3,
        "selftext": "Sessions got shorter and people reported feeling better afterwards.",
        "image": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "ux_heretic",
                "score": 204,
                "time": "4h ago",
                "body": "Infinite scroll was invented to maximize ad impressions at the expense of human circadian rhythms. Finishing a feed gives closure."
            },
            {
                "author": "metric_anxious",
                "score": 88,
                "time": "3h ago",
                "body": "Good luck convincing venture capital to adopt this metric. 'Time-well-spent' doesn't look as shiny in quarterly pitch decks."
            },
            {
                "author": "clean_markup",
                "score": 41,
                "time": "1h ago",
                "body": "This is why RSS readers and numbered pagination will always feel superior for intentional reading."
            }
        ]
    },
    {
        "subreddit": "VaporwaveAesthetics",
        "title": "Console menus as comfort objects",
        "author": "memcard",
        "score": 1210,
        "num_comments": 3,
        "selftext": "Idling on a title screen was its own kind of rest.",
        "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "dreamcast_spiral",
                "score": 402,
                "time": "6h ago",
                "body": "Sega Dreamcast BIOS menu: that slow orange swirl and the ticking sound of the internal clock battery that never stayed charged."
            },
            {
                "author": "gamecube_intro",
                "score": 219,
                "time": "4h ago",
                "body": "Rolling the GameCube cube around on the home screen while the kalimba chime echoed in the background."
            },
            {
                "author": "crt_scanline",
                "score": 98,
                "time": "2h ago",
                "body": "Booting up the PS2 in the dark and seeing the transparent towers populate based on your save file history was magical."
            }
        ]
    },
    {
        "subreddit": "Atlanta",
        "title": "Small record shops are still where scenes get archived",
        "author": "southsidecrate",
        "score": 2044,
        "num_comments": 3,
        "selftext": "Flyers on the wall, mixtapes in a bin, someone who remembers everything.",
        "image": "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "crate_digger404",
                "score": 460,
                "time": "5h ago",
                "body": "Wax 'N' Facts in Little Five Points and WuXTry in Decatur. The smell of cardboard, dust, and decades of local pressing history."
            },
            {
                "author": "peachtree_groove",
                "score": 198,
                "time": "3h ago",
                "body": "The handwritten genre dividers by the clerks have more curation wisdom than any Spotify algorithmic discovery playlist."
            },
            {
                "author": "dungeon_family_fan",
                "score": 85,
                "time": "1h ago",
                "body": "Found a promo single with Organized Noize production notes scribbled in Sharpie on the sleeve. You can't download that."
            }
        ]
    },
    {
        "subreddit": "mildlyinteresting",
        "title": "This library kept its card catalog next to the new touchscreens",
        "author": "dewey_decimal",
        "score": 4310,
        "num_comments": 3,
        "selftext": "People use both. The drawers get more browsing than the screens.",
        "image": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "archivist_dan",
                "score": 920,
                "time": "9h ago",
                "body": "Those solid oak drawers will still be functioning in 200 years. The touchscreen will be e-waste in 5 years when OS support drops."
            },
            {
                "author": "pencil_smell",
                "score": 430,
                "time": "7h ago",
                "body": "There's serendipity in thumbing through cards. You catch adjacent subjects you never would have thought to type into a search query."
            },
            {
                "author": "ui_skeptic",
                "score": 115,
                "time": "3h ago",
                "body": "Also, pulling out a drawer and hearing that satisfying wooden friction sound is therapeutic."
            }
        ]
    },
    {
        "subreddit": "cassetteculture",
        "title": "Found an old Walkman in my parent's attic. The belt was melted, but the magic is intact.",
        "author": "magnetic_tape",
        "score": 1420,
        "num_comments": 3,
        "selftext": "Spent an hour cleaning the capstan with isopropyl alcohol. Worth every second.",
        "image": "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "capstan_cleaner",
                "score": 350,
                "time": "6h ago",
                "body": "Get a multi-pack of assorted square rubber belts from eBay for $5. Once you swap the belt and deoxit the volume pot, it runs like 1986."
            },
            {
                "author": "type_iv_metal",
                "score": 180,
                "time": "4h ago",
                "body": "Nothing compares to that mechanical 'CHUNK' when you press down PLAY and feel the flywheel start spinning in your hand."
            },
            {
                "author": "magnetic_tape",
                "score": 72,
                "time": "2h ago",
                "body": "OP here: just replaced the belt! Popped in an old mixtape from high school. The wow and flutter gave me literal goosebumps."
            }
        ]
    },
    {
        "subreddit": "CozyPlaces",
        "title": "Rain on the skylight while testing out a new CRT monitor setup",
        "author": "scanline_dream",
        "score": 2950,
        "num_comments": 3,
        "selftext": "Amber phosphors make late-night coding feel completely different.",
        "image": "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "amber_glow",
                "score": 580,
                "time": "8h ago",
                "body": "Amber phosphor displays are criminally underrated. The gentle decay of the characters as you scroll text is hypnotic."
            },
            {
                "author": "flyback_hum",
                "score": 260,
                "time": "5h ago",
                "body": "That subtle 15kHz flyback transformer hum, rain pattering against glass, and a warm cup of roasted barley tea. Heaven."
            },
            {
                "author": "pixel_pitch",
                "score": 104,
                "time": "2h ago",
                "body": "Modern OLED screens are sharp, but CRTs have that natural phosphor bloom that makes text feel physical rather than digital."
            }
        ]
    },
    {
        "subreddit": "cyberdeck",
        "title": "Hand-wired cyberdeck with ortholinear mechanical keys and an e-ink sunlight terminal",
        "author": "grid_walker",
        "score": 3410,
        "num_comments": 4,
        "selftext": "Built inside a pelican case with a Raspberry Pi 5, 40% split keyboard, and 12-hour battery bank. Zero glare under direct midday sun.",
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "ortho_clack",
                "score": 710,
                "time": "5h ago",
                "body": "That e-ink refresh rate for vim editing is actually surprisingly crisp. How did you handle partial screen redraws?"
            },
            {
                "author": "pelican_mod",
                "score": 380,
                "time": "3h ago",
                "body": "This is the exact aesthetic William Gibson wrote about in Neuromancer. Functional, rugged, completely decoupled from cloud dependencies."
            },
            {
                "author": "grid_walker",
                "score": 195,
                "time": "2h ago",
                "body": "OP: Used Waveshare's fast-refresh IT8951 driver in greyscale mode. Typing lag is under 40ms, perfectly usable for long prose."
            },
            {
                "author": "battery_nerd",
                "score": 62,
                "time": "45m ago",
                "body": "12 hours of battery without a backlit panel means you could literally work in a tent during a week-long off-grid trek."
            }
        ]
    },
    {
        "subreddit": "synthesizers",
        "title": "FM synthesis sounds cold until you run it through an analog bucket-brigade delay",
        "author": "operator_six",
        "score": 1680,
        "num_comments": 3,
        "selftext": "Yamaha DX7 bell patches tend to sound brittle, but 300ms of BBD delay rolls off the digital glass and turns it into pure autumn twilight.",
        "image": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "chorus_depth",
                "score": 415,
                "time": "6h ago",
                "body": "Add a subtle analog CE-2 style chorus pedal right before the delay. The stereo modulation makes 4-operator patches sound enormous."
            },
            {
                "author": "filter_sweep",
                "score": 220,
                "time": "4h ago",
                "body": "The contrast between mathematically precise FM carrier/modulator ratios and unpredictable bucket-brigade clock noise is chef's kiss."
            },
            {
                "author": "tape_head",
                "score": 92,
                "time": "1h ago",
                "body": "Brian Eno's secret on Apollo: taking clinical Yamaha FM tones and printing them hot onto multitrack tape to squash the transients."
            }
        ]
    },
    {
        "subreddit": "mechanicalkeyboards",
        "title": "Lubed vintage Cherry MX Blacks in a solid milled brass chassis: typing feels like rain on stone",
        "author": "keeb_zenith",
        "score": 2890,
        "num_comments": 3,
        "selftext": "Harvested switches from a 1988 Wyse terminal board, cleaned in an ultrasonic bath, lubed with Krytox 205g0, and mounted on a 4mm brass plate.",
        "image": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "thock_artisan",
                "score": 610,
                "time": "7h ago",
                "body": "Nothing made today matches the natural smoothness of worn-in 35-year-old POM sliders. You can't simulate decades of keystrokes with factory lube."
            },
            {
                "author": "heavy_springs",
                "score": 280,
                "time": "5h ago",
                "body": "That deep acoustic thock must sound like footsteps on marble. Any sound test recording available?"
            },
            {
                "author": "vintage_terminal",
                "score": 105,
                "time": "2h ago",
                "body": "Saving old terminal switches from recycling bins is God's work. Those Wyse boards were built to survive artillery fire."
            }
        ]
    },
    {
        "subreddit": "lofihiphop",
        "title": "Tape saturation vs digital bitcrushing: why real magnetic flutter hits differently",
        "author": "sp404_drift",
        "score": 2130,
        "num_comments": 3,
        "selftext": "SP-404 vinyl sims are iconic, but running drum breaks through a cheap Marantz portable cassette recorder gives you non-linear saturation you can't fake.",
        "image": "https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "head_demag",
                "score": 490,
                "time": "6h ago",
                "body": "Tape compression acts like an intelligent dynamic EQ. It naturally tames harsh hi-hats while gluing the kick and snare together."
            },
            {
                "author": "sample_chop",
                "score": 235,
                "time": "3h ago",
                "body": "Let the battery run low on the cassette deck too—the slight voltage sag introduces unpredictable pitch wow that sounds like nostalgia itself."
            },
            {
                "author": "drum_machine_88",
                "score": 78,
                "time": "1h ago",
                "body": "Digital plugins simulate the wobble, but tape heads introduce genuine odd-order harmonics and magnetic hysteresis."
            }
        ]
    },
    {
        "subreddit": "minidisc",
        "title": "20 years later, the tactile click of inserting a MiniDisc is still unmatched by modern tech",
        "author": "sharp_md",
        "score": 3240,
        "num_comments": 3,
        "selftext": "Found my Sony MZ-R50 portable recorder. Spring-loaded magnesium alloy slot, physical volume wheel, and LCD remote control cord.",
        "image": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "atrac_master",
                "score": 740,
                "time": "8h ago",
                "body": "ATRAC compression was ahead of its time. And labeling tracks on that tiny dot-matrix display felt like programming a lunar lander."
            },
            {
                "author": "mech_satisfaction",
                "score": 390,
                "time": "5h ago",
                "body": "The mechanical shutter sliding open as the disc slides into the magnesium chassis... click-clack. Modern glass slabs feel completely lifeless in comparison."
            },
            {
                "author": "tokyo_commute",
                "score": 155,
                "time": "2h ago",
                "body": "I still record yearly physical audio mixtapes onto color-coded MiniDiscs. It gives an album a tangible beginning, middle, and end."
            }
        ]
    },
    {
        "subreddit": "futurebeats",
        "title": "Sampling dial-up modem handshakes and airport terminal chimes for ambient soundscapes",
        "author": "signal_corps",
        "score": 1190,
        "num_comments": 3,
        "selftext": "Pitched the 56k modem carrier sequence down three octaves and added shimmer reverb. The frequency negotiation sounds like whale songs from cyberspace.",
        "image": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "baud_rate",
                "score": 310,
                "time": "4h ago",
                "body": "V.90 negotiation tones contain pure FM chirp modulation. Pitched down -36 semitones, the high-band train becomes a rhythmic industrial pulse."
            },
            {
                "author": "changi_terminal",
                "score": 142,
                "time": "3h ago",
                "body": "Airport chimes are specifically engineered in major fifths and fourths to soothe travelers without causing auditory fatigue. Perfect ambient source material."
            },
            {
                "author": "granular_sky",
                "score": 55,
                "time": "1h ago",
                "body": "Granular synthesis on dial-up static turns glitch noise into lush, ethereal glass clouds."
            }
        ]
    },
    {
        "subreddit": "retrobattlestations",
        "title": "Dual CRT workstation running NetBSD with a custom orange amber monochrome theme",
        "author": "amber_terminal",
        "score": 4120,
        "num_comments": 4,
        "selftext": "Sony Trinitron Multiscan 20se hooked up via BNC cables. 1600x1200 at 85Hz. Text clarity is razor-sharp with zero motion blur.",
        "image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "phosphor_p3",
                "score": 980,
                "time": "9h ago",
                "body": "People who grew up on 60Hz LCDs have no idea how buttery smooth an 85Hz CRT raster scan actually feels on the eyes during text scrolling."
            },
            {
                "author": "bsd_daemon",
                "score": 460,
                "time": "6h ago",
                "body": "NetBSD on classic hardware is poetry. Fast boot, rock-solid stability, zero telemetry background daemons eating RAM."
            },
            {
                "author": "degauss_coil",
                "score": 180,
                "time": "2h ago",
                "body": "Please tell me you hit the manual degauss button every morning just to hear that thunderous CLUNK-BUZZ."
            },
            {
                "author": "amber_terminal",
                "score": 112,
                "time": "1h ago",
                "body": "OP: Every single morning without fail. It shakes the dust off the entire desk."
            }
        ]
    },
    {
        "subreddit": "IndieGaming",
        "title": "Why low-poly 1998 graphics create stronger environmental atmosphere than hyper-realism",
        "author": "poly_dithering",
        "score": 2780,
        "num_comments": 3,
        "selftext": "When geometry is sparse and textures are dithered 256-color pixels, your imagination does 50% of the rendering. The fog in Silent Hill worked because what you couldn't see was scarier.",
        "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "affine_texture",
                "score": 620,
                "time": "7h ago",
                "body": "Affine texture warping and vertex wobble gave early 3D worlds an uncanny, dreamlike instability. High fidelity leaves zero room for mystery."
            },
            {
                "author": "crt_shader_dev",
                "score": 310,
                "time": "4h ago",
                "body": "Pairing low poly models with pre-rendered ambient audio backgrounds created a sense of isolation that modern ray-traced open worlds completely fail to replicate."
            },
            {
                "author": "dreamfall",
                "score": 125,
                "time": "2h ago",
                "body": "Morrowind and Thief II felt like endless alien continents because your mind filled in the blanks between the low-res textures."
            }
        ]
    },
    {
        "subreddit": "audiophile",
        "title": "Open-back planar magnetic headphones changed how I perceive room reverberation",
        "author": "soundstage_flux",
        "score": 1940,
        "num_comments": 3,
        "selftext": "Listening to live jazz recordings: you can actually hear the dimensions of the venue and the acoustic bounce off the back brick wall.",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "planar_bass",
                "score": 450,
                "time": "6h ago",
                "body": "Planar drivers move air with lightning-fast transient response because the diaphragm is driven evenly across its entire surface. Zero cone breakup."
            },
            {
                "author": "room_acoustic",
                "score": 210,
                "time": "3h ago",
                "body": "The trade-off is zero noise isolation. If your refrigerator turns on in the kitchen, it joins the jazz quartet."
            },
            {
                "author": "tube_preamp",
                "score": 88,
                "time": "1h ago",
                "body": "Pair them with an OTL tube amp. The slight second-harmonic bloom rounds out planar precision into holographic warmth."
            }
        ]
    },
    {
        "subreddit": "analog",
        "title": "35mm grain study: Kodak Portra 400 shot at dusk through a 1978 Canon FD 50mm f/1.4",
        "author": "halation_glow",
        "score": 3670,
        "num_comments": 3,
        "selftext": "Neon signs reflecting on wet asphalt after an evening storm. Scanned flat on a Noritsu lab scanner with zero digital sharpening.",
        "image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "grain_structure",
                "score": 810,
                "time": "8h ago",
                "body": "That subtle red halation around the sodium-vapor streetlights is pure cinema. Digital sensors blow out highlights; film rolls them off gently."
            },
            {
                "author": "manual_focus",
                "score": 395,
                "time": "5h ago",
                "body": "The vintage Canon FD glass has a creamy spherical aberration wide open that gives portrait subjects a three-dimensional pop."
            },
            {
                "author": "darkroom_rats",
                "score": 140,
                "time": "2h ago",
                "body": "There is an honesty to film grain that digital noise simulation filters just can't match. It looks like particulate matter suspended in amber."
            }
        ]
    },
    {
        "subreddit": "chiptunes",
        "title": "Squeezing 4-channel polyphony out of the original Game Boy DMG-01 sound chip",
        "author": "lsdj_tracker",
        "score": 1850,
        "num_comments": 3,
        "selftext": "Two pulse channels, one custom 4-bit wave channel, and white noise. Restricting your toolset to 4 mono voices forces melodic ingenuity.",
        "image": "https://images.unsplash.com/photo-1531525645387-7f14be1bdbbd?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "pulse_width",
                "score": 470,
                "time": "5h ago",
                "body": "Fast arpeggios simulating 3-note chords at 60Hz is the greatest auditory trick in video game history."
            },
            {
                "author": "dmg_bassline",
                "score": 240,
                "time": "3h ago",
                "body": "The custom wave channel on the Game Boy can pump out astonishingly heavy sub-bass when you draw custom waveforms in LSDJ."
            },
            {
                "author": "prosound_mod",
                "score": 82,
                "time": "1h ago",
                "body": "Did you do the internal prosound mod to bypass the noisy headphone amp? The signal-to-noise ratio improves noticeably."
            }
        ]
    },
    {
        "subreddit": "unixporn",
        "title": "Tiling window manager with CRT scanline shaders, Tokyo Night palette, and custom polybar",
        "author": "neovim_ascetic",
        "score": 4580,
        "num_comments": 3,
        "selftext": "bspwm setup configured for pure keyboard navigation. No mouse required. Memory footprint on cold boot is 184MB.",
        "image": "https://images.unsplash.com/photo-1629654297299-c8506221ca97?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "dotfiles_pls",
                "score": 1120,
                "time": "10h ago",
                "body": "Dotfiles repository link where? That translucent terminal blur with the cyan borders is absolute aesthetic perfection."
            },
            {
                "author": "ram_optimizer",
                "score": 540,
                "time": "7h ago",
                "body": "Under 200MB RAM usage in 2026 feels like time travel. A single modern browser tab takes 800MB just to display a recipe."
            },
            {
                "author": "neovim_ascetic",
                "score": 260,
                "time": "4h ago",
                "body": "OP: Dotfiles pushed to GitHub! Polybar configs, alacritty yaml, and the picom shader are in the repo."
            }
        ]
    },
    {
        "subreddit": "typography",
        "title": "Bitmap fonts from 1990s arcade instruction cards are masterpieces of micro-legibility",
        "author": "pixel_grid",
        "score": 2150,
        "num_comments": 3,
        "selftext": "Fitting Japanese kanji and uppercase Latin characters into an 8x8 pixel grid with single-pixel stroke widths required insane spatial precision.",
        "image": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "raster_foundry",
                "score": 530,
                "time": "6h ago",
                "body": "Every pixel had to pull triple duty: silhouette, optical weight, and contrast. Modern vector fonts often feel sterile by comparison."
            },
            {
                "author": "capcom_archive",
                "score": 265,
                "time": "3h ago",
                "body": "Street Fighter II and Neo Geo font artists were true calligraphers working under extreme technological austerity."
            },
            {
                "author": "monospaced_life",
                "score": 90,
                "time": "1h ago",
                "body": "Using classic 8x8 bitmap fonts in programming terminal windows actually reduces eye strain once you get used to the crisp edges."
            }
        ]
    },
    {
        "subreddit": "SlowWeb",
        "title": "RSS feeds and personal static sites: rediscovering the quiet web of 2004",
        "author": "static_garden",
        "score": 3890,
        "num_comments": 3,
        "selftext": "Replaced my algorithmic social media feeds with 40 RSS feeds from independent blogs. No engagement algorithms, no rage bait, no promoted posts. Just human thoughts on their own schedule.",
        "image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "gemini_capsule",
                "score": 890,
                "time": "8h ago",
                "body": "The internet was so much healthier when it was a collection of distinct destinations you visited intentionally rather than a firehose dumped down your throat."
            },
            {
                "author": "feed_curator",
                "score": 410,
                "time": "5h ago",
                "body": "When an RSS feed hasn't updated in three months and suddenly a new essay appears, it feels like receiving a letter in the mail from an old friend."
            },
            {
                "author": "indie_web",
                "score": 175,
                "time": "2h ago",
                "body": "No likes, no follower counts, no quote tweets. Just ideas written because someone cared enough to write them."
            }
        ]
    },
    {
        "subreddit": "industrialdesign",
        "title": "Braun T3 pocket radio by Dieter Rams: the enduring power of honest design",
        "author": "less_is_better",
        "score": 2640,
        "num_comments": 3,
        "selftext": "Designed in 1958. A perforated speaker grille, a thumb dial, and an off-white housing. Decades later, Jony Ive used its exact silhouette for the original iPod.",
        "image": "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "ten_principles",
                "score": 630,
                "time": "7h ago",
                "body": "'Good design is as little design as possible.' Dieter Rams proved that functional clarity outlasts all fleeting fashion trends."
            },
            {
                "author": "tactile_knob",
                "score": 290,
                "time": "4h ago",
                "body": "The friction-damped thumbwheel tuning knob felt weighted and precise. You knew exactly where you were on the AM band by finger feel."
            },
            {
                "author": "bauhaus_line",
                "score": 110,
                "time": "1h ago",
                "body": "Timeless objects don't scream for attention. They sit quietly in the room until you need them, then perform flawlessly."
            }
        ]
    },
    {
        "subreddit": "fieldrecording",
        "title": "3 AM hydrophone recordings of ice cracking under geothermal pressure in an alpine lake",
        "author": "subsurface_mic",
        "score": 1760,
        "num_comments": 3,
        "selftext": "Lowered two Aquarian Audio hydrophones through a 20cm bore hole into a sub-alpine lake. The sound carries low-frequency acoustic pings like extraterrestrial sonar.",
        "image": "https://images.unsplash.com/photo-1483921020237-2ff51e8e4b22?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "sound_designer",
                "score": 430,
                "time": "5h ago",
                "body": "Ice cracking underwater generates instantaneous laser-like dispersive frequency sweeps. Sci-fi Foley artists have used this for blaster sounds since Star Wars."
            },
            {
                "author": "deep_freeze",
                "score": 205,
                "time": "3h ago",
                "body": "Listening to this on studio monitors shook my subwoofers down to 18Hz. The sheer physical power of shifting ice sheets is humbling."
            },
            {
                "author": "frost_resonance",
                "score": 74,
                "time": "1h ago",
                "body": "Do you plan to release a lossless 24-bit/96kHz recording pack? Ambient producers would pay good money for this."
            }
        ]
    },
    {
        "subreddit": "glitch_art",
        "title": "Circuit bending a Panasonic video mixer into pure cathode ray feedback loops",
        "author": "sync_loss",
        "score": 2310,
        "num_comments": 3,
        "selftext": "Solder-bridged the color-burst oscillator pins to the wipe pattern generator. Turning the rotary fader causes the video signal to tear into psychedelic neon ribbons.",
        "image": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "raster_warp",
                "score": 560,
                "time": "6h ago",
                "body": "Analog video feedback is chaotic mathematics visualized. A micro-millimeter adjustment of the gain potentiometer changes the entire fractal topology."
            },
            {
                "author": "vhs_rip",
                "score": 270,
                "time": "4h ago",
                "body": "Run that output straight into an old CRT television and film the screen with a high framerate lens. The optical moiré patterns will blow your mind."
            },
            {
                "author": "bent_circuit",
                "score": 98,
                "time": "1h ago",
                "body": "Old composite video signals have so much forgiving slop in the sync pulses. Digital HDMI just displays an HDCP black screen error if a single bit is wrong."
            }
        ]
    },
    {
        "subreddit": "solarpunk",
        "title": "Off-grid solar-powered Raspberry Pi node running a local mesh community forum",
        "author": "sun_node",
        "score": 3520,
        "num_comments": 3,
        "selftext": "Mounted on an apartment balcony with a 25W solar panel and 18650 lithium pack. Neighbors can connect via local Wi-Fi to share tools, plant cuttings, and repair advice.",
        "image": "https://images.unsplash.com/photo-1509391365360-2e959784a276?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "mesh_beacon",
                "score": 790,
                "time": "7h ago",
                "body": "Local-first, community-owned infrastructure is the future. If municipal power or ISP goes down, the local bulletin board keeps running."
            },
            {
                "author": "battery_chemist",
                "score": 380,
                "time": "4h ago",
                "body": "How does the battery handle freezing winter nights? Did you insulate the enclosure with neoprene?"
            },
            {
                "author": "sun_node",
                "score": 185,
                "time": "2h ago",
                "body": "OP: Double-walled 3D printed ABS box with closed-cell foam. The Pi's own CPU idle heat (approx 35°C) keeps the battery cells well above freezing!"
            }
        ]
    },
    {
        "subreddit": "vintageaudio",
        "title": "Re-capped a 1977 Marantz 2275 receiver. The blue dial illumination alone is therapy.",
        "author": "warm_bias",
        "score": 4210,
        "num_comments": 3,
        "selftext": "Replaced 48 dried-out electrolytic capacitors, cleaned all rotary pots with Caig DeoxIT, and replaced burnt incandescent fuse lamps with warm soft LEDs.",
        "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=800&q=80",
        "comments": [
            {
                "author": "gyro_touch",
                "score": 940,
                "time": "9h ago",
                "body": "The Gyro-Touch tuning flywheel! Spinning that horizontal metal wheel across the dial feels like operating a heavy precision Swiss lathe."
            },
            {
                "author": "transistor_warmth",
                "score": 470,
                "time": "6h ago",
                "body": "Those 1970s Marantz phono preamps have such an authoritative, punchy midrange. Vinyl sounds thick, organic, and effortless."
            },
            {
                "author": "soldering_iron",
                "score": 195,
                "time": "3h ago",
                "body": "Recapping a 2275 is a labor of love—that tone board is cramped. But hearing it power up cleanly without any DC offset click is the sweetest reward."
            }
        ]
    }
]

_COMMON_SUB_BANK = {
    "AskReddit": {
        "img": None,
        "topics": [
            ("What small daily habit quietly improved your life more than you expected?", "Started keeping a glass of water by my bed and leaving my phone in the hallway."),
            ("What movie scene gives you chills every single time you rewatch it?", "Mine is the docking sequence in Interstellar with the organ swelling."),
            ("What is a skill that takes less than 20 hours to learn but pays off forever?", "Touch typing and basic knife skills in the kitchen."),
            ("What obsolete piece of technology do you genuinely miss?", "Dedicated MP3 players with physical buttons you could operate inside your pocket."),
            ("What is the best piece of advice someone gave you in passing?", "Never take criticism from someone you wouldn't take advice from."),
            ("Which video game soundtrack still lives rent-free in your head?", "Chrono Trigger and Donkey Kong Country 2 still hit like magic."),
            ("What is something that used to be a luxury and is now an everyday annoyance?", "Constant instant reachability via smartphones."),
            ("What book made you sit in silence for ten minutes after finishing the last page?", "The Left Hand of Darkness by Ursula K. Le Guin."),
        ],
        "replies": [
            "Honestly, this thread is the exact reminder I needed today.",
            "I tried this six months ago and never looked back. Total game changer.",
            "Underrated answer right here. More people need to hear this.",
            "Came here expecting jokes, leaving with genuinely solid life advice.",
            "Hard disagree on the second half, though the first point is spot on.",
        ],
    },
    "todayilearned": {
        "img": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("TIL that Nintendo was founded in 1889 as a playing card company in Kyoto.", "They made handmade hanafuda cards long before video games existed."),
            ("TIL octopuses have three hearts, nine brains, and blue copper-based blood.", "Two hearts pump blood to the gills while the third circulates it to the body."),
            ("TIL the Voyager 1 Golden Record carries 90 minutes of music and greetings in 55 languages.", "It is currently over 15 billion miles away from Earth."),
            ("TIL sharks existed before trees and before Saturn's rings formed.", "Fossil evidence dates early shark species back more than 400 million years."),
            ("TIL Oxford University is older than the Aztec Empire by more than two centuries.", "Teaching existed at Oxford in 1096; Tenochtitlan was founded in 1325."),
            ("TIL honey found in ancient Egyptian tombs is still edible after 3,000 years.", "Low moisture and natural acidity prevent bacteria from growing."),
            ("TIL the 'Amen Break' is a 6-second drum solo from 1969 that birthed entire genres.", "It became the backbone of hip-hop, jungle, and drum and bass."),
            ("TIL astronauts grow up to 2 inches taller in space due to spinal decompression.", "Gravity normally compresses the vertebrae on Earth."),
        ],
        "replies": [
            "The fact that sharks predate trees always breaks my sense of deep time.",
            "There's a great documentary about the Amen Break and how it shaped electronic music.",
            "Imagine how wild it must be to taste 3,000-year-old tomb honey.",
            "Every time I read about Voyager 1, I'm amazed the transmitter still responds.",
            "Classic TIL, but still fascinating every time it pops up.",
        ],
    },
    "Showerthoughts": {
        "img": None,
        "topics": [
            ("Your stomach thinks all potatoes are mashed.", "Once you chew them, there's really no difference down there."),
            ("A library is just a physical cloud server for stories.", "Zero subscription fees and no battery anxiety."),
            ("Every mirror you've ever bought at a store was technically used.", "Someone else already looked into it before you."),
            ("Sleeping is basically a free trial of turning it off and back on again.", "Works surprisingly well for both computers and humans."),
            ("Music is just wiggly air that makes humans feel emotions.", "Different frequencies of pressure waves somehow equal nostalgia."),
            ("Reading a book is staring at marked dead trees and hallucinating vividly.", "Humans really invented telepathy across centuries."),
            ("The first person to hear a parrot talk must have been terrified.", "Imagine walking through the woods and a bird repeats your sentence."),
            ("We spend the first year of life learning to walk and talk, and the rest sitting down and being quiet.", "Strange reversal of priorities."),
        ],
        "replies": [
            "This is peak 2 AM ceiling-staring philosophy.",
            "I will never look at mashed potatoes the same way again.",
            "Wiggly air is honestly the most accurate description of music.",
            "Wait until you realize your tongue knows how every surface feels just by looking at it.",
        ],
    },
    "gaming": {
        "img": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Games that respect your time with a clean 12-hour campaign are a breath of fresh air.", "Not every title needs 150 hours of repetitive map icons."),
            ("What single-player game has the most atmospheric hub world?", "Firelink Shrine in Dark Souls and Majula in DS2 still feel unmatched."),
            ("Why do 2000s UI sound effects feel so much punchier than modern minimalist menus?", "Every button press had tactile weight and personality."),
            ("Replaying PS2 classics on a CRT makes you realize how much motion clarity we lost.", "Zero sample-and-hold blur makes 60fps look liquid smooth."),
            ("Indie devs are carrying the entire medium right now with weird, focused experiments.", "Small teams taking real creative risks."),
            ("Do you ever boot up a game just to hang out in the town and listen to the music?", "Sometimes the vibe is the whole point."),
            ("Local split-screen co-op deserves a massive comeback.", "Nothing beats sitting on the same couch with four controllers."),
            ("Dynamic music that layers instruments as you enter combat never gets old.", "Interactive audio elevates every boss fight."),
        ],
        "replies": [
            "Majula's acoustic guitar theme hits my soul every single time.",
            "Give me a tight 10-hour handcrafted campaign over a bloated 100-hour checklist any day.",
            "CRTs really were black magic for motion resolution.",
            "Adaptive soundtracks like in Portal 2 and Hades are pure art.",
            "Split-screen Halo 3 nights were peak gaming.",
        ],
    },
    "science": {
        "img": "https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Deep-sea researchers document bioluminescent organisms communicating in rhythmic pulses.", "Light patterns appear to coordinate feeding behavior at 2,000 meters."),
            ("New battery electrolyte formulation survives 4,000 charge cycles with minimal degradation.", "Solid-state prototypes continue moving closer to commercial scale."),
            ("Study finds forest mycorrhizal networks redistribute carbon to shaded seedlings.", "Underground fungal threads act like a slow-motion nutrient grid."),
            ("Astronomers map unexpected water vapor plumes on an icy outer-system moon.", "Spectroscopy data confirms active subsurface chemistry."),
            ("Acoustic metamaterials can now block low-frequency urban noise using thin panels.", "Tuned resonance chambers cancel hum without heavy foam."),
            ("Researchers synthesize biodegradable circuit boards from mycelium and cellulose.", "E-waste reduction could start at the substrate level."),
            ("Long-term sleep study links consistent wake times to sharper memory consolidation.", "Regularity matters even more than total weekend catch-up hours."),
            ("Ocean buoys detect subtle shifts in deep-current thermal transport.", "Continuous sensor arrays are improving climate model resolution."),
        ],
        "replies": [
            "Acoustic metamaterials for apartment walls would sell out overnight.",
            "Fungal networks being nature's fiber-optic grid never ceases to amaze me.",
            "4,000 cycles would mean a phone battery outlasts the rest of the hardware by a decade.",
            "Peer-reviewed replication will be key here, but the methodology looks solid.",
        ],
    },
    "technology": {
        "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Right-to-repair laws push modular laptops with user-swappable GPUs and ports.", "Standardized screws and schematic diagrams are making a comeback."),
            ("Open-source local AI models now run smoothly on modest desktop hardware.", "Privacy-first offline tooling is maturing rapidly."),
            ("E-ink monitors are finding a dedicated niche among writers and programmers.", "Zero flicker and paper-like contrast under natural light."),
            ("Why small, single-purpose gadgets often outlast do-everything smart devices.", "No forced cloud servers means they never get bricked."),
            ("Mesh networking experiments bring resilient community Wi-Fi to rural valleys.", "Low-power solar nodes bridging miles of terrain."),
            ("Web browsers are testing built-in reader modes that strip trackers and bloat.", "A 40KB article shouldn't require 18MB of JavaScript."),
            ("Physical knobs and tactile switches are returning to car dashboards.", "Safety testing proved touchscreens force eyes off the road."),
            ("Self-hosting personal photos and music on a tiny home server is easier than ever.", "Own your archive without monthly rent."),
        ],
        "replies": [
            "Bring back physical climate-control dials in every car immediately.",
            "A 18MB webpage for three paragraphs of text is modern web insanity.",
            "Self-hosting my music library on a local NAS was the best tech project I did this year.",
            "Right-to-repair is the single most important consumer tech movement right now.",
        ],
    },
    "movies": {
        "img": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Practical miniatures and matte paintings still age better than most modern CGI.", "Real light hitting physical models has undeniable weight."),
            ("What film has the best opening 10 minutes with almost no dialogue?", "Up, There Will Be Blood, and WALL-E come to mind immediately."),
            ("Why 90-minute tight thrillers feel rarer—and better—than 3-hour epics.", "Pacing is a lost art when editors aren't afraid to cut."),
            ("Sound design appreciation: the subtle room tone in quiet sci-fi films.", "Silence and low hums build more tension than loud explosions."),
            ("Rewatching Blade Runner 2049 on a good sound system is a religious experience.", "Every synth swell vibrates through the floorboards."),
            ("Which director consistently uses color palettes to tell half the story?", "Wong Kar-wai and Wes Anderson turn every frame into a painting."),
            ("Midnight repertory screenings of 35mm prints beat streaming at home every time.", "Hearing a crowd react together is irreplaceable."),
            ("What underrated soundtrack completely elevates its movie?", "Tron: Legacy and The Social Network are masterpieces."),
        ],
        "replies": [
            "The miniature work in The Thing and Blade Runner still looks jaw-dropping.",
            "Tight 95-minute movies are undefeated on a weeknight.",
            "WALL-E's first 30 minutes is a silent film masterclass.",
            "Nothing beats seeing a 35mm print in an old theater with real grain.",
        ],
    },
    "music": {
        "img": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Listening to an entire album front-to-back without skipping feels radical now.", "Track sequencing used to be an art form of its own."),
            ("What album sounds completely different—and better—when played at night?", "Burial's Untrue and Portishead's Dummy belong to 2 AM rain."),
            ("Why odd time signatures like 7/8 and 5/4 feel hypnotic when grooved right.", "Your brain stops counting and starts riding the cycle."),
            ("Collecting physical CDs and cassettes again because streaming catalogs vanish.", "Nothing beats owning an album nobody can delist."),
            ("What bassline is so good you immediately recognize the song in two notes?", "Chameleon by Herbie Hancock and Money by Pink Floyd."),
            ("Live studio sessions where you can hear the room acoustics beat over-polished mixes.", "Tiny imperfections make music breathe."),
            ("Game and anime OSTs are introducing millions to jazz fusion and breakbeat.", "Japanese city pop and Shibuya-kei live on in modern soundtracks."),
            ("What instrument tone immediately gives you goosebumps?", "A warm Rhodes electric piano through a gentle tremolo."),
        ],
        "replies": [
            "Untrue by Burial at 2 AM in a rainy city is an unmatched atmosphere.",
            "Odd meters like 7/8 feel natural once you stop overthinking the beat.",
            "Owning physical media means your favorite tracks never disappear over licensing.",
            "Rhodes + tape echo is instant serotonin.",
        ],
    },
    "pics": {
        "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Fog rolling over the valley right before sunrise this morning.", "Caught five minutes of pink light before it vanished."),
            ("An abandoned neon sign still humming in the alley after a summer storm.", "Reflections on wet asphalt never get old."),
            ("My grandfather's 1974 workbench, untouched since he retired.", "Every chisel and ruler has its exact silhouette on the pegboard."),
            ("Empty subway station in Tokyo at 1:15 AM after the last train.", "Quiet geometry and fluorescent hum."),
            ("Sunlight refracting through a prism onto an old stack of vinyl records.", "accidental rainbow across the sleeves."),
            ("Morning frost patterns on a greenhouse windowpane.", "Looks like fern leaves drawn in ice."),
            ("The view from a fire lookout tower above the clouds.", "Worth every mile of the hike up."),
            ("A stray cat sleeping on a warm CRT monitor at a repair shop.", "Peak cozy energy."),
        ],
        "replies": [
            "That pegboard silhouette organization is deeply satisfying.",
            "The reflections on wet pavement look straight out of a movie still.",
            "Cats always find the warmest piece of vintage electronics in any room.",
            "Amazing light—five minutes later and that shot is gone forever.",
        ],
    },
    "funny": {
        "img": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("My cat stared at an empty corner for 20 minutes and now I'm checking property listings.", "Either there's a ghost or a tiny moth and I'm not waiting to find out."),
            ("I bought a label maker and now nothing in my kitchen is safe.", "Even the toaster is labeled 'TOASTER'."),
            ("Accidentally said 'you too' when the delivery driver told me to enjoy my food.", "Guess I have to move to another city now."),
            ("Me at 11 PM: I will wake up at 6 AM and conquer the world. Me at 6 AM: snooze.", "Two completely different people inhabit this body."),
            ("Tried to take a 'quick' 20-minute nap and woke up in a different century.", "Didn't know what day, year, or planet it was."),
            ("My brain remembers every lyric to a 2006 commercial jingle, but not why I walked into the kitchen.", "Storage priorities are broken."),
            ("Put my phone down to rest my eyes, immediately picked up my bigger screen.", "Digital minimalism is going great."),
            ("Ordered one wrench online and it arrived in a box large enough for a refrigerator.", "At least I got four miles of bubble wrap."),
        ],
        "replies": [
            "The label maker phase is a rite of passage. Label the label maker next.",
            "Waking up from a 3-hour accidental nap with pillow creases on your face is pure time travel.",
            "Your cat definitely saw a greeble in the corner.",
            "I once said 'love you' to my dentist by accident. You'll recover in 5-7 years.",
        ],
    },
    "aww": {
        "img": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Adopted this senior shelter dog today and he immediately fell asleep on my shoes.", "Ten years old and already owns the living room."),
            ("Tiny ducklings learning how to navigate a garden step for the first time.", "Lots of wobbling, zero regrets."),
            ("My rescue cat finally trusted me enough to sit on my keyboard during work.", "Productivity dropped 100%, happiness rose 500%."),
            ("Two golden retrievers greeting each other with their favorite plush toys.", "Pure tail-wagging diplomacy."),
            ("A hedgehog curled up inside a knitted wool mitten.", "Peak winter coziness."),
            ("Baby otter floating on its back holding its mom's paw.", "Nature's sweetest anchor."),
            ("Crow brought a shiny bottle cap to the balcony after we left unsalted peanuts.", "Building an avian trade network."),
            ("Golden hour nap in a sunbeam on the living room rug.", "Charging solar batteries."),
        ],
        "replies": [
            "Thank you for adopting a senior pup! They have the gentlest souls.",
            "If a cat sits on your keyboard, it's legally a mandatory break.",
            "A crow trade network is the ultimate neighborhood perk.",
            "10/10 would let him sleep on my shoes forever.",
        ],
    },
    "LifeProTips": {
        "img": None,
        "topics": [
            ("LPT: Keep a 'done' list alongside your to-do list so you actually see your progress.", "Reduces end-of-day burnout dramatically."),
            ("LPT: If a task takes less than two minutes, do it immediately instead of scheduling it.", "Stops tiny chores from piling into a mountain."),
            ("LPT: Freeze leftover coffee in ice cube trays for iced coffee that never waters down.", "Simple, cheap, and works every summer."),
            ("LPT: Take a photo of the back of your router/TV before unplugging cables to move.", "Saves 30 minutes of squinting at ports later."),
            ("LPT: Set your phone to grayscale two hours before bed to make scrolling boring.", "Your brain naturally puts it down faster."),
            ("LPT: Always pack a spare pair of socks and a small flashlight in your car glovebox.", "You only need them once to be glad they're there."),
            ("LPT: Read the 3-star reviews on products—they're usually the most honest and detailed.", "Less hype, less rage, more real pros and cons."),
            ("LPT: Rename your saved files with YYYY-MM-DD at the start so they sort chronologically.", "Future you will thank present you."),
        ],
        "replies": [
            "YYYY-MM-DD is the only sane date format for file naming.",
            "The 3-star review trick is genuinely the smartest shopping habit.",
            "Grayscale mode before bed cut my late-night screen time in half.",
            "Coffee ice cubes are elite-tier summer prep.",
        ],
    },
    "explainlikeimfive": {
        "img": None,
        "topics": [
            ("ELI5: Why does music sound sadder in a minor key and happier in a major key?", "Frequency ratios and cultural conditioning both play a role."),
            ("ELI5: How do noise-canceling headphones erase sound using more sound?", "Destructive wave interference flips the waveform upside down."),
            ("ELI5: Why does time seem to speed up as we get older?", "Fewer novel memories per year makes stretches blend together."),
            ("ELI5: How does a vinyl record needle turn tiny plastic grooves into a full orchestra?", "Microscopic left-right and up-down vibrations drive a tiny magnet."),
            ("ELI5: Why do we see different colors on a screen using only red, green, and blue dots?", "Human eyes have three types of color cones that blend those signals."),
            ("ELI5: How does an airplane wing actually keep a heavy metal tube in the sky?", "Air pressure differences and downward deflection of airflow."),
            ("ELI5: Why does hot water freeze faster than cold water in certain conditions?", "The Mpemba effect involves convection, evaporation, and supercooling."),
            ("ELI5: How do submarines navigate underwater without GPS signals?", "Inertial gyroscopes, sonar mapping, and ocean floor charts."),
        ],
        "replies": [
            "Think of noise canceling like two opposite ocean waves meeting and flattening out!",
            "The vinyl needle explanation still feels like magic—a rock dragging through plastic makes a symphony.",
            "Novelty compressing perceived time is why traveling makes a weekend feel like a week.",
            "Super clear breakdown, thank you!",
        ],
    },
    "space": {
        "img": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("James Webb captures crystal-clear infrared rings around a distant dusty star.", "Each concentric shell marks a periodic stellar wind pulse."),
            ("Perseverance rover spots layered sedimentary rocks in an ancient Martian delta.", "Clear signs of slow-moving water billions of years ago."),
            ("Amateur astronomers photograph Jupiter's Great Red Spot from a backyard 8-inch Dobsonian.", "Lucky imaging stacks thousands of frames into sharp detail."),
            ("Why Titan's thick nitrogen atmosphere makes it one of the most fascinating moons.", "Methane rain, liquid lakes, and low gravity."),
            ("Observing the Orion Nebula through binoculars on a moonless winter night.", "That faint fuzzy patch is a stellar nursery 1,344 light-years away."),
            ("How solar sails use pure photon momentum to propel spacecraft without fuel.", "Sunlight itself becomes the wind."),
            ("Mapping the cosmic web: galaxies arranged along vast filaments of dark matter.", "The universe looks remarkably like a neural network at grand scale."),
            ("Listening to radio emissions from Saturn converted into eerie audio waves.", "Plasma oscillations sound like a sci-fi synth pad."),
        ],
        "replies": [
            "Saturn's radio emissions genuinely sound like an ambient modular synth.",
            "Backyard astrophotography with lucky imaging blows my mind every time.",
            "Titan having methane rain and thick haze makes it feel like a retro sci-fi cover.",
            "We are literally stardust looking back at stellar nurseries.",
        ],
    },
    "books": {
        "img": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Finished Neuromancer for the first time—wild how much cyberpunk DNA started in 1984.", "The opening line about a dead television channel still hits hard."),
            ("What cozy, low-stakes sci-fi or fantasy novel feels like a warm cup of tea?", "Becky Chambers' Monk & Robot series is pure comfort."),
            ("Why secondhand paperbacks with someone else's train ticket inside feel special.", "Every used book carries a quiet little history."),
            ("Reading 20 pages every morning with coffee instead of checking the news.", "Completely changes the tone of the entire day."),
            ("What non-fiction book reads like a gripping thriller?", "Endurance by Alfred Lansing and The Devil in the White City."),
            ("Appreciation for public libraries: audiobooks, quiet desks, and zero algorithms.", "One of the finest inventions in human civilization."),
            ("Which short story collection can you recommend in a heartbeat?", "Stories of Your Life and Others by Ted Chiang."),
            ("Building a home bookshelf slowly over ten years instead of buying it all at once.", "A map of everywhere your curiosity has traveled."),
        ],
        "replies": [
            "Ted Chiang's short stories stay with you for years.",
            "Switching morning news for 20 pages of fiction saved my sanity.",
            "Found a 1978 boarding pass inside a used Ursula Le Guin paperback once—framed it!",
            "Public libraries are undefeated.",
        ],
    },
    "food": {
        "img": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Homemade ramen broth simmered for 10 hours with charred ginger and kombu.", "Worth every minute of patience."),
            ("A cast-iron skillet, good butter, and sourdough bread: simple comfort perfection.", "Crispy edges and a soft center."),
            ("What cheap pantry ingredient instantly upgrades almost any savory dish?", "A dash of miso paste or toasted sesame oil."),
            ("First attempt at baking crusty no-knead Dutch oven bread.", "That crackle sound as it cools on the rack is pure joy."),
            ("Midnight street tacos from a tiny cart on the corner always beat fine dining.", "Charred onion, fresh cilantro, lime, done."),
            ("Learning to make proper French-style soft-scrambled eggs changed breakfast forever.", "Low heat, constant stirring, take it off before it looks done."),
            ("Roasted garlic spread on warm focaccia with flaky sea salt.", "The entire apartment smells incredible."),
            ("Why cold leftover pizza at 9 AM hits a completely different frequency.", "Unexplained culinary physics."),
        ],
        "replies": [
            "Miso paste in brown butter pasta is an absolute cheat code.",
            "Hearing fresh bread crackle as it cools is top-tier ASMR.",
            "Low-and-slow scrambled eggs take five extra minutes and taste 10x better.",
            "Drop the ramen tare recipe please!",
        ],
    },
    "programming": {
        "img": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Deleting 800 lines of over-engineered abstraction and replacing it with 40 clean lines.", "Best feeling in software engineering."),
            ("Why YAML configs are so much nicer to edit by hand than nested JSON.", "Comments, clean indentation, and no trailing-comma headaches."),
            ("Spent 3 hours debugging a race condition that turned out to be a cached browser tab.", "We've all been there at least once."),
            ("Writing small single-file tools with zero external dependencies feels refreshing.", "Fast, portable, and readable years later."),
            ("The magic of keyboard-driven editors and terminal workflows.", "Once muscle memory kicks in, editing flows like thought."),
            ("Documenting the 'why' instead of the 'what' makes codebases age gracefully.", "Future maintainers will silently thank you."),
            ("Building small creative audio/visual side projects just for the fun of it.", "Reminds you why you started coding in the first place."),
            ("Automated tests that run in under 2 seconds make refactoring fearless.", "Instant feedback loop changes everything."),
        ],
        "replies": [
            "Deleting code is always more satisfying than writing it.",
            "YAML + clean helper functions is unbeatable for readable configs.",
            "That cached tab bug hits way too close to home.",
            "Side projects with synths and visuals keep the spark alive!",
        ],
    },
    "EarthPorn": {
        "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Alpine granite peaks glowing amber at alpenglow in the Dolomites.", "Zero filters, just crisp mountain air at 2,800m."),
            ("Misty cedar forest after autumn rain in the Pacific Northwest.", "Everything smelled like moss and wet pine."),
            ("Mirror-still glacial lake reflecting the Milky Way before dawn.", "Silence so complete you could hear your heartbeat."),
            ("Basalt sea stacks standing against turquoise swells in Iceland.", "Raw volcanic geometry shaped by the North Atlantic."),
            ("Golden aspens along a winding mountain pass in late October.", "Peak autumn color lasted only four days."),
            ("Morning mist rising off a quiet fjord in western Norway.", "Waterfalls cascading straight down mossy cliffs."),
            ("Red sandstone canyons catching the last slant of desert sunlight.", "Warm terracotta shadows stretching for miles."),
            ("Snow-dusted pines framing a frozen waterfall in Banff.", "Crisp -12°C morning with bluebird skies."),
        ],
        "replies": [
            "The sheer scale of those granite walls is breathtaking.",
            "Pacific Northwest moss and cedar after rain is heaven on Earth.",
            "Incredible reflection—looks like a glass mirror.",
            "Adding this trail to my bucket list immediately.",
        ],
    },
    "DIY": {
        "img": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Restored a thrifted 1960s desk lamp with braided cloth cord and a brass dimmer.", "Total cost under $25 and built like a tank."),
            ("Built custom walnut monitor stand and cable tray for my home desk.", "Finished with three coats of tung oil."),
            ("Repaired a sticky cassette deck mechanism with fresh silicone grease and a new belt.", "Runs quieter than the day it left the factory."),
            ("Framed old transit maps and vintage concert posters with thrifted oak frames.", "Instant character for a bare hallway."),
            ("Made a passive acoustic phone speaker dock out of a scrap block of maple.", "Warm midrange resonance without any batteries."),
            ("Soldered a custom mechanical macro pad with a rotary encoder knob.", "Turning a physical dial for volume beats keyboard shortcuts."),
            ("Refinished a beaten-up mid-century coffee table found on the curb.", "Sanding through 40 years of varnish revealed gorgeous teak grain."),
            ("Organized every stray charging cable into labeled canvas pouches.", "No more tangled drawer monsters."),
        ],
        "replies": [
            "Braided cloth cord on vintage brass lamps is an instant upgrade.",
            "Curbside teak finds are the dream—nothing beats real solid wood.",
            "A physical rotary knob for volume should be mandatory on every desk.",
            "Clean cable management is pure peace of mind.",
        ],
    },
    "history": {
        "img": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("The Antikythera mechanism: a 2,000-year-old bronze astronomical analog computer.", "Precision gearwork centuries ahead of its era."),
            ("How pneumatic tube networks once delivered mail across entire cities at 30 mph.", "Paris had nearly 300 miles of underground brass tubes."),
            ("Letters from 19th-century lighthouse keepers reveal quiet, disciplined daily routines.", "Pages filled with weather logs, books read, and passing ships."),
            ("Before standardized time zones, every town set its clock by local solar noon.", "Railroads forced the world to synchronize clocks."),
            ("The 1970s Xerox PARC engineers who invented the GUI, Ethernet, and laser printing.", "One small lab shaped fifty years of computing."),
            ("Ancient Roman concrete self-heals cracks using reactive lime clasts.", "Harbor piers have survived 2,000 years of saltwater waves."),
            ("How medieval scribes created vibrant blue pigments from lapis lazuli.", "More expensive than gold leaf at the time."),
            ("Early mechanical synthesizers like the Telharmonium weighed 200 tons.", "It streamed live music over telephone lines in 1906."),
        ],
        "replies": [
            "Paris's pneumatic mail tubes feel straight out of steampunk fiction.",
            "Xerox PARC in the 70s had an absurd concentration of genius.",
            "200-ton synthesizer streaming over phone lines in 1906 is wild!",
            "Roman marine concrete outlasting modern rebar concrete is humbling.",
        ],
    },
    "Art": {
        "img": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Gouache study of rain-soaked neon storefronts at dusk.", "Opaque matte pigment makes the highlights pop."),
            ("Ink and watercolor sketchbooks filled during daily train commutes.", "20 minutes a day adds up to hundreds of scenes."),
            ("Why limited 4-color palettes create stronger mood than using every color.", "Constraint forces harmony."),
            ("Linocut printmaking: carving textures by hand and pulling the first proof.", "The tactile press reveal never gets old."),
            ("Pixel art landscapes inspired by 1990s PC adventure games.", "Dithering skies with just 16 colors."),
            ("Charcoal figure studies focusing on dramatic chiaroscuro lighting.", "Finding form through shadow alone."),
            ("Risograph printing: fluorescent pink and cyan ink layers slightly off-register.", "Beautiful analog imperfection."),
            ("Architectural isometric drawings of cozy retro-futuristic apartments.", "Tiny details in every corner."),
        ],
        "replies": [
            "Risograph pink + cyan layering is pure visual candy.",
            "A 4-color palette forces every hue to work together—love the discipline.",
            "Daily train sketchbook routines produce the most honest observational art.",
            "Matte gouache under warm light has such a velvety texture.",
        ],
    },
    "photography": {
        "img": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Shooting a single 50mm prime lens for a whole year teaches you to frame with your feet.", "You start seeing focal lengths before raising the camera."),
            ("Why overcast days give the softest, most flattering natural light.", "The sky turns into a giant diffused softbox."),
            ("Rediscovering an old CCD digital point-and-shoot from 2005.", "Warm color science and nostalgic flash look."),
            ("Night street photography after rain using a fast f/1.8 lens.", "Puddles double every neon reflection."),
            ("Printing your favorite 10 photos of the year instead of leaving them on a drive.", "Physical prints hit differently on a wall."),
            ("How black-and-white contrast strips away distraction and reveals pure geometry.", "Light, shadow, and line."),
            ("Developing C-41 color film at home in a kitchen sink.", "Surprisingly approachable once you nail temperature control."),
            ("Long-exposure coastal waves turning turbulent surf into smooth mist.", "30 seconds with a 10-stop ND filter."),
        ],
        "replies": [
            "A 50mm prime for a full year is the best photography bootcamp.",
            "Printing photos is essential—screens flatten everything.",
            "Old 2000s CCD sensors really do have a distinct filmic warmth.",
            "Overcast softbox light is undefeated for portraits.",
        ],
    },
    "gadgets": {
        "img": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Pocket-sized Field Notes + brass pen: still the fastest note-taking device ever made.", "Zero boot time, infinite battery."),
            ("Compact retro handhelds have perfected pick-up-and-play emulation.", "20 minutes of GBA on a lunch break feels effortless."),
            ("Why physical mute switches and dedicated volume wheels feel so premium.", "Instant hardware certainty without menus."),
            ("Solar-powered Casio G-Shock watches that run 20 years without a battery swap.", "Peak functional reliability."),
            ("Portable USB-C DACs turning any pair of wired IEMs into a studio rig.", "Massive clarity upgrade for $30."),
            ("E-reader with warm amber frontlight for late-night reading without eye strain.", "Holds thousands of books on a two-month charge."),
            ("Mechanical kitchen timers that tick softly and ring with a real brass bell.", "No phone distractions while cooking."),
            ("Compact GaN chargers shrunk laptop power bricks to the size of an ice cube.", "One tiny brick powers everything in a backpack."),
        ],
        "replies": [
            "Solar Casio + pocket notebook + wired IEMs is an unbeatable EDC.",
            "A real brass bell kitchen timer is so much nicer than a phone alarm.",
            "Dedicated hardware mute switches should be on every device.",
            "GaN chargers saved half the space in my travel bag.",
        ],
    },
    "television": {
        "img": "https://images.unsplash.com/photo-1522869635100-9f4c5e86aa37?auto=format&fit=crop&w=800&q=80",
        "topics": [
            ("Miss the era of 22-episode seasons with cozy filler episodes where characters just hang out.", "World-building breathes when not every minute is plot-critical."),
            ("What TV show has the best title sequence you never skip?", "Severance, Cowboy Bebop, and True Detective Season 1."),
            ("Miniseries that tell a complete, tight story in 8 episodes and actually end.", "Resolution beats dragging a show for seven seasons."),
            ("Late-night animation blocks shaped an entire generation's taste in electronic music.", "Those bumps between shows were pure art."),
            ("What sitcom still holds up effortlessly twenty years later?", "30 Rock and Parks and Recreation have jokes every five seconds."),
            ("Sci-fi shows that focus on atmosphere and mystery over endless CGI battles.", "Station Eleven and Dark reward patient viewers."),
            ("The soundtracks of 90s detective dramas were sneaky jazz showcases.", "Saxophone over rainy cityscapes."),
            ("Watching one episode a week with friends instead of binging in a weekend.", "Anticipation and weekly theories make shows twice as fun."),
        ],
        "replies": [
            "Cowboy Bebop's opening is mandatory viewing every single episode.",
            "Adult Swim bumps introduced me to half my favorite ambient and hip-hop artists.",
            "Weekly episode discussions are so much better than weekend binges.",
            "Filler episodes are where you actually fall in love with the cast.",
        ],
    },
    "philosophy": {
        "img": None,
        "topics": [
            ("Marcus Aurelius's Meditations was never meant to be published—it was his private journal.", "Reading someone's honest self-reminders feels remarkably modern."),
            ("Why boredom is essential for creativity and original thought.", "Constant stimulation leaves zero room for your mind to wander."),
            ("Alan Watts on music: you don't dance to reach the end of the song.", "The point of the melody is the playing itself."),
            ("The difference between solitude and loneliness: one restores, the other drains.", "Learning to enjoy your own company is a quiet superpower."),
            ("Diogenes carrying a lantern in broad daylight remains peak philosophical performance art.", "Minimalism taken to its absolute extreme."),
            ("Why slow craftsmanship brings meaning in an age of instant convenience.", "Effort and care leave a trace you can feel."),
            ("Stoicism isn't suppressing emotion—it's separating what you control from what you don't.", "Actionable clarity under pressure."),
            ("How architecture and room lighting subtly shape how we think and feel.", "Warm, quiet spaces invite deeper reflection."),
        ],
        "replies": [
            "Alan Watts's music analogy completely reframed how I think about daily routines.",
            "Protecting 20 minutes of pure boredom a day is where all my best ideas come from.",
            "Meditations hitting so hard 1,800 years later proves human nature hasn't changed.",
            "Solitude by choice is deeply restorative.",
        ],
    },
}


def _build_popular_posts():
    """Deterministically generate 190+ varied posts with scored comments across common Reddit communities."""
    rng = random.Random(2026)
    handles = [
        "midnight_owl", "pixel_drifter", "coffee_and_vinyl", "quiet_signal", "retro_orbit",
        "neon_rain", "wanderlust_99", "analog_spark", "city_lights", "sunday_reader",
        "tape_loop", "starlight_bus", "velvet_echo", "moss_garden", "terminal_fox",
        "amber_lamp", "vinyl_crate", "cobalt_sky", "paper_boat", "copper_wire",
    ]
    times = ["18m ago", "42m ago", "1h ago", "2h ago", "3h ago", "5h ago", "7h ago", "9h ago", "12h ago"]
    suffixes = [
        "",
        " (Evening Thread)",
        " — curious what everyone thinks",
        " [Discussion]",
        " — sharing my setup",
        " (2026 Edition)",
        " — anyone else notice this?",
        " [Weekend Notes]",
    ]
    extra = []
    sub_names = list(_COMMON_SUB_BANK.keys())
    # Generate 200 additional posts (8 base topics * 25 subreddits = 200 unique posts!)
    for idx in range(200):
        sub = sub_names[idx % len(sub_names)]
        bank = _COMMON_SUB_BANK[sub]
        topic_idx = (idx // len(sub_names)) % len(bank["topics"])
        base_title, base_body = bank["topics"][topic_idx]
        cycle = idx // (len(sub_names) * len(bank["topics"]))
        title = base_title if cycle == 0 else f"{base_title}{suffixes[(idx + cycle) % len(suffixes)]}"
        author = handles[(idx * 3 + rng.randint(0, 7)) % len(handles)]
        post_score = rng.randint(180, 18500)

        num_c = rng.randint(3, 5)
        comments = []
        used_replies = rng.sample(bank["replies"], k=min(num_c, len(bank["replies"])))
        base_top = rng.randint(140, 1450)
        for c_i, r_text in enumerate(used_replies):
            if c_i == 0:
                c_score = base_top
            elif c_i == num_c - 1 and rng.random() < 0.15:
                c_score = rng.randint(-4, 6)
            else:
                c_score = max(3, int(base_top / (c_i + 1.4)) + rng.randint(-15, 25))
            comments.append({
                "author": handles[(idx + c_i * 5 + 2) % len(handles)],
                "score": c_score,
                "time": times[(c_i * 2 + rng.randint(0, 2)) % len(times)],
                "body": r_text,
            })

        extra.append({
            "subreddit": sub,
            "title": title,
            "author": author,
            "score": post_score,
            "num_comments": len(comments),
            "selftext": base_body,
            "image": bank["img"] if (bank["img"] and idx % 3 != 2) else None,
            "comments": comments,
        })
    return extra


SAMPLE.extend(_build_popular_posts())

_LATIN_WORDS = [
    "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
    "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
    "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud",
    "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
    "consequat", "duis", "aute", "irure", "reprehenderit", "voluptate", "velit",
    "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint", "occaecat",
    "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia", "deserunt",
    "mollit", "anim", "id", "est", "laborum", "nox", "silentium", "umbra", "lux",
    "sonus", "vita", "tempus", "ratio", "forma", "spatium", "locus", "carmen",
]

_LOREM_SUBS = [
    "LoremIpsum", "AskReddit", "philosophy", "Showerthoughts",
    "todayilearned", "music", "Art", "analog", "ambientmusic",
]


def _latin_sentence(rng, min_words=6, max_words=13):
    words = [rng.choice(_LATIN_WORDS) for _ in range(rng.randint(min_words, max_words))]
    words[0] = words[0].capitalize()
    return " ".join(words) + "."


def generate_lorem_posts(count=3, start_idx=0):
    """Dynamically generate Lorem Ipsum / Latin posts with scored comments when scrolling beyond the feed."""
    rng = random.Random(2026 + start_idx)
    times = ["just now", "4m ago", "19m ago", "1h ago", "2h ago"]
    generated = []
    for offset in range(count):
        idx = start_idx + offset
        sub = _LOREM_SUBS[idx % len(_LOREM_SUBS)]
        title = _latin_sentence(rng, 6, 12).rstrip(".")
        body = f"{_latin_sentence(rng, 8, 15)} {_latin_sentence(rng, 5, 11)}"
        author = f"{rng.choice(_LATIN_WORDS)}_{rng.choice(_LATIN_WORDS)}"
        num_c = rng.randint(3, 5)
        comments = []
        top_score = rng.randint(45, 890)
        for c_i in range(num_c):
            c_score = top_score if c_i == 0 else max(-3, int(top_score / (c_i + 1.5)) + rng.randint(-12, 18))
            comments.append({
                "author": f"{rng.choice(_LATIN_WORDS)}_{rng.randint(10, 99)}",
                "score": c_score,
                "time": times[c_i % len(times)],
                "body": _latin_sentence(rng, 7, 16),
            })
        generated.append({
            "subreddit": sub,
            "title": title,
            "author": author,
            "score": rng.randint(12, 2400),
            "num_comments": len(comments),
            "selftext": body,
            "image": None,
            "comments": comments,
        })
    return generated

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
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry')[:50]:
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                author_elem = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
                
                title = title_elem.text if title_elem is not None else "Untitled"
                author = author_elem.text if author_elem is not None else "unknown"
                clean_author = author.replace("/u/", "")
                
                comments = generate_default_comments(title, "all")
                
                posts.append({
                    "title": title,
                    "selftext": "Live transmission pulled via RSS stream.",
                    "author": clean_author,
                    "subreddit": "all",
                    "score": 42,
                    "num_comments": len(comments),
                    "image": None,
                    "src": "RSS",
                    "comments": comments
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
