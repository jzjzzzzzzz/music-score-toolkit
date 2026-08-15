"""Key normalization and MuseScore tonal-pitch-class helpers."""

from __future__ import annotations


KEY_TO_SEMITONE = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "Fb": 4,
    "E#": 5,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
    "Cb": 11,
}

KEY_SIGNATURES = {
    "Cb": -7,
    "Gb": -6,
    "Db": -5,
    "Ab": -4,
    "Eb": -3,
    "Bb": -2,
    "F": -1,
    "C": 0,
    "G": 1,
    "D": 2,
    "A": 3,
    "E": 4,
    "B": 5,
    "F#": 6,
    "C#": 7,
}

MIDI_TO_TPC_SHARP = {
    0: 14,
    1: 21,
    2: 16,
    3: 23,
    4: 18,
    5: 13,
    6: 20,
    7: 15,
    8: 22,
    9: 17,
    10: 24,
    11: 19,
}

MIDI_TO_TPC_FLAT = {
    0: 14,
    1: 9,
    2: 16,
    3: 11,
    4: 18,
    5: 13,
    6: 8,
    7: 15,
    8: 10,
    9: 17,
    10: 12,
    11: 19,
}


class KeyNameError(ValueError):
    """Raised when a key name cannot be normalized."""


def normalize_key(value: str) -> str:
    """Normalize ASCII or Unicode major-key notation.

    Examples: ``bb`` -> ``Bb``, ``F♯`` -> ``F#``.
    """

    compact = value.strip().replace("♭", "b").replace("♯", "#")
    if not compact:
        raise KeyNameError("Key name cannot be empty.")
    normalized = compact[0].upper() + compact[1:].replace("B", "b")
    if normalized not in KEY_TO_SEMITONE:
        choices = ", ".join(KEY_SIGNATURES)
        raise KeyNameError(f"Unsupported major key {value!r}. Expected one of: {choices}.")
    return normalized


def calculate_shift(from_key: str, to_key: str) -> int:
    """Return the nearest signed semitone shift between two major keys."""

    source = normalize_key(from_key)
    target = normalize_key(to_key)
    shift = KEY_TO_SEMITONE[target] - KEY_TO_SEMITONE[source]
    if shift > 6:
        shift -= 12
    elif shift < -6:
        shift += 12
    return shift


def spelling_for_key(key: str) -> str:
    """Return the default accidental family for a target key."""

    normalized = normalize_key(key)
    return "flat" if "b" in normalized or KEY_SIGNATURES.get(normalized, 0) < 0 else "sharp"


def tpc_for_pitch(midi_pitch: int, spelling: str) -> int:
    """Map a MIDI pitch to a MuseScore tonal pitch class."""

    mapping = MIDI_TO_TPC_FLAT if spelling == "flat" else MIDI_TO_TPC_SHARP
    return mapping[midi_pitch % 12]

