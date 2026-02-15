#!/usr/bin/env python

"""
bwMIDIMapper - A tool to convert MIDI files between different drum mappings.

Copyright © 2026 Antti-Pekka Meronen (bulkware).
This project is licensed under the GPLv3 License.
SPDX-License-Identifier: GPL-3.0-or-later

Usage:
python bwmidimapper.py "infile.mid" "outfile.mid" --force-percussion \
    --log-level DEBUG --tempo 140 --time-signature 7/4 --remove-duplicates
"""

# Python imports
import argparse  # Parser for command-line options, arguments and subcommands
import logging  # Logging facility for Python
import sys  # System-specific parameters and functions
from importlib.resources import files  # The implementation of import
from pathlib import Path  # Object-oriented filesystem paths

# bwMIDIMapper imports
from .appconfig import AppConfig
from .midihandler import MIDIHandler


def main(argv=None):

    """A tool to convert MIDI files between different drum mappings."""

    # Declare variables
    map_file = "ad2gm.csv"
    map_path = files("bwmidimapper").joinpath("data").joinpath("ad2gm.csv")

    # Initialize AppConfig instance
    appconfig = AppConfig()

    # Initialize ArgumentParser
    parser = argparse.ArgumentParser(
        description="bwMIDIMapper - A tool to convert MIDI files between different drum mappings."
    )

    # Define arguments
    parser.add_argument("infile", type=str, help="Input MIDI file with source drum mapping.")
    parser.add_argument("outfile", type=str, help="Output MIDI file with target drum mapping.")
    parser.add_argument("--drum-map", default=map_path, type=str,
                        help=f"Drum mapping file. Default is: '{map_file}'.")
    parser.add_argument("--discard-unmapped", action="store_true",
                        help="Discard notes that are not defined in the drum map.")
    parser.add_argument("--force-percussion", action="store_true",
                        help="Force mapped notes onto General MIDI percussion channel 10.")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging verbosity level.")
    parser.add_argument("--preserve-meta", action="store_true",
                        help="Preserve tempo/time signature meta events from source file (may " +
                             "create duplicates meta events).")
    parser.add_argument("--remove-duplicates", action="store_true", help="Remove duplicate notes.")
    parser.add_argument("--tempo", default=None, type=int,
                        help="Tempo for output MIDI file, e.g. 120.")
    parser.add_argument("--time-signature", default=None, type=appconfig.time_signature,
                        help="Time signature for output MIDI file, eg. 4/4.")

    # Parse arguments
    args = parser.parse_args(argv)

    # Configure logging
    logging.basicConfig(
        datefmt="%Y-%d-%m %H:%M:%S",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=getattr(logging, args.log_level)
    )

    # Validate input file
    if not Path(args.infile).exists():
        logging.error("Input MIDI file not found: %s", args.infile)
        sys.exit(2)

    # Validate tempo
    if args.tempo is not None:
        if not 20 <= args.tempo <= 300:
            logging.error("Tempo out of range: %s. Must be 20-300 BPM.", args.tempo)
            sys.exit(2)

    # Read drum mapping
    try:
        drum_map = appconfig.read_mapping(args.drum_map)
    except Exception as exc:  # pylint: disable=W0718
        logging.exception("AppConfig failed: %s", exc)
        sys.exit(1)

    # Process MIDI data using bwMIDIHandler
    midihandler = MIDIHandler(args, drum_map)
    try:
        midihandler.process_file(args.infile, args.outfile)
    except Exception as exc:  # pylint: disable=W0718
        logging.exception("Conversion failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
