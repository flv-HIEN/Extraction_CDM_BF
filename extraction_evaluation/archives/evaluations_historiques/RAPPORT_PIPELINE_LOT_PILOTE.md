# Évaluation de la pipeline — lot_pilote_12_documents

*Calculée à partir de la sortie indiquée à l’exécution et des 12 PDF du lot.*

La mesure normalise la casse, les accents et la ponctuation. La ligne **événement principal** est l’indicateur à retenir : une prédiction doit avoir le même document, la même date, le même nom et la même fonction que la référence. La détection de personne est conservée pour diagnostiquer les noms manqués ; elle ne suffit pas à déclarer une nomination correcte.

| Niveau | Champs exigés | VP | FP | FN | Précision | Rappel | F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| détection de personne | `document_id + nom` | 566 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| événement principal | `document_id + date_conseil + nom + fonction` | 565 | 1 | 1 | 99.8% | 99.8% | 99.8% |
| événement complet | `document_id + date_conseil + nom + fonction + ministere + type_nomination` | 565 | 1 | 1 | 99.8% | 99.8% | 99.8% |

Les éventuels écarts de l’événement principal sont dans `ecarts_pipeline_lot_pilote.csv`. Cette évaluation sert au développement : le lot pilote ne doit pas être utilisé pour déclarer une performance finale, car ses PDF ont été consultés pendant l’amélioration des règles.
