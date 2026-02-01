# bwMIDIMapper

A tool to convert MIDI files between different drum mappings.


## Foreword

<p>I made this package because I wasn't able to import my drum MIDI files to
TuxGuitar without some processing. I wanted to make notation and tablatures for
our songs so my fellow bandmates could learn our songs that way. I wanted to
include our drum tracks in these notation and tablature files since we had
those in MIDI format anyway. So I thought I could just export those from my DAW
and import them to TuxGuitar. The first problem was that the note numbers I had
used in my DAW were not the same as defined in General MIDI standard, so I had
to make some kind of conversion for those. I asked around about this kind of
MIDI conversion and while I had some luck, I didn't succeed:<br/>
[TuxGuitar - Drum (re)mapping #930](https://github.com/helge17/tuxguitar/discussions/930)<br />
[Ardour - Exporting MIDI drums as General MIDI](https://discourse.ardour.org/t/exporting-midi-drums-as-general-midi/112486)</p>

<p>At first I tried to use Ardour's LUA plugin called "MIDI Note Mapper":<br/>
[Ardour - MIDI Note Mapper](https://github.com/Ardour/ardour/blob/master/share/scripts/midi_remap.lua)</p>

<p>And then I tried other plugins as well, but you get the idea. I also tried
to create my own LUA plugin for this purpose, but all of those had the same
fundamental problem. Ardour's export does not seem use those plugins when you
export a MIDI file. Also, even if I was able to remap MIDI notes to other MIDI
notes, Ardour does not seem to export channel, tempo or time signature. Or
maybe you could configure the channel for notes, but I thought the track's
channel setting would be used in exports but it doesn't seem to have any
effect. The main problem for me is the channel, because TuxGuitar seems to
import MIDI files differently when the MIDI channel is 10 (percussion channel).
</p>

<p>Se here we are. I hope this package helps someone else, too. If not, feel
free to leave an issue, pull request or drop an email =)</p>

## Basic usage

Here is one of the commands I use to run this:
```
python3 bwmidimapper.py "infile.mid" "outfile.mid" --force-percussion \
    --tempo 140 --time-signature 7/4 --log-level DEBUG
```

The only required parameters are `infile` and `outfile`, but if your DAW
exports MIDI files like mine, the other parameters are needed as well. All the
parameters are described in detail below.


## Parameters

| Parameter            | Description                                                                                    |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| `infile`             | Input MIDI file with source drum mapping.                                                      |
| `outfile`            | Output MIDI file with target drum mapping.                                                     |
| `--tempo`            | (Optional) Tempo for output MIDI file, e.g. 140.                                               |
| `--time-signature`   | (Optional) Time signature for output MIDI file, eg. 7/4.                                       |
| `--drum-map`         | (Optional) Drum mapping file. Default is: 'ad2gm.csv'.                                         |
| `--force-percussion` | (Optional) Force mapped notes onto General MIDI percussion channel 10.                         |
| `--preserve-meta`    | (Optional) Preserve tempo/time signature meta events from source file (may create duplicates). |
| `--log-level`        | (Optional) Logging verbosity level.                                                            |


## Drum mapping CSV files

The CSV file format the main script uses is pretty flexible. You can look at
the file `ad2gm.csv` which comes with this package for a concrete example. Here
is a list of things to take into consideration:

- Header rows can be used because those are discarded in the mapping process.
- Only rows that have integers in the first two columns are used.
- You can create "placeholder" mappings by leaving out the output note number.
- Only the first two columns are used so feel free to include your own columns.
- Use UTF-8 encoding for your MIDI mapping CSV file.
- Use double quotes as a text separator and comma as a field delimiter:
```
"001","004"
"002","005"
"003","006"
```


## Running on Linux

Open your terminal application and run the following commands.

### Creating a virtual environment where you can run the package's main script
`python3 -m venv bwmidiremapper`

### Entering the virtual environment directory
`cd bwmidiremapper`

### Activating the virtual environment
`source bin/activate`

### Updating the Python's package manager (pip)
`pip install --upgrade pip`

### Installing dependencies
`pip install mido pycodestyle pytest setuptools`

### Creating and entering a directory for the package
```
cd ~
mkdir scripts
cd scripts
```

### Downloading the source
`git clone https://github.com/bulkware/bwmidiremapper.git`

### Entering package directory
`cd bwmidiremapper`

### Running the package's main script
`python3 bwmidiremapper.py`
