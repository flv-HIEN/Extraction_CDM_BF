"""Consolide les extractions existantes ; ne lance aucune extraction PDF."""
import csv
from pathlib import Path
from datetime import datetime, timezone
import shutil

BASE = Path(__file__).resolve().parent
LOTS = ('developpement_12', 'evaluation_30', 'reste')

def lire(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

def consolider():
    rows, seen, columns = [], set(), None
    for lot in LOTS:
        _, selected = lire(BASE / 'lots' / f'{lot}.csv')
        ids = {r['document_id'] for r in selected}
        if ids & seen:
            raise ValueError(f'Documents partagés entre lots : {lot}')
        seen.update(ids)
        fields, data = lire(BASE / 'evaluation' / f'extractions_pipeline_{lot}.csv')
        _, manifest = lire(BASE / 'evaluation' / f'extractions_pipeline_{lot}_manifeste.csv')
        if len(manifest) != len(ids) or {r['document_id'] for r in manifest} != ids:
            raise ValueError(f'Manifeste incomplet : {lot}')
        if columns is not None and columns != fields:
            raise ValueError(f'Schéma différent : {lot}')
        columns = fields
        if any(r['document_id'] not in ids for r in data):
            raise ValueError(f'Extraction hors lot : {lot}')
        counts = __import__('collections').Counter(r['document_id'] for r in data)
        if any(counts[r['document_id']] != int(r['nominations_candidates']) for r in manifest):
            raise ValueError(f'Effectifs incohérents : {lot}')
        rows.extend(data)
    target = BASE / 'nominations_2015_2025.csv'
    if target.exists():
        backup = BASE / 'archives/consolidations'
        backup.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        shutil.copy2(target, backup / f'nominations_2015_2025_{stamp}.csv')
    temporary = target.with_suffix('.csv.tmp')
    with temporary.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(target)
    print(f'{len(rows)} nominations candidates ; {sum(r["date_conseil"].startswith("2022-") for r in rows)} en 2022 : {target}')

if __name__ == '__main__':
    consolider()
