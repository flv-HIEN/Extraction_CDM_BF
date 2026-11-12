# Audit de ministere_analyse et référentiel historique — 11 novembre 2026

## Diagnostic prioritaire

La cause est reproduite : des sous-rubriques de représentation deviennent des valeurs de `ministere` à l'extraction ; le notebook les recopie dans `ministere_analyse` sans contrôle de type. Une seconde confusion touche les ministères représentés dans les conseils, distincts du ministère de la rubrique. Une concordance vers 2026 ajoute un risque indépendant de fusion de périmètres historiques.

**Aucun pipeline, notebook ni export de production n'a été modifié.** Les nouveaux fichiers sont dans ce dossier uniquement. Le script d'audit est autonome ; RapidFuzz a été installé dans l'environnement `memoire_env` pour produire les scores.

## Périmètre et unité statistique

Source : `normalisation/fiabilisation/nominations_2015_2025_fiabilise.csv` ; SHA-256 `7a1019a177321bad6ca23fde10ba025ef643f81d96cc0becef419b39632230df`.

- 23183 enregistrements sources ; 23183 après date valide, poste non vide et restriction explicite à 2015–2025.
- 1194 libellés distincts de `ministere_analyse`, après nettoyage des espaces et remplacement du vide.
- 2032 lignes et 762 libellés signalés par des règles lexicales prudentes. **Ce ne sont pas autant d'erreurs démontrées** : les institutions non ministérielles légitimes sont aussi signalées pour les séparer des ministères.
- Les nombres portent sur des lignes candidates, pas des personnes distinctes ni des événements validés. Le filtre du notebook ne dédoublonne pas et n'exige pas `conserver_evenement`. L'audit ne transforme pas ces totaux en statistiques finales.

`frequences_ministere_analyse.csv` fournit chaque libellé, sa fréquence, sa part et onze colonnes annuelles. `ministeres_valeurs_suspectes.csv` fournit une ligne par nomination signalée avec identifiant, date, PDF, page, extrait initial et contexte natif relu. `ligne_csv` désigne le numéro d'enregistrement augmenté de l'en-tête, pas une ligne physique dans un CSV multiligne. Les pages sont les pages PDF à partir de 1. `nom_retrouve_texte_natif=0` exige une vérification visuelle/OCR ; ce n'est pas une preuve d'absence.

| Année | Lignes | Libellés distincts | Lignes signalées |
|---|---:|---:|---:|
| 2015 | 2610 | 202 | 253 |
| 2016 | 2633 | 204 | 306 |
| 2017 | 2160 | 203 | 267 |
| 2018 | 2044 | 186 | 190 |
| 2019 | 1769 | 166 | 198 |
| 2020 | 1415 | 115 | 112 |
| 2021 | 1874 | 130 | 144 |
| 2022 | 1844 | 167 | 155 |
| 2023 | 2296 | 119 | 145 |
| 2024 | 2130 | 112 | 113 |
| 2025 | 2408 | 119 | 149 |

### Classification indicative

| Classe | Lignes |
|---|---:|
| ministere_apparent_a_verifier | 21151 |
| institution_non_ministerielle_apparente | 1056 |
| titre_contamine_probable | 454 |
| libelle_ambigu_a_verifier | 287 |
| categorie_representation_probable | 235 |

### Libellés les plus fréquents

| Libellé | Fréquence |
|---|---:|
| MINISTERE DE L’ECONOMIE, DES FINANCES ET DU DEVELOPPEMENT | 978 |
| MINISTERE DE L’ADMINISTRATION TERRITORIALE, DE LA DECENTRALISATION ET DE LA SECURITE | 889 |
| MINISTERE DE L’ADMINISTRATION TERRITORIALE, DE LA DECENTRALISATION ET DE LA SECURITE INTERIEURE | 726 |
| MINISTERE DE L’ECONOMIE ET DES FINANCES | 714 |
| MINISTERE DE LA JUSTICE, DES DROITS HUMAINS ET DE LA PROMOTION CIVIQUE | 697 |
| MINISTERE DE L’ENSEIGNEMENT SUPERIEUR, DE LA RECHERCHE SCIENTIFIQUE ET DE L’INNOVATION | 635 |
| MINISTERE DE LA SECURITE | 629 |
| MINISTERE DE L’ECONOMIE, DES FINANCES ET DE LA PROSPECTIVE | 582 |
| MINISTERE DE L’ENSEIGNEMENT SUPERIEUR, DE LA RECHERCHE ET DE L’INNOVATION | 550 |
| MINISTERE DE LA JUSTICE ET DES DROITS HUMAINS, CHARGE DES RELATIONS AVEC LES INSTITUTIONS | 485 |
| MINISTERE DE L’ENVIRONNEMENT, DE L’EAU ET DE L’ASSAINISSEMENT | 391 |
| PRESIDENCE DU FASO | 390 |
| MINISTERE DE L’EDUCATION NATIONALE ET DE L’ALPHABETISATION | 377 |
| MINISTERE DE L’ADMINISTRATION TERRITORIALE ET DE LA DECENTRALISATION | 341 |
| MINISTERE DE LA CULTURE, DES ARTS ET DU TOURISME | 331 |

