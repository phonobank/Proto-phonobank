"""
Check whether two cascades give the same results on a lexicon, using DiaSim.

    cldfbench phonobank.compare pardess1990 raw/pardess1990/oct26-romanian-extractor-cfr.txt \\
        --lexicon pardess1990-lexicon.txt --diasim ~/projects/DiaSim

Each cascade is either a cite key (the cascade is written out from the CLDF
data first) or the path to a cascade file.

Method (after Clayton Marr's compareCascades in DiaSim's UTILS.py):
    1. Run DiaSim with the first cascade on the lexicon.
    2. Turn its predictions at each stage into a new lexicon, in which those
       predictions are the forms DiaSim compares against.
    3. Run DiaSim with the second cascade on that lexicon.
    4. The cascades agree if the second run reproduces the first run's output
       for every form (overall accuracy 1.0).

The comparison is of the final output, and of any stage the second cascade
marks as gold ('~'). Stages marked black ('=') are not compared.

Exits with status 0 if the cascades agree, 1 if they do not.
"""

import csv
import logging
import os
import pathlib
import shutil
import subprocess
import tempfile

from cldfbench_phonobank import Dataset
from phonobank_commands.cascade import emit

# DiaSim file conventions (as in DiaSim's UTILS.py).
STAGE_OUT_DELIM = " | "
GOLD_ONSET_FLAG = "{"
RECONSTR_FLAG = "*"
BOUNDARY = "#"
ABSENT_INDIC = "..."
ID_FLAG = "ɸ"
CMT_FLAG = "$"
HEADER_FLAG = "="
HEADER_DELIM = ","
LEX_DELIM = " , "
PHONE_DELIM = " "

ACCURACY_REPORT = "goldAnalysis.txt"
EDIT_DISTANCES = "resultEditDistances.csv"
OVERALL_ACCURACY_LABEL = "Overall accuracy:"


def register(parser):
    parser.add_argument(
        "cascade1",
        help="cite key, or path to a cascade file",
    )
    parser.add_argument(
        "cascade2",
        help="cite key, or path to a cascade file",
    )
    parser.add_argument(
        "--lexicon",
        required=True,
        help="DiaSim lexicon file to run both cascades on",
    )
    parser.add_argument(
        "--diasim",
        default=os.environ.get("DIASIM"),
        help="DiaSim directory, containing the compiled bin/ (default: $DIASIM)",
    )
    parser.add_argument(
        "--symbols",
        default=None,
        help="symbol definitions file, if not DiaSim's default symbolDefs.csv",
    )
    parser.add_argument(
        "--impl",
        default=None,
        help="feature implications file, if not DiaSim's default",
    )
    parser.add_argument(
        "--keep",
        default=None,
        help="directory in which to keep DiaSim's output (default: deleted afterwards)",
    )


def run(args):
    if not args.diasim:
        raise ValueError("give the DiaSim directory with --diasim, or set $DIASIM")
    diasim = pathlib.Path(args.diasim).expanduser().resolve()
    if not (diasim / "bin" / "DiachronicSimulator.class").exists():
        raise ValueError("{} has no compiled bin/DiachronicSimulator.class".format(diasim))

    if args.keep:
        work = pathlib.Path(args.keep).resolve()
        work.mkdir(parents=True, exist_ok=True)
    else:
        work = pathlib.Path(tempfile.mkdtemp(prefix="phonobank-compare-"))

    try:
        cascade1 = cascade_file(args.cascade1, work / "cascade1.txt")
        cascade2 = cascade_file(args.cascade2, work / "cascade2.txt")
        lexicon = pathlib.Path(args.lexicon).resolve()
        options = []
        if args.symbols:
            options += ["-symbols", str(pathlib.Path(args.symbols).resolve())]
        if args.impl:
            options += ["-impl", str(pathlib.Path(args.impl).resolve())]

        # 1. First cascade on the lexicon.
        run1 = work / "run1"
        run_diasim(diasim, run1, lexicon, cascade1, options)

        # 2. Its predictions become the forms to compare against.
        comparison = work / "cascade1_predictions.txt"
        outgraph = run1 / "run1_stagewise_output_graph.csv"
        comparison.write_text(outgraph_to_lexicon(outgraph), encoding="utf-8")

        # 3. Second cascade on that lexicon.
        run2 = work / "run2"
        run_diasim(diasim, run2, comparison, cascade2, options)

        # 4. Agreement means 100% accuracy.
        accuracy = overall_accuracy(run2 / ACCURACY_REPORT)
        differences = differing_forms(run2 / EDIT_DISTANCES)
    finally:
        if not args.keep:
            shutil.rmtree(work, ignore_errors=True)

    if accuracy == 1.0:
        args.log.info("cascades agree on all forms")
        return 0

    args.log.warning("cascades disagree: overall accuracy {}".format(accuracy))
    for form_id, first, second in differences:
        print("{}\t{}\t{}".format(form_id, first, second))
    return 1


