# Sorties de la fiabilisation

`nominations_2015_2025_fiabilise.csv` est le fichier consolidé produit par `normalisation/fiabiliser_nominations.py` (ou son notebook). Il conserve toutes les lignes et colonnes de la source et ajoute notamment :

- `id_personne` : identifiant numérique persistant ;
- `nom_normalise`, `matricule_normalise` : valeurs préparées pour les rapprochements ;
- `ministere_harmonise` : libellé harmonisé selon le dictionnaire `dictionnaires/ministeres.csv` ;
- `statut_identite`, `statut_harmonisation_ministere` : état de vérification ;
- les autres colonnes de contrôle des dates, doublons et trajectoires.

Les valeurs originales `nom`, `matricule` et `ministere` sont conservées. Cet export n'exclut aucune ligne : les alertes et statuts permettent de distinguer les valeurs harmonisées automatiquement des validations humaines. Il reprend le contenu de `nominations_annotees.csv` sous un nom explicite pour la base consolidée.

Les sous-ensembles dédoublonnés et les trajectoires strictes restent dans leurs fichiers séparés. L'harmonisation des libellés ne remplace pas la concordance historique vers les ministères de 2026 du dossier `normalisation/ministeres/`.
