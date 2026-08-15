# Auto Transpose

Small Python toolkit for music-score conversion and transposition workflows around MuseScore, SmartScore, MusicXML, PDF, and MSCZ files.

## What It Does

- `AutoTranspose.py`: reads `test.mscz`, transposes notes from one key to another, writes `out.mscz`, then exports `out.pdf` through MuseScore.
- `PDFtoMXCZ.py`: launches SmartScore for manual PDF recognition, watches an output folder for MusicXML/MXL, then converts it to MSCZ with MuseScore.
- `XMLtoPDF.py`: converts a MusicXML/XML score to PDF with MuseScore.

## Requirements

Python dependencies are standard library only.

External tools:

- MuseScore 4, available on `PATH` or through `MUSESCORE_PATH`.
- SmartScore, available on `PATH` or through `SMARTSCORE_PATH` for `PDFtoMXCZ.py`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Usage

Transpose the sample score:

```bash
.venv/bin/python AutoTranspose.py
```

Convert MusicXML to PDF:

```bash
MUSICXML_FILE=test.xml PDF_FILE=out.pdf .venv/bin/python XMLtoPDF.py
```

Convert a scanned PDF through SmartScore and MuseScore:

```bash
PDF_FILE=test.pdf OUTPUT_DIR=output .venv/bin/python PDFtoMXCZ.py
```

## Notes

- Sample files such as `test.mscz`, `test.pdf`, and `test.xml` are included for local testing.
- Generated files such as `out.mscz`, `out.pdf`, and `output/` should be regenerated as needed.
- The SmartScore step requires manual recognition and correction inside SmartScore.
