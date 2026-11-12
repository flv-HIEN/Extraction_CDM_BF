# Audit initial du lot d'annotation

*Préparé à partir des fichiers locaux le 25 septembre 2026. Le lot complet n'est pas encore annoté : aucun score global de précision, rappel ou F1 n'est donc calculé.*

| Mesure | Résultat |
|---|---:|
| PDF sélectionnés | 37 |
| PDF par année | 3 pour chacune des années 2015–2021 et 2023–2025 ; 7 pour 2022 |
| Prédictions présentes dans les CSV existants | 1 056 |
| PDF sélectionnés sans CSV existant | 6 |
| PDF où le titre de rubrique n'a pas été détecté | 7 |
| Alertes automatiques | 182 sur 141 lignes distinctes |
| Documents déjà examinés intégralement | 2 : un avec 4 nominations, un sans rubrique de nominations |

## Types d'alertes

| Type | Nombre d'alertes | Interprétation |
|---|---:|---|
| Ministère vide | 55 | Champ absent, pas nécessairement erreur : vérifier le document. |
| Date extraite différente de la date du nom de fichier | 53 | La date peut avoir été prise dans le corps du texte ; le nom de fichier peut aussi être erroné. |
| Rubrique de nominations non détectée | 42 | Peut indiquer une variante de mise en page, un PDF sans rubrique ou un échec de lecture du texte. |
| Nom prédit absent du texte situé après le titre « NOMINATIONS » | 32 | Peut signaler une extraction hors rubrique, mais aussi une variante de nom ou une rubrique non correctement bornée. |

Une ligne peut produire plusieurs alertes. Ces chiffres comptent des **signaux de contrôle**, pas des faux positifs prouvés.

## Cas vérifiés et priorités

- **Erreur confirmée** : la ligne 2 de `CDM - 2015_01_07.csv` attribue à Michel KAFANDO un poste que le [compte rendu du 7 janvier 2015](https://www.consulat-burkinaespagne.org/51600_fr/Compte-rendu-du-Conseil-des-ministres-du-07-janvier-2015/) attribue à Honoré Grégoire KARAMBERY. Le nom de Michel KAFANDO apparaît dans l'introduction et Honoré Grégoire KARAMBERY n'apparaît pas comme `nom` dans ce CSV. Ce cas contient donc à la fois un **faux positif** et une **annonce manquée**. Il montre qu'une recherche sur tout le texte peut traverser les frontières des annonces.
- **Dates à vérifier** : des lignes de `CDM - 2015_07_01.pdf` portent `2014-07-24` et des lignes de `CDM - 2022_06_01.pdf` portent `2015-11-24`. Cela concorde avec le fait que la fonction actuelle prend la première date trouvée dans le texte ; il faut vérifier la date de séance dans les PDF avant correction.
- **Lecture du PDF** : `CDM - 2016_01_16.pdf` ne donne que deux caractères avec `pdfminer`. Il faut traiter ce document par OCR ou l'exclure explicitement des calculs de rappel, avec justification.
- **Absence de CSV** : six PDF du lot n'ont pas de CSV associé. Les annoter quand même permettra de voir si l'extracteur a ignoré des annonces ou si le document n'en contient pas.

## Première référence annotée

Le compte rendu `CDM - 2021_01_20.pdf` a été lu jusqu'à la fin de sa rubrique « NOMINATIONS ». Quatre annonces individuelles sont inscrites dans `reference_annotations.csv`. Le CSV existant contient quatre prédictions : deux validées, une fausse et une partielle. La prédiction fausse attribue la première fonction à Roch Marc Christian KABORE, cité avant la rubrique, alors que l'annonce nomme Basile OUEDRAOGO sous la PRIMATURE. La prédiction partielle inclut « pour compter du 13 novembre 2019 » dans le libellé de fonction ; cette date de prise d'effet doit être un champ distinct. `CDM - 2015_12_23.pdf` a été examiné comme document sans rubrique de nominations ; il fournit un exemple négatif.

Ces deux documents sont un **pilote d'annotation**, pas un échantillon suffisant pour estimer la performance générale. Les 35 autres documents restent à annoter.

## Étape suivante

Annoter ensuite `CDM - 2015_01_07.pdf` pour l'erreur connue, `CDM - 2016_01_16.pdf` après OCR et un PDF de 2022 pour les problèmes de date. Ajuster les consignes si des cas ne rentrent pas dans le schéma. Annoter le reste du lot, puis comparer les annonces de référence avec les prédictions.
