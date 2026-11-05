"""S00 command entry point; no capture, order processing or data writes."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from importlib.metadata import version


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="notesync",
        description="S00 scaffold. Import, parsing and export are not implemented yet.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version('line-note-order-sync')}",
    )
    parser.parse_args(argv)
    parser.print_help()
    return 0
