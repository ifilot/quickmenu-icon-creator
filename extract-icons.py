#!/usr/bin/env python3
"""Losslessly split QuikMenu 3.x DEF libraries and render their icons.

Usage: python3 extract-icons.py SOURCE_DIRECTORY [OUTPUT_DIRECTORY]
Requires Pillow. Source directory must contain QM_COLOR.DEF / QM_MONO.DEF.
"""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw

HEADER = bytes((31, 0, 31, 0))
RECORD_SIZE = 1032
EGA = (
    (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
    (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
    (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255),
    (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255),
)


def decode(record, mono=False):
    """BGI color planes run from most to least significant; mono uses 128 bytes."""
    image = Image.new("RGBA", (32, 32))
    for y in range(32):
        for x in range(32):
            shift = 7 - x % 8
            if mono:
                offset = y * 4 + x // 8
                color = 15 * ((record[4 + offset] >> shift) & 1)
                mask = (record[520 + offset] >> shift) & 1
            else:
                offset = y * 16 + x // 8
                color = sum(((record[4 + offset + b * 4] >> shift) & 1)
                            << (3 - b) for b in range(4))
                mask = sum(((record[520 + offset + b * 4] >> shift) & 1)
                           << (3 - b) for b in range(4))
                if mask not in (0, 15):
                    raise ValueError("Non-binary color mask")
            image.putpixel((x, y), (*EGA[color], 255 if mask else 0))
    return image


def extract(source, output):
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"palette": "Standard EGA RGB; monochrome black/white",
                "numbering": "1-based library record order", "libraries": []}
    for kind, name, extension in (("color", "QM_COLOR.DEF", "ICC"),
                                   ("mono", "QM_MONO.DEF", "ICM")):
        path = source / name
        if not path.exists():
            continue
        data = path.read_bytes()
        if not data or len(data) % RECORD_SIZE:
            raise ValueError(f"{path}: not a whole number of 1032-byte records")
        dest = output / kind
        dest.mkdir(exist_ok=True)
        count = len(data) // RECORD_SIZE
        sheet = Image.new("RGB", (800, 40 + ((count + 9) // 10) * 90), "#dddddd")
        draw = ImageDraw.Draw(sheet)
        draw.text((12, 12), f"QuikMenu 3.1 / {kind} / {count} icons", fill="black")
        records = []
        for index in range(count):
            start = index * RECORD_SIZE
            record = data[start:start + RECORD_SIZE]
            if record[:4] != HEADER or record[516:520] != HEADER:
                raise ValueError(f"{path}: invalid header at record {index + 1}")
            stem = f"{kind.upper()}{index + 1:03}"
            (dest / f"{stem}.{extension}").write_bytes(record)
            image = decode(record, mono=kind == "mono")
            image.save(dest / f"{stem}.png")
            x, y = index % 10 * 80 + 8, index // 10 * 90 + 40
            sheet.paste(image.resize((64, 64), Image.Resampling.NEAREST), (x, y),
                        image.resize((64, 64), Image.Resampling.NEAREST))
            draw.text((x, y + 67), f"{index + 1:03}", fill="black")
            records.append({"number": index + 1, "offset": start,
                            "sha256": hashlib.sha256(record).hexdigest()})
        sheet.save(output / f"{kind}-contact-sheet.png")
        # Reassembly must recover the entire source, including unused mono padding.
        assert b"".join((dest / f"{kind.upper()}{i + 1:03}.{extension}").read_bytes()
                        for i in range(count)) == data
        manifest["libraries"].append({"source": name, "count": count,
            "sha256": hashlib.sha256(data).hexdigest(), "records": records})
        print(f"{name}: {count} icons; byte-for-byte reassembly verified")
    if not manifest["libraries"]:
        raise FileNotFoundError("No QM_COLOR.DEF or QM_MONO.DEF in source directory")
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    with ZipFile(output / "quickmenu-icons.zip", "w", ZIP_DEFLATED) as archive:
        for path in sorted(output.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".icc", ".icm", ".png", ".json", ".txt"}:
                archive.write(path, path.relative_to(output))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path, nargs="?", default=Path("extracted"))
    args = parser.parse_args()
    extract(args.source, args.output)
