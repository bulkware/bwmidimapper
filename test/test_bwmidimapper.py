"""
Test bwMIDIMapper - Unit tests for bwMIDIMapper.

Copyright © 2026 Antti-Pekka Meronen (bulkware).
This project is licensed under the GPLv3 License.
SPDX-License-Identifier: GPL-3.0-or-later

Usage:
pytest -q test_bwmidimapper.py
"""

# Python imports
import io  # Core tools for working with streams
import os  # Miscellaneous operating system interfaces

import tempfile  # Generate temporary files and directories
from pathlib import Path  # Object-oriented filesystem paths

# 3rd party imports
import mido  # MIDI Objects for Python
import pytest  # Simple powerful testing with Python

# bwMIDIMapper imports
from bwmidimapper.main import read_mapping, convert_midi


def write_sample_csv(path: Path):
    """Write a simple MIDI drum mapping CSV file."""

    with open(path, "w", newline="", encoding="utf-8") as fh:
        fh.write('"INP","OUT","AD2","GM"\n')
        fh.write('"---","---","---","--"\n')
        fh.write('"036","036","Kick","Electric Bass Drum"\n')
        fh.write('"038","040","Snare Open Hit","Electric Snare or Rimshot"\n')
        fh.write('\n')


def test_read_mapping_accepts_valid_csv(tmp_path):
    """Test reading simple MIDI drum mapping CSV file."""

    # Create a new MIDI drum mapping file
    csv_path = os.path.join(tmp_path, "mapping.csv")
    write_sample_csv(csv_path)

    # Read drum mapping file
    mapping = read_mapping(str(csv_path))

    # Check if drum mappings are valid
    assert isinstance(mapping, dict)
    assert mapping.get(36) == 36
    assert mapping.get(38) == 40

    # Check for unexpected drum mappings
    assert all(0 <= k <= 127 and 0 <= v <= 127 for k, v in mapping.items())


def create_simple_midi(path: Path):
    """Create a simple MIDI file for testing."""

    # Create a new MIDI file and a track
    outfile_midi = mido.MidiFile()
    track = mido.MidiTrack()
    outfile_midi.tracks.append(track)

    # Set tempo meta message
    track.append(
        mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0)
    )

    # Set time signature meta message
    track.append(
        mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0)
    )

    # Set some note messages
    track.append(
        mido.Message("note_on", note=36, velocity=64, time=0, channel=9)
    )
    track.append(
        mido.Message("note_off", note=36, velocity=64, time=240, channel=9)
    )
    track.append(
        mido.Message("note_on", note=38, velocity=64, time=0, channel=0)
    )
    track.append(
        mido.Message("note_off", note=38, velocity=64, time=240, channel=0)
    )

    # Save output MIDI file
    outfile_midi.save(path)

    # Return output MIDI file path
    return path


def test_convert_midi_basic_mapping(tmp_path):
    """Test converting MIDI mapping."""

    # Declare variables
    csv_path: str = os.path.join(tmp_path, "mapping.csv")  # CSV drum mapping
    infile: str = os.path.join(tmp_path, "infile.mid")  # Input MIDI file
    infile_path = Path(infile)  # Input MIDI file Path object
    outfile: str = os.path.join(tmp_path, "outfile.mid")  # Output MIDI file
    outfile_midi: None = None  # Output MIDI file data
    outfile_path = Path(outfile)  # Output MIDI file Path object
    messages: list = []  # MIDI messages

    # Generate a sample drum mapping CSV file
    write_sample_csv(csv_path)

    # Generate a sample MIDI file
    create_simple_midi(infile)

    # Read mapping from CSV file
    drum_mapping = read_mapping(csv_path)

    # Convert MIDI file with default flags
    convert_midi(
        drum_map=drum_mapping,
        infile=infile,
        outfile=outfile,
        tempo=None,
        ts=None,
        force_percussion=False,
        preserve_meta=True,
    )

    # Verify output file exists and contains expected messages
    assert outfile_path.exists()
    outfile_midi = mido.MidiFile(outfile)

    # Loop tracks from MIDI file
    for track in outfile_midi.tracks:

        # Loop messages from track
        for msg in track:

            # Skip meta messages
            if msg.is_meta:
                continue

            # Append other messages
            messages.append(msg)

    # Find messages by type/note
    note36_msgs = [m for m in messages if getattr(m, "note", None) == 36]
    note40_msgs = [m for m in messages if getattr(m, "note", None) == 40]

    # Check note message counts
    assert len(note36_msgs) >= 2
    assert len(note40_msgs) >= 2

    # Ensure channel behavior, original note 36 was on channel 9
    assert all(m.channel == 9 for m in note36_msgs)

    # Ensure channel mapped note was kept on channel 0
    assert any(m.channel == 0 for m in note40_msgs)


def test_convert_midi_force_percussion(tmp_path):
    """Test MIDI conversion parameter for forcing percussion"""

    # Declare variables
    csv_path: str = os.path.join(tmp_path, "mapping.csv")  # CSV drum mapping
    infile: str = os.path.join(tmp_path, "infile.mid")  # Input MIDI file
    infile_path = Path(infile)  # Input MIDI file Path object
    outfile: str = os.path.join(tmp_path, "outfile.mid")  # Output MIDI file
    outfile_path = Path(outfile)  # Output MIDI file Path object
    mapped_notes = [36, 40]  # Expected mapped note values
    messages: list = []  # MIDI messages

    # Generate a sample drum mapping CSV file
    write_sample_csv(csv_path)

    # Generate a sample MIDI file
    create_simple_midi(infile)

    # Convert MIDI file with "force_percussion" and "preserve_meta" enabled
    convert_midi(
        drum_map=read_mapping(csv_path),
        infile=infile,
        outfile=outfile,
        tempo=None,
        ts=None,
        force_percussion=True,
        preserve_meta=True,
    )

    # Create a new output MIDI file
    outfile_midi = mido.MidiFile(outfile)

    # Loop tracks from MIDI file
    for track in outfile_midi.tracks:

        # Loop messages from track
        for msg in track:

            # Skip meta messages
            if msg.is_meta:
                continue

            # Append other messages
            messages.append(msg)

    # All mapped messages should be on percussion channel (9)
    for msg in messages:
        if getattr(msg, "note", None) in mapped_notes:
            assert msg.channel == 9
