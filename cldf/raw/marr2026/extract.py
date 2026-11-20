"""Extract Clayton's Albanian cascade.

Right now, ONLY from Archaic Proto-Albanian onwards.

TODO Ask Clayton about header format, but for now just write comments as usual
Writing this one by hand to validate the workflow
"""
import re

FILES = ["DiaCLEA18_Archaic_Proto_Albanian.txt"]
SOURCE = "marr2026"

LANGUAGES = {
    "Archaic Proto-Albanian": "archaic-proto-albanian",
    "Classical Proto-Albanian": "classical-proto-albanian",
    "Middle Proto-Albanian I": "middle-proto-albanian-i",
    "Middle Proto-Albanian II": "middle-proto-albanian-ii",
    "Late Proto-Albanian I": "late-proto-albanian-i",
    "Late Proto-Albanian II": "late-proto-albanian-ii",
    "Late Proto-Albanian III": "late-proto-albanian-iii",
    "Proto-Tosk-SGheg": "proto-tosk-sgheg",
    "Proto-Tosk": "proto-tosk",
    "Old North Tosk": "old-north-tosk",
    "Standard Albanian": "standard-albanian",
}
