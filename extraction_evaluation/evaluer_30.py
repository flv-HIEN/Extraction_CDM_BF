"""Mesure sur 30 PDF relus intégralement, y compris ceux sans nomination."""
import argparse
import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from configuration_pipeline import DOSSIER

def lire(p):
    with Path(p).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def normaliser(s):
    s=''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s)

def mesurer(predictions, reference, champs):
    def compter(rows):
        return Counter(tuple(normaliser(row.get(c,'')) for c in champs) for row in rows)
    p,r=compter(predictions),compter(reference)
    vp=sum((p&r).values());fp=sum((p-r).values());fn=sum((r-p).values())
    precision=vp/(vp+fp) if vp+fp else 0
    rappel=vp/(vp+fn) if vp+fn else 0
    return dict(vp=vp,fp=fp,fn=fn,precision=precision,rappel=rappel,f1=2*vp/(2*vp+fp+fn) if 2*vp+fp+fn else 0)

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--predictions',type=Path,required=True)
    a.add_argument('--reference',type=Path,required=True)
    a.add_argument('--validation',type=Path,default=DOSSIER/'lots/validation_30.csv')
    a.add_argument('--rapport',type=Path,default=DOSSIER/'evaluation/mesures_30.json')
    args=a.parse_args()
    lot={x['document_id'] for x in lire(DOSSIER/'lots/evaluation_30.csv')}
    validations=lire(args.validation)
    if len(lot)!=30 or not lot <= {x['document_id'] for x in validations if x['statut']=='valide'}:
        a.error('Les 30 PDF doivent être relus intégralement et marqués valide dans validation_30.csv.')
    pred,ref=lire(args.predictions),lire(args.reference)
    if any(x['document_id'] not in lot for x in pred+ref):
        a.error('Présence de documents hors du lot des 30 PDF.')
    if any(x.get('statut_verification')!='valide' for x in ref):
        a.error('Chaque annotation de référence doit avoir statut_verification=valide.')
    for rows in (pred,ref):
        if any(not x.get('nom','').strip() for x in rows):a.error('Annotation sans nom.')
    niveaux={'personne':['document_id','nom'], 'evenement':['document_id','date_conseil','nom','fonction'], 'complet':['document_id','date_conseil','nom','fonction','ministere']}
    result={n:mesurer(pred,ref,c) for n,c in niveaux.items()}
    args.rapport.parent.mkdir(parents=True,exist_ok=True)
    args.rapport.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
