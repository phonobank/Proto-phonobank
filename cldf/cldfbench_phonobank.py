"""Proto-phonobank: CLDF dataset of phonological rule cascades from DiaSim files.

Each extraction lives in its own directory under raw/:

    raw/<citekey>/
        <cascade>.txt   the DiaSim cascade file
        source.bib      the BibTeX entry for the source
        cascade.py      what is specific to this extraction (see below)

cascade.py must define:
    FILE        name of the cascade file in the same directory
    SOURCE      BibTeX cite key of the source (must match source.bib)
    LANGUAGES   dict: names in the '$ DiaSim cascade:' line -> IDs in etc/languages.csv
    HEADER_RE   compiled regex for rule header comments, with the named groups
                source_rule_id, name and page
and may define:
    comment_only(lines)   returns extra comment-only rules (dicts with
                          source_rule_id, name, page) for files that do not
                          write them as headers without a rule line

Everything defined by DiaSim itself (comments, stage markers, the chain line,
rule lines) is parsed here, once, for all extractions.

Build with `cldfbench makecldf cldfbench_phonobank.py`, then check with
`cldf validate cldf/Generic-metadata.json`.
"""

import importlib.util
import pathlib
import re

from cldfbench import CLDFSpec
from cldfbench import Dataset as BaseDataset

CLDF = "http://cldf.clld.org/v1.0/terms.rdf#"

# DiaSim conventions (as in DiaSim's UTILS.py).
CMT_FLAG = "$"
GOLD_STAGENAME_FLAG = "~"
BLACK_STAGENAME_FLAG = "="

# The file's own statement of the whole chain: "$ DiaSim cascade: A > B > C".
CHAIN_RE = re.compile(r"DiaSim cascade:\s*(?P<chain>.+?)\s*$")

REQUIRED = ("FILE", "SOURCE", "LANGUAGES", "HEADER_RE")


def strip_comment(line):
    """Remove a DiaSim comment (CMT_FLAG to the end of the line)."""
    return line.split(CMT_FLAG)[0].strip()


def make_id(*parts):
    """Join parts into a CLDF ID; CLDF IDs allow only letters, digits, '_' and '-'."""
    return re.sub(r"[^A-Za-z0-9_\-]", "_", "-".join(str(part) for part in parts))


def is_extension(parent, child):
    """True if identifier child is a subdivision of parent: M5.2 -> M5.2a, R13 -> R13B."""
    if not parent or not child or not child.startswith(parent) or child == parent:
        return False
    return re.match(r"[.A-Za-z]", child[len(parent):]) is not None


