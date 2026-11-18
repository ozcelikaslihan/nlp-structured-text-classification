"""Download the public TTC-4900 CSV without using any cloud LLM API."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/savasy/TurkishTextClassification/master/TTC4900.csv"
DESTINATION = Path("data/raw/TTC4900.csv")


def main() -> None:
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {URL}")
    with urllib.request.urlopen(URL, timeout=120) as response:
        data = response.read()
    DESTINATION.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    print(f"Saved {len(data):,} bytes to {DESTINATION}")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()

