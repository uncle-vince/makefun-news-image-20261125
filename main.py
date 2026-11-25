#!/usr/bin/env python3
"""Verify and copy the entry image for make.fun news-image-20261125.

The entry itself is a single 1024x1024 PNG, "The World in One Image -
25 November 2026": forty dated news stories (twelve cards plus
twenty-eight briefs) across seven regions on one page.

This program is the reproducible handle on that image. It does not
trust the file by name: it recomputes the PNG's SHA-256 fingerprint,
checks the fingerprint and the exact byte size against the values
recorded below, reads the pixel dimensions straight out of the PNG
IHDR chunk, and only then copies the image to the destination the
caller asks for. A changed, truncated or swapped image fails loudly
instead of being passed on.
"""

import hashlib
import shutil
import struct
import sys
from pathlib import Path

EXPECTED_SHA256 = "81444c8fd61a71e2af5bf713c95a855f080deb7df713ece5ea3eefeafb893437"
EXPECTED_BYTES = 90042
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_ENTRY_BYTES = 1024 * 1024  # hard cap: the entry image must stay under 1 MiB


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Return (width, height) parsed from the PNG signature + IHDR."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file (bad 8-byte signature)")
    if data[12:16] != b"IHDR":
        raise ValueError("first PNG chunk is not IHDR")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def verify(path: Path) -> bytes:
    """Load *path* and check it against the recorded fingerprint."""
    data = path.read_bytes()
    if len(data) > MAX_ENTRY_BYTES:
        raise ValueError(
            f"{path.name} is {len(data)} bytes, over the 1 MiB cap "
            f"({MAX_ENTRY_BYTES} bytes)"
        )
    if len(data) != EXPECTED_BYTES:
        raise ValueError(
            f"{path.name} is {len(data)} bytes, expected {EXPECTED_BYTES}"
        )
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(
            f"{path.name} SHA-256 is {digest}, expected {EXPECTED_SHA256}"
        )
    width, height = png_dimensions(data)
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ValueError(
            f"{path.name} is {width}x{height}, "
            f"expected {EXPECTED_WIDTH}x{EXPECTED_HEIGHT}"
        )
    return data


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    destination = Path(argv[1]) if len(argv) > 1 else here / "entry_verified.png"
    if not source.is_file():
        print(f"missing entry image: {source}", file=sys.stderr)
        return 1
    try:
        verify(source)
    except ValueError as exc:
        print(f"verification failed: {exc}", file=sys.stderr)
        return 1
    shutil.copyfile(source, destination)
    print(f"ok: {source.name} matches SHA-256 {EXPECTED_SHA256}")
    print(f"copied verified image to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