def cascade_file(spec, path):
    """Return a cascade file for spec: the file itself, or one written from the CLDF."""
    if pathlib.Path(spec).is_file():
        return pathlib.Path(spec).resolve()
    text = emit(Dataset().cldf_reader(), spec)
    path.write_text(text, encoding="utf-8")
    return path


def run_diasim(diasim, out, lexicon, cascade, options):
    """Run DiaSim from its own directory (it finds bin/ and its default files there)."""
    command = [
        "java",
        "-cp",
        "bin",
        "DiachronicSimulator",
        "-out",
        str(out),
        "-lexicon",
        str(lexicon),
        "-rules",
        str(cascade),
    ] + options + [
        "-diacrit",
        "-files_only",
    ]
    result = subprocess.run(
        command,
        cwd=diasim,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not (out / ACCURACY_REPORT).exists():
        raise RuntimeError(
            "DiaSim failed on {} with {}:\n{}".format(
                lexicon.name,
                cascade.name,
                (result.stderr or result.stdout)[-2000:],
            )
        )


def outgraph_to_lexicon(path):
    """Turn a stagewise output graph into a lexicon whose forms are the predictions.

    The graph's rows look like
        0      | #owi# | *#oʍ# | *#oʍ# {GOLD: #oʍ#}
    with the form ID first. The lexicon keeps the stage columns, with gold
    annotations, reconstruction marks and word boundaries removed and the
    phones separated by spaces, and the form ID as a ɸ comment.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    header = [strip_gold(name) for name in lines[0].split(STAGE_OUT_DELIM)[1:]]
    out = [HEADER_FLAG + HEADER_DELIM.join(header)]
    for line in lines[1:]:
        if STAGE_OUT_DELIM not in line:
            continue
        cells = line.split(STAGE_OUT_DELIM)
        form_id = cells[0].strip()
        forms = [prediction_to_form(cell) for cell in cells[1:]]
        out.append("{} {}{}{}".format(LEX_DELIM.join(forms), CMT_FLAG, ID_FLAG, form_id))
    return "\n".join(out) + "\n"


def strip_gold(cell):
    """Remove a '{GOLD: ...}' annotation."""
    return cell.split(GOLD_ONSET_FLAG)[0].strip()


def prediction_to_form(cell):
    """'*#oʍ# {GOLD: #oʍ#}' -> 'o ʍ'; '...' stays as it is."""
    form = strip_gold(cell)
    if form == ABSENT_INDIC:
        return form
    form = form.lstrip(RECONSTR_FLAG).strip().strip(BOUNDARY)
    return PHONE_DELIM.join(tokenize(form))


def tokenize(form):
    # lingpy logs heavily when it first loads its sound-class models.
    import lingpy
    logging.getLogger("lingpy").setLevel(logging.WARNING)
    return lingpy.ipa2tokens(form)


def overall_accuracy(path):
    """Read the overall accuracy from DiaSim's goldAnalysis.txt."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(OVERALL_ACCURACY_LABEL):
            return float(line[len(OVERALL_ACCURACY_LABEL):].strip())
    raise ValueError("no '{}' line in {}".format(OVERALL_ACCURACY_LABEL, path))


def differing_forms(path):
    """Rows of resultEditDistances.csv where the two cascades' outputs differ."""
    with path.open(encoding="utf-8", newline="") as handle:
        return [
            (row["ID"], row["gold"], row["CFR_prediction"])
            for row in csv.DictReader(handle)
            if row["rawLevenshteinED"] != "0"
        ]
