"""
Write the DiaSim cascade file for one chain from the CLDF data.

    cldfbench phonobank.cascade pardess1990-daco-romanian -o pardess1990.txt
    cldfbench phonobank.cascade pardess1990     # a cite key, if it has one chain

The output contains, in order:
    - the origin, as a '$|' line
    - each rule's header comment ($ <id> <name> $$PG: <page>), once per source rule
    - the rule lines, in the source's own order (Source_Order)
    - each intermediate stage in the form it was written ('$|', '=' or '~')
    - comment-only rules as header comments marked [COMMENT-ONLY]
    - the output, as a '$|' line
"""

import pathlib

from pycldf.sources import Sources

from cldfbench_phonobank import Dataset
from phonobank_cfr import STAGE_FLAG
from phonobank_cfr import marker_for
from phonobank_cfr import stage_line


def register(parser):
    parser.add_argument(
        "chain",
        help="chain ID (e.g. pardess1990-daco-romanian), or a cite key with one chain",
    )
    parser.add_argument(
        "-o",
        "--out",
        default=None,
        help="output file (default: print to the terminal)",
    )


def run(args):
    cldf = Dataset().cldf_reader()
    text = emit(cldf, args.chain)
    if args.out:
        pathlib.Path(args.out).write_text(text, encoding="utf-8")
        args.log.info("wrote {}".format(args.out))
    else:
        print(text, end="")


def source_keys(row):
    """Cite keys in a row's Source column, without page locators."""
    return [Sources.parse(reference)[0] for reference in row["Source"]]


def page_of(row, source_key):
    """The page locator for source_key in a row's Source column, or None."""
    for reference in row["Source"]:
        key, page = Sources.parse(reference)
        if key == source_key:
            return page
    return None


def resolve_chain(cldf, spec):
    """Return the chains.csv row for a chain ID, or for a cite key with one chain."""
    chains = list(cldf.iter_rows("chains.csv"))
    for chain in chains:
        if chain["ID"] == spec:
            return chain
    matches = [chain for chain in chains if spec in source_keys(chain)]
    if len(matches) == 1:
        return matches[0]
    if matches:
        raise ValueError("{} has several chains; give one of: {}".format(
            spec,
            ", ".join(chain["ID"] for chain in matches),
        ))
    raise ValueError("no chain or source {!r}".format(spec))


def header_line(rule, page):
    text = "$ {}".format(rule["Source_Rule_ID"])
    if rule["Name"]:
        text = "{} {}".format(text, rule["Name"])
    if page:
        text = "{}  $$PG: {}".format(text, page)
    if rule["Comment_Only"]:
        text = "{} [COMMENT-ONLY]".format(text)
    return text


def rule_line(rule):
    text = "{} > {}".format(rule["Input"], rule["Output"])
    if rule["Context"]:
        text = "{} / {}".format(text, rule["Context"])
    return text


def emit(cldf, spec):
    """Return the DiaSim cascade text for a chain (see resolve_chain)."""
    chain = resolve_chain(cldf, spec)
    source_key = source_keys(chain)[0]

    cascades = sorted(
        (row for row in cldf.iter_rows("cascades.csv") if row["Chain_ID"] == chain["ID"]),
        key=lambda row: row["Chain_Position"],
    )
    index_of_cascade = {cascade["ID"]: i for i, cascade in enumerate(cascades)}
    cascade_of_rule = {
        row["Rule_ID"]: index_of_cascade[row["Cascade_ID"]]
        for row in cldf.iter_rows("cascade_rules.csv")
        if row["Cascade_ID"] in index_of_cascade
    }
    rules = sorted(
        (row for row in cldf.iter_rows("rules.csv") if row["Chain_ID"] == chain["ID"]),
        key=lambda row: row["Source_Order"],
    )

    def boundary(i):
        # The stage after cascade i, as it was written.
        return ["", stage_line(marker_for(cascades[i]["Target_Gold"]), cascades[i]["Target_Stage"])]

    lines = [stage_line(STAGE_FLAG, cascades[0]["Source_Stage"])]
    current = 0   # index of the cascade whose rules are being written
    for rule in rules:
        index = cascade_of_rule.get(rule["ID"])
        if index is not None:
            # Close every cascade up to this rule's one (some may have no rules).
            while current < index:
                lines += boundary(current)
                current += 1

        # A header starts each source rule: a comment-only rule, or the first
        # line (Sub_Index 1) of a rule that has one or more rule lines.
        if rule["Source_Rule_ID"] and (rule["Comment_Only"] or rule["Sub_Index"] == 1):
            lines.append("")
            lines.append(header_line(rule, page_of(rule, source_key)))

        if not rule["Comment_Only"]:
            lines.append(rule_line(rule))

    while current < len(cascades) - 1:
        lines += boundary(current)
        current += 1
    lines.append("")
    lines.append(stage_line(STAGE_FLAG, cascades[-1]["Target_Stage"]))
    return "\n".join(lines) + "\n"
