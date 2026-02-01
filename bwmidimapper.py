#!/usr/bin/env python

"""
bwMIDIMapper

A tool to convert MIDI files between different drum mappings.

Copyright © 2026 Antti-Pekka Meronen (bulkware).
This project is licensed under the GPLv3 License.
SPDX-License-Identifier: GPL-3.0-or-later

Usage:
python bwmidimapper.py "infile.mid" "outfile.mid" --force-percussion \
    --log-level DEBUG --tempo 140 --time-signature 7/4
"""

# Python imports
import argparse  # Parser for command-line options, arguments and subcommands
import csv  # CSV File Reading and Writing
import logging  # Logging facility for Python
import re  # Regular expression operations
import sys  # System-specific parameters and functions
from typing import Dict, Optional, Tuple  # Support for type hints
from pathlib import Path  # Object-oriented filesystem paths

# 3rd party imports
import mido  # MIDI Objects for Python


def time_signature(ts: str) -> Tuple[int, int]:

    """
    Parse and validate a time signature string like "4/4".

    :param ts: Time signature for output MIDI file, eg. 4/4.
    :type ts: str

    :return: Tuple[int, int]
    """

    # Declare variables
    beat_units = [1, 2, 4, 8, 16, 32]  # Valid beat units
    ts_regex = re.compile(r"^(\d+)\/(\d+)$")  # RegEx for time signatures

    # Match time signature using RegEx
    ts_match = ts_regex.match(ts)

    # Check RegEx match
    if not ts_match:
        raise argparse.ArgumentTypeError(
            f"Invalid time signature: '{ts}'. Expected format: N/D (e.g. 4/4)"
        )

    # Grab beats and units from RegEx match
    beats, unit = int(ts_match.group(1)), int(ts_match.group(2))

    # Validate beats and unit
    if beats < 1:
        raise argparse.ArgumentTypeError(
            f"Invalid beats-per-bar: {beats}. Beats-per-bar must be >= 1."
        )
    if unit not in beat_units:
        raise argparse.ArgumentTypeError(
            f"Invalid beat unit: {unit}. Allowed beat units: {beat_units}."
        )

    # Return beats and unit
    return (beats, unit)


# Drum mapping
def read_mapping(mapping_file: str) -> Dict[int, int]:

    """Reads drum mapping from a CSV file.

    :param mapping_file: Input CSV file containing drum mapping.
    :type mapping_file: str

    :return: Dict[int, int]
    """

    # Declare variables
    drum_map: Dict[int, int] = {}
    note_regex = re.compile(r"^\d{1,3}$")  # Allow 0-127 numeric strings

    # Read drum mapping from CSV file
    with open(mapping_file, mode="r", newline="") as fh:

        # Open CSV file
        csv_file = csv.reader(fh, delimiter=",", quotechar='"')

        # Loop each line
        for line in csv_file:

            # Skip empty lines
            if not line:
                continue

            # Support files with headers by skipping non-numeric first cell
            input_note_raw = line[0].strip() if len(line) >= 1 else ""
            output_note_raw = line[1].strip() if len(line) >= 2 else ""

            # Skip mappings with empty input or output notes
            if not input_note_raw or not output_note_raw:
                continue

            # Check if input and output notes match 1-3 digit number
            if not note_regex.match(input_note_raw) or \
               not note_regex.match(output_note_raw):

                # Skip header rows or malformed rows
                continue

            # Convert input and output notes to integer values
            try:
                input_note = int(input_note_raw)
                output_note = int(output_note_raw)
            except ValueError:
                continue

            # Validate note numbers (0-127)
            if not 0 <= input_note <= 127:
                continue
            if not 0 <= output_note <= 127:
                continue

            # Add mapping to drum map
            drum_map[input_note] = output_note

    # Return drum map
    return drum_map


