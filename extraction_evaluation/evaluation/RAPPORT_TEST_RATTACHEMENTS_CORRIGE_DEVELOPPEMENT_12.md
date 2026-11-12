# Retest après correction des phrases multilignes

12 PDF traités, sans OCR, avec des sorties distinctes des extractions de production.

| Indicateur | Ancienne extraction | Premier test | Correction |
|---|---:|---:|---:|
| Nominations candidates | 516 | 473 | 516 |
| Libellés ministériels non vides distincts | 134 | 85 | 99 |

Les 43 occurrences document/nom absentes du premier test sont toutes retrouvées. Le multiensemble document/nom de l'extraction initiale et celui du retest sont identiques. Ce contrôle ne prouve pas l'exactitude de toutes les fonctions et affectations institutionnelles.

La vue structurée conserve les lignes pour détecter les titres. Une seconde vue remplace chaque saut de ligne par un espace, en conservant les offsets, pour reconnaître les annonces collectives. Un contrôle rejette les introductions de listes qui traverseraient la rubrique ou le décret suivant.

13 lignes sont classées comme institutions et 503 comme ministères. Aucune de ces 516 lignes ne déclenche d'alerte de titre manquant ; cela ne vaut pas validation humaine. La baisse des libellés ne remplace pas une mesure de précision/rappel. Les deux PDF sans candidat restent présents dans le manifeste.

Tests : 8 tests d'extraction, dont les listes collectives multilignes et la non-traversée des titres ; 16 tests de normalisation. Les extractions de production des trois lots, les annotations humaines et la base fiabilisée ne sont pas modifiées.
