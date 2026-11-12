# Premier lot d'évaluation de l'extraction

Ce dossier a été préparé par le notebook historique `Scripts/pipeline_et_validation/archive_mise_au_point/preparer_evaluation_extraction.ipynb`. Il contient un **échantillon à annoter**, les sorties de l'extracteur actuel et des alertes automatiques. Les alertes ne sont pas des erreurs confirmées et les prédictions ne constituent pas une vérité terrain.

## Fichiers

Pour commencer la validation, utiliser le [lot pilote de 12 PDF et son interface locale](LOT_PILOTE_VALIDATION.md). Lancer `python3 Scripts/pipeline_et_validation/validation_web/serveur.py` depuis le dossier de travail, puis ouvrir `http://localhost:8765`.

Pour mesurer la qualité finale sans relire les 406 PDF, suivre le [protocole de test indépendant et de relecture ciblée](PROTOCOL_TEST_INDEPENDANT.md). Son dossier de validation est isolé de la référence du lot pilote.

| Fichier | Usage |
|---|---|
| `documents_echantillon.csv` | Inventaire initial des comptes rendus choisis. Son ancien statut d'annotation et le nombre initial de caractères du PDF soumis à OCR ne reflètent pas la campagne récente ; utiliser `suivi_annotations.csv` pour l'état actuel. |
| `textes/*.txt` | Texte extrait de chaque PDF ; vérifier le PDF lorsque le texte est déformé. |
| `predictions_a_verifier.csv` | Lignes produites par l'extracteur actuel. `decision_humaine` peut recevoir `correcte`, `partielle` ou `fausse`. |
| `erreurs_a_verifier.csv` | Lignes signalées par des contrôles automatiques. Une même ligne peut apparaître plusieurs fois. Remplir `decision_humaine` et `correction` après vérification. |
| `reference_annotations.csv` | **Grille de travail remplie** : 2 411 lignes relevées dans les 37 documents, avec `statut_verification`. 575 lignes sont actuellement vérifiées ; filtrer ce statut avant toute évaluation. |
| `reference_annotations_validees.csv` | Les 575 annonces vérifiées sur treize comptes rendus. Ce fichier seul peut servir de référence pour ces documents. |
| `annotations_proposees.csv` | 2 407 nominations candidates relevées dans les textes des PDF, avant les corrections ponctuelles de la grille. Elles ne sont pas encore validées. |
| `annotations_consolidees_a_valider.csv` | Copie actualisée de la grille de travail : 575 annonces vérifiées et 1 836 propositions restantes. Régénérer après toute correction de `reference_annotations.csv`. |
| `suivi_annotations.csv` | État de chacun des 37 documents ; cinq sont sans nomination et trois sont entièrement annotés. |
| `SUIVI_CAMPAGNE_ANNOTATION.md` | Résultats de l'OCR, contrôles de couverture et limites de l'annotation assistée. |
| `RAPPORT_EVALUATION_LOT_PILOTE.md` | Première mesure reproductible de précision, rappel et F1 sur les douze PDF du lot pilote. |
| `resultats_appariement_lot_pilote.csv` | Détail de chaque vrai positif, faux positif et faux négatif utilisé dans le rapport. |
| `extractions_pipeline_lot_pilote.csv` | Sortie de la nouvelle pipeline : 566 candidats sur les douze PDF déjà validés. |
| `manifeste_pipeline_lot_pilote.csv` | Méthode de lecture retenue pour chaque PDF et alertes de lecture à traiter. |
| `RAPPORT_PIPELINE_LOT_PILOTE.md` | Mesure de la nouvelle pipeline : 566/566 noms détectés et 99,8 % de F1 sur l’événement principal `document + date + nom + fonction`, dans ce lot de développement. |

Le choix est reproductible : premier, médian et dernier PDF de chaque année 2015–2025, et tous les PDF de 2022 disponibles. Il met en évidence la faible couverture locale de 2022, mais il ne constitue pas un échantillon représentatif de toutes les séances du pays.

## Consignes d'annotation

