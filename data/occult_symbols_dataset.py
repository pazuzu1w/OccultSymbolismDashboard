"""
Comprehensive Occult Symbols Dataset
-----------------------------------
This module contains detailed data about occult symbols, their connections,
traditions, and elemental associations for visualization in the dashboard.
"""

# Define symbols with detailed properties
SYMBOLS = [
    # Ancient Egyptian Symbols
    {
        "id": 1,
        "name": "Ankh",
        "tradition": "Egyptian",
        "element": "Life",
        "century_origin": -30,
        "description": "Symbol of eternal life and the union of male and female energies",
        "usage": "Protection, fertility rituals, funerary rites",
        "visual_elements": ["cross", "loop", "key shape"],
    },
    {
        "id": 2,
        "name": "Eye of Horus",
        "tradition": "Egyptian",
        "element": "Protection",
        "century_origin": -25,
        "description": "Represents healing, protection, and royal power",
        "usage": "Amulets, temple inscriptions, medical treatments",
        "visual_elements": ["eye", "falcon marking", "teardrop"],
    },
    {
        "id": 3,
        "name": "Djed Pillar",
        "tradition": "Egyptian",
        "element": "Stability",
        "century_origin": -30,
        "description": "Symbol of stability, often representing the spine of Osiris",
        "usage": "Funeral rites, temple architecture, renewal ceremonies",
        "visual_elements": ["pillar", "horizontal bands", "platform base"],
    },

    # Greek Symbols
    {
        "id": 4,
        "name": "Caduceus",
        "tradition": "Greek",
        "element": "Air/Commerce",
        "century_origin": -6,
        "description": "Staff of Hermes featuring two intertwined serpents",
        "usage": "Alchemy, medicine, commerce, negotiation",
        "visual_elements": ["staff", "wings", "twin serpents"],
    },
    {
        "id": 5,
        "name": "Ouroboros",
        "tradition": "Greek/Egyptian",
        "element": "Infinity",
        "century_origin": -13,
        "description": "Serpent eating its own tail, symbolizing cyclical nature of existence",
        "usage": "Alchemy, gnosticism, cyclical cosmologies",
        "visual_elements": ["serpent", "circle", "self-consumption"],
    },
    {
        "id": 6,
        "name": "Tetraktys",
        "tradition": "Pythagorean",
        "element": "Harmony",
        "century_origin": -5,
        "description": "Triangular figure with ten points arranged in four rows",
        "usage": "Sacred geometry, numerology, meditative focus",
        "visual_elements": ["triangle", "dots", "numerical pattern"],
    },

    # Middle Eastern Traditions
    {
        "id": 7,
        "name": "Seal of Solomon",
        "tradition": "Judaic",
        "element": "Protection",
        "century_origin": 5,
        "description": "Six-pointed star created from two interlocking triangles",
        "usage": "Protection, summoning, binding of entities",
        "visual_elements": ["hexagram", "triangles", "interlocking"],
    },
    {
        "id": 8,
        "name": "Tree of Life",
        "tradition": "Kabbalah",
        "element": "Knowledge",
        "century_origin": 12,
        "description": "Diagram representing the process of divine creation",
        "usage": "Meditation, mystical studies, cosmological understanding",
        "visual_elements": ["sephirot", "paths", "vertical arrangement"],
    },
    {
        "id": 9,
        "name": "Hamsa",
        "tradition": "Middle Eastern",
        "element": "Protection",
        "century_origin": 6,
        "description": "Hand-shaped amulet for protection against the evil eye",
        "usage": "Protective amulets, home decorations, jewelry",
        "visual_elements": ["hand", "eye", "symmetrical fingers"],
    },

    # Norse Traditions
    {
        "id": 10,
        "name": "Vegvísir",
        "tradition": "Norse",
        "element": "Guidance",
        "century_origin": 17,
        "description": "Icelandic magical stave intended to help the bearer find their way",
        "usage": "Navigation, protection during journeys, spiritual guidance",
        "visual_elements": ["eight-pointed stave", "runic elements", "radial design"],
    },
    {
        "id": 11,
        "name": "Mjölnir",
        "tradition": "Norse",
        "element": "Strength/Protection",
        "century_origin": 9,
        "description": "Thor's hammer, representing strength, protection, and sanctification",
        "usage": "Protection amulets, consecration, symbolic tool in rituals",
        "visual_elements": ["hammer", "short handle", "rectangular head"],
    },
    {
        "id": 12,
        "name": "Runes",
        "tradition": "Norse",
        "element": "Multiple",
        "century_origin": 2,
        "description": "Alphabet used for writing, divination, and magic",
        "usage": "Divination, spells, communication, inscriptions",
        "visual_elements": ["angular characters", "straight lines", "few curves"],
    },

    # Eastern Traditions
    {
        "id": 13,
        "name": "Sri Yantra",
        "tradition": "Hindu",
        "element": "Cosmos",
        "century_origin": 4,
        "description": "Complex geometric diagram representing the cosmos and divine feminine",
        "usage": "Meditation, ritual focus, energy work",
        "visual_elements": ["interlocking triangles", "central point", "lotus petals"],
    },
    {
        "id": 14,
        "name": "Taiji (Yin-Yang)",
        "tradition": "Taoist",
        "element": "Balance",
        "century_origin": -6,
        "description": "Symbol representing the harmony of opposing forces",
        "usage": "Meditation, philosophical teaching, martial arts",
        "visual_elements": ["circle", "contrasting halves", "opposite dots"],
    },
    {
        "id": 15,
        "name": "Om",
        "tradition": "Hindu/Buddhist",
        "element": "Spirit",
        "century_origin": -10,
        "description": "Sacred sound and symbol representing the essence of consciousness",
        "usage": "Meditation, mantras, religious inscriptions",
        "visual_elements": ["curved form", "dot", "crescent"],
    },

    # Western Esoteric Traditions
    {
        "id": 16,
        "name": "Pentagram",
        "tradition": "Western Esoteric",
        "element": "Spirit/Elements",
        "century_origin": -3,
        "description": "Five-pointed star with various meanings across traditions",
        "usage": "Protection, elemental work, ritual magic",
        "visual_elements": ["five-pointed star", "internal pentagon", "single point up"],
    },
    {
        "id": 17,
        "name": "Unicursal Hexagram",
        "tradition": "Thelema",
        "element": "Union",
        "century_origin": 20,
        "description": "Six-pointed star drawn with a single unbroken line",
        "usage": "Thelemite rituals, planetary magic, symbolic of the divine will",
        "visual_elements": ["hexagram", "continuous line", "internal hexagon"],
    },
    {
        "id": 18,
        "name": "Rosy Cross",
        "tradition": "Rosicrucian",
        "element": "Divine Love",
        "century_origin": 17,
        "description": "Cross with a rose at its center, symbolic of spiritual unfoldment",
        "usage": "Meditation, initiation rituals, symbolic teachings",
        "visual_elements": ["cross", "rose", "center point"],
    },

    # Modern Occult Traditions
    {
        "id": 19,
        "name": "Triple Moon",
        "tradition": "Neo-Pagan",
        "element": "Feminine",
        "century_origin": 20,
        "description": "Symbol representing the three aspects of the goddess",
        "usage": "Goddess worship, lunar magic, women's spirituality",
        "visual_elements": ["crescent moons", "full moon", "horizontal alignment"],
    },
    {
        "id": 20,
        "name": "Sigil of Baphomet",
        "tradition": "Modern Occult",
        "element": "Earth",
        "century_origin": 19,
        "description": "Inverted pentagram containing a goat's head and Hebrew letters",
        "usage": "Left-hand path rituals, symbolism of materialism and carnality",
        "visual_elements": ["pentagram", "goat head", "Hebrew text"],
    },
    {
        "id": 21,
        "name": "Chaos Star",
        "tradition": "Chaos Magic",
        "element": "Possibility",
        "century_origin": 20,
        "description": "Eight-pointed star representing the forces of chaos",
        "usage": "Chaos magic workings, paradigm shifting, result magic",
        "visual_elements": ["arrows", "eight points", "radiating design"],
    },

    # Universal/Cross-Cultural
    {
        "id": 22,
        "name": "Flower of Life",
        "tradition": "Multiple",
        "element": "Creation",
        "century_origin": -5,
        "description": "Overlapping circle pattern found in many ancient cultures",
        "usage": "Sacred geometry, meditation, energy work",
        "visual_elements": ["overlapping circles", "hexagonal pattern", "radial symmetry"],
    },
    {
        "id": 23,
        "name": "Spiral",
        "tradition": "Multiple",
        "element": "Growth",
        "century_origin": -100,
        "description": "Universal symbol of growth, evolution, and cyclical progression",
        "usage": "Meditation, representing life cycles, decorative and spiritual art",
        "visual_elements": ["curved line", "expanding circles", "inward/outward movement"],
    },
    {
        "id": 24,
        "name": "Vesica Piscis",
        "tradition": "Multiple",
        "element": "Divine Union",
        "century_origin": -10,
        "description": "Almond shape created by the intersection of two circles",
        "usage": "Sacred geometry, symbolic representation of divine union, architectural guide",
        "visual_elements": ["overlapping circles", "almond shape", "central area"],
    },

    # Renaissance Occult Symbols
    {
        "id": 25,
        "name": "Monas Hieroglyphica",
        "tradition": "Renaissance Hermeticism",
        "element": "Unity",
        "century_origin": 16,
        "description": "Esoteric symbol created by John Dee representing cosmic unity",
        "usage": "Alchemical operations, meditation on cosmic principles",
        "visual_elements": ["lunar crescent", "solar circle", "cross"],
    },
    {
        "id": 26,
        "name": "Squared Circle",
        "tradition": "Alchemy",
        "element": "Transformation",
        "century_origin": 15,
        "description": "Symbol representing the philosopher's stone and perfect harmony",
        "usage": "Alchemical transformation, meditation on perfection",
        "visual_elements": ["circle", "square", "inscribed shapes"],
    },
    {
        "id": 27,
        "name": "Rebis",
        "tradition": "Alchemy",
        "element": "Unity",
        "century_origin": 16,
        "description": "Hermaphroditic figure representing the perfect union of opposites",
        "usage": "Alchemical symbolism, meditation on duality and unity",
        "visual_elements": ["dual-natured figure", "sun and moon", "male and female"],
    },

    # Enochian and Hermetic Symbols
    {
        "id": 28,
        "name": "Enochian Alphabet",
        "tradition": "Enochian",
        "element": "Communication",
        "century_origin": 16,
        "description": "Alphabet allegedly received through angelic communication",
        "usage": "Angelic magic, scrying, communication with non-physical entities",
        "visual_elements": ["angular letters", "unique characters", "symbolic script"],
    },
    {
        "id": 29,
        "name": "Hexagram of Solomon",
        "tradition": "Hermetic/Ceremonial Magic",
        "element": "Control",
        "century_origin": 15,
        "description": "Six-pointed star used in ceremonial magic for protection and control",
        "usage": "Spirit evocation, protection during rituals, banishing",
        "visual_elements": ["hexagram", "internal hexagon", "planetary symbols"],
    },
    {
        "id": 30,
        "name": "Tetragrammaton",
        "tradition": "Kabbalah/Hermetic",
        "element": "Divine Name",
        "century_origin": -10,
        "description": "Four-letter Hebrew name of God with immense mystical significance",
        "usage": "Invocation, amulets, meditation on divine qualities",
        "visual_elements": ["Hebrew letters", "square arrangement", "symbolic positioning"],
    },
]

