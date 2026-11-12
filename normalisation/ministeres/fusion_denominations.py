"""Fusion automatique des dénominations explicitement reliées par la table locale."""
import re
import csv
from pathlib import Path
import unicodedata
from functools import lru_cache
from .table_concordance_ministeres_2015_2025_vers_2026 import (
    CONCORDANCE_MINISTERES_2015_2025_VERS_2026 as TABLE, REFERENTIEL_2026,
)

def cle(value):
    text=unicodedata.normalize('NFKD', value.upper().replace('Œ','OE'))
    return re.sub(r'[^A-Z0-9]+',' ',''.join(c for c in text if not unicodedata.combining(c))).strip()

INDEX={}
for titre, rule in TABLE.items():
    for variant in {cle(titre),cle(titre).replace(' GARDE DES SCEAUX','')}:
        if variant in INDEX and INDEX[variant]['codes_ref_2026']!=rule['codes_ref_2026']:
            raise ValueError('Concordance contradictoire : '+variant)
        INDEX[variant]=rule
for code,titre in REFERENTIEL_2026.items():
    INDEX.setdefault(cle(titre),dict(codes_ref_2026=(code,),type_concordance='reference',
                                   perimetres_non_couverts_2026=(),note=''))

def charger_alias(path=None):
    path = Path(path) if path else Path(__file__).with_name('alias_ministeres.csv')
    aliases = {}
    if not path.exists():
        return aliases
    with path.open(encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            if row['statut'] != 'verifie':
                continue
            source, target = cle(row['variante']), cle(row['intitule_officiel'])
            if not source or target not in INDEX:
                raise ValueError('Alias sans cible officielle connue : ' + row['variante'])
            if not row['justification'].strip() or not row['reference_documentaire'].strip():
                raise ValueError('Alias sans justification/référence : ' + row['variante'])
            if source in aliases and aliases[source]['cible'] != target:
                raise ValueError('Alias contradictoire : ' + row['variante'])
            if source in INDEX and INDEX[source]['codes_ref_2026'] != INDEX[target]['codes_ref_2026']:
                raise ValueError('Alias contredisant la table officielle : ' + row['variante'])
            aliases[source] = dict(cible=target, intitule=row['intitule_officiel'],
                                  justification=row['justification'], reference=row['reference_documentaire'])
    return aliases

ALIASES = charger_alias()

@lru_cache(maxsize=None)
def fusionner(libelle):
    alias = ALIASES.get(cle(libelle))
    rule=INDEX.get(alias['cible'] if alias else cle(libelle))
    result=dict(alias_ministere_applique=alias['intitule'] if alias else '',
                reference_alias_ministere=alias['reference'] if alias else '',
                code_ministere_reference='', ministere_reference='',
                codes_ministeres_candidats='', statut_fusion_ministere='non_repertorie',
                type_concordance_ministere='', note_concordance_ministere='')
    if not libelle.strip():
        result['statut_fusion_ministere']='sans_ministere'
        return result
    if not rule:
        return result
    codes=rule['codes_ref_2026']
    result.update(codes_ministeres_candidats=' | '.join(codes),
                  type_concordance_ministere=rule['type_concordance'],
                  note_concordance_ministere=rule.get('note',''))
    if len(codes)!=1:
        result['statut_fusion_ministere']='correspondance_multiple_a_verifier'
    elif rule.get('perimetres_non_couverts_2026'):
        result['statut_fusion_ministere']='perimetre_partiel_a_verifier'
    elif 'convention' in (rule['type_concordance']+' '+rule.get('note','')).lower():
        result['statut_fusion_ministere']='convention_a_verifier'
    else:
        result.update(code_ministere_reference=codes[0],ministere_reference=REFERENTIEL_2026[codes[0]],
                      statut_fusion_ministere='fusion_automatique_table')
    return result
