"""Extraction of Pardess (1990): Latin > Balkan Romance > Common Romanian > Daco-Romanian.

Headers look like "$ R3A Reduction of final [m] (P6A) $$PG: 48-49".
Comment-only (morphological) rules are written as headers with no rule line
under them, which the shared parser handles, so no comment_only() is needed.
"""

import re

FILE = "oct26-romanian-extractor-cfr.txt"
SOURCE = "pardess1990"

# Names in the '$ DiaSim cascade:' line -> language IDs in etc/languages.csv.
LANGUAGES = {
    "Latin": "latin",
    "Balkan Romance": "balkan-romance",
    "Common Romanian": "common-romanian",
    "Daco-Romanian": "daco-romanian",
}

HEADER_RE = re.compile(
    r"^\$\s*"
    r"(?P<source_rule_id>R\d+[A-Za-z]*)\s+"
    r"(?P<name>.*?)\s+"
    r"\$\$PG:\s*(?P<page>.*?)\s*$"
)
