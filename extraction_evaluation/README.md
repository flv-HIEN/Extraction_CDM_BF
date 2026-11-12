# Extraction et évaluation : protocole 12 / 30 / reste

Le corpus unique est `donnees/comptes_rendus/total/` (orthographe existante : comptes_rendus).
Les dossiers Scripts, scripts_corpus, Dossier_extraction et evaluation_extraction ont été fusionnés ici.

## Extracteur unique

`extraire_nominations_2015.py` est la seule implémentation courante, pour toutes les années du corpus. `extraire_nominations_2015.ipynb` appelle ce script. Les deux notebooks concurrents ont été retirés.

```bash
python3 extraction_evaluation/extraire_nominations_2015.py --lot developpement_12
python3 extraction_evaluation/extraire_nominations_2015.py --lot evaluation_30
# Après validation des résultats :
python3 extraction_evaluation/extraire_nominations_2015.py --lot reste
```

Ajouter `--ocr` pour reconnaître les pages sans texte natif (Tesseract fra+eng requis). Dépendance Python : PyMuPDF (`fitz`). Utiliser l'environnement `memoire_env`. Le texte natif est conservé lorsqu'il existe ; aucun OCR n'est lancé par défaut. Les PDF avec un texte natif dégradé nécessitent une relecture.

Les sorties sont dans `evaluation/extractions_pipeline_<lot>.csv` avec un manifeste associé : document, source, SHA-256, nombre de pages OCR et nombre de candidats (y compris zéro). `--output` et `--manifeste` permettent de choisir les chemins. `--source` choisit un autre dossier contenant les mêmes fichiers du lot ; il ne déclenche pas le traitement de tout ce dossier.

Les colonnes historiques (`emploi`, `grade`, `classe`, `echelon`, `poste_nomination`, etc.) sont conservées. `fonction` reprend `poste_nomination` pour assurer la compatibilité avec `evaluer_30.py`. Les lignes sont des candidats avec `statut_verification=a_verifier`.

Les manifestes des lots restent ceux du protocole précédent. Les extractions produites avant l'unification doivent être régénérées avec cet extracteur avant toute comparaison.

## Étapes

1. Mettre au point les règles sur les 12 PDF de `lots/developpement_12.csv`.
2. Figer les règles avant de traiter les 30 PDF de `lots/evaluation_30.csv` ; ne pas les utiliser pour ajuster les règles et ensuite annoncer une performance indépendante.
3. Relire intégralement ces 30 PDF. Renseigner toutes les nominations dans `lots/reference_30.csv`, avec `statut_verification=valide`. Marquer chaque document `valide` dans `lots/validation_30.csv`, y compris les documents sans nomination. Les prédictions ne constituent pas une référence.
4. Calculer précision, rappel et F1 avec la commande ci-dessous, ou le notebook `evaluer_rappel_pipeline.ipynb`.
5. Examiner les erreurs et les scores avant d'appliquer la version retenue au lot `reste` (394 PDF). Tout nouvel ajustement après examen des 30 PDF exige un nouveau lot pour mesurer une performance indépendante.

```bash
python3 extraction_evaluation/evaluer_30.py \
  --predictions extraction_evaluation/evaluation/extractions_pipeline_evaluation_30.csv \
  --reference extraction_evaluation/lots/reference_30.csv
```

Les manifestes ont été tirés avec la graine 20261023 sur les noms triés du corpus, sans chevauchement des noms de fichiers. Ils contiennent les empreintes SHA-256. Tirage aléatoire simple, non stratifié. L'historique d'utilisation éventuelle de ces PDF n'a pas été audité ; ce lot ne garantit donc pas une indépendance vis-à-vis des anciens travaux.

Les métriques utilisent un appariement exact après normalisation des espaces, de la casse, des accents et de la ponctuation, avec comptage des doublons : VP = intersection, FP = prédictions non appariées, FN = références non appariées. Trois niveaux sont rapportés : personne, événement (document/date/nom/fonction), complet (avec ministère). Une division sans dénominateur donne 0.