1. Lire **toute la rubrique « NOMINATIONS »** du PDF, pas seulement les lignes déjà extraites. Vérifier chaque ligne `a_verifier` de `reference_annotations.csv`, ajouter les annonces manquantes et supprimer les mentions qui ne sont pas des nominations. Si le document n'a aucune nomination, le noter dans le suivi sans inventer de ligne.
2. Renseigner `document_id` exactement comme dans l'inventaire, la page du PDF et un `extrait_exact` assez court pour retrouver l'annonce. La date retenue est celle de la séance, vérifiée dans le document.
3. Utiliser `type_nomination` parmi `fonction_individuelle`, `conseil_administration` ou `autre`. Garder le libellé de la fonction tel que publié dans `fonction` ; la normalisation viendra ensuite.
4. Pour les listes introduites par « Sont nommés... », créer une ligne pour chaque personne et reprendre la fonction annoncée par l'en-tête de liste.
5. Laisser une valeur vide si elle n'est pas explicitement donnée. Signaler les doutes dans `commentaire`. Ne pas déduire un ministère, un matricule ou une civilité à partir d'un autre document.
6. Après avoir fini le document, mettre `statut_verification` à `verifie_sur_pdf` pour ses lignes, puis comparer la référence avec `predictions_a_verifier.csv` ; marquer les sorties correctes, partielles et fausses. Les annonces présentes dans la référence mais absentes des prédictions sont les **faux négatifs**.

Si possible, faire annoter indépendamment au moins 20 % des documents par une deuxième personne. Conserver les deux versions et arbitrer les désaccords avant de calculer les scores.

## Exemple d'erreur déjà vérifiée

Dans `CDM - 2015_01_07.csv`, la ligne 2 attribue la direction générale de la garde de sécurité pénitentiaire à Michel KAFANDO. Le compte rendu l'attribue à Honoré Grégoire KARAMBERY. C'est un **faux positif par passage au-delà des frontières de l'annonce**. Vérifier le [compte rendu diffusé par le consulat du Burkina Faso](https://www.consulat-burkinaespagne.org/51600_fr/Compte-rendu-du-Conseil-des-ministres-du-07-janvier-2015/).

## Mesures à produire après annotation

Une prédiction est un vrai positif seulement si elle correspond à une annonce de référence et si les champs évalués sont exacts. Calculer d'abord au niveau événement : `précision = VP/(VP+FP)`, `rappel = VP/(VP+FN)`, puis `F1`. Calculer ensuite les scores par champ. Publier les résultats par année et pour les documents dont le texte est difficile à extraire. Ne pas calculer de score sur les seules prédictions, car cela masquerait les annonces manquées.

## Reproduire le lot

Dans l'environnement `memoire_env` :

```bash
jupyter lab Scripts/pipeline_et_validation/archive_mise_au_point/preparer_evaluation_extraction.ipynb
```

Le script réécrit l'inventaire, les prédictions et les alertes en conservant les décisions humaines dont la clé `(document_id, ligne_csv, raison)` reste identique. Il ne réécrit pas `reference_annotations.csv` si ce fichier existe déjà. Sauvegarder une copie de travail avant une régénération après modification des CSV sources, car les numéros de ligne peuvent alors changer.

Pour reproduire l'annotation assistée et le fichier consolidé :

```bash
jupyter lab Scripts/pipeline_et_validation/archive_mise_au_point/proposer_annotations.ipynb
jupyter lab Scripts/pipeline_et_validation/archive_mise_au_point/assembler_annotations.ipynb
```

Ces scripts ne transforment pas automatiquement les propositions en référence vérifiée. `proposer_annotations.py` réécrit les propositions issues du texte ; `assembler_annotations.py` lit la grille de travail et réécrit sa copie consolidée ainsi que le suivi, sans toucher à `reference_annotations.csv`.

Pour reproduire la première évaluation après toute correction du lot validé :

```bash
jupyter lab Scripts/pipeline_et_validation/archive_mise_au_point/evaluer_lot_pilote.ipynb
```

## Nouvelle pipeline d’extraction

Activer l’environnement puis lancer la pipeline sur un ou plusieurs PDF, ou sur le corpus local :

```bash
conda activate memoire_env
jupyter lab Scripts/pipeline_et_validation/pipeline_extraction_nominations.ipynb
```

Elle produit une table de candidats et un manifeste par PDF dans `evaluation_extraction/`. Le manifeste indique si le texte provient du PDF ou de l’OCR français. Pour mesurer les noms retrouvés contre les références validées, utiliser :

```bash
jupyter lab Scripts/pipeline_et_validation/evaluer_rappel_pipeline.ipynb
```

La documentation détaillée et les options sont dans [PIPELINE_EXTRACTION.md](PIPELINE_EXTRACTION.md). Le score du lot pilote guide le développement ; réserver des PDF non utilisés pour le test final qui servira à vérifier l’objectif de rappel de 99 %.
