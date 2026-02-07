#!/usr/bin/env python

"""bwConfigHandler - A class to handle configurations in bwMIDIMapper."""

# Python imports
import argparse  # Parser for command-line options, arguments and subcommands
import csv  # CSV File Reading and Writing
import re  # Regular expression operations

# Local imports
from typing import Tuple, Dict


class AppConfig:

    """A class to handle configurations in bwMIDIMapper."""

    def __init__(self):
        pass

    def time_signature(self, ts: str) -> Tuple[int, int]:

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
    def read_mapping(self, mapping_file: str) -> Dict[int, int]:

        """Reads drum mapping from a CSV file.

        :param mapping_file: Input CSV file containing drum mapping.
        :type mapping_file: str

        :return: Dict[int, int]
        """

        # Declare variables
        drum_map: Dict[int, int] = {}
        note_regex = re.compile(r"^\d{1,3}$")  # Allow 0-127 numeric strings

        # Read drum mapping from CSV file
        with open(mapping_file, encoding="UTF-8", mode="r", newline="") as fh:

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
                if not note_regex.match(input_note_raw) or not note_regex.match(output_note_raw):

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
