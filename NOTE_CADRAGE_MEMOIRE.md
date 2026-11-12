# Renforcer le mémoire : extraction des nominations dans les comptes rendus du Conseil des ministres

*Note de travail fondée sur les fichiers du dossier, audit du 24 septembre 2026.*

## 1. Apport scientifique et utilité publique

**Titre proposé** — *Extraction traçable des nominations dans les comptes rendus du Conseil des ministres du Burkina Faso et analyse de leur évolution temporelle.*

**Question centrale** — Dans quelle mesure peut-on construire, à partir des comptes rendus publics, une base de nominations suffisamment fiable et traçable pour suivre les tendances par période, ministère, fonction et civilité ?

L'apport le plus défendable est un **observatoire reproductible des nominations annoncées** : chaque donnée renvoie à son document et à son passage source, les erreurs d'extraction sont mesurées, et les graphiques signalent les lacunes du corpus. Il peut aider les chercheurs, journalistes et administrations à retrouver les annonces et à comparer leur distribution dans le temps. Il ne mesure ni la qualité des personnes nommées, ni l'efficacité des politiques publiques.

La source officielle publie des comptes rendus avec une rubrique de nominations ; certains distinguent les nominations individuelles de celles dans les conseils d'administration. Il faut donc définir explicitement le périmètre étudié. Voir la [page des comptes rendus de la Présidence du Faso](https://www.presidencedufaso.bf/compte-rendu-du-conseil-des-ministres/) et un [exemple du Service d'information du Gouvernement](https://www.sig.gov.bf/actualites/details?cHash=e6789260bd9fa418c7991b6d1f4a8481&tx_news_pi1%5Baction%5D=detail&tx_news_pi1%5Bcontroller%5D=News&tx_news_pi1%5Bnews%5D=2216).

## 2. Ce que montrent les fichiers actuels

| Constat vérifié | Conséquence pour le mémoire |
|---|---|
| `total_donnees` contient 406 PDF et 353 CSV ; 7 PDF portent 2022 dans leur nom. | Un creux en 2022 peut venir d'une collecte incomplète. Construire d'abord un inventaire des séances attendues, trouvées, lues et extraites. Des [comptes rendus officiels de 2022](https://www.sig.gov.bf/fileadmin/user_upload/CONSEIL_DES_MINISTRES_N__018_DU_29_JUIN_2022.pdf) sont accessibles. |
| Les 353 CSV contiennent 12 472 lignes, dont 322 répétitions sur la clé provisoire `(date, nom, poste, ministère)` ; cette clé peut aussi fusionner de vrais événements distincts. | Mesurer et examiner les doublons avant toute série temporelle. |
| `Scripts/nominations_pseudonymised.csv` contient 2 910 lignes, 851 identifiants et 307 dates ; le notebook source applique `NB_OCC_MIN = 3`. | Ce fichier est un sous-échantillon de personnes souvent citées. Ses proportions et tendances ne représentent pas l'ensemble des nominations. Conserver une table complète pour l'analyse descriptive, puis créer une cohorte distincte pour les parcours. |
| Le fichier final contient 129 lignes codées `F` sur 2 910 (4,4 %). Dans les CSV sources, 737 lignes sur 12 472 ont la civilité `Madame` (5,9 %). | Ces taux décrivent les **lignes présentes dans ces fichiers**, pas la part des femmes dans la fonction publique ni un écart d'accès aux postes. Le filtre et les erreurs d'extraction peuvent modifier le résultat. |
| Le CSV du 7 janvier 2015 attribue à Michel KAFANDO une nomination à la direction de la garde de sécurité pénitentiaire, avec ministère vide. Le [compte rendu diffusé par le consulat du Burkina Faso](https://www.consulat-burkinaespagne.org/51600_fr/Compte-rendu-du-Conseil-des-ministres-du-07-janvier-2015/) attribue cette nomination à Honoré Grégoire KARAMBERY. | Faux positif avéré : les règles doivent isoler la rubrique et rattacher nom, fonction et ministère au **même passage**. |
| Les notebooks construisent `end_date` avec la date de la nomination suivante, puis avec une date fixe pour le dernier événement. | Cela ne prouve pas la durée effective d'occupation du poste. Une personne peut recevoir plusieurs nominations, et la fin d'une fonction n'est pas nécessairement annoncée au conseil. |

Ces chiffres proviennent d'un comptage des fichiers et lignes ; ils ne sont pas encore des indicateurs validés par annotation humaine.

## 3. Hypothèses de recherche et indicateurs

1. **H1 — Qualité d'extraction.** Un repérage des rubriques et des phrases de nomination, suivi d'une extraction contrôlée des arguments, réduit les faux positifs par rapport aux règles actuelles. Mesures : précision, rappel et F1 au niveau de l'**événement complet** et de chaque champ (nom, fonction, ministère, date).
2. **H2 — Couverture documentaire.** Les variations du nombre brut de nominations dépendent en partie du nombre de comptes rendus disponibles et exploitables. Mesures : taux de couverture par année ; nominations par séance documentée ; part des documents sans texte récupérable ; intervalle de confiance ou au minimum effectifs sous chaque graphique.
3. **H3 — Analyse temporelle.** Une fois la couverture et la qualité contrôlées, on peut décrire l'évolution des types de fonctions et des ministères. Mesures : distribution annuelle ou trimestrielle, avec versions brutes et normalisées par séance ; périodes incomplètes signalées.
4. **H4 — Parcours observés.** Chez les personnes liées avec confiance, les suites de **nominations observées** présentent des motifs récurrents. Mesures : transitions entre catégories de fonction et de ministère, avec nombre de personnes et proportion de liens vérifiés. Ne pas appeler ces intervalles des durées de mandat.

## 4. Protocole de données et d'évaluation

### 4.1 Inventaire et unité d'observation

Faire un registre `documents.csv` : `document_id`, date indiquée dans le texte, date du fichier, URL officielle, format, nombre de pages, texte extrait oui/non, rubrique nominations oui/non, raison d'échec. Vérifier les décalages entre date du titre, date de réunion et date de publication. L'unité d'observation principale est **l'annonce de nomination**, pas la personne, la phrase ou le PDF.

Créer une table `nominations.csv` : `event_id`, `document_id`, `date_conseil`, `type_nomination` (individuelle / conseil d'administration / autre), `nom_brut`, `matricule_brut` si nécessaire pour l'appariement interne, `fonction_brute`, `fonction_normalisee`, `ministere_brut`, `ministere_normalise`, `civilite`, `extrait_source`, `page`, `confiance`, `statut_validation`. La normalisation doit conserver la valeur brute et sa version de référence. Ne pas publier les matricules ni les extraits personnels dans un jeu public sans examen adapté.

### 4.2 Jeu de référence

Choisir environ 30 à 40 comptes rendus, stratifiés par année, format, longueur et présence de listes particulières ; surreprésenter 2022 et les documents où les règles échouent. Annoter toutes les annonces dans ces documents, y compris les **zéros**. Écrire des consignes pour les cas ambigus : listes groupées, nominations en conseil d'administration, mentions du président en introduction, noms composés, ministère implicite. Faire annoter indépendamment au moins 20 % du lot par une seconde personne si possible et arbitrer les désaccords.

Séparer les documents de développement et de test. Ne jamais régler les règles sur le test. Comparer la méthode actuelle à une chaîne corrigée : détection de rubrique → segmentation de l'annonce → extraction des champs → contrôles de cohérence. Publier une matrice d'erreurs et 5 à 10 exemples anonymisés ou limités aux informations déjà publiques, avec lien vers la source.

### 4.3 Contrôles automatiques

- Rejeter une nomination extraite de l'introduction avant la rubrique de nominations, sauf vérification explicite.
- Détecter les lignes sans ministère, date, fonction ou passage source ; compter séparément les cas où le ministère est légitimement absent.
- Signaler les mêmes `(personne, fonction, date)` répétés et les mêmes personnes avec plusieurs fonctions le même jour pour contrôle humain.
- Comparer, par document, le nombre de puces ou entrées de la rubrique au nombre d'événements extraits ; cette comparaison est un signal, pas une vérité terrain.
- Vérifier les résultats par année et par format PDF/HTML afin de détecter une qualité très inégale.

## 5. Analyse temporelle et rôle de Tanat

La **série temporelle principale** doit utiliser tous les événements validés : nombre de nominations par mois ou trimestre et nombre par séance disponible. Afficher le nombre de documents en parallèle. Un mois sans document doit être marqué `donnée manquante` plutôt que `zéro nomination`. Éviter une prévision ARIMA tant que le corpus est incomplet et que la qualité d'extraction n'est pas mesurée. Les ruptures politiques ou administratives éventuelles demandent une interprétation documentaire ; une courbe seule n'établit pas une cause.

Pour **Tanat**, représenter chaque nomination comme un **événement daté** et analyser les séquences d'événements : première nomination observée, succession de fonctions, changements de ministère, motifs de mobilité. Une séquence d'états avec une date de fin n'est justifiée que si la fin du poste est documentée par une autre source. Le temps entre deux nominations peut être publié sous le nom « intervalle entre annonces observées », avec censure en début et fin de période, et jamais comme « durée de poste ».

L'appariement des personnes doit être évalué à part. Un matricule identique est un indice fort, mais les absences, erreurs OCR et homonymies imposent une catégorie `lien incertain`. Les identifiants pseudonymes créés à partir du nom et du matricule peuvent encore être réidentifiables par recoupement ; séparer la table interne de correspondance des résultats diffusés.

## 6. Résultats à livrer

1. **Corpus documenté** : inventaire, taux de couverture, règles de collecte et provenance.
2. **Extracteur évalué** : code reproductible, consignes d'annotation, jeu de référence, précision/rappel/F1, typologie des erreurs.
3. **Table d'événements contrôlée** : nominations et passages sources, avec statut de validation.
4. **Analyse descriptive et Tanat** : graphiques normalisés, motifs de nominations observées, analyses de sensibilité avec et sans les événements incertains et les années incomplètes.
5. **Restitution publique légère** : tableaux agrégés par période et catégorie, recherche par document source, limites de couverture visibles.

## 7. Plan de mémoire proposé

1. **Introduction** — contexte burkinabè, problème de données non structurées, question de recherche, limites, contributions.
2. **État de l'art ciblé** — extraction d'événements administratifs, appariement d'entités, évaluation des corpus, analyse de séquences ; terminer chaque partie par ce qui manque pour le cas étudié. Le chapitre 2 actuel expose NER, relations et événements, mais relie encore peu ces méthodes au type exact d'annonce à extraire et à l'évaluation envisagée.
3. **Corpus et méthode** — collecte, annotation, schéma, extraction, normalisation, appariement, protocole de test.
4. **Résultats d'extraction** — couverture, métriques, exemples d'erreurs, robustesse par année et format.
5. **Résultats temporels et séquentiels** — indicateurs descriptifs, Tanat, sensibilité aux données manquantes et aux liens incertains.
6. **Discussion et recommandations** — utilité de l'observatoire, interprétations autorisées, limites et pistes pour une mise à jour régulière.

**Priorité immédiate** : corriger et évaluer l'extraction sur un échantillon de référence, puis reconstruire les séries à partir de l'ensemble des annonces valides. C'est cette étape qui donnera une base solide à l'analyse avec Tanat et à la contribution pour le Burkina Faso.

### Premier livrable préparé le 25 septembre 2026

Le dossier [`evaluation_extraction`](evaluation_extraction/LISEZ_MOI.md) contient un lot reproductible de 37 PDF à annoter, les textes extraits, les 1 056 prédictions existantes et 182 alertes automatiques sur 141 lignes distinctes. Le [`rapport initial`](evaluation_extraction/RAPPORT_INITIAL.md) distingue les erreurs confirmées des signaux à vérifier. Lors de ce premier livrable, la grille `reference_annotations.csv` contenait quatre annonces vérifiées du 20 janvier 2021 et 35 documents restaient à examiner. Le notebook historique [`preparer_evaluation_extraction.ipynb`](Scripts/pipeline_et_validation/archive_mise_au_point/preparer_evaluation_extraction.ipynb) permet de régénérer le lot.

### Avancement du 25 septembre 2026

L'[annotation assistée](evaluation_extraction/SUIVI_CAMPAGNE_ANNOTATION.md) a parcouru les 35 documents restants. Quatre documents supplémentaires ont été contrôlés comme ne contenant aucune nomination ; le PDF du 16 janvier 2016 a été lu par OCR. Deux comptes rendus courts ont ensuite été relus et ajoutés aux résultats vérifiés : 16 nominations étaient alors validées dans trois documents. Les 29 autres documents portaient 2 395 propositions traçables dans les passages PDF. La grille `reference_annotations.csv` réunit les 2 411 lignes avec un statut de vérification ; **seul `reference_annotations_validees.csv` peut servir de vérité terrain**. Les champs déduits du contexte demandaient encore une relecture avant le calcul des métriques globales.

Au 25 septembre 2026, la grille candidate a été complétée : les fonctions et institutions des 2 411 lignes sont renseignées, les postes de préfet portent leur département lorsqu'il figure dans l'annonce, une nomination masquée par la coquille « Monsioeur » a été ajoutée et une fin de fonctions retirée. Chaque extrait est retrouvé dans le texte du PDF et chaque numéro de page est valide. **Ces contrôles automatiques ne remplacent pas la validation humaine** : à cette date, 2 395 lignes demeuraient `a_verifier`, et le calcul du rappel global restait suspendu à la relecture des 29 documents positifs.

### Lot pilote et interface de validation — 26 septembre 2026

Un [premier lot de 12 PDF](evaluation_extraction/LOT_PILOTE_VALIDATION.md) couvre les années 2015 à 2025, les nominations individuelles, les listes collectives, les conseils d’administration, les exclusions de révocations et fins de fonctions, ainsi qu’un document négatif traité par OCR. Ses 566 lignes sont maintenant vérifiées. Le [manifeste](evaluation_extraction/lot_pilote_12_documents.csv) précise l’ordre de relecture, les difficultés et les chemins des sources.

L’interface locale se lance avec `python3 Scripts/pipeline_et_validation/validation_web/serveur.py`, puis s’ouvre sur `http://localhost:8765`. Elle affiche le PDF et les annotations côte à côte, permet de corriger, ajouter ou supprimer une ligne, et enregistre une sauvegarde avant chaque modification des fichiers. La validation d’un document entier exige une confirmation explicite du relecteur ; elle actualise la référence vérifiée et le suivi.

Le lot pilote a été relu intégralement le 27 septembre 2026 : ses 566 annonces, dont zéro dans le PDF négatif traité par OCR, sont désormais validées. Avec les trois documents déjà validés auparavant, la référence compte 575 annonces dans treize documents ; 1 836 propositions sur les vingt-quatre autres documents positifs restent à contrôler. L'évaluation exploratoire de l'extracteur sur le lot pilote mesure 97,6 % de précision, 64,7 % de rappel et 77,8 % de F1 pour la détection de la personne nommée. Quand la fonction exacte est requise, le F1 est de 72,1 %. Le [rapport détaillé](evaluation_extraction/RAPPORT_EVALUATION_LOT_PILOTE.md) et les [appariements](evaluation_extraction/resultats_appariement_lot_pilote.csv) rendent ces résultats vérifiables.

Ce lot constitue un échantillon raisonné de développement et d’évaluation exploratoire, sans garantie de représentativité. Ces PDF ayant déjà servi à examiner les erreurs de l’extracteur, un autre lot devra être réservé au test final indépendant. Le seul document OCR étant négatif, ce pilote ne suffit pas à mesurer l’extraction de nominations sur des scans positifs.

### Pipeline d’extraction révisée — 27 septembre 2026

La nouvelle [pipeline reproductible](Scripts/pipeline_et_validation/pipeline_extraction_nominations.ipynb) sépare la lecture du PDF, le recours à l’OCR français lorsque le texte est insuffisant, l’identification de la rubrique des nominations, l’extraction des personnes et la journalisation de chaque document. Sur les douze PDF du lot pilote, elle retrouve les **566 noms nommés sur 566**, sans candidat supplémentaire, y compris les listes collectives et le PDF négatif lu par OCR. Lorsque la fonction exacte est aussi exigée, elle obtient 565 vrais positifs, 1 faux positif et 1 faux négatif : 99,8 % de précision, rappel et F1. Le [rapport de mesure](evaluation_extraction/RAPPORT_PIPELINE_LOT_PILOTE.md), les [candidats](evaluation_extraction/extractions_pipeline_lot_pilote.csv) et le [manifeste de lecture](evaluation_extraction/manifeste_pipeline_lot_pilote.csv) permettent de reproduire ce résultat.

Ce score de 100 % concerne la détection du **nom** dans ce lot de développement ; il ne démontre pas encore un rappel supérieur à 99 % pour toutes les annonces ni l’exactitude de tous les champs (fonction, institution, date). L’objectif opérationnel est donc un rappel d’événement supérieur ou égal à 99 % sur un lot final indépendant, comprenant notamment des scans positifs et des modèles documentaires qui n’ont pas servi à modifier les règles.