# Define connections between symbols
CONNECTIONS = [
    # Egyptian Connections
    {"source": 1, "target": 2, "strength": 0.8, "description": "Core symbols of Egyptian spirituality"},
    {"source": 1, "target": 3, "strength": 0.7, "description": "Fundamental symbols of Egyptian afterlife beliefs"},
    {"source": 2, "target": 3, "strength": 0.6, "description": "Protection and stability in Egyptian magical practice"},
    {"source": 1, "target": 5, "strength": 0.5, "description": "Symbols of eternal cycles and regeneration"},

    # Greek Connections
    {"source": 4, "target": 5, "strength": 0.6, "description": "Hermetic and alchemical symbolism"},
    {"source": 4, "target": 6, "strength": 0.5, "description": "Classical Greek spiritual symbolism"},
    {"source": 5, "target": 14, "strength": 0.7, "description": "Cyclical representations of cosmic order"},
    {"source": 6, "target": 16, "strength": 0.6, "description": "Geometric symbols with numerical significance"},

    # Middle Eastern Connections
    {"source": 7, "target": 8, "strength": 0.8, "description": "Central symbols in Jewish mysticism"},
    {"source": 8, "target": 30, "strength": 0.9, "description": "Key components of Kabbalistic practice"},
    {"source": 7, "target": 9, "strength": 0.5, "description": "Protective symbols from Middle Eastern traditions"},
    {"source": 8, "target": 18, "strength": 0.6, "description": "Mystical diagrams showing divine emanation"},

    # Norse Connections
    {"source": 10, "target": 11, "strength": 0.7, "description": "Protective symbols in Norse tradition"},
    {"source": 11, "target": 12, "strength": 0.8, "description": "Core elements of Norse magical practice"},
    {"source": 10, "target": 12, "strength": 0.9, "description": "Runic symbols and magical staves"},

    # Eastern Connections
    {"source": 13, "target": 14, "strength": 0.6, "description": "Eastern symbols of cosmic harmony"},
    {"source": 13, "target": 15, "strength": 0.7, "description": "Sacred symbols in Hindu spirituality"},
    {"source": 14, "target": 15, "strength": 0.5, "description": "Symbols of eastern philosophical concepts"},
    {"source": 13, "target": 22, "strength": 0.8,
     "description": "Sacred geometry patterns with spiritual significance"},

    # Western Esoteric Connections
    {"source": 16, "target": 17, "strength": 0.9, "description": "Star symbols in western occultism"},
    {"source": 16, "target": 20, "strength": 0.7, "description": "Pentagram variations in different traditions"},
    {"source": 17, "target": 18, "strength": 0.5, "description": "Symbolic evolution in western esoteric orders"},
    {"source": 18, "target": 25, "strength": 0.6, "description": "Symbolic integration of multiple traditions"},

    # Modern Occult Connections
    {"source": 19, "target": 21, "strength": 0.5, "description": "Modern occult symbolic systems"},
    {"source": 20, "target": 21, "strength": 0.7, "description": "Recent symbols with countercultural associations"},
    {"source": 21, "target": 16, "strength": 0.6, "description": "Reinterpretation of traditional symbols"},

    # Universal Connections
    {"source": 22, "target": 23, "strength": 0.8, "description": "Universal growth and creation symbols"},
    {"source": 22, "target": 24, "strength": 0.9, "description": "Fundamental sacred geometry patterns"},
    {"source": 23, "target": 24, "strength": 0.7, "description": "Geometric expressions of natural growth principles"},

    # Renaissance and Alchemical Connections
    {"source": 25, "target": 26, "strength": 0.8, "description": "Renaissance hermetic symbolic systems"},
    {"source": 26, "target": 27, "strength": 0.9, "description": "Key alchemical transformation symbols"},
    {"source": 25, "target": 27, "strength": 0.7, "description": "Symbolic representations of hermetic principles"},
    {"source": 26, "target": 5, "strength": 0.6, "description": "Alchemical symbols of transformation and cycles"},

    # Hermetic and Ceremonial Connections
    {"source": 28, "target": 29, "strength": 0.7, "description": "Ceremonial magic systems"},
    {"source": 29, "target": 30, "strength": 0.8, "description": "Divine names and protective diagrams"},
    {"source": 28, "target": 30, "strength": 0.6, "description": "Angelic and divine name correspondences"},
    {"source": 29, "target": 7, "strength": 0.9, "description": "Variations of the hexagram in magical practice"},

    # Cross-Traditional Connections
    {"source": 16, "target": 8, "strength": 0.7,
     "description": "Integration of Kabbalistic and western magical symbols"},
    {"source": 15, "target": 21, "strength": 0.4, "description": "Eastern influences on chaos magic"},
    {"source": 14, "target": 26, "strength": 0.5,
     "description": "Balance symbolism across eastern and western traditions"},
    {"source": 22, "target": 13, "strength": 0.8, "description": "Sacred geometry across multiple traditions"},
    {"source": 4, "target": 11, "strength": 0.3, "description": "Divine messengers and mythological tools"},
    {"source": 1, "target": 24, "strength": 0.5, "description": "Symbols of life and generation"},
    {"source": 17, "target": 24, "strength": 0.6, "description": "Geometric harmony in mystical symbolism"},
    {"source": 5, "target": 23, "strength": 0.7, "description": "Spiral and cyclical symbolism"},
    {"source": 6, "target": 22, "strength": 0.8, "description": "Numerical and geometric sacred patterns"},
]

