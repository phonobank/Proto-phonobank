"""
Write the DiaSim cascade file for one source from the CLDF data.

    cldfbench phonobank.cascade pardess1990 -o pardess1990.txt

The output contains, in order:
    - the '$ DiaSim cascade: A > B > C' line, rebuilt from the stage names
    - each rule's header comment ($ <id> <name> $$PG: <page>), once per source rule
    - the rule lines, in the source's own order (Source_Order)
    - a stage marker between consecutive cascades ('~' gold, '=' black)
    - comment-only rules as header comments marked [COMMENT-ONLY]

Only the rule lines and stage markers matter to DiaSim; the comments are there
so the file can be checked against the source by eye.
"""

import pathlib

from pycldf.sources import Sources

from cldfbench_phonobank import Dataset


def register(parser):
    parser.add_argument(
        "source",
        help="cite key of the source whose cascade to write, e.g. pardess1990",
    )
    parser.add_argument(
        "-o",
        "--out",
        default=None,
        help="output file (default: print to the terminal)",
    )


def run(args):
    cldf = Dataset().cldf_reader()
    text = emit(cldf, args.source)
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


def chain_for(cascades):
    """Order one source's cascades by following each target to the next source.

    Returns the cascades as a list running from the first input to the output.
    """
    targets = {cascade["Target_Language_ID"] for cascade in cascades}
    starts = [cascade for cascade in cascades if cascade["Source_Language_ID"] not in targets]
    if len(starts) != 1:
        raise ValueError("expected one starting cascade, found {}".format(len(starts)))

    by_source_language = {cascade["Source_Language_ID"]: cascade for cascade in cascades}
    ordered = [starts[0]]
    while ordered[-1]["Target_Language_ID"] in by_source_language:
        ordered.append(by_source_language[ordered[-1]["Target_Language_ID"]])
    if len(ordered) != len(cascades):
        raise ValueError("cascades do not form a single chain")
    return ordered


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


def emit(cldf, source_key):
    """Return the DiaSim cascade text for source_key from the pycldf dataset cldf."""
    cascades = [
        row for row in cldf.iter_rows("cascades.csv")
        if source_key in source_keys(row)
    ]
    if not cascades:
        raise ValueError("no cascades for source {!r}".format(source_key))
    cascades = chain_for(cascades)

    rules = sorted(
        (row for row in cldf.iter_rows("rules.csv") if source_key in source_keys(row)),
        key=lambda row: row["Source_Order"],
    )

    # Which cascade each executable rule fires in.
    cascade_ids = {cascade["ID"] for cascade in cascades}
    cascade_of_rule = {
        row["Rule_ID"]: row["Cascade_ID"]
        for row in cldf.iter_rows("cascade_rules.csv")
        if row["Cascade_ID"] in cascade_ids
    }
    cascade_by_id = {cascade["ID"]: cascade for cascade in cascades}

    stage_names = [cascades[0]["Source_Stage"]] + [c["Target_Stage"] for c in cascades]
    lines = ["$ DiaSim cascade: {}".format(" > ".join(stage_names))]

    current = None   # ID of the cascade whose rules are being written
    for rule in rules:
        cascade_id = cascade_of_rule.get(rule["ID"])
        if cascade_id is not None and cascade_id != current:
            if current is not None:
                # Close the previous cascade with its target's stage marker.
                finished = cascade_by_id[current]
                flag = "~" if finished["Target_Gold"] else "="
                lines.append("")
                lines.append("{}{}".format(flag, finished["Target_Stage"]))
            current = cascade_id

        # A header starts each source rule: a comment-only rule, or the first
        # line (Sub_Index 1) of a rule that has one or more rule lines.
        if rule["Source_Rule_ID"] and (rule["Comment_Only"] or rule["Sub_Index"] == 1):
            lines.append("")
            lines.append(header_line(rule, page_of(rule, source_key)))

        if not rule["Comment_Only"]:
            lines.append(rule_line(rule))

    return "\n".join(lines) + "\n"
