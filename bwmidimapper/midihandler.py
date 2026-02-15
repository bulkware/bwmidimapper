#!/usr/bin/env python

"""MIDIHandler - A class to handle MIDI processing in bwMIDIMapper."""

# Python imports
import argparse  # Parser for command-line options, arguments and subcommands
import logging  # Logging facility for Python

# Local imports
from typing import Optional, Dict

# 3rd party imports
import mido  # MIDI Objects for Python


class MIDIHandler:  # pylint: disable=R0903

    """A class to handle MIDI processing in bwMIDIMapper."""

    def __init__(self, args: argparse.Namespace, drum_map: Dict[int, int]):
        self.args = args  # Arguments
        self.drum_map = drum_map  # Drum mapping to use while processing
        self.percussion_channel = 9  # Channel 10 = percussions, 0-based index
        self.active_notes = {}  # Active notes dict to identify duplicate notes

    def _insert_meta(self, new_track: mido.MidiTrack) -> None:

        """Insert meta data in MIDIHandler."""

        # Insert user-specified tempo/time-signature metas into track 0 only
        if self.args.tempo is not None:
            new_track.append(
                mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(float(self.args.tempo)), time=0)
            )
        if self.args.time_signature is not None:
            ts = self.args.time_signature
            new_track.append(
                mido.MetaMessage("time_signature", numerator=ts[0], denominator=ts[1], time=0)
            )

    def _process_note(self, msg: mido.Message) -> Optional[mido.Message]:

        """Process MIDI notes in MIDIHandler."""

        # Duplicate-note handling
        if self.args.remove_duplicates:
            active_note = (msg.channel, msg.note)
            if msg.type == "note_on" and getattr(msg, "velocity", 0) > 0:
                if active_note in self.active_notes:
                    logging.info("Duplicate note, channel='%s', note='%s'", msg.channel, msg.note)
                    return None
                self.active_notes[active_note] = msg
            elif msg.type == "note_off":
                if active_note in self.active_notes:
                    del self.active_notes[active_note]
            elif msg.type == "note_on" and getattr(msg, "velocity", 0) == 0:
                self.active_notes.pop(active_note, None)

        # Copy message (preserve time)
        new_msg = msg.copy()

        # Map notes
        original = getattr(msg, "note", None)
        if original is not None:
            mapped = self.drum_map.get(original, None)
        else:
            mapped = None

        if mapped is not None:
            new_msg.note = mapped
            # Optionally, set percussion channel
            if self.args.force_percussion or msg.channel == self.percussion_channel:
                logging.info(
                    "Percussion channel %s is forced for note %s",
                    self.percussion_channel + 1, original
                )
                new_msg.channel = self.percussion_channel
        else:
            logging.debug("Note %s not defined in DrumMap; keeping original.", original)

        return new_msg

    def process_file(self, infile: str, outfile: str) -> None:

        """Process MIDI files in MIDIHandler."""

        # Read input MIDI file
        mid = mido.MidiFile(infile)

        # Preserve ticks per beat
        new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)

        # Process MIDI tracks
        for track_index, track in enumerate(mid.tracks):
            new_track = mido.MidiTrack()

            # Insert metas in track 0 unless preserving source metas
            if track_index == 0 and not self.args.preserve_meta:
                self._insert_meta(new_track)

            new_mid.tracks.append(new_track)

            for msg in track:
                # Process note messages
                if msg.type in ("note_on", "note_off"):
                    logging.info("Note %s", msg)
                    new_msg = self._process_note(msg)
                    if new_msg is not None:
                        new_track.append(new_msg)

                # Process meta messages
                elif msg.is_meta:
                    if self.args.preserve_meta:
                        new_track.append(msg.copy())
                    else:
                        logging.debug(
                            "Skipping meta message %s (preserve_meta=%s).",
                            msg.type, self.args.preserve_meta
                        )
                else:
                    # Other channel messages are kept unchanged
                    new_track.append(msg.copy())

            # Ensure explicit end_of_track meta is present for this new track
            if self.args.preserve_meta:
                new_track.append(mido.MetaMessage("end_of_track", time=0))

        # Save output MIDI file
        new_mid.save(outfile)
        logging.info("New MIDI file saved as: %s", outfile)
