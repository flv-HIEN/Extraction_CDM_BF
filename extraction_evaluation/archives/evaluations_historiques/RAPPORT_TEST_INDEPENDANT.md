# Évaluation de la pipeline — lot_test_independant

*Calculée à partir de la sortie indiquée à l’exécution et des 28 PDF du lot.*

La mesure normalise la casse, les accents et la ponctuation. La ligne **événement principal** est l’indicateur à retenir : une prédiction doit avoir le même document, la même date, le même nom et la même fonction que la référence. La détection de personne est conservée pour diagnostiquer les noms manqués ; elle ne suffit pas à déclarer une nomination correcte.

| Niveau | Champs exigés | VP | FP | FN | Précision | Rappel | F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| détection de personne | `document_id + nom` | 709 | 5 | 33 | 99.3% | 95.6% | 97.4% |
| événement principal | `document_id + date_conseil + nom + fonction` | 693 | 21 | 49 | 97.1% | 93.4% | 95.2% |
| événement complet | `document_id + date_conseil + nom + fonction + ministere + type_nomination` | 693 | 21 | 49 | 97.1% | 93.4% | 95.2% |

Les éventuels écarts de l’événement principal sont dans `ecarts_test_independant.csv`. Cette évaluation sert au développement : le lot pilote ne doit pas être utilisé pour déclarer une performance finale, car ses PDF ont été consultés pendant l’amélioration des règles.
