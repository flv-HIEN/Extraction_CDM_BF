# Pipeline d’extraction des nominations

La pipeline est dans le notebook [`pipeline_extraction_nominations.ipynb`](../Scripts/pipeline_et_validation/pipeline_extraction_nominations.ipynb). Elle remplace l’exécution manuelle du notebook historique comme base de travail reproductible, tout en conservant les CSV historiques pour comparer les résultats.

Elle applique quatre étapes :

1. extraction de texte avec `pdfminer` ;
2. OCR français à 200 % si le texte est trop court ;
3. détection de la rubrique des nominations, des sous-rubriques de conseils d’administration, révocations et fins de fonctions ;
4. extraction de chaque personne, de son contexte et des champs disponibles, avec page, extrait source, méthode de lecture et niveau de confiance.

Les personnes citées uniquement comme remplacées, ainsi que les révocations et fins de fonctions, sont exclues. Les sorties restent des candidats et doivent être validées dans la grille de référence.

## Lancer la pipeline

Activer d’abord l’environnement du mémoire, qui contient `pdfminer`, PyMuPDF, Tesseract et les dépendances OCR :

```bash
conda activate memoire_env
```

Pour un PDF :

Ouvrir le notebook, inscrire le chemin dans `PDFS_A_TRAITER`, puis choisir `SORTIE` et `MANIFESTE` dans la cellule de paramètres.

Pour tout le corpus :

Laisser `PDFS_A_TRAITER = []` pour traiter tout `total_donnees`.

Les fichiers par défaut sont `extractions_pipeline.csv` et `manifeste_pipeline.csv` dans `evaluation_extraction/`. La pipeline ne modifie ni les CSV historiques de `total_donnees`, ni les références validées.

## Objectif de qualité

Sur le lot pilote relu, les règles de détection retrouvent les 566 noms de référence au niveau `document + nom`, après correction du cas « Aboubakar, TRAORE ». L’indicateur principal exige aussi la date et la fonction : il est de 565 vrais positifs, 1 faux positif et 1 faux négatif, soit 99,8 % de précision, rappel et F1. Ce résultat sert à guider le développement : il ne prouve pas 99 % sur tous les formats du corpus.

La sortie du lot pilote est conservée dans `extractions_pipeline_lot_pilote.csv` et son contrôle dans [`RAPPORT_PIPELINE_LOT_PILOTE.md`](RAPPORT_PIPELINE_LOT_PILOTE.md). Pour le reproduire :

Ouvrir ensuite [`evaluer_rappel_pipeline.ipynb`](../Scripts/pipeline_et_validation/evaluer_rappel_pipeline.ipynb), renseigner les chemins du lot pilote ou du test indépendant dans la cellule de paramètres, puis exécuter la cellule de calcul.

La cible de plus de 99 % doit être mesurée sur un lot final indépendant, qui comprend des PDF avec texte natif, des listes collectives, des conseils d’administration et des scans positifs soumis à OCR. Pour chaque version, publier le rappel, la précision, le F1 et la liste des faux négatifs. Un seuil de 99 % de rappel doit être atteint sur ce lot final, sans ajout de règles après l’avoir consulté.
