"""Quechua cascades: Proto-Quechuan > six varieties, one file per variety.

The files have no rule headers, so HEADER_RE is not defined and rule IDs are
numbered by line within each chain (e.g. quechua_cm-quechua-amazonas-line3).
The matching *-lex-cm.txt files are DiaSim lexicons; they are not read here.
"""

FILES = [
    "amazonas-cfr-cm.txt",
    "ancash-cfr-cm.txt",
    "ayacucho-cfr-cm.txt",
    "cuzco-cfr-cm.txt",
    "ecuador-cfr-cm.txt",
    "junin-cfr-cm.txt",
]

# TODO: the real BibTeX cite key (and entry in source.bib).
SOURCE = "quechua_cm"

# Stage names in the files ('$|', '=' and '~' lines) -> language IDs in etc/languages.csv.
LANGUAGES = {
    "Proto-Quechuan": "proto-quechuan",
    "Amazonas": "quechua-amazonas",
    "Ancash": "quechua-ancash",
    "Ayacucho": "quechua-ayacucho",
    "Cuzco": "quechua-cuzco",
    "Ecuador": "quechua-ecuador",
    "Junin": "quechua-junin",
}