def convert_midi(drum_map: Dict[int, int], infile: str, outfile: str,
                 tempo: Optional[int] = None,
                 ts: Optional[Tuple[int, int]] = None,
                 force_percussion: bool = False,
                 preserve_meta: bool = False) -> None:

    """
    A tool to convert MIDI files between different drum mappings.

    :param drum_map: Drum mapping dictionary to use for conversion.
    :type drum_map: Dict[int, int]
    :param infile: Input MIDI file with source drum mapping.
    :type infile: str
    :param outfile: Output MIDI file with target drum mapping.
    :type outfile: str
    :param tempo: Tempo for output MIDI file.
    :type tempo: Optional[int]
    :param ts: Time signature for output MIDI file.
    :type ts: Optional[Tuple[int, int]]
    :param force_percussion: If True, mapped notes are forced to channel 9.
    :type force_percussion: bool
    :param preserve_meta: If True, keep original tempo/time_signature metas.
    :type preserve_meta: bool

    :return: None
    """

    # Declare variables
    percussion_channel = 9  # MIDI channel 10 = percussions, 0-based index

    # Read input MIDI file
    mid = mido.MidiFile(infile)

    # Preserve ticks per beat
    new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)

    # Process MIDI tracks
    for track_index, track in enumerate(mid.tracks):

        # Create new MIDI track for output MIDI file
        new_track = mido.MidiTrack()

        # Insert user-specified tempo/time-signature metas into track 0 only,
        # unless preserve_meta is True.
        if track_index == 0 and not preserve_meta:

            # Set tempo if specified
            if tempo is not None:
                new_track.append(
                    mido.MetaMessage(
                        "set_tempo",
                        tempo=mido.bpm2tempo(float(tempo)),
                        time=0
                    )
                )

            # Set time signature if specified
            if ts is not None:
                new_track.append(
                    mido.MetaMessage(
                        "time_signature",
                        numerator=ts[0],
                        denominator=ts[1],
                        time=0
                    )
                )

        # Append new track to output MIDI file
        new_mid.tracks.append(new_track)

        # Process track's MIDI messages
        for msg in track:

            # Process note numbers for note_on/note_off
            if msg.type in ("note_on", "note_off"):

                # Reset loop variables
                mapped = None  # Mapped MIDI note number
                new_msg = None  # New MIDI message
                original = None  # (Possible) original MIDI note number

                # Copy message (preserves time)
                new_msg = msg.copy()

                # Retrieve (possible) mapped MIDI note number
                original = getattr(msg, "note", None)
                if original is not None:
                    mapped: Optional[int] = drum_map.get(original, None)

                # If mapping exists, set mapped note
                if mapped is not None:
                    new_msg.note = mapped

                    # Optionally, set percussion channel
                    if force_percussion or msg.channel == percussion_channel:
                        new_msg.channel = percussion_channel
                else:
                    # No mapping: keep original note and channel
                    logging.debug(
                        "Note %s not defined in DrumMap; keeping original.",
                        original
                    )

                # Append new message
                new_track.append(new_msg)

            # Process meta messages
            elif msg.is_meta:

                # Skip meta messages to avoid duplicates unless track has none
                # and user didn't set meta messages
                if preserve_meta:
                    new_track.append(msg.copy())
                else:
                    logging.debug(
                        "Skipping meta message %s (preserve_meta=%s).",
                        msg.type, preserve_meta
                    )
            else:
                # Other channel messages are kept unchanged
                new_track.append(msg.copy())

        # Ensure explicit end_of_track meta is present for this new track
        if preserve_meta:
            new_track.append(mido.MetaMessage("end_of_track", time=0))

    # Save output MIDI file
    new_mid.save(outfile)
    logging.info("New MIDI file saved as: %s", outfile)


def main(argv=None):

    # Declare constants
    SCRIPTS_PATH = os.path.dirname(os.path.realpath(__file__))  # Scripts path
    WORKING_PATH = os.getcwd()  # Working path
    MAPPING_FILE = os.path.join(SCRIPTS_PATH, "ad2gm.csv")  # Mapping file path

    # Initialize ArgumentParser
    parser = argparse.ArgumentParser(
        description="A tool to convert MIDI files between different drum "
                    "mappings."
    )

    # Define arguments
    parser.add_argument(
        "infile", type=str,
        help="Input MIDI file with source drum mapping."
    )
    parser.add_argument(
        "outfile", type=str,
        help="Output MIDI file with target drum mapping."
    )
    parser.add_argument(
        "--tempo", default=None, type=int,
        help="Tempo for output MIDI file, e.g. 120."
    )
    parser.add_argument(
        "--time-signature", default=None, type=time_signature,
        help="Time signature for output MIDI file, eg. 4/4."
    )
    parser.add_argument(
        "--drum-map", default=MAPPING_FILE, type=str,
        help=f"Drum mapping file. Default is: '{MAPPING_FILE}'."
    )
    parser.add_argument(
        "--force-percussion", action="store_true",
        help="Force mapped notes onto General MIDI percussion channel 10."
    )
    parser.add_argument(
        "--preserve-meta", action="store_true",
        help="Preserve tempo/time signature meta events from source file "
             "(may create duplicates)."
    )
    parser.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity level."
    )

    # Parse arguments
    args = parser.parse_args()

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
            logging.error(
              "Tempo out of range: %s. Must be 20-300 BPM.", args.tempo
            )
            sys.exit(2)

    # Read drum mapping from a CSV file
    try:
        drum_map = read_mapping(args.drum_map)
    except FileNotFoundError:
        logging.error("Drum mapping file not found: %s", args.drum_map)
        sys.exit(2)

    # Convert MIDI file
    try:
        convert_midi(
            drum_map,
            args.infile,
            args.outfile,
            args.tempo,
            args.time_signature,
            force_percussion=args.force_percussion,
            preserve_meta=args.preserve_meta
        )
    except Exception as exc:
        logging.exception("Conversion failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
