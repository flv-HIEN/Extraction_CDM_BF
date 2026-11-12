# Extraction et normalisation des nominations

## Organisation

- `donnees/comptes_rendus/` : corpus des comptes rendus du Conseil des ministres, classés par année, et copies historiques conservées dans leurs sous-dossiers.
- `donnees/decrets_remaniement/` : documents de remaniement ministériel, séparés du corpus des comptes rendus.
- `extraction_evaluation/` : extracteur principal, notebooks, pipeline, interface de validation et évaluations. Les résultats annuels auparavant dans `donnees/` sont dans `resultats/`, leurs scripts dans `scripts_corpus/`. `Scripts/` conserve les travaux historiques et archives.
- `normalisation/` : création et fiabilisation des identifiants, revue des identités et tests ; `fiabilisation/` contient les résultats et dictionnaires ; `ministeres/` contient les référentiels, scripts et résultats de normalisation des ministères.
- `analyses/` : notebooks exploratoires de trajectoires.
- `presentation_avancement/`, `Chapitre2Z.docx`, `NOTE_CADRAGE_MEMOIRE.md` : présentation et documents du mémoire.
- `wsl_setup/` : configuration de l'environnement.

Les copies de corpus et de résultats ont été conservées : leur présence ne signifie pas qu'elles sont synchronisées. Les archives RAR restent intactes et peuvent contenir des copies anciennes.

## Commandes depuis la racine

```bash
python3 extraction_evaluation/extraire_nominations_2015.py --help
python3 normalisation/fiabiliser_nominations.py --help
python3 normalisation/appliquer_decisions_revue.py --help
python3 -m unittest discover -s normalisation -p 'test_*.py'
python3 extraction_evaluation/validation_web/serveur.py --help
```

Pour extraire une année, fournir explicitement `--source donnees/comptes_rendus/2015` et `--output extraction_evaluation/resultats/nominations_2015.csv`.
La fiabilisation utilise par défaut `extraction_evaluation/nominations_2015_2025.csv` et écrit dans `normalisation/fiabilisation/`.
Le script de normalisation des ministères conserve son entrée et ses sorties locales dans `normalisation/ministeres/`.

Les notebooks et documents historiques conservent leurs anciens chemins et sorties : adapter les chemins à cette arborescence avant de les réexécuter. Les chemins de provenance enregistrés dans les CSV et JSON sont conservés pour la traçabilité.

`REORGANISATION.json` répertorie les déplacements et le nombre de fichiers de données dont l'intégrité a été vérifiée par SHA-256.

Le protocole actuel et l’extracteur unique sont décrits dans [extraction_evaluation/README.md](extraction_evaluation/README.md). Les anciens dossiers ont été fusionnés ; les travaux historiques sont dans `extraction_evaluation/archives/`.
