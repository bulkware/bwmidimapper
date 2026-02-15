"""bwMIDIMapper - A tool to convert MIDI files between different drum mappings."""

# Avoid importing the submodule at import time
def main(*args, **kwargs):
    from .main import main as _main
    return _main(*args, **kwargs)
