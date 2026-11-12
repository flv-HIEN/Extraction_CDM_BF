# Récapitulatif de l’extraction des nominations

## 1. Chaîne mise en place

La chaîne [d’extraction](../Scripts/pipeline_et_validation/pipeline_extraction_nominations.ipynb) lit d’abord le texte natif des PDF avec `pdfminer`. Lorsque ce texte est insuffisant, elle utilise un OCR français. Les règles intégrées à ce même notebook repèrent ensuite les rubriques de nominations, les personnes, les fonctions, les institutions et les conseils d’administration. Chaque candidat conserve le PDF source, la page, un extrait, la méthode de lecture et un niveau de confiance.

Le corpus comprend **406 PDF**. La chaîne y a produit **21 687 candidats**. Ce nombre est une sortie automatique ; il ne représente pas encore 21 687 nominations validées.

## 2. Évaluation indépendante

L’évaluation ne porte pas sur le lot pilote utilisé pour régler les règles. Elle utilise un lot indépendant de **28 PDF**, sélectionné avant la relecture et isolé dans [`test_independant`](test_independant/). Les PDF couvrent un scan lu par OCR, des documents sans candidat, des conseils d’administration, des listes longues, des champs incomplets et des documents standards de 2015 à 2025.

La référence humaine validée contient **742 nominations**. La version figée de la pipeline avait produit **714 candidats** dans ces mêmes PDF.

| Niveau de mesure | VP | FP | FN | Précision | Rappel | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Détection de personne : `document + nom` | 709 | 5 | 33 | 99,3 % | 95,6 % | 97,4 % |
| Événement principal : `document + date + nom + fonction` | 693 | 21 | 49 | **97,1 %** | **93,4 %** | **95,2 %** |
| Événement complet : événement principal + ministère + type | 693 | 21 | 49 | **97,1 %** | **93,4 %** | **95,2 %** |

L’indicateur à retenir dans le mémoire est l’**événement principal**. Une personne est correctement trouvée seulement si elle est associée à la bonne fonction, dans le bon compte rendu et à la bonne date.

## 3. Lecture des résultats

La pipeline retrouve bien les personnes lorsqu’elle les détecte : la précision au niveau du nom est de 99,3 %. La limite principale est le rappel : **33 personnes nommées ne sont pas détectées** dans la référence indépendante.

L’écart entre la détection de personne et l’événement principal montre aussi **16 annonces** où le nom est trouvé mais où la fonction ou la date ne correspond pas exactement. Ces divergences créent à la fois un faux positif et un faux négatif dans la mesure stricte.

Les écarts sont concentrés dans quelques documents :

| Document | Observation |
|---|---|
| `CDM - 2010_09_24.pdf` | 13 nominations de référence, aucune prédiction : le scan OCR est le premier problème à résoudre. |
| `CDM - 2017_03_15.pdf` | 14 noms manqués, probablement liés à une liste ou à une structure de conseil d’administration. |
| `CDM - 2015_04_11.pdf` | Les 86 personnes sont détectées, mais 8 fonctions de conseils d’administration sont trop génériques ou vides. |
| `CDM - 2015_04_14.pdf` | Même problème : les 47 personnes sont détectées, mais 8 fonctions ne reprennent pas correctement l’organisme ou le rôle. |
| `CDM - 2018_01_17.pdf` | 3 noms supplémentaires doivent être examinés comme faux positifs. |
| `CDM - 2023_02_08.pdf` | 2 écarts de noms ou de segmentation produisent 2 faux positifs et 2 faux négatifs. |

Le fichier [`ecarts_test_independant.csv`](ecarts_test_independant.csv) contient le détail des 70 écarts stricts.

## 4. Conclusion méthodologique

L’objectif de rappel supérieur ou égal à 99 % n’est **pas atteint** sur le test indépendant : le rappel observé est de 93,4 %. Ce résultat est plus crédible que le score de 100 % obtenu sur le lot pilote, car les 28 PDF de test n’avaient pas servi à ajuster les règles.

La version actuelle est néanmoins utilisable comme extracteur assisté : elle réduit fortement le volume à contrôler et identifie les passages candidats. Pour construire les séries Tanat, conserver deux jeux de données distincts :

1. les annonces validées humainement, à utiliser pour les résultats principaux ;
2. les candidats automatiques, à utiliser seulement pour une analyse de sensibilité, avec `confiance_extraction` et `methode_lecture` visibles.

## 5. Prochaine version de la pipeline

Les améliorations doivent être développées sur les PDF de [`file_relecture_developpement_prioritaire.csv`](file_relecture_developpement_prioritaire.csv), jamais sur ce test déjà utilisé. Les priorités sont :

1. améliorer la lecture des scans, par exemple avec un prétraitement d’image et un second extracteur visuel comme Qwen-VL ;
2. reconstruire la fonction complète dans les conseils d’administration en héritant de l’en-tête et du nom de l’organisme ;
3. renforcer la segmentation des listes collectives afin de ne pas omettre des personnes ;
4. traiter les variantes de ponctuation, les noms coupés et les fonctions vides ;
5. sélectionner ensuite un **nouveau** lot indépendant pour mesurer la version améliorée.

Il ne faut plus modifier la version évaluée pour recalculer les résultats ci-dessus. Toute correction constitue une nouvelle version de la pipeline et doit être évaluée sur d’autres PDF réservés à cet effet.
