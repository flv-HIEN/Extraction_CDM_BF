"""Fusionne les fichiers annuels de nominations sans modifier leur schéma."""

from __future__ import annotations

import csv
from pathlib import Path


FIELDS = [
    "document_id", "date_conseil", "civilite", "nom", "matricule",
    "emploi", "grade", "classe", "echelon", "ministere",
    "poste_nomination", "page", "extrait_exact",
]
YEARS = range(2015, 2026)
OUTPUT = Path("nominations_2015_2025.csv")


def main() -> None:
    rows: list[dict[str, str]] = []
    for year in YEARS:
        source = Path(f"nominations_{year}.csv")
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != FIELDS:
                raise ValueError(f"Colonnes inattendues dans {source}")
            rows.extend(reader)

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} lignes écrites dans {OUTPUT}")


if __name__ == "__main__":
    main()
