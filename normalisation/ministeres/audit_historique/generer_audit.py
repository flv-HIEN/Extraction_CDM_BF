"""Audit en lecture seule du corpus ; écrit uniquement dans ce dossier.
Exécution : python generer_audit.py (pandas, pymupdf et rapidfuzz requis).
"""
from pathlib import Path
from collections import Counter
import hashlib, importlib.util, json, re, unicodedata
import pandas as pd
import pymupdf
from rapidfuzz import fuzz, process
from rapidfuzz.distance import Levenshtein

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE=ROOT/'normalisation/fiabilisation/nominations_2015_2025_fiabilise.csv'
def key(s):
    s=unicodedata.normalize('NFKD',s.replace('œ','oe').replace('Œ','OE'))
    return re.sub('[^A-Z0-9]+',' ',''.join(c for c in s if not unicodedata.combining(c)).upper()).strip()
def uid(s):return hashlib.sha256(s.encode()).hexdigest()[:12]
def write(name,rows,columns=None):
    pd.DataFrame(rows,columns=columns).to_csv(OUT/name,index=False,encoding='utf-8-sig')
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

df=pd.read_csv(SOURCE,dtype=str,keep_default_na=False)
df['ligne_csv']=range(2,len(df)+2) # numéro d'enregistrement + en-tête, non ligne physique multiligne
df['date']=pd.to_datetime(df.date_conseil,errors='coerce')
df['annee']=df.date.dt.year.astype('Int64')
df['ministere_analyse']=df.ministere.str.strip().replace('','Ministère non renseigné')
# Reproduction du filtre de la cellule 6, puis restriction explicite à 2015–2025.
base=df[df.date.notna() & df.poste_nomination.str.strip().ne('') & df.annee.between(2015,2025)].copy()
def kind(s):
    k=key(s)
    if k=='MINISTERE NON RENSEIGNE':return 'non_renseigne'
    if re.match(r'^(PERSONNEL|ETUDIANTS?|ELEVES?|AUTEURS?|ARTISTES?|ENSEIGNANTS?|TRAVAILLEURS?|USAGERS|MEMBRES REPRESENTANT|REPRESENTANTS?|ORGANISATIONS|SYNDICATS|CORPS PROFESSORAL|BUREAU DES ELEVES)\b',k):return 'categorie_representation_probable'
    if re.match(r'^MINISTERE (DE|DES|DU|D)\b',k):
        return 'ministere_apparent_a_verifier' if len(s)<=220 and not re.search(r'\b(MONSIEUR|MADAME|NOMME|PERSONNES)\b',k) else 'titre_contamine_probable'
    if re.match(r'^(PRESIDENCE|PRIMATURE|PREMIER MINISTERE|AUTORITE|COMMISSION|SECRETARIAT|CONSEIL|AGENCE|OFFICE|UNIVERSITE|CHAMBRE|ASSOCIATION|FEDERATION|CAISSE|SOCIETE|LIGUE|BRIGADE|ARMEE|GENDARMERIE|CENTRE|ORDRE|OBSERVATOIRE|SERVICES DU PREMIER)\b',k):return 'institution_non_ministerielle_apparente'
    return 'libelle_ambigu_a_verifier'
base['classe_audit']=base.ministere_analyse.map(kind)
counts=base.groupby('ministere_analyse').size().sort_values(ascending=False)
annual=pd.crosstab(base.ministere_analyse,base.annee).reindex(columns=range(2015,2026),fill_value=0)
stats=[]
for label,n in counts.items():
    stats.append(dict(ministere_analyse=label,classe_audit=kind(label),frequence=int(n),part_pct=round(100*n/len(base),4),**{str(y):int(annual.loc[label,y]) for y in range(2015,2026)}))
write('frequences_ministere_analyse.csv',stats)
# Mise en cache des textes, avec pages physiques à partir de 1.
cache={}
def pages_for(doc):
    if doc not in cache:
        p=ROOT/'donnees/comptes_rendus/total'/doc
        if not p.exists():
            hits=list((ROOT/'donnees/comptes_rendus').glob('*/'+doc));p=hits[0] if hits else p
        cache[doc]=(p,[page.get_text() for page in pymupdf.open(p)]) if p.exists() else (p,[])
    return cache[doc]
susp=base[base.classe_audit.ne('ministere_apparent_a_verifier')].copy()
records=[]
for _,r in susp.iterrows():
    p,pages=pages_for(r.document_id)
    pn=int(r.page) if r.page.isdigit() else 0
    text=pages[pn-1] if 0<pn<=len(pages) else ''
    normalized=' '.join(text.split())
    idx=normalized.casefold().find(' '.join(r.nom.split()).casefold())
    evidence=normalized[max(0,idx-600):idx+len(r.nom)+350] if idx>=0 else normalized[:1200]
    records.append(dict(id_ligne_source=r.id_ligne_source,ligne_csv=r.ligne_csv,ministere_analyse=r.ministere_analyse,classe_audit=r.classe_audit,date_conseil=r.date_conseil,annee=r.annee,nom=r.nom,poste_nomination=r.poste_nomination,document_id=r.document_id,pdf_source=str(p.relative_to(ROOT)),page=r.page,extrait_exact=r.extrait_exact,texte_source_page=evidence,nom_retrouve_texte_natif=int(idx>=0),frequence_libelle=int(counts[r.ministere_analyse]),decision_proposee='revue_contextuelle_sans_modification',**{str(y):int(annual.loc[r.ministere_analyse,y]) for y in range(2015,2026)}))
