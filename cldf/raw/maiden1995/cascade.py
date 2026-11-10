"""Extraction of Maiden (1995), ch. 2: Classical Latin > Proto-Romance > Italian.

Headers look like "$ M4.6.4.1a Proto-Romance syncope before [l] ...  $$PG: 31, 44-46".
Identifiers are Maiden's section numbers, prefixed with M.

Comment-only changes are not written as headers. They are a bulleted list in
the block after the "$ COMMENT-ONLY:" banner at the end of the file:

    $ - 4.6.4 (pp. 44-45): sporadic deletion of unstressed i, e after l, r ...
    $   naturalmente); apheresis by reanalysis of the article ...

comment_only() reads that list. The conventions block at the top of the file
also uses "$ - " bullets, which is why reading starts at the banner.
"""

import re

FILE = "oct26-italian-extractor-cfr.txt"
SOURCE = "maiden1995"

# Names in the '$ DiaSim cascade:' line -> language IDs in etc/languages.csv.
LANGUAGES = {
    "Classical Latin": "latin",
    "Proto-Romance": "proto-romance",
    "(standard, Florentine-based) Italian": "italian",
}

HEADER_RE = re.compile(
    r"^\$\s*"
    r"(?P<source_rule_id>M\d+(?:\.\d+)*[a-z]?)\s+"
    r"(?P<name>.*?)\s+"
    r"\$\$PG:\s*(?P<page>.*?)\s*$"
)

BANNER = "$ COMMENT-ONLY:"

# "$ - 4.6.4 (pp. 44-45): text"; also "7.1-7.2 (pp. 59-63):" and
# "6.1 (p. 58) / 8.1 (p. 71):", where only the first page reference is kept.
ENTRY_RE = re.compile(
    r"^\$ - "
    r"(?P<section>[\d.]+(?:-[\d.]+)?)\s+"
    r"\(pp?\.\s*(?P<page>[^)]*)\)"
    r"[^:]*:\s*"
    r"(?P<text>.*)$"
)
CONTINUATION_RE = re.compile(r"^\$\s{2,}(?P<text>\S.*)$")


def comment_only(lines):
    """Return the comment-only list as dicts: source_rule_id, name, page."""
    entries = []
    in_list = False
    for line in lines:
        if line.startswith(BANNER):
            in_list = True
            continue
        if not in_list:
            continue
        match = ENTRY_RE.match(line)
        if match:
            entries.append({
                "source_rule_id": "M" + match.group("section"),
                "name": match.group("text").strip(),
                "page": match.group("page").strip(),
            })
            continue
        match = CONTINUATION_RE.match(line)
        if match and entries:
            entries[-1]["name"] += " " + match.group("text").strip()
    return entries