## Localisation exacte de la construction et cause

1. `analyses/test3_avant_fiabilisation.ipynb`, cellule Python d'indice **6** (septième cellule), construit la colonne directement :

```python
donnees_evolution["ministere_analyse"] = (
    donnees_evolution["ministere"].astype("string").fillna("").str.strip()
    .replace("", "Ministère non renseigné")
)
```

Il n'existe donc pas de fonction dédiée qui valide un ministère à cette étape. La cellule 7 agrège ces chaînes. La cellule 2 indique `sep=';'`, alors que le fichier actuel est séparé par des virgules : son exécution fraîche doit être corrigée lors de la reprise du notebook. Les sorties sauvegardées ne démontrent pas que le code courant a été réexécuté.

2. `extraction_evaluation/archives/scripts_corpus/extraire_nominations_2015.py`, fonction **`extract_from_pdf`**, lignes 461–477 : les expressions `AU TITRE DU/DE LA/DES…` produisent des événements `ministry` même pour des catégories de personnes. Lignes 785–798 : `if is_ministry or not group_post: ministry = candidate` autorise une catégorie lorsque le poste collectif est vide. Ce poste est réinitialisé aux changements de section/décret (lignes 805–812). L'état de la liste de personnes contrôle ainsi à tort la nature institutionnelle d'une rubrique. Le nettoyage `clean_ministry` n'est pas une validation de type.

3. La réexécution en mémoire de cet extracteur archivé, sans OCR, sur les PDF du 27 janvier et du 28 octobre 2015 retrouve les valeurs litigieuses ; voir `comparaison_extracteurs.csv`. Cela établit un mécanisme reproductible compatible avec les exports, sans prétendre reconstituer la commande historique exacte qui les a générés.

4. L'extracteur actuel `extraction_evaluation/extraire_nominations_2015.py` contient déjà `detect_rattachements` (ligne 104) et `context_resolver` (ligne 135) : catégorie conservée séparément, réinitialisation aux sections, rejet de titres suspects. Le rapport local `extraction_evaluation/evaluation/RAPPORT_TEST_RATTACHEMENTS_CORRIGE_DEVELOPPEMENT_12.md` précise que ses essais n'ont pas remplacé les données de production. La base analysée conserve les anciennes catégories.

5. **Limite persistante du code actuel** : `context_resolver` traite le dernier « Au titre du ministère… » comme nouveau parent et les catégories suivantes en héritent. Pour Kayouré Idrissa IMMA, le résultat devient le ministère de la Communication (tronqué), alors que la rubrique B, page 31, est le **ministère de la Culture et du Tourisme** et l'organisme nommé est le **BBDA**. Remplacer les exports par cette seule version ne suffit donc pas.

## Cas vérifiés dans le texte PDF

| Valeur | Personne | PDF | Page | Conclusion |
|---|---|---|---:|---|
| Artistes-interprètes ou exécutants | Bali Bertrand BAZIE dit Bazbill | CDM - 2015_01_27.pdf | 34 | Qualité de représentation au BBDA ; rubrique ministérielle B page 31 : Culture et Tourisme. |
| Auteurs compositeurs d’œuvres musicales traditionnelles | Kayouré Idrissa IMMA dit Kisto Koinbré | CDM - 2015_01_27.pdf | 32 | Catégorie de représentation ; le dernier ministère cité page 32 représente un autre siège. |
| étudiants | Hassane OUEDRAOGO | CDM - 2015_10_28.pdf | 22 | La sous-rubrique « Au titre des étudiants » n'est pas une institution ; le bloc commence sur la page précédente. |
| Personnel de l’Office national d’identification | Moustapha KAFANDO | CDM - 2015_10_28.pdf | 20 | Représentant du personnel de l'ONI ; rubrique A : ministère de la Sécurité. |

Les extraits et identifiants des nominations sont dans le CSV des suspects. La revue doit remonter avant la page de la personne lorsque le bloc a commencé sur une autre page ; un voisinage de texte seul ne suffit pas à attribuer une tutelle.

## Corrections proposées, sans application

