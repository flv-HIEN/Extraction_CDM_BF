# Sorties de la fiabilisation

`nominations_2015_2025_fiabilise.csv` est le fichier consolidé produit par `normalisation/fiabiliser_nominations.py` (ou son notebook). Il conserve toutes les lignes et colonnes de la source et ajoute notamment :

- `id_personne` : identifiant numérique persistant ;
- `nom_normalise`, `matricule_normalise` : valeurs préparées pour les rapprochements ;
- `ministere_harmonise` : libellé harmonisé selon le dictionnaire `dictionnaires/ministeres.csv` ;
- `statut_identite`, `statut_harmonisation_ministere` : état de vérification ;
- les autres colonnes de contrôle des dates, doublons et trajectoires.

Les valeurs originales `nom`, `matricule` et `ministere` sont conservées. Cet export n'exclut aucune ligne : les alertes et statuts permettent de distinguer les valeurs harmonisées automatiquement des validations humaines. Il reprend le contenu de `nominations_annotees.csv` sous un nom explicite pour la base consolidée.

Les sous-ensembles dédoublonnés et les trajectoires strictes restent dans leurs fichiers séparés. L'harmonisation des libellés ne remplace pas la concordance historique vers les ministères de 2026 du dossier `normalisation/ministeres/`.

## Actualisation de la source

### Règle d'identité retenue le 7 novembre 2026

Sur instruction de l'utilisatrice, un même nom associé à plusieurs matricules
de format reconnu désigne des personnes distinctes. Ces couples restent séparés
et sont classés `coherent_nom_matricule` lorsque leur matricule n'est pas partagé
entre plusieurs noms. Cette règle ne constitue pas une validation au PDF.
Un matricule partagé reste à vérifier, y compris si le nom possède aussi d'autres
matricules. Les noms sans matricule et les matricules atypiques restent provisoires.

Depuis la racine : `python3 extraction_evaluation/consolider_lots.py`, puis `python3 normalisation/fiabiliser_nominations.py`. La consolidation réunit les trois lots existants, vérifie leur couverture contre les manifestes et sauvegarde l’ancien CSV. Aucune extraction PDF n’est relancée.

Les décisions anciennes visant une ligne sans matricule sont ignorées. Les nouveaux imports de rattachement impliquant une personne sans matricule sont refusés. Chaque ligne sans matricule conserve son identité distincte.

## Fusion automatique des dénominations historiques

La fiabilisation utilise désormais `normalisation/ministeres/fusion_denominations.py`, fondé sur la table locale de concordance vers le référentiel 2026. `ministere` reste la source, `ministere_historique` conserve l'harmonisation lexicale et `ministere_harmonise` reçoit le libellé commun lorsque la correspondance est unique et non conventionnelle. Le code est dans `code_ministere_reference`.

Les rapprochements sont exacts après nettoyage typographique, sans fusion floue. Une correction manuellement validée dans le dictionnaire reste prioritaire. Les correspondances multiples, les périmètres partiels, les conventions et les titres non répertoriés conservent leur libellé historique et sont signalés dans `statut_fusion_ministere` et `rapport_fusion_ministeres.csv`. Les catégories multiples ne dupliquent aucune ligne.

Ce regroupement analytique réutilise le référentiel local ; il ne certifie pas l'identité juridique des ministères dans le temps. La fusion peut modifier les identifiants de postes et les regroupements d'événements, car ils tiennent compte du ministère harmonisé. Les identifiants de personnes restent gérés séparément.
