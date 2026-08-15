# Music Score Toolkit

[![CI](https://github.com/jzjzzzzzzz/music-score-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/jzjzzzzzzz/music-score-toolkit/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)

A safe, testable Python toolkit for transposing MuseScore MSCZ files and
running explicit MuseScore/SmartScore conversion workflows.

This repository consolidates the maintained functionality of
[`auto-transpose`](https://github.com/jzjzzzzzzz/auto-transpose) and
[`Auto-Music-Transpose`](https://github.com/jzjzzzzzzz/Auto-Music-Transpose).
The original repositories remain available as read-only archives.

## Why this repository exists

The original prototypes demonstrated direct MSCX editing and desktop score
conversion. This consolidation keeps those workflows while adding a package
boundary, a real CLI, atomic output writes, actionable dependency discovery,
and regression tests against both original MSCZ samples.

## Features

- Transpose every `.mscx` entry inside a MuseScore `.mscz` archive.
- Update MIDI pitch, MuseScore TPC spelling, and conventional key signatures.
- Preserve chords, rests, ties, rhythm, lyrics, layout files, thumbnails, and
  other archive members.
- Abort before writing output when a transposition exceeds MIDI `0..127`.
- Convert MusicXML, MSCZ, and other MuseScore-supported inputs through the
  MuseScore 4 CLI.
- Launch SmartScore for manual PDF recognition, wait for MusicXML export, and
  complete the conversion to MSCZ.
- Run without third-party Python packages for core transposition.

## Installation

```bash
git clone https://github.com/jzjzzzzzzz/music-score-toolkit.git
cd music-score-toolkit
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

On Windows, activate with `.venv\Scripts\activate`.

## Quick start

Transpose a B-flat score to C:

```bash
music-score transpose input.mscz output.mscz \
  --from-key Bb \
  --to-key C
```

The command prints a machine-readable report:

```json
{
  "from_key": "Bb",
  "to_key": "C",
  "semitone_shift": 2,
  "notes_changed": 184,
  "key_signatures_changed": 1,
  "score_entries_changed": 1
}
```

Transpose and export a PDF through MuseScore:

```bash
music-score transpose input.mscz output.mscz \
  --from-key Bb --to-key C --export-pdf output.pdf
```

Convert MusicXML to PDF or MSCZ:

```bash
music-score convert score.musicxml score.pdf
music-score convert score.musicxml score.mscz
```

Run the retained SmartScore-assisted recognition workflow:

```bash
music-score recognize scan.pdf ./recognized --timeout 1800
```

SmartScore recognition remains a manual proofreading step. Save the exported
`.mxl`, `.musicxml`, or `.xml` file in the requested output directory; the
toolkit detects it and asks MuseScore to create the final MSCZ file.

## Desktop dependencies

Core MSCZ transposition uses only the Python standard library. Conversion and
recognition commands discover optional desktop tools in this order:

1. `MUSESCORE_PATH` or `SMARTSCORE_PATH`
2. an executable on `PATH`
3. common macOS and Windows installation locations

Example:

```bash
export MUSESCORE_PATH="/Applications/MuseScore 4.app/Contents/MacOS/mscore"
```

## Python API

```python
from music_score_toolkit import transpose_mscz

report = transpose_mscz(
    "input.mscz",
    "output.mscz",
    from_key="Bb",
    to_key="C",
)
print(report.notes_changed)
```

## Reliability boundaries

- Major keys in conventional sharp/flat notation are supported.
- The target key determines default enharmonic spelling; explicit source-note
  flat/sharp preferences are retained when present.
- The toolkit changes score semantics conservatively, but it is not an
  engraving engine. Review complex notation in MuseScore after conversion.
- Microtonal notation, custom key signatures, percussion staves, and unusual
  MuseScore extensions are not normalized automatically.
- PDF optical music recognition is delegated to SmartScore. For a dedicated
  Audiveris workflow, see
  [`PDFtoMSCZ`](https://github.com/jzjzzzzzzz/PDFtoMSCZ).

## Development

```bash
python -m pip install -e '.[dev]'
ruff check src tests
pytest
```

Tests include generated XML cases and both MSCZ files from the source
repositories. External desktop applications are isolated from unit tests.

## Repository map

```text
src/music_score_toolkit/   maintained package
tests/                     unit and source-fixture regression tests
legacy/                    original script snapshots for provenance
docs/                      architecture and maintenance documentation
MIGRATION.md               old-command migration guide
```

## Project status

Active consolidation release. New issues and changes belong in this
repository; the two source repositories are retained as archived historical
records.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). Original MIT
and Apache-2.0 source provenance is documented in [MIGRATION.md](MIGRATION.md).

