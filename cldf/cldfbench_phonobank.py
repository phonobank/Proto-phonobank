"""Proto-phonobank: CLDF dataset of phonological rule cascades from DiaSim files.

Each source lives in its own directory under raw/:

    raw/<directory>/
        <cascade>.txt   one or more DiaSim cascade files (see phonobank_cfr.py)
        source.bib      the BibTeX entry for the source
        cascade.py      what is specific to this source (see below)

cascade.py must define:
    FILES       names of the cascade files in the same directory
    SOURCE      BibTeX cite key of the source (must match source.bib)
    LANGUAGES   dict: stage names used in the files -> IDs in etc/languages.csv
and may define:
    HEADER_RE   compiled regex for rule header comments, with the named groups
                source_rule_id, name and page (omit if the files have none)
    comment_only(lines)
                returns extra comment-only rules (dicts with source_rule_id,
                name, page) for files that do not write them as headers
                without a rule line

Each cascade file is one chain (origin to output). Its IDs are scoped by the
chain: <source>-<output language>, e.g. pardess1990-daco-romanian.

Build with `cldfbench makecldf cldfbench_phonobank.py`, then check with
`cldf validate cldf/Generic-metadata.json`.
"""

import importlib.util
import pathlib
import re

from cldfbench import CLDFSpec
from cldfbench import Dataset as BaseDataset

from phonobank_cfr import MARKERS
from phonobank_cfr import parse_cascade

CLDF = "http://cldf.clld.org/v1.0/terms.rdf#"

REQUIRED = ("FILES", "SOURCE", "LANGUAGES")


