"""Proto-phonobank: CLDF dataset of phonological rule cascades from DiaSim files.

Each source lives in its own directory under raw/:

    raw/<directory>/
        <cascade>.txt   one or more DiaSim cascade files (see phonobank_cfr.py)
        source.bib      the BibTeX entry for the source
        extract.py      what is specific to this source (see below)

extract.py must define:
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
from phonobank_lexicon import parse_lexicon

CLDF = "http://cldf.clld.org/v1.0/terms.rdf#"

REQUIRED = ("FILES", "SOURCE", "LANGUAGES")

ID_DELIM = "-"


def make_id(*parts):
    """Join parts into a CLDF ID; CLDF IDs allow only letters, digits, '_' and '-'."""
    return re.sub(r"[^A-Za-z0-9_\-]", "_", ID_DELIM.join(str(part) for part in parts))


def load_extraction(directory):
    """Import raw/<directory>/extract.py and check it defines what is required."""
    path = directory / "extract.py"
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
        if path.is_dir() and (path / "extract.py").exists()
    )
    for directory in directories:
        yield directory, load_extraction(directory)


def read_languages(etc_dir):
    """Read the table of languages, which lives by default in etc/.

    If any language in a cascade or wordlist does _not_ exist in this file,
    the build will raise a ValueError and stop. This is to avoid data being
    loaded which is not explicitly assigned to a language.
    The format should be CSV, with ID, Name and Glottocode cols. ID and name
    are required, Glottocode is not, as it's quite possible we might have
    e.g. protolanguages from a source with no Glottocode assigned.
    TODO Isaac - put this info in the README
    """    
    languages = {
        row["ID"]: {
            "ID": row["ID"],
            "Name": row["Name"],
            "Glottocode": row["Glottocode"] or None,
        }
        for row in etc_dir.read_csv("languages.csv", dicts=True)
    }
    return languages


def read_chain(path, extraction):
    """Read one cascade file of an extraction.

    Returns (stages, parsed), as from parse_cascade, with any comment-only rules
    from the extraction's comment_only() hook added at the end.
    """
    header_re = getattr(extraction, "HEADER_RE", None)
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

    return stages, parsed


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "phonobank"

    def cldf_specs(self):
        return CLDFSpec(
            dir=self.cldf_dir,
            module="Generic",
            metadata_fname="cldf-metadata.json",
        )

    def cmd_download(self, args):
        pass

    def schema(self, cldf):
        """Declare the tables, their columns and the links between them."""
        cldf.add_component("LanguageTable")
        cldf.add_component("ParameterTable")    # concepts, one per gloss
        cldf.add_component("FormTable")         # every form: protoforms and reflexes
        cldf.add_component("CognatesetTable")   # etyma
        cldf.add_component("CognateTable")      # links each form to its etymon

        ## Default columns for above tables:
        ## ParameterTable: ID, Name, Description
        ## FormTable: ID, Language_ID, Parameter_ID and Form (all required), Segments, Comment, Source
        ## CognatesetTable: ID, Description, Source
        ## CognateTable: ID, Form_ID and Cognateset_ID (all required), Segment_Slice, Alignment, Source

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

        languages = read_languages(self.etc_dir)
        used_languages = set()
        chain_ids = set()
        parameter_ids = set()
        rule_count = 0

        ## Step through each data source directory in raw/ and import the data
        ## therein into the CLDF.
        ## Each data source lives in its own directory in raw/, and should have:
        ## - a source.bib file with aource information in bibtex format
        ## - one or more DiaSim-format cascades as text files
        ## - zero or more lexicon files in DiaSim format TODO format as a CLDF wordlist-
        ## type TSV file?
        ## - optionally an extraction.py Python source file, which is called by a hook
        ## in this function to do custom, per-source processing.
        ## TODO Isaac - transfer this info into README
        for directory, extraction in iter_extractions(self.raw_dir):
            source_key = extraction.SOURCE
            header_re = getattr(extraction, "HEADER_RE", None)
            args.writer.cldf.add_sources(*self.raw_dir.read_bib(directory / "source.bib"))

            ##
            ## Process each file in the data source dir
            ##
            for filename in extraction.FILES:
                path = directory / filename

                stages, parsed = read_chain(path, extraction)
                
                language_ids = []

                ## Verify that languages referred to in cascades/wordlists exist in
                ## etc/languages.tsv
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
                        " " * len(chain_id) + cascade_ids[step][len(chain_id):],
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

            ##
            ## OK, now we process the lexicon files from the raw source dirs. Using
            ## getattr won't choke if the file has it not
            ##

            for filename in getattr(extraction, "LEXICONS", {}): 
                path = directory / filename
                lines = path.read_text(encoding="utf-8").splitlines()
                header, entries = parse_lexicon(lines)

                ## We're enforcing the presence of a header naming the stages
                if not header:
                    raise ValueError("{}: no = header line with stages!".format(path))
                
                ## Make sure that the stages named in the header actually exist in
                ## the data...
                language_ids = []
                for name in header:
                    ## in the extraction itself...
                    if name not in extraction.LANGUAGES:
                        raise ValueError("{}: no LANGUAGES entry for {!r}".format(path, name))
                    language_id = extraction.LANGUAGES[name]
                    if language_id not in languages:
                        raise ValueError("{!r} is not in etc/languages.csv".format(language_id))
                    language_ids.append(language_id)
                    used_languages.add(language_id)

                ## Now add the data into the CLDF tables. Each entry is one etymon:
                ## the forms on a line are its protoform and reflexes, so they share
                ## one cognate set.
                lexicon_id = make_id(source_key, path.stem)
                for entry in entries:
                    line, forms, gloss = entry["line"], entry["forms"], entry["gloss"]
                    if not gloss:
                        raise ValueError("{}: line {}: no gloss".format(path, line))

                    parameter_id = make_id(gloss)
                    if parameter_id not in parameter_ids:
                        parameter_ids.add(parameter_id)
                        args.writer.objects["ParameterTable"].append({
                            "ID": parameter_id,
                            "Name": gloss,
                        })

                    cognateset_id = make_id(lexicon_id, line)
                    args.writer.objects["CognatesetTable"].append({
                        "ID": cognateset_id,
                        "Source": [source_key],
                    })

                    for index, (language_id, phones) in enumerate(zip(language_ids, forms)):
                        if phones is None:
                            continue
                        form_id = make_id(cognateset_id, index + 1)
                        args.writer.objects["FormTable"].append({
                            "ID": form_id,
                            "Language_ID": language_id,
                            "Parameter_ID": parameter_id,
                            "Form": "".join(phones),
                            "Segments": phones,
                            "Source": [source_key],
                        })
                        args.writer.objects["CognateTable"].append({
                            "ID": form_id,
                            "Form_ID": form_id,
                            "Cognateset_ID": cognateset_id,
                            "Source": [source_key],
                        })                    

        args.log.info("{} chains, {} languages, {} rules in total".format(
            len(chain_ids),
            len(used_languages),
            rule_count,
        ))
        args.writer.objects["LanguageTable"].extend(
            languages[language_id] for language_id in sorted(used_languages)
        )
