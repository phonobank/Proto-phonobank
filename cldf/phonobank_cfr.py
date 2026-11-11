"""Reading DiaSim cascade files, with the Proto-phonobank stage convention.

A cascade file holds one chain of stages. Each stage is marked on a line of
its own, and the rules between two stages form one cascade:

    $| Proto-Quechuan          origin: a '$|' line before the first rule
    q > k
    =Some Stage                intermediate stage DiaSim stops at (black)
    ~Other Stage               intermediate stage with gold forms
    $| Hidden Stage            intermediate stage DiaSim does not see
    h > ∅
    $| Amazonas                output: a '$|' line after the last rule

To DiaSim a '$|' line is a comment, so the file still runs unchanged. The
origin and output must be '$|' lines, since DiaSim has no marker for them.

Everything else follows DiaSim: '$' starts a comment, and a rule line is
'A > B' or 'A > B / C __ D'.
"""

import re

# DiaSim conventions (as in DiaSim's UTILS.py).
CMT_FLAG = "$"
GOLD_STAGENAME_FLAG = "~"
BLACK_STAGENAME_FLAG = "="

# Proto-phonobank: a stage that is a comment to DiaSim.
STAGE_FLAG = "$|"

# The three kinds of stage marker. Stored in CLDF as Target_Gold:
# True for gold, False for black, empty for a '$|' stage.
MARKERS = {
    STAGE_FLAG: None,
    BLACK_STAGENAME_FLAG: False,
    GOLD_STAGENAME_FLAG: True,
}


def strip_comment(line):
    """Remove a DiaSim comment (CMT_FLAG to the end of the line)."""
    return line.split(CMT_FLAG)[0].strip()


def stage_marker(line):
    """Return (marker, name) if the line marks a stage, else None."""
    text = line.strip()
    if text.startswith(STAGE_FLAG):
        return STAGE_FLAG, text[len(STAGE_FLAG):].strip()
    text = strip_comment(line)
    if text and text[0] in (GOLD_STAGENAME_FLAG, BLACK_STAGENAME_FLAG):
        return text[0], text[1:].strip()
    return None


def stage_line(marker, name):
    """Write a stage marker line: '$| Name', '=Name' or '~Name'."""
    if marker == STAGE_FLAG:
        return "{} {}".format(STAGE_FLAG, name)
    return "{}{}".format(marker, name)


def marker_for(gold):
    """The stage marker for a Target_Gold value (True, False or None)."""
    for marker, value in MARKERS.items():
        if value is gold:
            return marker
    raise ValueError("no stage marker for {!r}".format(gold))


def structural_lines(text):
    """The lines that define a cascade: stage markers and rule lines, in order.

    Comments are dropped, and runs of spaces count as one space, so two files
    that differ only in comments and spacing give the same list.
    """
    lines = []
    for line in text.splitlines():
        stage = stage_marker(line)
        if stage:
            lines.append(stage_line(*stage))
            continue
        content = " ".join(strip_comment(line).split())
        if content:
            lines.append(content)
    return lines


def is_extension(parent, child):
    """True if identifier child is a subdivision of parent: M5.2 -> M5.2a, R13 -> R13B."""
    if not parent or not child or not child.startswith(parent) or child == parent:
        return False
    return re.match(r"[.A-Za-z]", child[len(parent):]) is not None


def parse_rule_line(text):
    """Split a rule line into (input, output, context); context may be None."""
    if " / " in text:
        change, context = text.split(" / ", 1)
    else:
        change, context = text, None
    if " > " not in change:
        raise ValueError("not a rule line: {!r}".format(text))
    inp, out = change.split(" > ", 1)
    return inp.strip(), out.strip(), context.strip() if context else None


def parse_cascade(lines, header_re=None):
    """Parse one cascade file.

    header_re, if given, matches rule header comments, with the named groups
    source_rule_id, name and page. Without it, rules have no identifiers.

    Returns (stages, rules):
        stages  (marker, name) for each stage, in order; the first is the
                origin and the last the output
        rules   dicts in file order; 'step' is the index of the cascade (the
                rules between stages[step] and stages[step + 1])
    """
    stages = []
    rules = []
    header = None      # the current rule header, if any
    lines_under = 0    # rule lines seen under that header

    def close_header():
        # A header with no rule line under it is a comment-only rule.
        if header is not None and lines_under == 0:
            rules.append({
                "step": len(stages) - 1,
                "source_rule_id": header["source_rule_id"],
                "name": header["name"],
                "page": header["page"],
                "sub_index": None,
                "input": None,
                "output": None,
                "context": None,
                "comment_only": True,
            })

    for number, line in enumerate(lines, start=1):
        stage = stage_marker(line)
        if stage:
            close_header()
            stages.append(stage)
            header = None
            lines_under = 0
            continue

        if header_re is not None:
            match = header_re.match(line)
            if match:
                close_header()
                header = match.groupdict()
                lines_under = 0
                continue

        text = strip_comment(line)
        if not text:
            continue

        if not stages:
            raise ValueError("line {}: rule before the origin '$|' line".format(number))
        try:
            inp, out, context = parse_rule_line(text)
        except ValueError as error:
            raise ValueError("line {}: {}".format(number, error))
        lines_under += 1
        rules.append({
            "step": len(stages) - 1,
            "source_rule_id": header["source_rule_id"] if header else None,
            "name": header["name"] if header else None,
            "page": header["page"] if header else None,
            "sub_index": lines_under,
            "input": inp,
            "output": out,
            "context": context,
            "comment_only": False,
        })

    close_header()

    if len(stages) < 2:
        raise ValueError("needs an origin and an output '$|' line")
    if stages[0][0] != STAGE_FLAG or stages[-1][0] != STAGE_FLAG:
        raise ValueError("the origin and output must be '$|' lines")
    if rules and rules[-1]["step"] == len(stages) - 1 and not rules[-1]["comment_only"]:
        raise ValueError("rule after the output '$|' line")

    # A header with no rule line whose identifier is extended by the next
    # header (M5.2 followed by M5.2a) is a section heading, not a comment-only
    # rule. The extension must start with a letter or '.', so that M1 followed
    # by M10a does not count.
    rules = [
        rule for i, rule in enumerate(rules)
        if not (
            rule["comment_only"]
            and i + 1 < len(rules)
            and is_extension(rule["source_rule_id"], rules[i + 1]["source_rule_id"])
        )
    ]

    return stages, rules
