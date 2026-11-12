"""Contrôles de cohérence des livrables ; aucune écriture."""
from pathlib import Path
import csv,hashlib,json
p=Path(__file__).resolve().parent
b=json.loads((p/'bilan_audit.json').read_text())
def read(name):
    with (p/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
f=read('frequences_ministere_analyse.csv');s=read('ministeres_valeurs_suspectes.csv');r=read('referentiel_institutions.csv');c=read('correspondances_institutions_a_valider.csv')
assert len(f)==b['libelles_uniques']
assert sum(int(x['frequence']) for x in f)==b['lignes_analyse']
for y,annual in b['annuel'].items():assert sum(int(x[y]) for x in f)==annual['lignes']
assert len(s)==b['lignes_signalees']
assert len({x['ministere_analyse'] for x in s})==b['libelles_signales']
assert all(not x['id_institution_valide'] and not x['validite_debut'] and not x['validite_fin'] for x in r)
for x in c:
    assert x['application_automatique']=='0' and x['statut_validation']=='a_valider'
    for col in ['score_rapidfuzz_ratio','score_token_sort_ratio','score_token_set_ratio','score_levenshtein_normalise']:assert 0<=float(x[col])<=100
assert hashlib.sha256((p.parents[2]/b['source']).read_bytes()).hexdigest()==b['sha256']
assert all((p/name).exists() for name in ['AUDIT_MINISTERES.md','ministeres_valeurs_suspectes.csv','referentiel_institutions.csv','correspondances_institutions_a_valider.csv'])
print('Contrôles de cohérence : OK')
print('Attestations officielles locales :',sum(bool(x.get('attestation_officielle_source')) for x in r))
