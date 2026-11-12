from pathlib import Path
import csv
RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "extraction_evaluation"
CORPUS = RACINE / "donnees" / "comptes_rendus" / "total"
def charger_lot(nom):
    if nom not in {"developpement_12", "evaluation_30", "reste"}:
        raise ValueError(nom)
    with (DOSSIER / "lots" / (nom + ".csv")).open(encoding="utf-8-sig", newline="") as f:
        return [RACINE / row["pdf_source"] for row in csv.DictReader(f)]
