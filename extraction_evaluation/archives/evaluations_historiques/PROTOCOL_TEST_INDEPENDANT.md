# Test indépendant et relecture ciblée

Ce protocole évite de valider manuellement les 406 PDF du corpus tout en permettant une mesure défendable de la qualité d’extraction.

## Fichiers produits

La [pipeline complète](../Scripts/pipeline_et_validation/pipeline_extraction_nominations.ipynb) a traité les **406 PDF** et produit 21 687 candidats dans [`extractions_pipeline_corpus.csv`](extractions_pipeline_corpus.csv), ainsi qu’un diagnostic de lecture par PDF dans [`manifeste_pipeline_corpus.csv`](manifeste_pipeline_corpus.csv).

Le dossier [`test_independant`](test_independant/) contient un test **verrouillé** de 28 PDF, non présents dans l’échantillon de développement, le lot pilote ou la référence déjà validée. Il comprend 714 candidats et couvre :

- un scan lu par OCR et quatre PDF sans candidat ;
- quatre documents avec conseils d’administration ;
- trois documents dont certains champs sont à revoir ;
- deux listes longues ;
- treize documents standards répartis entre 2015 et 2025, complétés par un document sans candidat.

Le manifeste [`lot_test_independant.csv`](test_independant/lot_test_independant.csv) conserve la graine de sélection, les strates, les chemins sources et les effectifs. [`empreinte_pipeline.json`](test_independant/empreinte_pipeline.json) conserve les empreintes des deux scripts employés. [`predictions_pipeline_figee.csv`](test_independant/predictions_pipeline_figee.csv) est la sortie à comparer à la référence humaine : ne pas la régénérer ni modifier les règles avant l’évaluation.

## Valider le test

Lancer l’interface sur le dossier isolé du test :

```bash
conda activate memoire_env
python Scripts/pipeline_et_validation/validation_web/serveur.py \
  --dossier-validation evaluation_extraction/test_independant \
  --lot lot_test_independant.csv \
  --port 8766
```

Ouvrir `http://localhost:8766`. Pour chaque PDF, lire la rubrique complète des nominations dans le PDF, corriger les propositions, ajouter les nominations absentes et retirer les lignes qui ne sont pas des nominations. Valider ensuite le document dans l’interface. Les fichiers du test sont séparés de `reference_annotations.csv` et de la campagne déjà réalisée.

Après la sélection du lot, ne pas ajuster `pipeline_extraction_nominations.py` avant le calcul des scores. Les erreurs trouvées dans ce lot pourront servir à une version suivante, mais cette version devra être mesurée sur un nouveau test indépendant.

Faire relire indépendamment au moins six PDF, avec une priorité pour un scan, une liste longue et deux conseils d’administration. Conserver les deux annotations et noter l’arbitrage.

## Évaluer après la validation complète

Lorsque les 28 PDF sont tous validés, exécuter :

```bash
jupyter lab Scripts/pipeline_et_validation/evaluer_rappel_pipeline.ipynb
```

Dans la cellule de paramètres, choisir `predictions_pipeline_figee.csv`, `lot_test_independant.csv`, `reference_annotations_validees.csv`, `RAPPORT_TEST_INDEPENDANT.md` et `ecarts_test_independant.csv`. L’indicateur principal du rapport exige `document + date_conseil + nom + fonction`. La détection par nom sert uniquement à diagnostiquer les noms manqués. Les 714 candidats ne sont pas les 714 annonces de référence : la relecture peut en ajouter ou en supprimer.

## Développer sans contaminer le test

[`file_relecture_developpement_prioritaire.csv`](file_relecture_developpement_prioritaire.csv) classe les 378 autres PDF par risque : OCR, absence de candidat, champs incomplets, conseils d’administration et listes longues. Utiliser cette file pour améliorer les règles et valider une partie du corpus destinée à Tanat. Les 28 PDF du test n’y figurent pas.

Les sorties complètes restent des candidats. Pour les analyses Tanat, conserver `methode_lecture`, `confiance_extraction` et le statut de validation afin de pouvoir comparer les résultats obtenus avec les seules annonces validées et avec l’ensemble des candidats.
