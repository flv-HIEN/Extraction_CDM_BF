# Évaluation exploratoire de l’extracteur — lot pilote

*Calculée le 27 septembre 2026 à partir des 12 PDF relus intégralement.*

Le lot comporte **566 annonces de référence** dans onze documents positifs et un document négatif traité par OCR. L’extracteur contient **375 prédictions** pour ces documents.

## Détection des personnes nommées

Une prédiction est appariée une à une à une référence lorsque le document et le nom normalisé correspondent. Quand la même personne apparaît plusieurs fois dans un document, la fonction la plus semblable départage les annonces. Cette mesure indique si l’extracteur retrouve la personne dans le bon compte rendu ; les champs sont contrôlés séparément.

| VP | FP | FN | Précision | Rappel | F1 |
|---:|---:|---:|---:|---:|---:|
| 366 | 9 | 200 | 97.6% | 64.7% | 77.8% |

L’extracteur produit peu de personnes hors référence (9 faux positifs), mais omet 200 annonces. Les faux positifs incluent les signatures du Président du Faso ou du Premier ministre reprises comme si elles étaient des nominations.

## Événement avec fonction exacte

Une annonce est considérée exacte sur le noyau `document + date + nom + fonction` seulement si ces quatre éléments concordent après normalisation des accents, de la casse et de la ponctuation.

| Annonces exactes | Précision | Rappel | F1 |
|---:|---:|---:|---:|
| 339 | 90.4% | 59.9% | 72.1% |

## Exactitude des champs parmi les personnes appariées

Un champ est comparé seulement lorsqu’il est renseigné à la fois dans la prédiction et la référence. Le dénominateur ne mesure donc pas la couverture d’un champ vide.

| Champ | Correct | Comparable | Exactitude |
|---|---:|---:|---:|
| `date_conseil` | 361 | 366 | 98.6% |
| `civilite` | 366 | 366 | 100.0% |
| `matricule` | 344 | 344 | 100.0% |
| `fonction` | 344 | 366 | 94.0% |
| `ministere` | 321 | 353 | 90.9% |

## Résultats par document

| Document | Prédictions | Références | VP | FP | FN | Événements exacts | Précision | Rappel | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CDM - 2015_07_01.pdf | 6 | 7 | 5 | 1 | 2 | 0 | 83.3% | 71.4% | 76.9% |
| CDM - 2016_01_16.pdf | 0 | 0 | 0 | 0 | 0 | 0 | — | — | — |
| CDM - 2017_01_05.pdf | 25 | 32 | 24 | 1 | 8 | 24 | 96.0% | 75.0% | 84.2% |
| CDM - 2024_07_10.pdf | 11 | 16 | 10 | 1 | 6 | 10 | 90.9% | 62.5% | 74.1% |
| CDM - 2021_06_09.pdf | 0 | 36 | 0 | 0 | 36 | 0 | — | 0.0% | 0.0% |
| CDM - 2020_01_08.pdf | 41 | 55 | 40 | 1 | 15 | 37 | 97.6% | 72.7% | 83.3% |
| CDM - 2023_01_11.pdf | 55 | 69 | 55 | 0 | 14 | 54 | 100.0% | 79.7% | 88.7% |
| CDM - 2016_12_28.pdf | 35 | 59 | 34 | 1 | 25 | 34 | 97.1% | 57.6% | 72.3% |
| CDM - 2018_06_18.pdf | 30 | 70 | 29 | 1 | 41 | 20 | 96.7% | 41.4% | 58.0% |
| CDM -2019_10_30.pdf | 105 | 126 | 104 | 1 | 22 | 98 | 99.0% | 82.5% | 90.0% |
| CDM - 2022_06_16.pdf | 15 | 26 | 14 | 1 | 12 | 12 | 93.3% | 53.8% | 68.3% |
| CDM - 2025_06_18.pdf | 52 | 70 | 51 | 1 | 19 | 50 | 98.1% | 72.9% | 83.6% |

Le document négatif du 16 janvier 2016 ne comporte ni prédiction ni référence : une précision et un F1 ne sont donc pas définis pour lui. Le document du 9 juin 2021 contient 36 nominations de conseils d’administration et aucune prédiction : il montre une lacune importante de couverture.

## Limites d’interprétation

Ce lot sert à la mise au point et à l’évaluation exploratoire : des documents ont été examinés pendant la conception de l’annotation assistée. Ces résultats ne sont pas un test final indépendant. Réserver un autre échantillon, non consulté pendant les ajustements, avant de publier une performance finale.

Les détails de chaque appariement, faux positif et faux négatif sont dans [`resultats_appariement_lot_pilote.csv`](resultats_appariement_lot_pilote.csv). Ils permettent d’examiner les erreurs de fonction et de compléter une typologie d’erreurs dans le mémoire.
