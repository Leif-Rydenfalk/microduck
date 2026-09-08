#!/usr/bin/env python3
"""extract_makerworld.py — reproduce reference/makerworld-3250889/files/ from the archive.

MakerWorld's zip of model 3250889 stores its entry names as UTF-8 WITH the zip
UTF-8 flag (flag_bits 0x808) — measured 2026-09-03 on the raw central directory:
entry 1's name bytes are 30 32 5f e5 b7 a6 ... = "02_左". An earlier hand-written
manifest claimed GBK; that was wrong, and this tool is the measurement. macOS
`unzip` still refuses the names ("Illegal byte sequence") under a C locale, so
extract with Python's zipfile, which honours the flag.

Usage:  python3 tools/extract_makerworld.py [archive.zip] [out_dir]
Prints one line per entry: name, bytes, sha256. Exit 1 if any entry's size
disagrees with the archive's central directory.
"""
import hashlib, os, sys, unicodedata, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ARCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    REPO, "reference", "makerworld-3250889", "archive",
    "Microduck+机器鸭结构件（仿真模型导出+·+15+分件）.zip")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(REPO, "reference", "makerworld-3250889", "files")


def main():
    z = zipfile.ZipFile(ARCH)
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    for info in z.infolist():
        name = unicodedata.normalize("NFC", info.filename)
        if "/" in name or name.startswith("."):
            print("refused entry name %r" % name, file=sys.stderr); bad += 1; continue
        data = z.read(info)
        if len(data) != info.file_size:
            print("SIZE MISMATCH %s: %d read vs %d declared" % (name, len(data), info.file_size), file=sys.stderr); bad += 1
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(data)
        print("%s %d %s utf8flag=%s" % (name, len(data), hashlib.sha256(data).hexdigest(), bool(info.flag_bits & 0x800)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
