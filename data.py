"""Shared data loader: live Reddit JSON when online, bundled sample posts otherwise.
Each post may carry an 'image' URL (Reddit preview/thumbnail). art() builds a generated fallback image."""
import html, hashlib, requests, streamlit as st
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