## Historique

`archives/` conserve les anciens scripts, notebooks, données TanaT et archives RAR. `archives/evaluations_historiques/` conserve les résultats des anciennes campagnes ; `evaluation/` est réservé au protocole actuel. `validation_web/` utilise désormais le lot courant des 30 PDF ; les archives restent séparées.

Aucun score du nouveau lot n'est disponible avant extraction et annotation humaine. Le notebook courant ne contient aucune ancienne sortie.

## Interface de validation des 30 PDF

Ouvrir `lancer_validation_locale.ipynb` dans `memoire_env`, puis exécuter les cellules. Utiliser le nouveau lien affiché (port automatiquement disponible). Le lancement en ligne de commande est également possible :

```bash
python3 extraction_evaluation/validation_web/serveur.py --port 0
```

L’interface charge exactement `lots/evaluation_30.csv` et vérifie les empreintes des PDF. Le texte est extrait du PDF page par page avec PyMuPDF ; pour les scans sans texte, utiliser le PDF affiché. Elle propose les candidats de `evaluation/extractions_pipeline_evaluation_30.csv` à la première ouverture d’un document non annoté. En l’absence de ce fichier, la saisie manuelle reste possible. Les propositions ne sont jamais validées automatiquement.

Après correction exhaustive, indiquer le relecteur, confirmer la lecture intégrale et cliquer sur « Valider tout le document ». Les lignes sont enregistrées dans `lots/reference_30.csv` avec `statut_verification=valide`, et le document est marqué `valide` dans `lots/validation_30.csv`. Une liste vide peut être validée après confirmation de l’absence de nomination. L’enregistrement d’un brouillon retire la validation du document. Les suppressions enregistrées ne sont pas remplacées par les anciennes propositions.

Le journal des relecteurs est dans `lots/validations_30.json`. Les sauvegardes des fichiers précédents sont dans `lots/sauvegardes_validation/`. Les modifications concurrentes sont détectées ; recharger avant de sauvegarder en cas de conflit. Aucune ancienne annotation n’est recopiée depuis les archives.

## Rattachement institutionnel : règles d'extraction

L'extracteur conserve les lignes du PDF pour repérer les titres de rubrique. Un détecteur commun traite les listes et la prose des conseils d'administration. Les captures s'arrêtent avant une personne, une annonce de nomination, une puce ou une nouvelle rubrique. Un simple récit « le ministre de… » ne suffit plus à attribuer un ministère.

- `ministere` : uniquement un titre ministériel reconnu ;
- `institution` : primature, présidence, autorité, etc., séparées des ministères ;
- `categorie_representation` : personnel, usagers, associations, etc. Une catégorie conserve le rattachement parent s'il est connu, sans le remplacer ;
- `type_rattachement`, `rattachement_source` et `alerte_extraction_ministere` : type, texte capturé et motif d'incertitude.

Une nouvelle rubrique principale efface le contexte antérieur. Les annonces dans une même rubrique peuvent partager son titre. Le ministère reste vide avec une alerte si aucun titre ministériel ou institutionnel fiable ne s'applique. Une coupure de page seule n'efface pas le contexte car une rubrique peut continuer sur la page suivante.

Ces changements ne modifient pas les anciens CSV. Tester d'abord le lot de développement avec des sorties séparées avant toute réextraction générale. Les nouveaux CSV comportent des colonnes supplémentaires : ne pas les mélanger avec les anciennes extractions lors de la consolidation. La précision et le rappel doivent être réévalués, notamment après retrait des anciennes inférences contextuelles.

### Annonces collectives multilignes

Les titres sont détectés dans la vue structurée ; les règles de nominations lisent une seconde vue où chaque retour à la ligne est remplacé par un espace, sans modifier les offsets. Les pages et les contextes restent alignés. Les annonces collectives traversant une nouvelle rubrique ou un nouveau décret sont rejetées. Cette séparation évite de perdre les fonctions communes des listes d'administrateurs lorsque les phrases s'étendent sur plusieurs lignes.
