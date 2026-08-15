# Architecture

## Design goals

1. Keep core transposition standard-library only.
2. Never silently corrupt a score when validation can fail closed.
3. Isolate optional desktop applications behind explicit workflows.
4. Preserve source-repository behavior through real regression fixtures.

## Modules

- `keys.py` normalizes major keys and contains semitone, key-signature, and
  MuseScore TPC mappings.
- `mscz.py` performs XML transformation and atomic MSCZ repacking.
- `tools.py` discovers MuseScore/SmartScore and runs MuseScore conversion.
- `workflows.py` coordinates the manual SmartScore export loop.
- `cli.py` provides stable user-facing commands and JSON reports.

## Transformation boundary

The engine parses the MSCX entry and only changes:

- `Note/pitch`
- `Note/tpc`
- `KeySig/accidental`

Other archive members are copied with their original `ZipInfo` metadata. This
keeps images, styles, audio settings, view settings, and container metadata
outside the transformation boundary.

## Atomicity

An output archive is built in the destination directory, closed, and moved
into place with `os.replace`. Validation failures remove the temporary file and
leave any existing destination untouched.

