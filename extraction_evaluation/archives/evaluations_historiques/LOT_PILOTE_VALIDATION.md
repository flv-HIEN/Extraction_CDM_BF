# Lot pilote de validation — 26 septembre 2026

La sélection raisonnée comprend **12 PDF couvrant 2015 à 2025**, avec **566 lignes désormais vérifiées**. Le PDF traité par OCR ne contient aucune nomination ; il permet de contrôler les faux positifs sur un document négatif. Les effectifs sont ceux enregistrés après la relecture intégrale du 27 septembre 2026.

| Ordre de relecture | PDF | Lignes actuelles | Intérêt pour la validation |
|---:|---|---:|---|
| 1 | [1er juillet 2015](<../total_donnees/CDM - 2015_07_01.pdf>) | 7 | Calibration sur un document déjà vérifié |
| 2 | [16 janvier 2016](<../total_donnees/CDM - 2016_01_16.pdf>) | 0 | OCR des deux pages, document négatif déjà contrôlé |
| 3 | [5 janvier 2017](<../total_donnees/CDM - 2017_01_05.pdf>) | 32 | Fonctions individuelles explicites |
| 4 | [10 juillet 2024](<../total_donnees/CDM - 2024_07_10.pdf>) | 16 | Petit document avec fonctions individuelles et conseils d’administration |
| 5 | [9 juin 2021](<../total_donnees/CDM - 2021_06_09.pdf>) | 36 | Conseils d’administration et rôles collectifs |
| 6 | [8 janvier 2020](<../total_donnees/CDM - 2020_01_08.pdf>) | 55 | Fonction coupée par un saut de page |
| 7 | [11 janvier 2023](<../total_donnees/CDM - 2023_01_11.pdf>) | 69 | Renouvellements de mandats et nominations |
| 8 | [28 décembre 2016](<../total_donnees/CDM - 2016_12_28.pdf>) | 59 | Rubrique au singulier, plusieurs fonctions pour une même personne |
| 9 | [18 juin 2018](<../total_donnees/CDM - 2018_06_18.pdf>) | 70 | Listes de préfets, membres de la CNCC, personnes remplacées |
| 10 | [30 octobre 2019](<../total_donnees/CDM -2019_10_30.pdf>) | 126 | Listes collectives et ponctuation inhabituelle dans un nom |
| 11 | [Fichier 2022_06_16 — séance du 8 juin 2022](<../total_donnees/CDM - 2022_06_16.pdf>) | 26 | Date discordante et révocations à exclure |
| 12 | [18 juin 2025](<../total_donnees/CDM - 2025_06_18.pdf>) | 70 | Fin de fonctions à exclure entre deux rubriques de nominations |

Le choix privilégie la diversité des structures et une charge de lecture plus accessible que celle du lot complet. Il comprend onze documents positifs et un négatif déjà contrôlé. Il ne permet pas de revendiquer une représentativité nationale ni de mesurer de manière fiable une performance par année. L’unique document OCR est négatif : une évaluation de l’extraction de nominations sur des scans demandera aussi des scans positifs dans un lot ultérieur.

Ces documents ont déjà été utilisés pour examiner ou corriger l’extracteur. Le lot sert donc à la **mise au point et à une évaluation exploratoire**. Un test final indépendant devra employer d’autres documents, réservés avant de nouveaux ajustements.

## Ouvrir l’interface locale

Depuis le dossier de travail, dans le terminal WSL :

```bash
python3 Scripts/pipeline_et_validation/validation_web/serveur.py
```

Ouvrir **http://localhost:8765** dans le navigateur Windows. Python 3.10 ou ultérieur suffit ; aucune bibliothèque Python supplémentaire n’est requise. Le serveur écoute uniquement sur l’interface locale. Arrêter avec `Ctrl+C`. Si le port est occupé, utiliser `--port 8766` et ouvrir l’adresse correspondante.

L’affichage intégré du PDF dépend du lecteur PDF du navigateur. Le lien « Ouvrir le PDF » et le bouton « Voir le texte extrait » restent disponibles. Pour un PDF traité par OCR, vérifier les caractères sur l’image originale avant de confirmer la transcription.

## Procédure par document

1. Choisir le document et parcourir toutes ses pages pour repérer les rubriques et les annonces absentes de la grille. Les pages sans annotation proposée doivent aussi être lues.
2. Sélectionner chaque ligne, vérifier ses champs et son extrait ; corriger, ajouter ou supprimer les annotations nécessaires. Un matricule non indiqué reste vide. Expliquer toute absence ou incertitude dans le commentaire.
3. Cliquer sur « Enregistrer le brouillon » pour conserver les corrections. Toutes les lignes de ce document restent ou redeviennent `a_verifier` ; les autres documents conservent leurs annotations et leur statut.
4. Après la lecture intégrale, renseigner le nom ou les initiales du relecteur, cocher la confirmation et cliquer sur « Valider tout le document ». Une liste vide doit également être confirmée pour acter l’absence de nomination.
5. Faire relire indépendamment une partie du lot avant de publier les résultats, en conservant les désaccords et leur résolution.

Chaque sauvegarde actualise `reference_annotations.csv`, `reference_annotations_validees.csv`, `annotations_consolidees_a_valider.csv` et `suivi_annotations.csv`. Le fichier `validations_documents.json` conserve la dernière décision par document, le relecteur et l’heure. Les versions précédentes de ces fichiers sont conservées dans `sauvegardes_validation/` avant écriture. Une modification concurrente détectée bloque l’enregistrement et demande un rechargement ; copier ses modifications avant de recharger si nécessaire.

Le script d’interface n’effectue aucune validation automatiquement. La sélection du lot et les tests de sauvegarde n’ont changé aucun statut de référence.

## Manifeste reproductible

Le [manifeste CSV](lot_pilote_12_documents.csv) contient les chemins sources, les raisons de sélection, les difficultés, les pages déjà annotées, les effectifs et l’ordre de relecture. Les PDF restent dans `total_donnees` et la grille principale demeure le fichier à corriger ; aucune copie divergente des annotations n’est créée pour ce lot.

Après une séance de validation, actualiser les effectifs du manifeste :

```bash
jupyter lab Scripts/pipeline_et_validation/archive_mise_au_point/selectionner_lot_pilote.ipynb
```

La sélection des documents est fixe. Le manifeste régénéré reflète les données courantes.