def make_id(*parts):
    """Join parts into a CLDF ID; CLDF IDs allow only letters, digits, '_' and '-'."""
    return re.sub(r"[^A-Za-z0-9_\-]", "_", "-".join(str(part) for part in parts))


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
    """Yield (directory, cascade module) for each raw/<directory>/ with a cascade.py."""
    directories = sorted(
        path for path in pathlib.Path(raw_dir).iterdir()
        if path.is_dir() and (path / "cascade.py").exists()
    )
    for directory in directories:
        yield directory, load_extraction(directory)


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
            "chains.csv",
            CLDF + "id",
            "Source_Language_ID",
            "Target_Language_ID",
            "Raw_File",
            CLDF + "source",
        )
        cldf.add_table(
            "rules.csv",
            CLDF + "id",
            "Chain_ID",
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
            "Chain_ID",
            {"name": "Chain_Position", "datatype": "integer"},
            "Source_Language_ID",
            "Target_Language_ID",
            # The stage names exactly as written in the cascade file. DiaSim
            # matches '=Name' markers against lexicon headers, so the emitter
            # needs these rather than the LanguageTable names.
            "Source_Stage",
            "Target_Stage",
            # True: gold (~); False: black (=); empty: a '$|' stage, or the output.
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

        cldf.add_foreign_key("chains.csv", "Source_Language_ID", "LanguageTable", "ID")
        cldf.add_foreign_key("chains.csv", "Target_Language_ID", "LanguageTable", "ID")
        cldf.add_foreign_key("rules.csv", "Chain_ID", "chains.csv", "ID")
        cldf.add_foreign_key("cascades.csv", "Chain_ID", "chains.csv", "ID")
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
        chain_ids = set()
        rule_count = 0

        for directory, extraction in iter_extractions(self.raw_dir):
            source_key = extraction.SOURCE
            header_re = getattr(extraction, "HEADER_RE", None)
            args.writer.cldf.add_sources(*self.raw_dir.read_bib(directory / "source.bib"))

            for filename in extraction.FILES:
                path = directory / filename
                lines = path.read_text(encoding="utf-8").splitlines()
                try:
                    stages, parsed = parse_cascade(lines, header_re)
                except ValueError as error:
                    raise ValueError("{}: {}".format(path, error))

                # Comment-only rules the extraction lists outside the headers.
                if hasattr(extraction, "comment_only"):
                    for extra in extraction.comment_only(lines):
                        parsed.append(dict(
                            extra,
                            step=len(stages) - 2,
                            sub_index=None,
                            input=None,
                            output=None,
                            context=None,
                            comment_only=True,
                            listed=True,
                        ))

                language_ids = []
                for _, name in stages:
                    if name not in extraction.LANGUAGES:
                        raise ValueError("{}: no LANGUAGES entry for {!r}".format(path, name))
                    language_id = extraction.LANGUAGES[name]
                    if language_id not in languages:
                        raise ValueError("{!r} is not in etc/languages.csv".format(language_id))
                    language_ids.append(language_id)
                    used_languages.add(language_id)

                chain_id = make_id(source_key, language_ids[-1])
                if chain_id in chain_ids:
                    raise ValueError("{}: a second chain {}".format(path, chain_id))
                chain_ids.add(chain_id)
                args.log.info("{}: {} ({})".format(
                    chain_id,
                    " > ".join(name for _, name in stages),
                    path.relative_to(self.dir),
                ))
                args.writer.objects["chains.csv"].append({
                    "ID": chain_id,
                    "Source_Language_ID": language_ids[0],
                    "Target_Language_ID": language_ids[-1],
                    "Raw_File": str(path.relative_to(self.raw_dir)),
                    "Source": [source_key],
                })

                # One cascade between each pair of consecutive stages.
                cascade_ids = []
                for step in range(len(stages) - 1):
                    cascade_id = make_id(chain_id, step + 1)
                    cascade_ids.append(cascade_id)
                    args.writer.objects["cascades.csv"].append({
                        "ID": cascade_id,
                        "Chain_ID": chain_id,
                        "Chain_Position": step + 1,
                        "Source_Language_ID": language_ids[step],
                        "Target_Language_ID": language_ids[step + 1],
                        "Source_Stage": stages[step][1],
                        "Target_Stage": stages[step + 1][1],
                        "Target_Gold": MARKERS[stages[step + 1][0]],
                        "Source": [source_key],
                    })

                rule_ids = set()
                position = {}    # step -> last position used
                comment_count = 0
                for order, rule in enumerate(parsed, start=1):
                    if rule["source_rule_id"] is None:
                        rule_id = make_id(chain_id, "line{}".format(order))
                    elif rule.get("listed"):
                        # From a comment_only() list: identifiers may repeat there
                        # (one section cited twice), so number them in list order.
                        comment_count += 1
                        rule_id = make_id(chain_id, "comment{}".format(comment_count))
                    elif rule["sub_index"] is None:
                        rule_id = make_id(chain_id, rule["source_rule_id"])
                    else:
                        rule_id = make_id(chain_id, rule["source_rule_id"], rule["sub_index"])
                    if rule_id in rule_ids:
                        raise ValueError("{}: duplicate rule ID {}".format(path, rule_id))
                    rule_ids.add(rule_id)

                    # The page goes into the CLDF source reference: key[page].
                    reference = source_key
                    if rule["page"]:
                        reference = "{}[{}]".format(source_key, rule["page"])

                    args.writer.objects["rules.csv"].append({
                        "ID": rule_id,
                        "Chain_ID": chain_id,
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
                        "ID": make_id(cascade_ids[step], position[step]),
                        "Cascade_ID": cascade_ids[step],
                        "Rule_ID": rule_id,
                        "Position": position[step],
                    })
                rule_count += len(rule_ids)

                for step in range(len(cascade_ids)):
                    args.log.info("{}: {} > {}: {} rules".format(
                        chain_id,
                        stages[step][1],
                        stages[step + 1][1],
                        position.get(step, 0),
                    ))
                comment_only = sum(1 for rule in parsed if rule["comment_only"])
                if comment_only:
                    args.log.info("{}: {} comment-only rules".format(chain_id, comment_only))

                # Rule lines with no header, in a source that has headers, usually
                # mean HEADER_RE does not match this file's headers.
                headerless = sum(1 for rule in parsed if rule["source_rule_id"] is None)
                if header_re is not None and headerless:
                    args.log.warning("{}: {} rule lines have no header; check HEADER_RE".format(
                        chain_id,
                        headerless,
                    ))

        args.log.info("{} chains, {} languages, {} rules in total".format(
            len(chain_ids),
            len(used_languages),
            rule_count,
        ))
        args.writer.objects["LanguageTable"].extend(
            languages[language_id] for language_id in sorted(used_languages)
        )
