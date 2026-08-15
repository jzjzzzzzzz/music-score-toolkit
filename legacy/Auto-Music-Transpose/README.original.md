Auto Transpose (MuseScore MSCZ Tool)
A Python tool that automatically transposes MuseScore .mscz files while preserving musical structure, including rhythm, rests, chords, and notation spelling.
It also exports the result directly to MusicXML / MSCZ and PDF via MuseScore.
Features

Automatic key-based transposition
Supports MuseScore .mscz files
Preserves rhythm, rests, ties, and structure
Avoids double sharps / double flats (enharmonic-aware spelling)
Keeps original note spelling preference (sharp/flat context)
Updates key signature automatically
Optional PDF export via MuseScore CLI

Requirements

Python 3.8+
MuseScore 4 installed

Set MuseScore path in code:

MUSESCORE_PATH = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"

Usage
1. Clone the repo

git clone https://github.com/jzjzzzzzzz/importMSCX.git

cd auto-transpose

2. Run the script

python importMSCX.py

3. Input

From key: Bb
To key: C

4. Output

out.mscz → transposed score
out.pdf → exported sheet music (optional)

How It Works

The tool directly modifies the internal .mscx file inside .mscz:

Extract .mscx from .mscz
Parse all note elements
Apply semitone shift based on key difference
Update:
MIDI pitch (<pitch>)
TPC (note spelling)
Key signature
Repack back into .mscz
Export via MuseScore (optional PDF)

Notes

This tool prioritizes correct pitch over engraving perfection.
Works best with MuseScore-generated .mscz files.
Complex notation (microtonal / special symbols) may require extra handling.

Project Structure

auto-transpose/
├── transpose.py
├── test.mscz
└── out.mscz

Future Improvements

GUI interface (drag & drop support)
Batch transposition
Automatic instrument detection (Bb / Eb instruments)
Better enharmonic decision system
Direct MuseScore plugin version

License

MIT License

Copyright (c) 2026 jzjzzzzzz