# Define traditions with detailed properties
TRADITIONS = [
    {
        "name": "Egyptian",
        "start_century": -30,
        "end_century": -1,
        "region": "North Africa",
        "major_texts": ["Book of the Dead", "Pyramid Texts", "Coffin Texts"],
        "key_figures": ["Imhotep", "Hermes Trismegistus (Thoth)"],
        "core_concepts": ["Afterlife", "Divine Kingship", "Magical Protection", "Cosmic Order (Ma'at)"],
        "historical_phases": ["Old Kingdom", "Middle Kingdom", "New Kingdom", "Late Period"],
        "modern_influence": "Revival in Hermeticism, Thelema, and New Age spirituality"
    },
    {
        "name": "Greek",
        "start_century": -8,
        "end_century": 3,
        "region": "Mediterranean",
        "major_texts": ["Orphic Hymns", "Corpus Hermeticum", "Chaldean Oracles"],
        "key_figures": ["Pythagoras", "Empedocles", "Iamblichus"],
        "core_concepts": ["Elemental Magic", "Celestial Harmony", "Divine Mathematics", "Mystery Cults"],
        "historical_phases": ["Archaic", "Classical", "Hellenistic", "Roman Period"],
        "modern_influence": "Foundation for Western ceremonial magic and Hermeticism"
    },
    {
        "name": "Norse",
        "start_century": 2,
        "end_century": 11,
        "region": "Scandinavia",
        "major_texts": ["Poetic Edda", "Prose Edda", "Galdrabók"],
        "key_figures": ["Odin", "Freya", "Egil Skallagrimsson"],
        "core_concepts": ["Rune Magic", "Seidr", "Fate", "Shapeshifting"],
        "historical_phases": ["Migration Period", "Viking Age", "Christianization"],
        "modern_influence": "Ásatrú revival, Germanic neopaganism, runic divination"
    },
    {
        "name": "Kabbalah",
        "start_century": 12,
        "end_century": 21,
        "region": "Mediterranean/Europe",
        "major_texts": ["Zohar", "Sefer Yetzirah", "Bahir", "Pardes Rimonim"],
        "key_figures": ["Rabbi Isaac Luria", "Rabbi Moses de León", "Abraham Abulafia"],
        "core_concepts": ["Divine Emanations", "Sacred Names", "Gematria", "Tree of Life"],
        "historical_phases": ["Early Spanish", "Lurianic", "Hasidic", "Hermetic Adaptation"],
        "modern_influence": "Foundational to Western occultism, Hermeticism, and ceremonial magic"
    },
    {
        "name": "Thelema",
        "start_century": 20,
        "end_century": 21,
        "region": "Global",
        "major_texts": ["The Book of the Law", "777", "Magick in Theory and Practice"],
        "key_figures": ["Aleister Crowley", "Jack Parsons", "Kenneth Grant"],
        "core_concepts": ["True Will", "New Aeon", "Ceremonial Magic", "Self-Deification"],
        "historical_phases": ["Formation", "O.T.O. Development", "Post-Crowley Expansion"],
        "modern_influence": "Significant impact on contemporary occultism and chaos magic"
    },
    {
        "name": "Neo-Pagan",
        "start_century": 20,
        "end_century": 21,
        "region": "Global",
        "major_texts": ["The Spiral Dance", "Witchcraft Today", "Drawing Down the Moon"],
        "key_figures": ["Gerald Gardner", "Doreen Valiente", "Starhawk"],
        "core_concepts": ["Nature Worship", "Goddess Spirituality", "Seasonal Cycles", "Folk Magic"],
        "historical_phases": ["Gardnerian Beginnings", "Feminist Revival", "Eclectic Expansion"],
        "modern_influence": "Mainstream alternative spirituality and ecological consciousness"
    },
    {
        "name": "Pythagorean",
        "start_century": -6,
        "end_century": -3,
        "region": "Mediterranean",
        "major_texts": ["The Golden Verses", "Fragments"],
        "key_figures": ["Pythagoras", "Philolaus", "Archytas"],
        "core_concepts": ["Sacred Geometry", "Number Mysticism", "Harmony of the Spheres", "Transmigration"],
        "historical_phases": ["Early Community", "Southern Italian Schools", "Neo-Pythagoreanism"],
        "modern_influence": "Mathematical mysticism and sacred geometry practices"
    },
    {
        "name": "Taoist",
        "start_century": -6,
        "end_century": 21,
        "region": "East Asia",
        "major_texts": ["Tao Te Ching", "I Ching", "The Secret of the Golden Flower"],
        "key_figures": ["Lao Tzu", "Chuang Tzu", "Wei Boyang"],
        "core_concepts": ["Balance", "Wu Wei", "Internal Alchemy", "Immortality Practices"],
        "historical_phases": ["Philosophical", "Alchemical", "Religious", "Modern"],
        "modern_influence": "Qigong, feng shui, Traditional Chinese Medicine, martial arts"
    },
    {
        "name": "Hindu",
        "start_century": -20,
        "end_century": 21,
        "region": "South Asia",
        "major_texts": ["Upanishads", "Tantric texts", "Yoga Sutras"],
        "key_figures": ["Patanjali", "Abhinavagupta", "Matsyendranath"],
        "core_concepts": ["Chakras", "Kundalini", "Mantra", "Yantra"],
        "historical_phases": ["Vedic", "Classical", "Tantric", "Modern"],
        "modern_influence": "Yoga, meditation practices, New Age energy work"
    },
    {
        "name": "Hermetic",
        "start_century": 2,
        "end_century": 21,
        "region": "Mediterranean/Global",
        "major_texts": ["Corpus Hermeticum", "Emerald Tablet", "Kybalion"],
        "key_figures": ["Hermes Trismegistus", "Marsilio Ficino", "Giordano Bruno"],
        "core_concepts": ["As Above So Below", "Divine Mind", "Transmutation", "Planetary Magic"],
        "historical_phases": ["Greco-Egyptian", "Arabic Preservation", "Renaissance Revival", "Modern"],
        "modern_influence": "Foundation for esoteric societies and ceremonial magic"
    },
    {
        "name": "Alchemy",
        "start_century": 2,
        "end_century": 18,
        "region": "Global",
        "major_texts": ["Emerald Tablet", "Rosarium Philosophorum", "Mutus Liber"],
        "key_figures": ["Paracelsus", "Nicolas Flamel", "Basil Valentine"],
        "core_concepts": ["Transmutation", "Philosopher's Stone", "Prima Materia", "Unity of Matter"],
        "historical_phases": ["Alexandrian", "Arabic", "European", "Spiritual"],
        "modern_influence": "Jungian psychology, spiritual transformation work"
    },
    {
        "name": "Modern Occult",
        "start_century": 19,
        "end_century": 21,
        "region": "Global",
        "major_texts": ["Magick in Theory and Practice", "The Satanic Bible", "Modern Magick"],
        "key_figures": ["Eliphas Levi", "Anton LaVey", "Israel Regardie"],
        "core_concepts": ["Will-based Magic", "Psychological Transformation", "Ceremonial Ritual"],
        "historical_phases": ["19th Century Revival", "Early 20th Century", "Counterculture", "Digital Age"],
        "modern_influence": "Contemporary magical practices, pop culture, alternative spirituality"
    },
    {
        "name": "Chaos Magic",
        "start_century": 20,
        "end_century": 21,
        "region": "Global",
        "major_texts": ["Liber Null", "Psychonaut", "Condensed Chaos"],
        "key_figures": ["Austin Osman Spare", "Peter Carroll", "Ray Sherwin"],
        "core_concepts": ["Paradigm Shifting", "Sigil Magic", "Results Focus", "Meta-belief"],
        "historical_phases": ["Formation", "IOT Development", "Cybernetic Expansion", "Internet Era"],
        "modern_influence": "Postmodern approach to magical systems, meme magic, tech-magic fusion"
    },
    {
        "name": "Enochian",
        "start_century": 16,
        "end_century": 21,
        "region": "Europe/Global",
        "major_texts": ["John Dee's Diaries", "The Enochian Evocation", "The Complete Enochian Dictionary"],
        "key_figures": ["John Dee", "Edward Kelley", "Golden Dawn Adapters"],
        "core_concepts": ["Angelic Language", "Watchtowers", "Aethyrs", "Elemental Tablets"],
        "historical_phases": ["Original System", "Golden Dawn Adaptation", "Modern Practice"],
        "modern_influence": "Complex magical language and cosmology used in high ritual magic"
    },
    {
        "name": "Renaissance Hermeticism",
        "start_century": 15,
        "end_century": 17,
        "region": "Europe",
        "major_texts": ["De Occulta Philosophia", "Monas Hieroglyphica", "Picatrix"],
        "key_figures": ["Heinrich Cornelius Agrippa", "John Dee", "Giordano Bruno"],
        "core_concepts": ["Natural Magic", "Celestial Influences", "Microcosm-Macrocosm", "Mathematical Magic"],
        "historical_phases": ["Early Revival", "Flourishing", "Scientific Transition"],
        "modern_influence": "Basis for later Western esoteric traditions and societies"
    },
]

