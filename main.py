#!/usr/bin/env python3
"""news-image-20261125: copy the rendered front page to /output/entry.png.

The image itself is drawn in code by compose_dense.py from spec.json and
stored in this repo as entry.png. This program copies it to the judge's
output path and verifies the copy byte-for-byte with SHA-256 so a truncated
or corrupted write can never pass silently.
"""

import hashlib
import os
import shutil
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
DESTINATION = "/output/entry.png"


MAX_BYTES = 1048576  # the bounty caps entry.png at 1 MiB


def fingerprint(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    if not os.path.exists(SOURCE):
        print("missing entry.png next to main.py", file=sys.stderr)
        return 1
    if os.path.getsize(SOURCE) > MAX_BYTES:
        print("entry.png exceeds the 1 MiB cap", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(DESTINATION), exist_ok=True)
    shutil.copyfile(SOURCE, DESTINATION)
    source_hash = fingerprint(SOURCE)
    dest_hash = fingerprint(DESTINATION)
    if source_hash != dest_hash:
        print("copy failed SHA-256 check", file=sys.stderr)
        return 1
    print("entry.png ->", DESTINATION)
    print("sha256:", dest_hash)
    print("bytes:", os.path.getsize(DESTINATION))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
