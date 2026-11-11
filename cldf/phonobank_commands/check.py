"""
Check that each cascade written out from the CLDF data matches its original file.

    cldfbench phonobank.check                           # every chain
    cldfbench phonobank.check quechua_cm pardess1990    # chains of given sources
    cldfbench phonobank.check pardess1990-daco-romanian # one chain

Compares the lines that define a cascade: stage markers ('$|', '=', '~') and
rule lines, in order. Comments are ignored, and runs of spaces count as one
space. Differences are shown as a diff (original first, then the version from
the CLDF).

This is a check of the import and export, not of what the rules do; for that,
see `cldfbench phonobank.compare`.

Exits with status 0 if every checked chain matches, 1 otherwise.
"""

import difflib

from cldfbench_phonobank import Dataset
from phonobank_cfr import structural_lines
from phonobank_commands.cascade import emit
from phonobank_commands.cascade import source_keys


def register(parser):
    parser.add_argument(
        "chain",
        nargs="*",
        help="chain IDs or cite keys to check (default: all)",
    )


def run(args):
    dataset = Dataset()
    cldf = dataset.cldf_reader()
    chains = list(cldf.iter_rows("chains.csv"))

    if args.chain:
        selected = [
            chain for chain in chains
            if chain["ID"] in args.chain or set(source_keys(chain)) & set(args.chain)
        ]
        known = {chain["ID"] for chain in chains}
        known |= {key for chain in chains for key in source_keys(chain)}
        unknown = [spec for spec in args.chain if spec not in known]
        if unknown:
            raise ValueError("no chain or source {}".format(", ".join(unknown)))
    else:
        selected = chains

    failed = []
    for chain in selected:
        original_path = dataset.raw_dir / chain["Raw_File"]
        original = structural_lines(original_path.read_text(encoding="utf-8"))
        exported = structural_lines(emit(cldf, chain["ID"]))

        if original == exported:
            args.log.info("{}: {} lines match".format(chain["ID"], len(original)))
            continue

        failed.append(chain["ID"])
        args.log.warning("{}: does not match {}".format(chain["ID"], chain["Raw_File"]))
        for line in difflib.unified_diff(
            original,
            exported,
            fromfile=chain["Raw_File"],
            tofile="{} (from CLDF)".format(chain["ID"]),
            lineterm="",
        ):
            print(line)

    return 1 if failed else 0
