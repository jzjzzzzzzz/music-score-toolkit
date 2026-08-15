import subprocess
from pathlib import Path
import sys
import time
import os
import shutil


def check_exists(path, name):
    if not path.exists():
        print(f"Error: {name} not found at {path}")
        sys.exit(1)
    print(f"{name} found at {path}")


def find_executable(env_name, commands, mac_paths, windows_path):
    configured = os.environ.get(env_name)
    if configured:
        return Path(configured)

    for command in commands:
        found = shutil.which(command)
        if found:
            return Path(found)

    for path in mac_paths:
        candidate = Path(path)
        if candidate.exists():
            return candidate

    return Path(windows_path)


def main():
    pdf_file = Path(os.environ.get("PDF_FILE", "test.pdf"))
    output_dir = Path(os.environ.get("OUTPUT_DIR", "output"))
    smartscore_exe = find_executable(
        "SMARTSCORE_PATH",
        ("SmartScore", "smartscore"),
        (
            "/Applications/SmartScore 64 Pro.app/Contents/MacOS/SmartScore 64 Pro",
            "/Applications/SmartScore.app/Contents/MacOS/SmartScore",
        ),
        r"C:\Program Files (x86)\Musitek\SmartScore X2 Professional Edition\SmartScore_pro.exe",
    )
    musescore_exe = find_executable(
        "MUSESCORE_PATH",
        ("mscore", "musescore", "MuseScore4"),
        ("/Applications/MuseScore 4.app/Contents/MacOS/mscore",),
        r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
    )

    check_exists(pdf_file, "PDF file")
    check_exists(smartscore_exe, "SmartScore executable")
    check_exists(musescore_exe, "MuseScore executable")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nLaunching SmartScore...")
    subprocess.Popen([str(smartscore_exe), str(pdf_file)])

    print(f"""
========================================
SmartScore manual processing required
========================================
1. SmartScore has been launched with the PDF file:
   {pdf_file}

2. In SmartScore:
   - Run recognition.
   - Proofread and correct any errors.
   - Export the score as MusicXML (.mxl).

3. Save the exported file to:
   {output_dir}

4. Close SmartScore after exporting.
""")

    print("Waiting for the MusicXML/MXL file to be generated...")

    score_file = None
    while score_file is None:
        candidates = (
            list(output_dir.rglob("*.mxl"))
            + list(output_dir.rglob("*.musicxml"))
            + list(output_dir.rglob("*.xml"))
        )
        if candidates:
            score_file = max(candidates, key=lambda p: p.stat().st_mtime)
        else:
            time.sleep(5)

    print(f"Score file detected: {score_file}")

    mscz_file = output_dir / (score_file.stem + ".mscz")

    print("\nConverting to MSCZ using MuseScore...")

    try:
        subprocess.run(
            [str(musescore_exe), str(score_file), "-o", str(mscz_file)],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print("MuseScore conversion failed.")
        print(e)
        sys.exit(1)

    print("\nConversion completed successfully.")
    print(f"MSCZ file location: {mscz_file}")


if __name__ == "__main__":
    main()