# Define element groupings and properties
ELEMENTS = [
    {
        "name": "Spirit",
        "symbols": [16, 15, 17],
        "traditions": ["Western Esoteric", "Hindu/Buddhist", "Thelema"],
        "correspondences": {
            "colors": ["Purple", "White", "Clear"],
            "directions": ["Center", "Above", "Within"],
            "qualities": ["Transcendence", "Consciousness", "Unity"]
        },
        "description": "The quintessence or fifth element, representing consciousness and divine essence"
    },
    {
        "name": "Protection",
        "symbols": [2, 7, 9, 11],
        "traditions": ["Egyptian", "Judaic", "Middle Eastern", "Norse"],
        "correspondences": {
            "colors": ["Blue", "Gold", "Silver"],
            "directions": ["All directions", "Threshold", "Boundary"],
            "qualities": ["Warding", "Shielding", "Deflection"]
        },
        "description": "Symbols that defend against negative influences, evil spirits, or harmful energies"
    },
    {
        "name": "Life",
        "symbols": [1, 22, 24],
        "traditions": ["Egyptian", "Multiple", "Multiple"],
        "correspondences": {
            "colors": ["Green", "Red", "Gold"],
            "directions": ["East", "Center", "Source"],
            "qualities": ["Vitality", "Growth", "Regeneration"]
        },
        "description": "Represents life force, generative powers, and the animation of matter"
    },
    {
        "name": "Balance",
        "symbols": [14, 19, 27],
        "traditions": ["Taoist", "Neo-Pagan", "Alchemy"],
        "correspondences": {
            "colors": ["Black and White", "Silver and Gold", "Red and Blue"],
            "directions": ["East-West", "Above-Below", "Internal-External"],
            "qualities": ["Harmony", "Equilibrium", "Complementarity"]
        },
        "description": "Symbols expressing harmony of opposing forces and cosmic equilibrium"
    },
    {
        "name": "Knowledge",
        "symbols": [8, 6, 28],
        "traditions": ["Kabbalah", "Pythagorean", "Enochian"],
        "correspondences": {
            "colors": ["Yellow", "Blue", "Purple"],
            "directions": ["North", "Above", "Within"],
            "qualities": ["Wisdom", "Understanding", "Illumination"]
        },
        "description": "Represents divine wisdom, hidden knowledge, and intellectual illumination"
    },
    {
        "name": "Transformation",
        "symbols": [5, 26, 23],
        "traditions": ["Greek/Egyptian", "Alchemy", "Multiple"],
        "correspondences": {
            "colors": ["Iridescent", "Red-to-White", "Green"],
            "directions": ["Cyclical", "Upward", "Spiral"],
            "qualities": ["Change", "Transmutation", "Evolution"]
        },
        "description": "Symbols of profound change, transformation, and spiritual evolution"
    },
    {
        "name": "Cosmos",
        "symbols": [13, 22, 30],
        "traditions": ["Hindu", "Multiple", "Kabbalah/Hermetic"],
        "correspondences": {
            "colors": ["Blue", "Gold", "Black with stars"],
            "directions": ["All directions", "Outward", "Expanding"],
            "qualities": ["Order", "Structure", "Harmony"]
        },
        "description": "Represents the ordered universe, cosmic patterns, and celestial harmony"
    },
    {
        "name": "Divine Union",
        "symbols": [24, 17, 27],
        "traditions": ["Multiple", "Thelema", "Alchemy"],
        "correspondences": {
            "colors": ["Red and White", "Purple and Gold", "Silver and Gold"],
            "directions": ["Center", "Vertical axis", "Meeting point"],
            "qualities": ["Oneness", "Integration", "Sacred Marriage"]
        },
        "description": "Symbolizes the union of divine forces, cosmic principles, or spiritual energies"
    }
]

