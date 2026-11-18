"""Inspect TTC-4900 encoding, delimiter, headers, and category counts."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

PATH = Path("data/raw/TTC4900.csv")


def main() -> None:
    if not PATH.exists():
        raise SystemExit("Run scripts/download_dataset.py first.")
    for encoding in ("utf-8-sig", "utf-8", "cp1254", "latin-1"):
        try:
            sample = PATH.read_text(encoding=encoding)[:8192]
            break
        except UnicodeDecodeError:
            continue
    else:
        raise SystemExit("Could not decode dataset.")
    dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    with PATH.open(encoding=encoding, newline="") as handle:
        rows = list(csv.reader(handle, dialect))
    print(f"encoding={encoding!r}, delimiter={dialect.delimiter!r}, rows={len(rows)}")
    print(f"first row={rows[0]}")
    for column in range(min(3, len(rows[0]))):
        counts = Counter(row[column].strip() for row in rows[1:] if len(row) > column)
        print(f"column {column} top values={counts.most_common(10)}")


if __name__ == "__main__":
    main()
