# Avancement de l'annotation des 35 PDF

*27 septembre 2026 — Le lot pilote de 12 PDF est entièrement relu et sert à une première évaluation. Les lignes hors de ce lot encore marquées `a_verifier` ne constituent pas une vérité terrain validée.*

## Résultat de la passe documentaire

| État | Documents | Nominations |
|---|---:|---:|
| Annotés et vérifiés : onze documents du lot pilote et deux documents antérieurs | 13 | 575 |
| Aucun événement de nomination, vérifié dans le texte | 5 | 0 |
| Propositions extraites de la rubrique, à valider | 19 | 1 836 |
| Total du lot | 37 | 2 411 lignes dans le fichier consolidé |

Les quatre nouveaux documents sans nomination sont `CDM - 2016_01_16.pdf`, `CDM - 2017_12_30.pdf`, `CDM - 2018_12_31.pdf` et `CDM - 2019_01_08.pdf`. Le document `CDM - 2015_12_23.pdf` avait déjà été contrôlé comme négatif. Le document du 16 janvier 2016 ne livrait que deux caractères par extraction de texte ; un OCR français de ses deux pages a produit un texte lisible et confirmé l'absence de rubrique de nominations.

Les 2 407 propositions courantes ont été construites **depuis les PDF**, sans reprendre les noms des CSV à évaluer. Une fin de fonctions a été retirée et une nomination supplémentaire, masquée par la coquille « Monsioeur », a été ajoutée. Le lot pilote de douze documents a ensuite été relu intégralement par HF : 559 lignes sont passées de proposition à référence vérifiée, y compris les corrections, ajouts et suppressions effectués pendant cette relecture. Chaque ligne porte le document, la page, le nom, un extrait source, le type d'annonce et les champs déduits. Le contrôle d'intégrité retrouve les 2 411 extraits dans les textes PDF, valide les numéros de page et ne trouve ni fonction ni institution vide. Le nom « Aboubakar TRAORE » est une correction proposée du texte « Aboubakar, TRAORE » et demande confirmation visuelle dans les documents non encore validés.

La [grille de travail demandée](reference_annotations.csv) contient les 2 411 lignes, avec un `statut_verification` explicite. Le [fichier vérifié](reference_annotations_validees.csv) conserve désormais 575 lignes contrôlées sur treize comptes rendus ; lui seul sert de référence pour ces documents. Le [suivi par document](suivi_annotations.csv) distingue les documents contrôlés des propositions à valider. L'[instantané consolidé](annotations_consolidees_a_valider.csv) reprend désormais la grille de travail actualisée, y compris ses corrections, sans changer le statut des lignes.

## Points qui demandent encore une vérification

- **Fonctions et institutions renseignées** : les 72 fonctions et 527 institutions initialement vides ont reçu une proposition issue du passage individuel ou d'un en-tête. Les valeurs héritées du contexte restent à contrôler, surtout lorsqu'un document contient plusieurs décrets ou listes successives.
- **Postes de préfet** : 438 fonctions génériques de la grille ont été précisées avec le département indiqué sur la ligne de la personne. Quelques annonces demeurent génériques lorsque le lieu n'est pas récupérable automatiquement.
- **Corrections ciblées** : deux représentants au conseil de l'INEFPRO, la ponctuation du nom « Aboubakar TRAORE » et deux matricules atypiques ont été corrigés ou signalés dans la grille. Leur statut reste `a_verifier`.
- **Fonctions héritées d'un en-tête** : de nombreuses lignes sont rattachées à une phrase collective ou à un contexte de conseil d'administration. L'intitulé doit être revu lorsque plusieurs listes ou décrets se suivent.
- **Date de séance discordante** : le fichier `CDM - 2022_06_16.pdf` indique « 08 juin 2022 » sur sa couverture et dans le texte de la séance. Les 26 propositions de ce document portent donc `2022-06-08`, avec un commentaire signalant la différence avec le nom du fichier.
- **Homonymies et nominations multiples** : un même nom peut apparaître plusieurs fois dans un document, avec un matricule, un poste ou un mandat différent. Ne pas dédoublonner sur le seul nom.

## Pour achever la vérité terrain

Ouvrir chaque PDF et vérifier, dans [reference_annotations.csv](reference_annotations.csv), chaque ligne marquée `a_verifier`. Corriger les fonctions et ministères, supprimer les mentions sans nomination, ajouter les éventuelles annonces absentes, puis mettre `statut_verification` à `verifie_sur_pdf`. Exporter ensuite uniquement ces lignes dans `reference_annotations_validees.csv`. Une seconde lecture indépendante d'une partie du lot permettra de mesurer les désaccords. Le calcul de précision, rappel et F1 viendra après cette étape.

## Première évaluation disponible

Le [rapport du lot pilote](RAPPORT_EVALUATION_LOT_PILOTE.md) compare les 375 prédictions existantes aux 566 annonces de référence du lot. La détection des personnes nommées atteint une précision de **97,6 %**, un rappel de **64,7 %** et un F1 de **77,8 %**. Lorsque la fonction doit aussi être exacte, le F1 tombe à **72,1 %**. Ces résultats sont exploratoires : les documents du lot ont servi à examiner les erreurs de l'extracteur ; un échantillon distinct reste nécessaire pour une évaluation finale.
