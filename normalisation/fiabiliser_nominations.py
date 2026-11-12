"""Préparation traçable des nominations, sans dépendance externe.

Exécution : python3 fiabiliser_nominations.py
Les CSV sources restent intacts. Les dictionnaires et décisions sont réutilisés.
Un identifiant cohérent automatiquement n'est pas une identité vérifiée au PDF.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


from ministeres.fusion_denominations import fusionner

ROOT = Path(__file__).resolve().parent
VERSION = "1.2"


def surface(value):
    value = unicodedata.normalize("NFC", value or "")
    value = value.translate(str.maketrans({"’": "'", "‘": "'", "ʼ": "'", "‐": "-", "‑": "-", "–": "-", "\u00a0": " "}))
    return re.sub(r"\s+", " ", value).strip().upper()


def key(value):
    value = unicodedata.normalize("NFKD", surface(value))
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"[^A-Z0-9]+", " ", value).strip()


def uid(prefix, *parts):
    payload = json.dumps(parts, ensure_ascii=False, separators=(",", ":"))
    return prefix + hashlib.sha256(payload.encode()).hexdigest()[:20]


def matricule(value):
    # Aucun remplacement O/0, aucune suppression de lettre ou de zéro initial.
    cleaned = re.sub(r"[\s.-]+", "", surface(value))
    return cleaned, bool(re.fullmatch(r"\d{3,8}[A-Z]?", cleaned))


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fields):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def poste_key(value):
    text = key(value)
    # Harmonisations grammaticales en tête seulement ; complément conservé.
    rules = [
        (r"^DIRECTRICES? GENERALES?\b", "DIRECTEUR GENERAL"),
        (r"^DIRECTEURS GENERAUX\b", "DIRECTEUR GENERAL"),
        (r"^DIRECTRICES?\b", "DIRECTEUR"),
        (r"^DIRECTEURS\b", "DIRECTEUR"),
        (r"^CHARGEES?\b", "CHARGE"),
        (r"^CHARGES\b", "CHARGE"),
        (r"^CHARGE DE MISSIONS\b", "CHARGE DE MISSION"),
        (r"^CONSEILLERES?\b", "CONSEILLER"),
        (r"^CONSEILLERS TECHNIQUES\b", "CONSEILLER TECHNIQUE"),
        (r"^ADMINISTRATRICES?\b", "ADMINISTRATEUR"),
        (r"^ADMINISTRATEURS\b", "ADMINISTRATEUR"),
        (r"^SECRETAIRES GENERAUX\b", "SECRETAIRE GENERAL"),
        (r"^INSPECTRICES?\b", "INSPECTEUR"),
        (r"^INSPECTEURS TECHNIQUES\b", "INSPECTEUR TECHNIQUE"),
    ]
    for pattern, replacement in rules:
        text = re.sub(pattern, replacement, text)
    return text


ROLE_RULES = [
    (r"^DIRECTEUR GENERAL ADJOINT\b", "Directeur général adjoint", "Direction", "a_preciser"),
    (r"^DIRECTEUR GENERAL\b", "Directeur général", "Direction", "a_preciser"),
    (r"^DIRECTEUR REGIONAL\b", "Directeur régional", "Direction", "regional"),
    (r"^DIRECTEUR PROVINCIAL\b", "Directeur provincial", "Direction", "provincial"),
    (r"^DIRECTEUR (?:DE |DU )?CABINET\b", "Directeur de cabinet", "Cabinet", "a_preciser"),
    (r"^DIRECTEUR\b", "Directeur", "Direction", "a_preciser"),
    (r"^SECRETAIRE GENERAL ADJOINT\b", "Secrétaire général adjoint", "Secrétariat général", "a_preciser"),
    (r"^SECRETAIRE GENERAL\b", "Secrétaire général", "Secrétariat général", "a_preciser"),
    (r"^CONSEILLER TECHNIQUE\b", "Conseiller technique", "Conseil", "a_preciser"),
    (r"^CHARGE DE MISSION\b", "Chargé de mission", "Appui", "a_preciser"),
    (r"^CHARGE D ETUDES\b", "Chargé d'études", "Appui", "a_preciser"),
    (r"^INSPECTEUR GENERAL\b", "Inspecteur général", "Inspection", "a_preciser"),
    (r"^INSPECTEUR TECHNIQUE\b", "Inspecteur technique", "Inspection", "a_preciser"),
    (r"^CHEF DE DEPARTEMENT\b", "Chef de département", "Encadrement", "a_preciser"),
    (r"^CHEF DE SERVICE\b", "Chef de service", "Encadrement", "a_preciser"),
    (r"^AGENT COMPTABLE\b", "Agent comptable", "Comptabilité", "a_preciser"),
    (r"^PREFETS?\b", "Préfet", "Administration territoriale", "departemental"),
    (r"^HAUTS? COMMISSAIRES?\b", "Haut-commissaire", "Administration territoriale", "provincial"),
    (r"^GOUVERNEURS?\b", "Gouverneur", "Administration territoriale", "regional"),
    (r"^ADMINISTRATEUR\b", "Administrateur", "Conseil d'administration / représentation", "a_preciser"),
    (r"^MEMBRES?\b", "Membre d'instance", "Instance collective", "a_preciser"),
]


def classify_poste(value):
    text = poste_key(value)
    for pattern, function, family, level in ROLE_RULES:
        if re.search(pattern, text):
            if re.search(r"\bPROVINCE\b", text):
                level = "provincial"
            elif re.search(r"\bREGION\b", text):
                level = "regional"
            nature = "mandat_instance" if family in {"Conseil d'administration / représentation", "Instance collective"} else "fonction_a_confirmer"
            return function, family, level, nature, "regle_lexicale_a_valider"
    if re.search(r"\bGRADE\b|^SONT INTEGRE|^DANS LES EMPLOIS", text):
        return "À qualifier", "À qualifier", "a_preciser", "grade_ou_integration_a_verifier", "a_verifier"
    return "À qualifier", "À qualifier", "a_preciser", "a_qualifier", "a_verifier"


DOMAINS = [
    (r"\bECONOMIE\b|\bFINANCES\b", "Economie et finances"),
    (r"\bADMINISTRATION TERRITORIALE\b|\bDECENTRALISATION\b", "Administration territoriale"),
    (r"\bSECURITE\b", "Sécurité"), (r"\bJUSTICE\b|\bDROITS HUMAINS\b", "Justice et droits humains"),
    (r"\bENSEIGNEMENT SUPERIEUR\b|\bRECHERCHE\b", "Enseignement supérieur et recherche"),
    (r"\bEDUCATION\b|\bENSEIGNEMENT DE BASE\b|\bENSEIGNEMENT SECONDAIRE\b|\bENSEIGNEMENTS SECONDAIRE\b", "Education"),
    (r"\bSANTE\b", "Santé"), (r"\bENVIRONNEMENT\b", "Environnement"),
    (r"\bEAU\b|\bHYDRAULIQUE|\bASSAINISSEMENT\b", "Eau et assainissement"),
    (r"\bAGRICULTURE\b", "Agriculture"), (r"\bRESSOURCES ANIMALES\b|\bHALIEUTIQUES\b", "Ressources animales et halieutiques"),
    (r"\bFONCTION PUBLIQUE\b|\bTRAVAIL\b", "Fonction publique et travail"),
    (r"\bAFFAIRES ETRANGERES\b|\bCOOPERATION\b", "Affaires étrangères et coopération"),
    (r"\bCULTURE\b|\bARTS\b|\bTOURISME\b", "Culture et tourisme"),
    (r"\bCOMMUNICATION\b", "Communication"), (r"\bSPORTS\b|\bLOISIRS\b", "Sports et loisirs"),
    (r"\bJEUNESSE\b|\bEMPLOI\b|\bINSERTION\b|\bFORMATION PROFESSIONNELLE\b", "Jeunesse, formation et emploi"),
    (r"\bENERGIE\b|\bMINES\b|\bCARRIERES\b", "Energie et mines"),
    (r"\bINFRASTRUCTURES\b|\bTRANSPORTS\b|\bMOBILITE\b", "Infrastructures et transports"),
    (r"\bURBANISME\b|\bHABITAT\b|\bFONCIERES\b", "Urbanisme et habitat"),
    (r"\bSOLIDARITE\b|\bFEMME\b|\bGENRE\b|\bACTION SOCIALE\b|\bHUMANITAIRE\b", "Action sociale et solidarité"),
    (r"\bCOMMERCE\b|\bINDUSTRI|\bARTISANAT\b", "Industrie et commerce"),
    (r"\bNUMERIQUE\b|\bDIGITALE\b|\bPOSTES\b", "Numérique et postes"),
    (r"\bDEFENSE\b", "Défense"), (r"^PRESIDENCE", "Présidence"),
    (r"^PREMIER MINISTERE$|^PRIMATURE$", "Primature"),
]


def ministry_key(value):
    return key(value).replace("TRRRITORIALE", "TERRITORIALE")


def dictionary(rows, field, path, is_poste):
    transform = poste_key if is_poste else ministry_key
    variants = defaultdict(list)
    for row in rows:
        variants[row[field]].append(row)
    existing_rows = read_csv(path) if path.exists() else []
    existing = {r["valeur_originale"]: r for r in existing_rows}
    if len(existing) != len(existing_rows):
        raise ValueError(f"Variantes en double dans {path}")
    canonical = defaultdict(Counter)
    for value, observations in variants.items():
        canonical[transform(value)][surface(value).strip(" ,;:.")] += len(observations)
    output = []
    for value in sorted(variants):
        observations = variants[value]
        code = transform(value)
        candidates = canonical[code]
        label = sorted(candidates, key=lambda s: (-candidates[s], s))[0]
        item = dict(existing.get(value, {}))
        defaults = {
            "valeur_originale": value, "cle_normalisee": code,
            "libelle_harmonise": label,
            "statut_validation": "normalisation_lexicale",
            "justification": "Casse, accents, ponctuation et espaces ; dénomination complète conservée.",
            "reference_validation": "",
        }
        if is_poste:
            function, family, level, nature, status = classify_poste(value)
            defaults.update(fonction_harmonisee=function, famille_fonction=family,
                            niveau_administratif=level, nature_nomination=nature,
                            statut_codage_fonction=status)
            defaults["justification"] += " Flexions de tête normalisées ; fonction proposée par règle lexicale."
        else:
            defaults["domaines_proposes"] = " | ".join(label for pattern, label in DOMAINS if re.search(pattern, code)) or "À qualifier"
            defaults["statut_codage_domaine"] = "proposition_lexicale_a_valider"
            defaults["alerte_intitule"] = (
                "intitule_long_ou_texte_absorbe_a_verifier"
                if len(value) > 240 or re.search(r"\bEST NOMM|\bLE CONSEIL|\bPOUR LE COMPTE|\bDECRET\b", code)
                else ""
            )
            if "TRRRITORIALE" in key(value):
                defaults["justification"] += " Correction explicite TRRRITORIALE → TERRITORIALE."
        for k, v in defaults.items():
            item.setdefault(k, v)
        if item["statut_validation"] == "valide_manuellement" and not (item.get("justification") and item.get("reference_validation")):
            raise ValueError(f"Validation sans justification/référence : {value}")
        if not item["libelle_harmonise"].strip() and not (field == "ministere" and not value.strip()):
            raise ValueError(f"Libellé harmonisé vide : {value}")
        item.update(nombre_lignes=str(len(observations)),
                    premiere_date_observee=min(r["date_conseil"] for r in observations),
                    derniere_date_observee=max(r["date_conseil"] for r in observations))
        output.append(item)
    # Les anciennes entrées restent disponibles si une variante disparaît du CSV.
    for value in sorted(existing.keys() - variants.keys()):
        output.append(dict(existing[value], nombre_lignes="0"))
    fields = list(dict.fromkeys(k for r in output for k in r))
    write_csv(path, output, fields)
    return {r["valeur_originale"]: r for r in output}


def assign_identities(rows):
    by_mat, by_name = defaultdict(set), defaultdict(set)
    for row in rows:
        row["nom_normalise"] = surface(row["nom"])
        row["cle_nom_recherche"] = key(row["nom"])
        mat, valid = matricule(row["matricule"])
        row["matricule_normalise"] = mat
        row["matricule_format_reconnu"] = int(valid)
        if valid and row["cle_nom_recherche"]:
            by_mat[mat].add(row["cle_nom_recherche"])
            by_name[row["cle_nom_recherche"]].add(mat)
    for row in rows:
        name, mat = row["cle_nom_recherche"], row["matricule_normalise"]
        valid = row["matricule_format_reconnu"]
        if not name:
            person, status = uid("P_", "sans_nom", row["id_ligne_source"]), "nom_absent"
        elif valid:
            person = uid("P_", "nom_matricule", name, mat)
            status = "coherent_nom_matricule"
            if len(by_mat[mat]) > 1:
                status = "a_verifier_matricule_partage"
            # Règle retenue : des matricules différents désignent des personnes
            # distinctes, même si leur nom est identique. Un matricule partagé
            # entre plusieurs noms reste à vérifier.
        else:
            # Pas de fusion automatique d'un nom seul avec une identité matriculée.
            person = (uid("P_", "provisoire", name, mat) if mat
                      else uid("P_", "sans_matricule", row["id_ligne_source"]))
            status = "provisoire_matricule_atypique" if mat else "provisoire_nom_seul"
        row.update(id_personne=person, statut_identite=status,
                   identite_eligible_strict=int(status == "coherent_nom_matricule"))
    return by_mat, by_name


def simplify_person_ids(rows, path):
    """Numérotation persistante : réordonner les lignes ne change pas les numéros."""
    records = read_csv(path) if path.exists() else []
    mapping = {r["cle_identite"]: r["id_personne"] for r in records}
    if len(mapping) != len(records) or len(set(mapping.values())) != len(records):
        raise ValueError("Correspondance des identifiants dupliquée.")
    if any(not v.isdecimal() or int(v) < 1 or str(int(v)) != v for v in mapping.values()):
        raise ValueError("Les identifiants de personnes doivent être des entiers positifs.")
    next_id = max((int(v) for v in mapping.values()), default=0) + 1
    for identity in sorted({r["id_personne"] for r in rows} - mapping.keys()):
        mapping[identity] = str(next_id)
        next_id += 1
    write_csv(path, [{"cle_identite": k, "id_personne": v}
                     for k, v in sorted(mapping.items(), key=lambda pair: int(pair[1]))],
              ["cle_identite", "id_personne"])
    for row in rows:
        row["id_personne"] = mapping[row["id_personne"]]
    return mapping


def apply_identity_decisions(rows, path, aliases=None):
    if not path.exists():
        write_csv(path, [], ["id_ligne_source", "id_personne_valide", "justification", "reference_documentaire"])
    decisions = read_csv(path)
    known = {r["id_ligne_source"]: r for r in rows}
    seen = set()
    for decision in decisions:
        line = decision["id_ligne_source"]
        if line in seen or line not in known:
            raise ValueError(f"Décision dupliquée ou ligne inconnue : {line}")
        seen.add(line)
        # Une ligne sans matricule constitue toujours une identité distincte.
        if not known[line]["matricule_normalise"]:
            continue
        if not all(decision.get(k, "").strip() for k in ["id_personne_valide", "justification", "reference_documentaire"]):
            raise ValueError(f"Décision d'identité incomplète : {line}")
        target = decision["id_personne_valide"].strip()
        target = (aliases or {}).get(target, target)
        if aliases is not None and target not in set(aliases.values()):
            raise ValueError(f"Identifiant cible inconnu : {target}. Utilisez le référentiel numérique.")
        # Ne pas rattacher non plus une ligne matriculée à une identité sans matricule.
        if any(r["id_personne"] == target and not r["matricule_normalise"] for r in rows):
            raise ValueError("Rattachement interdit à une personne sans matricule.")
        row = known[line]
        row.update(id_personne=target, statut_identite="valide_manuellement",
                   identite_eligible_strict=1, justification_identite=decision["justification"],
                   reference_identite=decision["reference_documentaire"])


def audit_events(rows):
    groups = defaultdict(list)
    for r in rows:
        r.update(groupe_doublon="", statut_doublon="non_detecte", id_ligne_retenue=r["id_ligne_source"],
                 conserver_evenement=1, groupe_simultane="", nb_evenements_meme_date=1,
                 statut_simultaneite="non_detectee")
        # Les familles de fonction ne servent JAMAIS à supprimer des événements.
        event = (r["id_personne"], r["date_conseil"], key(r["poste_harmonise"]), key(r["ministere_harmonise"]))
        r["id_evenement"] = uid("E_", *event)
        groups[event].append(r)
    for event, group in groups.items():
        if len(group) < 2:
            continue
        group_id = uid("D_", *event)
        texts = defaultdict(list)
        for r in group:
            # Un texte vide ne constitue jamais une preuve de duplication.
            text = surface(r["extrait_exact"]) or r["id_ligne_source"]
            texts[text].append(r)
        for subgroup in texts.values():
            ordered = sorted(subgroup, key=lambda r: (r["statut_date"] != "coherente_nom_fichier", r["document_id"], r["id_ligne_source"]))
            keeper = ordered[0]["id_ligne_source"]
            for i, r in enumerate(ordered):
                r["groupe_doublon"] = group_id
                if len(subgroup) > 1:
                    r["statut_doublon"] = "repetition_textuelle_retenue" if i == 0 else "repetition_textuelle_ecartee"
                    r["conserver_evenement"] = int(i == 0)
                    r["id_ligne_retenue"] = keeper
                if len(texts) > 1 and r["conserver_evenement"]:
                    r["statut_doublon"] = "doublon_potentiel_a_verifier"
    by_day = defaultdict(list)
    for r in rows:
        if r["conserver_evenement"]:
            by_day[(r["id_personne"], r["date_conseil"])].append(r)
    for event, group in by_day.items():
        if len(group) < 2:
            continue
        distinct = {(key(r["poste_harmonise"]), key(r["ministere_harmonise"])) for r in group}
        for r in group:
            r["groupe_simultane"] = uid("S_", *event)
            r["nb_evenements_meme_date"] = len(group)
            r["statut_simultaneite"] = "nominations_simultanees_possibles" if len(distinct) > 1 else "repetitions_a_verifier"
    # Chaque annotation de répétition garde la trace du contexte de la ligne retenue.
    lookup = {r["id_ligne_source"]: r for r in rows}
    for r in rows:
        if not r["conserver_evenement"]:
            keeper = lookup[r["id_ligne_retenue"]]
            for field in ["groupe_simultane", "nb_evenements_meme_date", "statut_simultaneite"]:
                r[field] = keeper[field]


def run(source, output):
    rows = read_csv(source)
    if not rows:
        raise ValueError("Le CSV source est vide")
    original_fields = list(rows[0])
    required = {"document_id", "date_conseil", "nom", "matricule", "ministere", "poste_nomination", "page", "extrait_exact"}
    if not required.issubset(original_fields):
        raise ValueError(f"Colonnes absentes : {required - set(original_fields)}")
    occurrences = Counter()
    for r in rows:
        fingerprint = uid("L_", [(k, r[k]) for k in sorted(original_fields)])
        occurrences[fingerprint] += 1
        r["id_ligne_source"] = f"{fingerprint}_{occurrences[fingerprint]}"
        r["justification_identite"] = r["reference_identite"] = ""
        try:
            day = date.fromisoformat(r["date_conseil"])
            in_period = 2015 <= day.year <= 2025
            status = "coherente_nom_fichier"
        except ValueError:
            in_period, status = False, "date_invalide"
        match = re.search(r"(20\d{2})[_-](\d{2})[_-](\d{2})", r["document_id"])
        r["date_nom_fichier"] = "-".join(match.groups()) if match else ""
        if status != "date_invalide":
            if not match:
                status = "nom_fichier_non_date"
            elif r["date_nom_fichier"] != r["date_conseil"]:
                status = "discordance_date_a_verifier"
        r.update(statut_date=status, dans_periode=int(in_period))

    dict_dir = output / "dictionnaires"
    ministries = dictionary(rows, "ministere", dict_dir / "ministeres.csv", False)
    positions = dictionary(rows, "poste_nomination", dict_dir / "postes.csv", True)
    for r in rows:
        m, p = ministries[r["ministere"]], positions[r["poste_nomination"]]
        r.update(ministere_harmonise=m["libelle_harmonise"], domaines_ministere_proposes=m["domaines_proposes"],
                 poste_harmonise=p["libelle_harmonise"], fonction_harmonisee=p["fonction_harmonisee"],
                 famille_fonction=p["famille_fonction"], niveau_administratif=p["niveau_administratif"],
                 nature_nomination=p["nature_nomination"], statut_codage_fonction=p["statut_codage_fonction"],
                 alerte_intitule_ministere=m.get("alerte_intitule", ""),
                 statut_harmonisation_ministere=m["statut_validation"], statut_harmonisation_poste=p["statut_validation"])
        r["ministere_historique"] = r["ministere_harmonise"]
        r.update(fusionner(r["ministere_historique"]))
        # Une correction validée manuellement reste prioritaire dans le dictionnaire.
        if m["statut_validation"] == "valide_manuellement":
            r["statut_fusion_ministere"] = "validation_manuelle_prioritaire"
        else:
            if r["alias_ministere_applique"]:
                r["ministere_historique"] = surface(r["alias_ministere_applique"])
                r["ministere_harmonise"] = key(r["alias_ministere_applique"])
                r["statut_harmonisation_ministere"] = "alias_verifie"
            if r["ministere_reference"]:
                r["ministere_harmonise"] = r["ministere_reference"]
                r["statut_harmonisation_ministere"] = "fusion_historique_automatique"
        r["id_poste"] = uid("POSTE_", key(r["ministere_harmonise"]), key(r["poste_harmonise"]))
    by_mat, by_name = assign_identities(rows)
    aliases = simplify_person_ids(rows, dict_dir / "correspondance_ids_personnes.csv")
    apply_identity_decisions(rows, dict_dir / "decisions_identites.csv", aliases)
    audit_events(rows)
    for r in rows:
        reasons = []
        if not r["dans_periode"]:
            reasons.append("hors_periode_ou_date_invalide")
        if not r["poste_nomination"].strip():
            reasons.append("poste_absent")
        if not r["ministere"].strip():
            reasons.append("ministere_absent")
        if r["alerte_intitule_ministere"] and r["statut_harmonisation_ministere"] != "valide_manuellement":
            reasons.append("intitule_ministere_a_verifier")
        if not r["identite_eligible_strict"]:
            reasons.append("identite_a_verifier")
        if r["statut_date"] != "coherente_nom_fichier":
            reasons.append("date_a_verifier")
        if not r["conserver_evenement"]:
            reasons.append("repetition_textuelle")
        if r["statut_doublon"] == "doublon_potentiel_a_verifier":
            reasons.append("doublon_a_verifier")
        if r["groupe_simultane"]:
            reasons.append("simultaneite_a_verifier")
        if r["nature_nomination"] in {"grade_ou_integration_a_verifier", "a_qualifier"}:
            reasons.append("nature_nomination_a_qualifier")
        r["motifs_exclusion_stricte"] = " | ".join(reasons)
        r["eligible_trajectoire_stricte"] = int(not reasons)
    # Si un épisode est ambigu, retirer seulement sa ligne créerait un faux saut.
    # Toute la personne est donc écartée du sous-ensemble de trajectoires strictes.
    blocked = {r["id_personne"] for r in rows if r["dans_periode"] and r["conserver_evenement"] and not r["eligible_trajectoire_stricte"]}
    # Une ligne sans matricule peut être un épisode intermédiaire d'une identité
    # matriculée. Ne pas connecter ses événements en ignorant ce candidat.
    known_by_name, known_by_mat = defaultdict(set), defaultdict(set)
    for r in rows:
        if r["matricule_format_reconnu"]:
            known_by_name[r["cle_nom_recherche"]].add(r["id_personne"])
            known_by_mat[r["matricule_normalise"]].add(r["id_personne"])
    uncertain_candidates = set()
    for r in rows:
        if r["dans_periode"] and r["conserver_evenement"] and not r["identite_eligible_strict"]:
            uncertain_candidates.update(known_by_name[r["cle_nom_recherche"]])
            uncertain_candidates.update(known_by_mat[r["matricule_normalise"]])
    blocked.update(uncertain_candidates)
    for r in rows:
        if r["eligible_trajectoire_stricte"] and r["id_personne"] in blocked:
            r["eligible_trajectoire_stricte"] = 0
            r["motifs_exclusion_stricte"] = (
                "episode_candidat_non_rattache" if r["id_personne"] in uncertain_candidates
                else "autre_evenement_personne_a_verifier"
            )
    fields = list(rows[0])
    reports = {}
    for r in rows:
        value = r["ministere"]
        if value not in reports:
            reports[value] = {k: r[k] for k in ["ministere", "ministere_historique", "ministere_harmonise",
                "code_ministere_reference", "codes_ministeres_candidats", "statut_fusion_ministere",
                "type_concordance_ministere", "note_concordance_ministere",
                "alias_ministere_applique", "reference_alias_ministere"]}
            reports[value]["nombre_lignes"] = 0
        reports[value]["nombre_lignes"] += 1
    report_rows = sorted(reports.values(), key=lambda x: (-x["nombre_lignes"], x["ministere"]))
    write_csv(output / "rapport_fusion_ministeres.csv", report_rows, list(report_rows[0]))
    write_csv(output / "nominations_annotees.csv", rows, fields)
    # Export consolidé : toutes les lignes et colonnes sources, enrichies des
    # identifiants, des ministères harmonisés et des statuts de contrôle.
    write_csv(output / "nominations_2015_2025_fiabilise.csv", rows, fields)
    clean = [r for r in rows if r["dans_periode"] and r["conserver_evenement"] and r["poste_nomination"].strip()]
    strict = [r for r in rows if r["eligible_trajectoire_stricte"]]
    write_csv(output / "nominations_dedoublonnees.csv", clean, fields)
    write_csv(output / "nominations_trajectoires_strictes.csv", strict, fields)
    write_csv(output / "doublons_audites.csv", [r for r in rows if r["groupe_doublon"]], fields)
    write_csv(output / "nominations_simultanees.csv", [r for r in rows if r["groupe_simultane"] and r["conserver_evenement"]], fields)
    write_csv(output / "dates_a_verifier.csv", [r for r in rows if r["statut_date"] != "coherente_nom_fichier"], fields)

    identities = defaultdict(list)
    for r in rows:
        identities[r["id_personne"]].append(r)
    reference = []
    for person, observations in sorted(identities.items()):
        reference.append({"id_personne": person, "noms_observes": " | ".join(sorted({r["nom"] for r in observations})),
                          "matricules_observes": " | ".join(sorted({r["matricule"] for r in observations})),
                          "statuts": " | ".join(sorted({r["statut_identite"] for r in observations})),
                          "nb_lignes": len(observations), "nb_dates": len({r["date_conseil"] for r in observations}),
                          "identite_eligible_strict": int(all(r["identite_eligible_strict"] for r in observations))})
    write_csv(output / "referentiel_personnes.csv", reference, list(reference[0]))
    index_mat, index_name = defaultdict(set), defaultdict(set)
    for r in rows:
        if r["matricule_format_reconnu"]:
            index_mat[r["matricule_normalise"]].add(r["id_personne"])
            index_name[r["cle_nom_recherche"]].add(r["id_personne"])
    reviews = []
    for r in rows:
        if r["identite_eligible_strict"]:
            continue
        candidates = (index_mat[r["matricule_normalise"]] | index_name[r["cle_nom_recherche"]]) - {r["id_personne"]}
        reviews.append(dict(r, ids_candidats=" | ".join(sorted(candidates)),
                            consigne="Examiner PDF, nom complet et matricule ; aucune fusion floue automatique."))
    write_csv(output / "identites_a_verifier.csv", reviews, fields + ["ids_candidats", "consigne"])
    summary = {
        "version_pipeline": VERSION,
        "sha256_source": hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        "nombre_lignes_source": len(rows),
        "nombre_lignes_dans_periode": sum(r["dans_periode"] for r in rows),
        "nombre_identifiants_personnes": len(identities),
        "statuts_identite_lignes": dict(Counter(r["statut_identite"] for r in rows)),
        "statuts_doublon_lignes": dict(Counter(r["statut_doublon"] for r in rows)),
        "nombre_groupes_doublons": len({r["groupe_doublon"] for r in rows if r["groupe_doublon"]}),
        "nombre_groupes_simultanes": len({r["groupe_simultane"] for r in rows if r["groupe_simultane"]}),
        "statuts_dates_lignes": dict(Counter(r["statut_date"] for r in rows)),
        "ministeres_originaux": len({r["ministere"] for r in rows}),
        "ministeres_harmonises": len({r["ministere_harmonise"] for r in rows}),
        "postes_originaux": len({r["poste_nomination"] for r in rows}),
        "postes_harmonises": len({r["poste_harmonise"] for r in rows}),
        "fonctions_proposees": dict(Counter(r["fonction_harmonisee"] for r in rows)),
        "nombre_lignes_dedoublonnees_dans_periode": len(clean),
        "nombre_lignes_trajectoires_strictes": len(strict),
        "nombre_personnes_trajectoires_strictes": len({r["id_personne"] for r in strict}),
        "limites": [
            "Identités cohérentes automatiquement, sans certification documentaire ni résolution exhaustive des homonymes.",
            "Les identités sans matricule restent provisoires ; candidats proposés séparément.",
            "Répétitions textuelles écartées dans la copie analytique, conservées intégralement dans les annotations.",
            "Les intitulés complets restent distincts des familles ; aucune fusion historique des ministères.",
            "Les familles, niveaux et domaines sont des propositions lexicales à valider.",
            "Les dates discordantes ne sont jamais corrigées automatiquement.",
            "Le sous-ensemble strict exclut une personne si un événement conservé dans la période reste ambigu ; il n'est pas représentatif de toute la population.",
            "La couverture documentaire et les erreurs non détectées d'extraction restent à auditer.",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "bilan_qualite.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT.parent / "extraction_evaluation" / "nominations_2015_2025.csv")
    parser.add_argument("--sortie", type=Path, default=ROOT / "fiabilisation")
    args = parser.parse_args()
    summary = run(args.source, args.sortie)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