# Define time periods for categorization
TIME_PERIODS = [
    {
        "name": "Ancient (before 0 CE)",
        "symbols": [1, 2, 3, 5, 6, 14, 15, 16, 22, 23, 24, 30],
        "description": "Symbols originating in ancient civilizations, often with religious significance",
        "key_developments": ["Sacred writing systems", "State religion symbolism", "Astronomical alignments"],
        "cultural_context": "Symbols were often restricted to priesthood and religious contexts"
    },
    {
        "name": "Classical (0-500 CE)",
        "symbols": [4, 13, 12],
        "description": "Symbols developed during Greco-Roman and early post-classical period",
        "key_developments": ["Mystery religions", "Syncretism", "Philosophical schools"],
        "cultural_context": "Blending of traditions as empires expanded and contracted"
    },
    {
        "name": "Medieval (500-1500 CE)",
        "symbols": [7, 8, 11],
        "description": "Symbols developed during European medieval period and equivalent eras elsewhere",
        "key_developments": ["Grimoire traditions", "Alchemical symbolism", "Religious mysticism"],
        "cultural_context": "Esoteric knowledge preserved in monastic and scholarly traditions"
    },
    {
        "name": "Early Modern (1500-1900 CE)",
        "symbols": [10, 18, 25, 26, 27, 28, 29],
        "description": "Symbols from Renaissance through the early industrial period",
        "key_developments": ["Hermetic revival", "Secret societies", "Printing of occult texts"],
        "cultural_context": "Scientific revolution created tension and synthesis with occult traditions"
    },
    {
        "name": "Modern (1900 CE-present)",
        "symbols": [17, 19, 20, 21],
        "description": "Symbols created or significantly reimagined in the modern era",
        "key_developments": ["New magical systems", "Psychological interpretation", "Digital sharing"],
        "cultural_context": "Democratization of occult knowledge and postmodern approaches to symbolism"
    }
]