Séparer dans chaque nomination : `ministere_rubrique_brut`, `organisme_conseil_brut`, `entite_representee_brut`, `categorie_representation`, `type_rattachement`, `rattachement_source`, page et positions du titre parent. Pour les conseils, un titre principal change la rubrique ; « Au titre du ministère X » change l'entité représentée ; « Au titre du personnel/des étudiants… » change la catégorie. Aucun de ces deux derniers événements ne doit écraser la rubrique. Un nouveau décret réinitialise l'organisme et la représentation, mais la rubrique reste valide jusqu'au titre principal suivant. Ne pas inférer juridiquement la tutelle de l'organisme à partir de la seule rubrique éditoriale.

Conserver `ministere` initial sans écrasement. Une catégorie prouvée quitte le champ ministériel d'analyse mais sa nomination demeure comptée ; affectation en `rattachement_a_valider` si le parent manque. Une présidence, une autorité ou une chambre peut être une institution valide, sans devenir un ministère. Un titre tronqué doit rester à vérifier ; un simple préfixe « Ministère » n'est pas une validation. Ne pas supprimer les lignes suspectes des totaux de nominations.

La normalisation `normaliser_nominations_2015_2025.py::chercher_regle` utilise déjà SequenceMatcher avec seuil 0,93, des préfixes et des alias ; elle renvoie vide pour les catégories. Elle ne répare donc pas `ministere_analyse`, qui lit le brut. `fusion_denominations.py::fusionner` peut produire `fusion_automatique_table` pour un code unique, y compris certains regroupements : un code analytique unique n'établit pas la continuité historique.

La table `table_concordance_ministeres_2015_2025_vers_2026.py` est une projection analytique avec conventions explicites. Exemples : Environnement vers AGRI_EAU_RAH ; Infrastructures et Habitat vers CONSTRUCTION_PATRIE ; Communication et Culture regroupées. Conserver ces codes éventuellement pour une analyse thématique séparée ; ne pas les utiliser comme identifiants historiques.

## Modèle historique proposé

| Champ | Règle |
|---|---|
| nom brut | Texte source immuable, PDF/page/positions associés. |
| nom normalisé | Nettoyage lexical seulement ; intitulé officiel distinct après vérification. |
| identifiant institution | Identifiant pérenne attribué après validation documentaire ; vide avant validation. |
| identifiant de version d'appellation | Une version datée par épisode documenté ; même nom à deux époques ne prouve pas une identité. |
| famille institutionnelle | Regroupement analytique éventuellement multiple, daté, justifié ; ne fusionne pas les institutions. |
| type | Ministère, présidence, primature, autorité, établissement public, organisation représentée, catégorie de personnes, inconnu. |
| validation | Observé ; à valider ; appellation attestée ; continuité validée ; rejeté ; ambigu. |
| validité | Début inclus, fin exclue ; acte source, date de l'acte et date d'effet distinctes. Date inconnue laissée vide. |
| relations | prédécesseur/successeur, renommage, fusion, scission, transfert de compétences ; acte, date, source et validation propres. |

Une fusion/scission crée des relations entre identifiants distincts. Un renommage conserve éventuellement l'identifiant seulement après preuve. Ne jamais traduire une absence d'une composition en disparition certaine, ni la dernière nomination observée en fin de validité.

Le référentiel livré inventorie les formes institutionnelles apparentes rencontrées. `IP_` et `VP_` sont des **identifiants provisoires lexicaux**, pas des identités administratives validées. `id_institution_valide` reste vide ; la famille reste `a_valider`. `premiere_observation` et `derniere_observation` ne sont pas des périodes juridiques ; `validite_debut` et `validite_fin` restent vides tant que les bornes ne sont pas justifiées. Les titres courts ou trompeurs peuvent encore être présents : c'est un référentiel de travail à contrôler.

## Sources historiques effectivement examinées et lacunes

Le décret local `donnees/decrets_remaniement/decret_remaniement2017.pdf`, n° 2017-075, daté du 20 février 2017, énumère notamment Sécurité, Administration territoriale et Décentralisation, Énergie, Mines et Carrières en portefeuilles distincts. Le script marque uniquement les intitulés complets retrouvés avant le nom du titulaire dans ce texte avec date et page. Cela atteste une appellation à cette date ; aucune relation de continuité n'en est déduite. Un décret de composition ne suffit pas toujours à établir les transferts de compétences : rechercher aussi les attributions et organisations.