write('ministeres_valeurs_suspectes.csv',records)
# Référentiel des formes institutionnelles rencontrées, identifiants PROVISOIRES.
ref=[]
for label,g in base.groupby('ministere_analyse',sort=True):
    typ=kind(label)
    if typ not in ('ministere_apparent_a_verifier','institution_non_ministerielle_apparente'):continue
    r=g.iloc[0];k=key(label)
    ref.append(dict(id_institution_provisoire='IP_'+uid(k),id_institution_valide='',id_version_appellation_provisoire='VP_'+uid(label),nom_brut=label,nom_normalise_lexical=k,famille_institutionnelle='a_valider',type_institution='ministere_apparent' if typ.startswith('ministere') else 'autre_institution_apparente',statut_validation='observe_corpus_identite_non_validee',premiere_observation=g.date_conseil.min(),derniere_observation=g.date_conseil.max(),validite_debut='',validite_fin='',nature_periode='observations_uniquement_non_validite_juridique',frequence=len(g),source_document=r.document_id,source_page=r.page,reference_source='donnees/comptes_rendus/total/'+r.document_id,preuve_continuite='',note='Aucune fusion historique ; une même clé lexicale ne prouve pas une identité institutionnelle.'))
# Attestations issues d'un acte officiel local effectivement lu : simples présences, aucune filiation.
act='donnees/decrets_remaniement/decret_remaniement2017.pdf'
actpages=[p.get_text() for p in pymupdf.open(ROOT/act)]
for row in ref:
    k=row['nom_normalise_lexical'].replace('MINISTERE ','MINISTRE ',1)
    if row['type_institution']=='ministere_apparent':
        for i,t in enumerate(actpages):
            if re.search(r'(?<![A-Z])'+re.escape(k)+r'(?: PORTE PAROLE DU GOUVERNEMENT)? (?:MONSIEUR|MADAME)\b', key(t)):
                row.update(attestation_officielle_date='2017-02-20',attestation_officielle_source=act,attestation_officielle_page=i+1,statut_validation='appellation_attestee_acte_local_identite_non_validee');break
write('referentiel_institutions.csv',ref)
# Trois candidats par forme, sans seuil d'acceptation, jamais appliqués.
keys=sorted({x['nom_normalise_lexical'] for x in ref if x['type_institution']=='ministere_apparent'})
bykey={k:next(x for x in ref if x['nom_normalise_lexical']==k) for k in keys}
pairs=[]
for k in keys:
    for target,score,_ in process.extract(k,[t for t in keys if t!=k],scorer=fuzz.ratio,limit=3):
        a,b=bykey[k],bykey[target]
        pairs.append(dict(id_source=a['id_institution_provisoire'],nom_source=a['nom_brut'],id_cible=b['id_institution_provisoire'],nom_cible=b['nom_brut'],score_rapidfuzz_ratio=round(score,3),score_token_sort_ratio=round(fuzz.token_sort_ratio(k,target),3),score_token_set_ratio=round(fuzz.token_set_ratio(k,target),3),distance_levenshtein=Levenshtein.distance(k,target),score_levenshtein_normalise=round(100*Levenshtein.normalized_similarity(k,target),3),premiere_observation_source=a['premiere_observation'],derniere_observation_source=a['derniere_observation'],premiere_observation_cible=b['premiere_observation'],derniere_observation_cible=b['derniere_observation'],statut_validation='a_valider',relation_historique='indeterminee',preuve_documentaire_continuite='',application_automatique=0))
write('correspondances_institutions_a_valider.csv',pairs)
# Comparaison reproductible des deux extracteurs, sans réécrire leurs exports.
comparisons=[]
for tag,path in [('archive','extraction_evaluation/archives/scripts_corpus/extraire_nominations_2015.py'),('actuel','extraction_evaluation/extraire_nominations_2015.py')]:
    m=load_module('audit_'+tag,path)
    for doc in ['CDM - 2015_01_27.pdf','CDM - 2015_10_28.pdf']:
        rs,_=m.extract_from_pdf(ROOT/'donnees/comptes_rendus/total'/doc)
        for r in rs:
            if any(n in r['nom'] for n in ['Bali Bertrand','Kayouré Idrissa','Hassane OUEDRAOGO','Moustapha KAFANDO']):comparisons.append(dict(version=tag,document_id=doc,**{k:r.get(k,'') for k in ['nom','page','ministere','categorie_representation','type_rattachement','rattachement_source']}))
write('comparaison_extracteurs.csv',comparisons)
summary=dict(source=str(SOURCE.relative_to(ROOT)),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),lignes_source=len(df),lignes_analyse=len(base),libelles_uniques=len(counts),lignes_signalees=len(susp),libelles_signales=susp.ministere_analyse.nunique(),classes=base.classe_audit.value_counts().to_dict(),annuel={str(y):dict(lignes=len(g),libelles_uniques=g.ministere_analyse.nunique(),lignes_signalees=int(g.classe_audit.ne('ministere_apparent_a_verifier').sum())) for y,g in base.groupby('annee')},referentiel_lignes=len(ref),paires=len(pairs),comparaison=comparisons)
(OUT/'bilan_audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='comparaison'},ensure_ascii=False,indent=2))
