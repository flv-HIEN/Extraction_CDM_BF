"""Importer un CSV de revue dans le traitement existant, sans perdre les décisions.

python3 appliquer_decisions_revue.py CHEMIN_DU_CSV --recalculer
Les contradictions avec une décision existante exigent --remplacer.
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fiabiliser_nominations import read_csv, run, write_csv

ROOT = Path(__file__).resolve().parent
FIELDS = ["id_ligne_source", "id_personne_valide", "justification", "reference_documentaire"]


def validate(records, known, label):
    seen = set()
    for row in records:
        if any(not row.get(k, "").strip() for k in FIELDS):
            raise ValueError(f"{label} : décision incomplète")
        line = row["id_ligne_source"]
        if line not in known:
            raise ValueError(f"{label} : ligne absente du corpus courant : {line}")
        if line in seen:
            raise ValueError(f"{label} : décision dupliquée pour {line}")
        seen.add(line)


def import_decisions(csv_path, folder, replace=False):
    annotated = folder / "nominations_annotees.csv"
    target = folder / "dictionnaires" / "decisions_identites.csv"
    if not annotated.exists():
        raise FileNotFoundError("Générer nominations_annotees.csv avant d'importer les décisions.")
    known = {r["id_ligne_source"] for r in read_csv(annotated)}
    # Accepte aussi un CSV ouvert puis enregistré avec le séparateur Excel français.
    text = csv_path.read_text(encoding="utf-8-sig")
    header = text.splitlines()[0] if text else ""
    incoming = list(csv.DictReader(io.StringIO(text), delimiter="," if "," in header else ";"))
    if not incoming:
        raise ValueError("Le CSV de décisions ne contient aucune décision.")
    annotations = read_csv(annotated)
    sans_matricule = {r["id_ligne_source"] for r in annotations
                     if "matricule" in r and not r.get("matricule", "").strip()}
    ids_sans_matricule = {r.get("id_personne") for r in annotations
                         if r["id_ligne_source"] in sans_matricule}
    if any(r.get("id_ligne_source") in sans_matricule or r.get("id_personne_valide") in ids_sans_matricule
           for r in incoming):
        raise ValueError("Rattachement interdit : les lignes sans matricule restent des personnes distinctes.")
    previous = read_csv(target) if target.exists() else []
    validate(incoming, known, "Import")
    validate(previous, known, "Décisions existantes")
    merged = {r["id_ligne_source"]: {k: r[k] for k in FIELDS} for r in previous}
    conflicts = [r["id_ligne_source"] for r in incoming if r["id_ligne_source"] in merged
                 and any(merged[r["id_ligne_source"]][k] != r[k] for k in FIELDS)]
    if conflicts and not replace:
        raise ValueError(f"{len(conflicts)} décisions diffèrent des décisions existantes. Examiner le CSV puis ajouter --remplacer pour les remplacer explicitement.")
    for row in incoming:
        merged[row["id_ligne_source"]] = {k: row[k] for k in FIELDS}
    target.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if target.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = target.with_name(f"decisions_identites.avant_import_{stamp}.csv")
        backup.write_bytes(target.read_bytes())
    descriptor, tmp = tempfile.mkstemp(dir=target.parent, suffix=".tmp", prefix="decisions_")
    os.close(descriptor)
    try:
        write_csv(Path(tmp), [merged[k] for k in sorted(merged)], FIELDS)
        os.replace(tmp, target)
    finally:
        Path(tmp).unlink(missing_ok=True)
    return {"importees": len(incoming), "total": len(merged), "remplacees": len(conflicts), "fichier": str(target), "sauvegarde": str(backup) if backup else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="CSV exporté depuis l'application")
    parser.add_argument("--dossier", type=Path, default=ROOT / "fiabilisation")
    parser.add_argument("--remplacer", action="store_true")
    parser.add_argument("--recalculer", action="store_true")
    args = parser.parse_args()
    result = import_decisions(args.csv, args.dossier, args.remplacer)
    print(f"{result['importees']} décisions importées ; {result['total']} décisions conservées au total.")
    print(f"Fichier : {result['fichier']}")
    if result["sauvegarde"]:
        print(f"Sauvegarde précédente : {result['sauvegarde']}")
    if args.recalculer:
        summary = run(ROOT.parent / "extraction_evaluation" / "nominations_2015_2025.csv", args.dossier)
        print(f"Traitement recalculé : {summary['nombre_lignes_trajectoires_strictes']} lignes éligibles aux trajectoires strictes.")
        print("Pour actualiser les fiches : node revue_identites/preparer_revue.cjs")


if __name__ == "__main__":
    main()
