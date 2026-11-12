"""Ajoute les colonnes de ministère normalisé au fichier des nominations.

Entrée  : nominations_2015_2025.csv
Sortie  : nominations_2015_2025_normalise.csv
Rapport : rapport_normalisation_ministeres.csv

Le fichier source n'est jamais modifié. Les deux nouvelles colonnes sont :
``ministere_normalise`` et ``code_ministere``.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from table_concordance_ministeres_2015_2025_vers_2026 import (
    CONCORDANCE_MINISTERES_2015_2025_VERS_2026,
    REFERENTIEL_2026,
)


DOSSIER = Path(__file__).resolve().parent
FICHIER_SOURCE = DOSSIER / "nominations_2015_2025.csv"
FICHIER_SORTIE = DOSSIER / "nominations_2015_2025_normalise.csv"
FICHIER_RAPPORT = DOSSIER / "rapport_normalisation_ministeres.csv"


def normaliser_texte(texte: str) -> str:
    """Uniformise casse, accents, apostrophes et ponctuation pour la comparaison."""
    texte = texte or ""
    texte = texte.translate(str.maketrans({"Œ": "OE", "œ": "oe", "Æ": "AE", "æ": "ae"}))
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(caractere for caractere in texte if not unicodedata.combining(caractere))
    texte = texte.upper().replace("’", "'").replace("`", "'")
    texte = re.sub(r"[^A-Z0-9]+", " ", texte)
    return " ".join(texte.split())


def versions_courtes(cle: str) -> set[str]:
    """Produit des variantes sûres de titres dont les compléments protocolaires sont omis."""
    versions = {cle}
    version = re.sub(r" GARDE DES SCEAUX", "", cle)
    version = re.sub(r" CHARGEE? DES RELATIONS AVEC LES INSTITUTIONS", "", version)
    versions.add(" ".join(version.split()))
    return versions


def construire_index():
    """Construit l'index des intitulés historiques vers les règles de concordance."""
    index = {}
    for libelle, regle in CONCORDANCE_MINISTERES_2015_2025_VERS_2026.items():
        for cle in versions_courtes(normaliser_texte(libelle)):
            index.setdefault(cle, regle)
    return index


INDEX_CONCORDANCE = construire_index()

# Alias relevés dans le CSV : titres tronqués ou formulations non officielles.
# Ils sont distincts de la table historique de concordance afin de préserver
# celle-ci comme référentiel des dénominations gouvernementales.
ALIASES_CSV_VERS_CODES = {
    "MINISTERE DE LA COMMUNICATION ET DES RELATIONS AVEC": ("COMMUNICATION_CULTURE_TOURISME",),
    "MINISTERE DE LA COMMUNICATION CHARGE DES RELATIONS AVEC": ("COMMUNICATION_CULTURE_TOURISME",),
    "MINISTERE DE LA JEUNESSE ET DE L ENTREPRENEURIAT DES JEUNES": ("SPORTS_JEUNESSE_EMPLOI",),
    "MINISTERE DE L AGRICULTURE ET DES AMENAGEMENTS": ("AGRI_EAU_RAH",),
    "MINISTERE EN CHARGE DE ENERGIE": ("ENERGIE_MINES_CARRIERES",),
    "MINISTERE EN CHARGE DES RESSOURCES HYDRAULIQUES": ("AGRI_EAU_RAH",),
    "MINISTERE COMMERCE DE L INDUSTRIE ET DE L ARTISANAT": ("INDUSTRIE_COMMERCE_ARTISANAT",),
    "MINISTERE DE LA FEMME DE L ACTION SOCIALE ET DE LA SOLIDARITE NATIONALE": ("FAMILLE_SOLIDARITE",),
    "MINISTERE DE L ACTION HUMANITAIRE ET DE LA SOLIDARITE": ("FAMILLE_SOLIDARITE",),
    "MINISTERE DE LA FONCTION PUBLIQUE ET DE LA SECURITE SOCIALE": ("SERVITEURS_PEUPLE",),
    "MINISTERE DU DEVELOPPEMENT INDUSTRIEL DU COMMERCE ET DES PETITES ET MOYENNES ENTREPRISES": ("INDUSTRIE_COMMERCE_ARTISANAT",),
    "MINISTERE DE L ENVIRONNEMENT ET DU DEVELOPPEMENT DURABLE": ("AGRI_EAU_RAH",),
    "MINISTERE DE L ECONOMIE DES FINANCES ET DU CHANGEMENT": ("ECONOMIE_FINANCES",),
    "MINISTERE DU DEVELOPPEMENT NUMERIQUE ET DES POSTES": ("TRANSITION_DIGITALE",),
    "MINISTERE DE L ECONOMIE NUMERIQUE ET DES POSTES": ("TRANSITION_DIGITALE",),
    "MINISTERE DE LA FEMME DE LA SOLIDARITE NATIONALE ET DE L ACTION HUMANITAIRE": ("FAMILLE_SOLIDARITE",),
    "MINISTERE DE LA COMMUNICATION": ("COMMUNICATION_CULTURE_TOURISME",),
    "MINISTERE CHARGE DES INFRASTRUCTURES": ("CONSTRUCTION_PATRIE",),
}

