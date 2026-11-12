# Dossier d’extraction 2015

Ouvrez `pipeline_extraction_et_evaluation_2015.ipynb` avec l’environnement Conda `memoire_env`, puis exécutez les cellules dans l’ordre.

Le notebook traite les 47 fichiers `CDM - 2015_*.pdf` de `../Scripts/donnees2015/`. Il utilise `pdfminer` en premier et Tesseract OCR français seulement si le texte classique est insuffisant. Les sorties sont écrites dans `resultats/`.

La première exécution a produit 2 598 nominations candidates. Ce sont des propositions de la pipeline, sans valeur de vérité terrain avant relecture humaine.

`reference_annotations_2015.csv` est une grille vide : elle doit être renseignée après relecture humaine des PDF. Les anciens CSV de `Scripts/donnees2015` sont des sorties historiques et ne doivent pas être utilisés comme référence pour les métriques.

Dépendances : `pdfminer.six`, `pymupdf`, `pytesseract`, `Pillow` et Tesseract avec le paquet de langue française (`fra`).
