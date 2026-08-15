import subprocess
from pathlib import Path
import sys
import os
import shutil


def find_musescore():
    configured = os.environ.get("MUSESCORE_PATH")
    if configured:
        return Path(configured)

    for command in ("mscore", "musescore", "MuseScore4"):
        found = shutil.which(command)
        if found:
            return Path(found)

    mac_app = Path("/Applications/MuseScore 4.app/Contents/MacOS/mscore")
    if mac_app.exists():
        return mac_app

    return Path(r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe")


def main():
    musicxml_file = Path(os.environ.get("MUSICXML_FILE", "test.xml"))
    pdf_file = Path(os.environ.get("PDF_FILE", musicxml_file.with_suffix(".pdf")))
    musescore_exe = find_musescore()

    if not musicxml_file.exists():
        print(f"MusicXML file not found: {musicxml_file}")
        sys.exit(1)

    if not musescore_exe.exists():
        print(f"MuseScore executable not found: {musescore_exe}")
        print("Set MUSESCORE_PATH to the MuseScore executable path.")
        sys.exit(1)

    subprocess.run(
        [str(musescore_exe), str(musicxml_file), "-o", str(pdf_file)],
        check=True,
    )

    print(f"PDF successfully created at: {pdf_file}")


if __name__ == "__main__":
    main()