Le [compte rendu officiel RTB du 12 mars 2025](https://www.rtb.bf/2025/03/12/compte-rendu-du-conseil-des-ministres-du-12-mars-2025/) décrit un retrait de la certification professionnelle de Burkina Suudu Bawdè vers la DGECC. Ce cas confirme l'intérêt de dater aussi les transferts de missions, indépendamment des noms. Ce changement n'est pas extrapolé aux autres institutions.

Le dictionnaire historique local et ses liens constituent un index de recherche, pas une preuve automatiquement validée. Sa première composition de 2015 commence le 19 juillet : elle ne couvre pas janvier–juin. `formationGouv2016.pdf` est décrit comme un texte d'attributions du 6 février, distinct de la composition du 12 janvier. Le nom du PDF de mars 2022 et la date annoncée divergent : vérifier le contenu et la date d'effet. Le PDF local `Remaniement-aout-2024.pdf` ne fournit pratiquement pas de texte natif : OCR/revue nécessaires. L'ancienne URL officielle MAE du décret 2017 renvoie 404 à la consultation ; le PDF local reste lisible. L'absence annoncée de changement en 2025 n'a pas été validée exhaustivement ici. **Aucune borne ou évolution supplémentaire n'est inventée.**

## Similarité : propositions uniquement

`correspondances_institutions_a_valider.csv` contient trois voisins par clé ministérielle apparente, avec scores et périodes d'observation, sans application. La recherche ne dépend pas d'un seuil et peut donc fournir des voisins médiocres : les scores servent à ordonner la revue. Catégories et institutions non ministérielles ne sont pas rapprochées d'un ministère par ce mécanisme.

Le [ratio RapidFuzz](https://rapidfuzz.github.io/RapidFuzz/Usage/fuzz.html) mesure une similarité Indel normalisée ; ce n'est pas la distance de Levenshtein. Nous livrons séparément ratio, token_sort_ratio, token_set_ratio, distance de Levenshtein à coûts unitaires et similarité de Levenshtein ramenée sur 100. `token_set_ratio` peut masquer un ajout de portefeuille : ne pas décider sur ce score.

La [distance de Levenshtein](https://rapidfuzz.github.io/RapidFuzz/Usage/distance/Levenshtein.html) mesure les insertions, suppressions et substitutions minimales. Les chaînes sont comparées après normalisation explicite de casse, accents et ponctuation, sans retirer les mots porteurs de compétences. Même un score de 100 ne valide ni les dates ni l'identité juridique. Un seuil élevé peut prioriser les fautes typographiques ; il doit être calibré sur des décisions humaines et ne déclenche aucune fusion.

## Priorités sur trois jours

1. **Jour 1 : réparer le sens des rattachements.** Valider les exemples ci-dessus et une liste ciblée de cas transversaux : rubrique principale, représentation ministérielle, catégorie, changement de page/décret, institution non ministérielle et titre OCR. Corriger seulement après cette revue la machine d'états ; réextraire vers un dossier distinct, comparer les multiensembles de nominations avant/après pour détecter pertes, doublons et changements de poste. Corriger le séparateur de lecture du notebook.
2. **Jour 2 : valider les libellés qui couvrent le plus de nominations.** Traiter les intitulés fréquents avant la longue traîne, documenter les dates nécessaires aux graphiques, garder les identités distinctes en l'absence de preuve. Vérifier les sources officielles et les dates d'effet pour chaque rapprochement utilisé ; OCR des actes utiles seulement. Réserver RapidFuzz à la file de revue.
3. **Jour 3 : figer les statistiques avec traçabilité.** Utiliser les événements dédoublonnés, annoncer l'unité (nomination ou personne), fixer la définition du rattachement étudié, afficher les inconnus et la couverture validée par année. Comparer résultats sur tous les événements et sur rattachements validés ; publier les écarts et l'empreinte des données. Distinguer ministère historique, famille thématique et représentation. Éviter les conclusions de trajectoires institutionnelles tant que les continuités ne sont pas prouvées.

Critère de sortie : aucune catégorie connue dans les ministères validés ; aucune fusion non documentée ; aucune perte inexpliquée de nomination ; incertitudes visibles et dénominateurs stables. L'exhaustivité du référentiel juridique 2015–2025 n'est pas requise pour publier des fréquences d'appellations historiques clairement délimitées.

## Reproduction et contrôles

```bash
/home/flaviehien/miniconda3/envs/memoire_env/bin/python normalisation/ministeres/audit_historique/generer_audit.py
python3 normalisation/ministeres/audit_historique/rediger_audit.py
```

Le script lit les données et les PDF locaux, produit les CSV et le bilan JSON dans ce dossier ; il ne lance pas de pipeline de production. Les contrôles de cohérence comparent les sommes globales/annuelles aux lignes filtrées, les lignes suspectes à leur sous-ensemble et les scores à leurs bornes. Parmi les lignes signalées, 1 995 noms sont retrouvés tels quels dans le texte natif de la page et 37 ne le sont pas ; ces 37 cas restent à revoir, sans attribution automatique. Les comparaisons d'extracteurs portent sur deux PDF de diagnostic et ne constituent pas une évaluation de précision/rappel de tout le corpus.

Référentiel : 566 formes ; propositions : 609 paires orientées ; attestations locales du décret 2017 : 118 formes.
