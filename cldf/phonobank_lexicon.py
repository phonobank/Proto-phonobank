"""Reading DiaSim lexicon files.

A lexicon has one row per etymon and one column per stage, the first being the
input (e.g. the proto-language) and the last the output:

    p a k a , p a k a $begin
    r a p r a , l a p l a $leaf, wing
    ... , a w i $a form absent at the first stage

Columns are separated by ' , ', phones by single spaces, and '...' marks a
form that is absent at that stage. Text after '$' is a comment; in Proto-
phonobank the comment on a row is its gloss.

DiaSim can also read the stage names from a first line beginning with '='
(e.g. '=Proto-Quechuan,Ancash'). Lexicons that lack one, or that name their
stages only in a comment, must be given the stage names by the caller.

This module knows only the file format, not CLDF.

TODO: Isaac - For now I'm sticking to the Diasim lexicon format for compatibilty, this
could be improved somewhat tho'
"""

# DiaSim conventions (as in DiaSim's UTILS.py).
CMT_FLAG = "$"
HEADER_FLAG = "="
HEADER_DELIM = ","
LEX_DELIM = ","
PH_DELIM = " "
ABSENT_INDIC = "..."


def parse_lexicon(lines):
    """Parse a DiaSim lexicon.

    Returns (header, entries):
        header   the stage names from a '=' line, or None if there is none
        entries  one dict per row, in file order, with
                     line     the line number in the file
                     forms    one item per column: a list of phones, or None
                              where the form is absent ('...')
                     gloss    the row's comment, or None
    """
    header = None
    entries = []
    for number, line in enumerate(lines, start=1):
        if header is None and not entries and line.startswith(HEADER_FLAG):
            header = [name.strip() for name in line[1:].split(HEADER_DELIM)]
            continue

        content, _, comment = line.partition(CMT_FLAG)
        if not content.strip():
            continue

        forms = []
        for cell in content.split(LEX_DELIM):
            cell = cell.strip()
            if not cell:
                raise ValueError("line {}: an empty column".format(number))
            if cell == ABSENT_INDIC:
                forms.append(None)
            else:
                forms.append([phone for phone in cell.split(PH_DELIM) if phone])
        entries.append({
            "line": number,
            "forms": forms,
            "gloss": comment.strip() or None,
        })

    widths = {len(entry["forms"]) for entry in entries}
    if len(widths) > 1:
        raise ValueError("rows have different numbers of columns: {}".format(sorted(widths)))
    if header is not None and widths and len(header) not in widths:
        raise ValueError("the header has {} stages but the rows {} columns".format(
            len(header),
            widths.pop(),
        ))
    return header, entries
