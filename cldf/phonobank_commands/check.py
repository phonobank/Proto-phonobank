"""
Check that each cascade written out from the CLDF data matches its original file.

    cldfbench phonobank.check                 # every source
    cldfbench phonobank.check pardess1990     # one or more given sources

Compares only what DiaSim reads: the rule lines and stage markers, in order.
Comments are ignored, and runs of spaces count as one space. Differences are
shown as a diff (original first, then the version from the CLDF).

This is a check of the import and export, not of what the rules do; for that,
see `cldfbench phonobank.compare`.

Exits with status 0 if every checked source matches, 1 otherwise.
"""

import difflib

from cldfbench_phonobank import CMT_FLAG
from cldfbench_phonobank import Dataset
from cldfbench_phonobank import iter_extractions
from phonobank_commands.cascade import emit


def register(parser):
    parser.add_argument(
        "source",
        nargs="*",
        help="cite keys of the sources to check (default: all)",
    )


def run(args):
    dataset = Dataset()
    cldf = dataset.cldf_reader()
    originals = {
        extraction.SOURCE: directory / extraction.FILE
        for directory, extraction in iter_extractions(dataset.raw_dir)
    }

    unknown = [key for key in args.source if key not in originals]
    if unknown:
        raise ValueError("no extraction in raw/ for {}".format(", ".join(unknown)))

    failed = []
    for source_key in args.source or sorted(originals):
        original_path = originals[source_key]
        original = diasim_lines(original_path.read_text(encoding="utf-8"))
        exported = diasim_lines(emit(cldf, source_key))

        if original == exported:
            args.log.info("{}: {} lines match".format(source_key, len(original)))
            continue

        failed.append(source_key)
        args.log.warning("{}: does not match {}".format(source_key, original_path.name))
        for line in difflib.unified_diff(
            original,
            exported,
            fromfile=original_path.name,
            tofile="{} (from CLDF)".format(source_key),
            lineterm="",
        ):
            print(line)

    return 1 if failed else 0


def diasim_lines(text):
    """The lines DiaSim reads: comments removed, blank lines dropped, spaces normalised."""
    lines = []
    for line in text.splitlines():
        content = " ".join(line.split(CMT_FLAG)[0].split())
        if content:
            lines.append(content)
    return lines