def load_extraction(directory):
    """Import raw/<directory>/cascade.py and check it defines what is required."""
    path = directory / "cascade.py"
    spec = importlib.util.spec_from_file_location("cascade_" + directory.name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    missing = [name for name in REQUIRED if not hasattr(module, name)]
    if missing:
        raise ValueError("{}: missing {}".format(path, ", ".join(missing)))
    return module


def iter_extractions(raw_dir):
    """Yield (directory, cascade module) for each raw/<citekey>/ with a cascade.py."""
    directories = sorted(
        path for path in pathlib.Path(raw_dir).iterdir()
        if path.is_dir() and (path / "cascade.py").exists()
    )
    for directory in directories:
        yield directory, load_extraction(directory)


def parse_cascade(lines, header_re):
    """Parse the DiaSim content of one cascade file.

    Returns (chain, stages, rules):
        chain   names from the '$ DiaSim cascade:' line, in order
        stages  (name, is_gold) for each in-file stage marker, in order
        rules   dicts in file order; 'step' is the index of the cascade step
                (0 = before the first stage marker) the rule belongs to
    """
    chain = None
    for line in lines:
        match = CHAIN_RE.search(line)
        if match:
            chain = [name.strip() for name in match.group("chain").split(">")]
            break
    if chain is None:
        raise ValueError("no '$ DiaSim cascade: A > B' line")

    stages = []
    rules = []
    step = 0
    header = None      # the current rule header, if any
    lines_under = 0    # rule lines seen under that header

    def close_header():
        # A header with no rule line under it is a comment-only rule.
        if header is not None and lines_under == 0:
            rules.append({
                "step": step,
                "source_rule_id": header["source_rule_id"],
                "name": header["name"],
                "page": header["page"],
                "sub_index": None,
                "input": None,
                "output": None,
                "context": None,
                "comment_only": True,
            })

    for line in lines:
        match = header_re.match(line)
        if match:
            close_header()
            header = match.groupdict()
            lines_under = 0
            continue

        text = strip_comment(line)
        if not text:
            continue

        if text[0] in (GOLD_STAGENAME_FLAG, BLACK_STAGENAME_FLAG):
            # Stage marker: '=' black (no lexicon column), '~' gold.
            close_header()
            stages.append((text[1:].strip(), text[0] == GOLD_STAGENAME_FLAG))
            header = None
            lines_under = 0
            step += 1
            continue

        # Otherwise a rule line: 'A > B' or 'A > B / C __ D'.
        lines_under += 1
        if " / " in text:
            change, context = text.split(" / ", 1)
        else:
            change, context = text, None
        inp, out = change.split(" > ", 1)
        rules.append({
            "step": step,
            "source_rule_id": header["source_rule_id"] if header else None,
            "name": header["name"] if header else None,
            "page": header["page"] if header else None,
            "sub_index": lines_under,
            "input": inp.strip(),
            "output": out.strip(),
            "context": context.strip() if context else None,
            "comment_only": False,
        })

    close_header()

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

    # The in-file stage markers must be exactly the chain's intermediate names.
    if [name for name, _ in stages] != chain[1:-1]:
        raise ValueError("stage markers do not match the '$ DiaSim cascade:' line")

    return chain, stages, rules


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "phonobank"

    def cldf_specs(self):
        return CLDFSpec(
            dir=self.cldf_dir,
            module="Generic",
            metadata_fname="Generic-metadata.json",
        )

    def cmd_download(self, args):
        pass

    def schema(self, cldf):
        """Declare the tables, their columns and the links between them."""
        cldf.add_component("LanguageTable")

        # A column given as a CLDF term URL gets that term's standard name and
        # meaning (ID, Name, Source); dicts define plain columns.
        cldf.add_table(
            "rules.csv",
            CLDF + "id",
            "Input",
            "Output",
            "Context",
            CLDF + "name",
            "Source_Rule_ID",
            {"name": "Sub_Index", "datatype": "integer"},
            {"name": "Comment_Only", "datatype": "boolean"},
            {"name": "Source_Order", "datatype": "integer"},
            CLDF + "source",
        )
        cldf.add_table(
            "cascades.csv",
            CLDF + "id",
            "Source_Language_ID",
            "Target_Language_ID",
            # The stage names exactly as written in the cascade file. DiaSim
            # matches '=Name' markers against lexicon headers, so the emitter
            # needs these rather than the LanguageTable names.
            "Source_Stage",
            "Target_Stage",
            {"name": "Target_Gold", "datatype": "boolean"},
            CLDF + "source",
        )
        cldf.add_table(
            "cascade_rules.csv",
            CLDF + "id",
            "Cascade_ID",
            "Rule_ID",
            {"name": "Position", "datatype": "integer"},
        )

        cldf.add_foreign_key("cascades.csv", "Source_Language_ID", "LanguageTable", "ID")
        cldf.add_foreign_key("cascades.csv", "Target_Language_ID", "LanguageTable", "ID")
        cldf.add_foreign_key("cascade_rules.csv", "Cascade_ID", "cascades.csv", "ID")
        cldf.add_foreign_key("cascade_rules.csv", "Rule_ID", "rules.csv", "ID")

    def cmd_makecldf(self, args):
        self.schema(args.writer.cldf)

        languages = {
            row["ID"]: {
                "ID": row["ID"],
                "Name": row["Name"],
                "Glottocode": row["Glottocode"] or None,
            }
            for row in self.etc_dir.read_csv("languages.csv", dicts=True)
        }
        used_languages = set()
        rule_ids = set()

        for directory, extraction in iter_extractions(self.raw_dir):
            source_key = extraction.SOURCE
            args.writer.cldf.add_sources(*self.raw_dir.read_bib(directory / "source.bib"))

            path = directory / extraction.FILE
            lines = path.read_text(encoding="utf-8").splitlines()
            try:
                chain, stages, parsed = parse_cascade(lines, extraction.HEADER_RE)
            except ValueError as error:
                raise ValueError("{}: {}".format(path, error))

            # Comment-only rules the extraction lists outside the headers.
            if hasattr(extraction, "comment_only"):
                for extra in extraction.comment_only(lines):
                    parsed.append(dict(
                        extra,
                        step=len(chain) - 2,
                        sub_index=None,
                        input=None,
                        output=None,
                        context=None,
                        comment_only=True,
                        listed=True,
                    ))

            gold = dict(stages)

            language_ids = []
            for name in chain:
                if name not in extraction.LANGUAGES:
                    raise ValueError("{}: no LANGUAGES entry for {!r}".format(directory, name))
                language_id = extraction.LANGUAGES[name]
                if language_id not in languages:
                    raise ValueError("{!r} is not in etc/languages.csv".format(language_id))
                language_ids.append(language_id)
                used_languages.add(language_id)

            # One cascade per step of the chain.
            step_ids = []
            for i in range(len(chain) - 1):
                cascade_id = make_id(source_key, language_ids[i], language_ids[i + 1])
                step_ids.append(cascade_id)
                args.writer.objects["cascades.csv"].append({
                    "ID": cascade_id,
                    "Source_Language_ID": language_ids[i],
                    "Target_Language_ID": language_ids[i + 1],
                    "Source_Stage": chain[i],
                    "Target_Stage": chain[i + 1],
                    # None for the last target: it is the output, not a stage marker.
                    "Target_Gold": gold.get(chain[i + 1]),
                    "Source": [source_key],
                })

            position = {}    # step -> last position used
            comment_count = 0
            for order, rule in enumerate(parsed, start=1):
                if rule["source_rule_id"] is None:
                    rule_id = make_id(source_key, "line{}".format(order))
                elif rule.get("listed"):
                    # From a comment_only() list: identifiers may repeat there
                    # (one section cited twice), so number them in list order.
                    comment_count += 1
                    rule_id = make_id(source_key, "comment{}".format(comment_count))
                elif rule["sub_index"] is None:
                    rule_id = make_id(source_key, rule["source_rule_id"])
                else:
                    rule_id = make_id(source_key, rule["source_rule_id"], rule["sub_index"])
                if rule_id in rule_ids:
                    raise ValueError("duplicate rule ID {}".format(rule_id))
                rule_ids.add(rule_id)

                # The page goes into the CLDF source reference: key[page].
                reference = source_key
                if rule["page"]:
                    reference = "{}[{}]".format(source_key, rule["page"])

                args.writer.objects["rules.csv"].append({
                    "ID": rule_id,
                    "Input": rule["input"],
                    "Output": rule["output"],
                    "Context": rule["context"],
                    "Name": rule["name"],
                    "Source_Rule_ID": rule["source_rule_id"],
                    "Sub_Index": rule["sub_index"],
                    "Comment_Only": rule["comment_only"],
                    "Source_Order": order,
                    "Source": [reference],
                })

                # Only executable rules are fired in a cascade.
                if rule["comment_only"]:
                    continue
                step = rule["step"]
                position[step] = position.get(step, 0) + 1
                args.writer.objects["cascade_rules.csv"].append({
                    "ID": make_id(step_ids[step], position[step]),
                    "Cascade_ID": step_ids[step],
                    "Rule_ID": rule_id,
                    "Position": position[step],
                })

        args.writer.objects["LanguageTable"].extend(
            languages[language_id] for language_id in sorted(used_languages)
        )