for alias, codes in ALIASES_CSV_VERS_CODES.items():
    INDEX_CONCORDANCE[alias] = {
        "codes_ref_2026": codes,
        "type_concordance": "alias_extraction_csv",
        "perimetres_non_couverts_2026": (),
        "note": "Alias de nettoyage propre au CSV des nominations.",
    }


def couper_texte_ajoute(texte_normalise: str) -> str:
    """Retire, lorsque détecté, le texte de décision collé après un intitulé."""
    separateurs = (
        " LES PERSONNES ",
        " MONSIEUR ",
        " MADAME ",
        " PRESIDENT ",
        " DIRECTEUR ",
        " DIRECTRICE ",
        " EN REMPLACEMENT ",
        " POUR UN PREMIER MANDAT ",
        " POUR UN MANDAT ",
        " AU TITRE ",
    )
    positions = [texte_normalise.find(separateur) for separateur in separateurs]
    positions = [position for position in positions if position > 0]
    return texte_normalise[: min(positions)] if positions else texte_normalise


def chercher_regle(libelle: str):
    """Retourne (règle, statut) ou (None, statut) pour un libellé du CSV."""
    cle = couper_texte_ajoute(normaliser_texte(libelle))
    if not cle.startswith("MINISTERE "):
        return None, "hors_ministere"

    if cle in INDEX_CONCORDANCE:
        return INDEX_CONCORDANCE[cle], "exact"

    # Des extractions OCR ajoutent parfois une phrase après le vrai intitulé.
    candidats_prefixe = [
        (len(cle_index), regle)
        for cle_index, regle in INDEX_CONCORDANCE.items()
        if cle.startswith(cle_index)
    ]
    if candidats_prefixe:
        return max(candidats_prefixe, key=lambda candidat: candidat[0])[1], "prefixe"

    # Tolérance limitée pour les fautes isolées : jamais appliquée à un texte long.
    if len(cle) <= 180:
        meilleur_cle, meilleur_score = max(
            (
                (cle_index, SequenceMatcher(None, cle, cle_index).ratio())
                for cle_index in INDEX_CONCORDANCE
            ),
            key=lambda resultat: resultat[1],
        )
        if meilleur_score >= 0.93:
            return INDEX_CONCORDANCE[meilleur_cle], "typo_probable"

    return None, "non_resolu"


def appliquer_concordance(regle):
    """Transforme une règle en valeurs destinées aux deux nouvelles colonnes."""
    if regle is None:
        return "", ""
    codes = regle["codes_ref_2026"]
    return " | ".join(REFERENTIEL_2026[code] for code in codes), " | ".join(codes)


def normaliser_fichier():
    """Écrit le CSV enrichi et le rapport des valeurs à examiner."""
    bilan = Counter()
    rapport = {}

    with FICHIER_SOURCE.open("r", encoding="utf-8", newline="") as entree:
        lecteur = csv.DictReader(entree)
        if not lecteur.fieldnames or "ministere" not in lecteur.fieldnames:
            raise ValueError("La colonne 'ministere' est absente du fichier source.")

        colonnes = list(lecteur.fieldnames)
        for colonne in ("ministere_normalise", "code_ministere"):
            if colonne not in colonnes:
                colonnes.append(colonne)

        with FICHIER_SORTIE.open("w", encoding="utf-8-sig", newline="") as sortie:
            redacteur = csv.DictWriter(sortie, fieldnames=colonnes)
            redacteur.writeheader()
            for ligne in lecteur:
                libelle = ligne.get("ministere", "")
                regle, statut = chercher_regle(libelle)
                ministere_normalise, code_ministere = appliquer_concordance(regle)
                ligne["ministere_normalise"] = ministere_normalise
                ligne["code_ministere"] = code_ministere
                redacteur.writerow(ligne)

                bilan[statut] += 1
                cle_rapport = (libelle, statut, code_ministere, ministere_normalise)
                rapport[cle_rapport] = rapport.get(cle_rapport, 0) + 1

    with FICHIER_RAPPORT.open("w", encoding="utf-8-sig", newline="") as sortie:
        colonnes_rapport = [
            "ministere_source",
            "occurrences",
            "statut_normalisation",
            "code_ministere",
            "ministere_normalise",
        ]
        redacteur = csv.DictWriter(sortie, fieldnames=colonnes_rapport)
        redacteur.writeheader()
        for (libelle, statut, code, normalise), occurrences in sorted(
            rapport.items(), key=lambda item: (-item[1], item[0][0])
        ):
            redacteur.writerow(
                {
                    "ministere_source": libelle,
                    "occurrences": occurrences,
                    "statut_normalisation": statut,
                    "code_ministere": code,
                    "ministere_normalise": normalise,
                }
            )

    return bilan


if __name__ == "__main__":
    resultats = normaliser_fichier()
    print(f"Fichier créé : {FICHIER_SORTIE.name}")
    print(f"Rapport créé : {FICHIER_RAPPORT.name}")
    for statut, occurrences in sorted(resultats.items()):
        print(f"{statut}: {occurrences}")
