# Test de développement : détection des rattachements

12 PDF traités sans OCR, sorties séparées des anciennes extractions.

| Indicateur | Avant | Test |
|---|---:|---:|
| Nominations candidates | 516 | 473 |
| Libellés ministériels distincts non vides | 134 | 85 |
| Lignes classées comme institutions | Non séparées | 11 |

Les 473 candidats retrouvés correspondent tous à une paire document/nom précédemment présente. 43 occurrences ne sont plus retrouvées ; aucune nouvelle occurrence n'est ajoutée à ce niveau de comparaison. Cela ne prouve pas que ces 43 anciennes lignes étaient toutes correctes ni que les 473 nouvelles sont validées. Le lot ne dispose pas ici d'une référence humaine exhaustive utilisée pour ce test : aucun score de précision/rappel/F1 n'est annoncé.

**Version non validée pour réextraction du corpus : examiner et corriger la régression potentielle de détection.** La réduction du nombre de libellés ne suffit pas à conclure à une amélioration.

| Document | Avant | Test |
|---|---:|---:|
| CDM - 2018_12_31.pdf | 0 | 0 |
| CDM - 2020_02_26.pdf | 51 | 51 |
| CDM - 2023_06_29.pdf | 40 | 37 |
| CDM - 2023_10_11.pdf | 69 | 69 |
| CDM - 2021_03_03.pdf | 31 | 29 |
| CDM - 2019_03_06.pdf | 11 | 11 |
| CDM - 2021_09_22.pdf | 97 | 92 |
| CDM - 2016_01_20.pdf | 1 | 1 |
| CDM - 2023_10_25.pdf | 94 | 90 |
| CDM - 2015_12_23.pdf | 0 | 0 |
| CDM - 2015_10_28.pdf | 46 | 17 |
| CDM - 2019_04_30.pdf | 76 | 76 |

Les lignes absentes sont dans `test_rattachements_developpement_12_lignes_absentes.csv`. Les anciens résultats des trois lots et les annotations de référence n'ont pas été modifiés.
