# Contributing

## Local checks

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
ruff check src tests
pytest
```

Keep external MuseScore and SmartScore processes out of unit tests. Add a
small, redistributable fixture when a score-format bug cannot be represented
with inline MSCX XML.

## Pull requests

- Explain the musical or workflow behavior being changed.
- Add tests for transposition and archive preservation.
- Document compatibility changes in `MIGRATION.md`.
- Do not commit generated output scores or PDFs.

