import zipfile
import xml.etree.ElementTree as ET
import subprocess
import os

MUSESCORE_PATH = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"


# Key to semitone mapping

KEY_TO_SEMITONE = {
    "C": 0, "G": 7, "D": 2, "A": 9, "E": 4, "B": 11,
    "F#": 6, "C#": 1, "F": 5, "Bb": 10, "Eb": 3,
    "Ab": 8, "Db": 1, "Gb": 6, "Cb": 11
}


# Key signature mapping

KEYSIG_MAP = {
    "Cb": -7, "Gb": -6, "Db": -5, "Ab": -4,
    "Eb": -3, "Bb": -2, "F": -1, "C": 0,
    "G": 1, "D": 2, "A": 3, "E": 4,
    "B": 5, "F#": 6, "C#": 7
}


# Calculate transposition shift

def calculate_shift(from_key, to_key):
    shift = KEY_TO_SEMITONE[to_key] - KEY_TO_SEMITONE[from_key]

    if shift > 6:
        shift -= 12
    elif shift < -6:
        shift += 12

    return shift


# Detect spelling preference from original note

def get_spelling_preference(note):
    acc = note.find("accidental")
    if acc is None or acc.text is None:
        return "auto"

    if "sharp" in acc.text:
        return "sharp"
    if "flat" in acc.text:
        return "flat"

    return "auto"


# MIDI to TPC mapping (sharp / flat aware)

MIDI_TO_TPC_SHARP = {
    0: 14, 1: 21, 2: 16, 3: 23, 4: 18, 5: 13,
    6: 20, 7: 15, 8: 22, 9: 17, 10: 24, 11: 19
}

MIDI_TO_TPC_FLAT = {
    0: 14, 1: 9, 2: 16, 3: 11, 4: 18, 5: 13,
    6: 8, 7: 15, 8: 10, 9: 17, 10: 12, 11: 19
}


# Convert MIDI pitch to TPC with spelling preference

def get_tpc(midi_pitch, pref):
    pc = midi_pitch % 12

    if pref == "flat":
        return MIDI_TO_TPC_FLAT[pc]
    if pref == "sharp":
        return MIDI_TO_TPC_SHARP[pc]

    return MIDI_TO_TPC_SHARP[pc]


# Transpose MSCX content

def transpose_mscx(mscx, from_key, to_key):
    shift = calculate_shift(from_key, to_key)
    print("Shift =", shift)

    root = ET.fromstring(mscx)
    count = 0

    for note in root.iter("Note"):
        pitch = note.find("pitch")
        if pitch is None or not pitch.text:
            continue

        old_pitch = int(pitch.text)
        new_pitch = max(0, min(127, old_pitch + shift))
        pitch.text = str(new_pitch)

        pref = get_spelling_preference(note)

        tpc = note.find("tpc")
        new_tpc = get_tpc(new_pitch, pref)

        if tpc is None:
            ET.SubElement(note, "tpc").text = str(new_tpc)
        else:
            tpc.text = str(new_tpc)

        count += 1

    # Update key signature
    for ks in root.iter("KeySig"):
        acc = ks.find("accidental")
        if acc is not None and to_key in KEYSIG_MAP:
            acc.text = str(KEYSIG_MAP[to_key])

    print("Notes:", count)

    return ET.tostring(root, encoding="utf-8").decode("utf-8")


# Repack MSCZ file

def repack(original, new_mscx, output):
    with zipfile.ZipFile(original) as zin:
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zout:
            for i in zin.infolist():
                if i.filename.endswith(".mscx"):
                    zout.writestr(i.filename, new_mscx)
                else:
                    zout.writestr(i, zin.read(i.filename))


# Export PDF using MuseScore

def export_pdf(mscz_file):
    pdf_file = mscz_file.replace(".mscz", ".pdf")

    subprocess.run([
        MUSESCORE_PATH,
        mscz_file,
        "-o",
        pdf_file
    ])

    print("PDF:", pdf_file)


# Main

def main():
    inp = "test.mscz"
    out = "out.mscz"

    from_key = input("From key: ")
    to_key = input("To key: ")

    with zipfile.ZipFile(inp) as z:
        mscx = [f for f in z.namelist() if f.endswith(".mscx")][0]
        content = z.read(mscx).decode()

    new = transpose_mscx(content, from_key, to_key)

    repack(inp, new, out)

    export_pdf(out)

    print("DONE")

if __name__ == "__main__":
    main()