# Add additional metadata for visualization purposes
VISUALIZATION_METADATA = {
    "symbol_categories": [
        {"name": "Protective", "symbols": [2, 7, 9, 10, 11, 29]},
        {"name": "Transformative", "symbols": [5, 23, 26, 27]},
        {"name": "Life-giving", "symbols": [1, 22, 24]},
        {"name": "Wisdom-bearing", "symbols": [6, 8, 13, 30]},
        {"name": "Unifying", "symbols": [14, 17, 24, 27]},
        {"name": "Cosmic", "symbols": [13, 16, 22, 25]}
    ],
    "regional_influence": [
        {"region": "Mediterranean", "intensity": 9,
         "traditions": ["Egyptian", "Greek", "Pythagorean", "Kabbalah", "Hermetic"]},
        {"region": "Northern Europe", "intensity": 7, "traditions": ["Norse", "Renaissance Hermeticism"]},
        {"region": "Middle East", "intensity": 8, "traditions": ["Judaic", "Kabbalah", "Hermetic"]},
        {"region": "South Asia", "intensity": 6, "traditions": ["Hindu"]},
        {"region": "East Asia", "intensity": 5, "traditions": ["Taoist"]},
        {"region": "North America", "intensity": 7, "traditions": ["Modern Occult", "Chaos Magic", "Neo-Pagan"]},
        {"region": "Western Europe", "intensity": 10,
         "traditions": ["Renaissance Hermeticism", "Alchemy", "Enochian", "Hermetic"]}
    ],
    "temporal_transitions": [
        {"source": "Egyptian", "target": "Hermetic", "strength": 0.8},
        {"source": "Greek", "target": "Renaissance Hermeticism", "strength": 0.7},
        {"source": "Pythagorean", "target": "Kabbalah", "strength": 0.5},
        {"source": "Norse", "target": "Neo-Pagan", "strength": 0.6},
        {"source": "Hermetic", "target": "Modern Occult", "strength": 0.9},
        {"source": "Kabbalah", "target": "Western Esoteric", "strength": 0.8},
        {"source": "Alchemy", "target": "Chaos Magic", "strength": 0.4},
        {"source": "Renaissance Hermeticism", "target": "Thelema", "strength": 0.7}
    ],
    "color_associations": {
        "Egyptian": "#D4AF37",  # Gold
        "Greek": "#1E90FF",  # Blue
        "Norse": "#708090",  # Slate gray
        "Kabbalah": "#4B0082",  # Indigo
        "Thelema": "#800080",  # Purple
        "Neo-Pagan": "#006400",  # Dark green
        "Pythagorean": "#FFD700",  # Gold
        "Taoist": "#000000",  # Black (yin) and #FFFFFF (yang)
        "Hindu": "#FF4500",  # Orange red
        "Modern Occult": "#8B0000",  # Dark red
        "Chaos Magic": "#000000",  # Black
        "Hermetic": "#B8860B",  # Dark goldenrod
        "Alchemy": "#CD7F32",  # Bronze
        "Enochian": "#9370DB",  # Medium purple
        "Renaissance Hermeticism": "#2F4F4F"  # Dark slate gray
    }
}


