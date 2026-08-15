# Migration guide

## Source repositories

| Archived repository | Retained capability | New location |
|---|---|---|
| [`auto-transpose`](https://github.com/jzjzzzzzzz/auto-transpose) | MSCZ transposition, MusicXML-to-PDF, SmartScore-to-MSCZ workflow | `music-score transpose`, `music-score convert`, `music-score recognize` |
| [`Auto-Music-Transpose`](https://github.com/jzjzzzzzzz/Auto-Music-Transpose) | Direct MSCX editing, key/TPC updates, optional PDF export | `music_score_toolkit.mscz` and `music-score transpose` |

The archived repositories keep their Git history, stars, issues, sample
assets, and original licenses. Their Python scripts are also copied under
`legacy/` as provenance snapshots; maintained code lives under `src/`.

## Command migration

### `AutoTranspose.py` or `ImportMSCX.py`

Old scripts used fixed `test.mscz` and `out.mscz` paths and prompted for keys.
Replace them with explicit arguments:

```bash
music-score transpose test.mscz out.mscz --from-key Bb --to-key C
```

Use `--export-pdf out.pdf` to retain the optional MuseScore PDF step.

### `XMLtoPDF.py`

Replace environment variables with positional paths:

```bash
music-score convert test.xml out.pdf
```

### `PDFtoMXCZ.py`

The interactive SmartScore workflow is retained under a correctly named
command:

```bash
music-score recognize test.pdf output --timeout 1800
```

For automated Audiveris optical music recognition, continue to use the
separate [`PDFtoMSCZ`](https://github.com/jzjzzzzzzz/PDFtoMSCZ) project.

## Behavior changes

- Output is written atomically instead of directly to the destination.
- Unsupported keys and malformed pitches produce actionable errors.
- Out-of-range MIDI values abort by default instead of being silently clipped.
- Optional desktop dependencies are configured through environment variables
  or discovered on common platforms.
- Machine-readable reports replace informal `print` statements.