# Function to get the dataset ready for the dashboard
def get_complete_dataset():
    """Returns the complete dataset for use in the visualization dashboard"""
    return {
        "symbols": SYMBOLS,
        "connections": CONNECTIONS,
        "traditions": TRADITIONS,
        "elements": ELEMENTS,
        "time_periods": TIME_PERIODS,
        "metadata": VISUALIZATION_METADATA
    }


# Example of how to access specific data
def get_symbol_by_id(symbol_id):
    """Retrieve a symbol by its ID"""
    for symbol in SYMBOLS:
        if symbol["id"] == symbol_id:
            return symbol
    return None


def get_symbols_by_tradition(tradition_name):
    """Get all symbols associated with a specific tradition"""
    return [symbol for symbol in SYMBOLS if tradition_name in symbol["tradition"]]


def get_connected_symbols(symbol_id):
    """Get all symbols directly connected to the specified symbol"""
    connected_ids = []
    for connection in CONNECTIONS:
        if connection["source"] == symbol_id:
            connected_ids.append(connection["target"])
        elif connection["target"] == symbol_id:
            connected_ids.append(connection["source"])

    return [get_symbol_by_id(id) for id in connected_ids]


def get_symbols_by_time_period(period_name):
    """Get all symbols from a specific time period"""
    for period in TIME_PERIODS:
        if period["name"] == period_name:
            return [get_symbol_by_id(id) for id in period["symbols"]]
    return []


def get_symbols_by_element(element_name):
    """Get all symbols associated with a specific element"""
    for element in ELEMENTS:
        if element["name"] == element_name:
            return [get_symbol_by_id(id) for id in element["symbols"]]
    return []


# Example of calculating additional metrics for visualization
def calculate_tradition_influence_score():
    """Calculate an influence score for each tradition based on symbols and connections"""
    tradition_scores = {}

    # Count symbols per tradition
    for symbol in SYMBOLS:
        traditions = symbol["tradition"].split("/")
        for tradition in traditions:
            if tradition not in tradition_scores:
                tradition_scores[tradition] = {"symbols": 0, "connections": 0, "score": 0}
            tradition_scores[tradition]["symbols"] += 1

    # Count connections involving each tradition
    for connection in CONNECTIONS:
        source_symbol = get_symbol_by_id(connection["source"])
        target_symbol = get_symbol_by_id(connection["target"])

        source_traditions = source_symbol["tradition"].split("/")
        target_traditions = target_symbol["tradition"].split("/")

        for tradition in set(source_traditions + target_traditions):
            if tradition in tradition_scores:
                tradition_scores[tradition]["connections"] += 1

    # Calculate composite score
    for tradition, data in tradition_scores.items():
        # Simple weighted formula: (2 * symbols) + connections
        data["score"] = (2 * data["symbols"]) + data["connections"]

    return tradition_scores

# You can add more specialized functions here for additional data processing