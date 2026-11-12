"""Extraction des nominations des comptes rendus du Conseil des ministres.

Le script utilise le texte embarqué dans les PDF et produit un CSV UTF-8 avec BOM,
directement ouvrable dans Excel. Il conserve dans ``extrait_exact`` la formulation
du document (les seuls changements sont la suppression des retours de ligne de mise
en page et des en-têtes de page).
"""

from __future__ import annotations

import csv
import argparse
import re
import shutil
import subprocess
from pathlib import Path

import fitz  # PyMuPDF


FIELDS = [
    "document_id",
    "date_conseil",
    "civilite",
    "nom",
    "matricule",
    "emploi",
    "grade",
    "classe",
    "echelon",
    "ministere",
    "poste_nomination",
    "page",
    "extrait_exact",
]

# L'OCR est une solution de repli : une couche texte, même courte, reste la
# source de référence. Ainsi, une reconnaissance imparfaite ne peut jamais
# remplacer ni faire perdre du texte natif.
OCR_MIN_TEXT_CHARS = 1
OCR_LANGUAGES = "fra+eng"


def clean(value: str) -> str:
    """Supprime seulement les artefacts de mise en page du PDF."""
    value = value.replace("\u00a0", " ").replace("\xad", "")
    value = re.sub(r"\bPage\s+\d+(?:\s+sur\s+\d+)?\b", " ", value, flags=re.I)
    # En-tête courant de certains comptes rendus de 2023, parfois inséré au
    # milieu d'une phrase lors de l'extraction du texte PDF.
    value = re.sub(r"\bPP-G(?:/TRANS)?\s+N[^\s]*\s+du\s+\d{1,2}\s+\w+\s+\d{4}\b", " ", value, flags=re.I)
    # Les retours de ligne après un trait d'union de césure (« ci- après »)
    # empêchent les expressions collectives de reconnaître « ci-après ».
    value = re.sub(r"(?<=[^\W\d_])-\s+(?=\w)", "-", value)
    return re.sub(r"\s+", " ", value).strip()


def ocr_page(page: fitz.Page) -> str:
    """Reconnaît une page image avec Tesseract, sans créer de fichier temporaire."""
    pixmap = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
    result = subprocess.run(
        ["tesseract", "stdin", "stdout", "-l", OCR_LANGUAGES, "--psm", "6"],
        input=pixmap.tobytes("png"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Échec OCR Tesseract : {message}")
    return clean(result.stdout.decode("utf-8", errors="replace"))


def extract_page_text(page: fitz.Page, use_ocr: bool) -> tuple[str, bool]:
    """Préserve le texte natif et utilise l'OCR seulement s'il est absent."""
    native_text = clean(page.get_text())
    if not use_ocr or len(native_text) >= OCR_MIN_TEXT_CHARS:
        return native_text, False
    ocr_text = ocr_page(page)
    if len(ocr_text) > len(native_text):
        return ocr_text, True
    return native_text, False


def clean_ministry(value: str) -> str:
    value = clean(value).rstrip(" -;:.")
    value = re.sub(r"\s+Pour\s+le\s+compte\b.*$", "", value, flags=re.I)
    # Artefact de mise en page rencontré dans deux comptes rendus où l'en-tête
    # « PREMIER MINISTERE » est joint à la phrase suivante.
    if re.match(r"^MINISTERE\s+Le\s+Conseil\s+a\b", value, flags=re.I):
        return "PREMIER MINISTERE"
    # Dans les conseils d'administration, « Au titre du ministère… » peut être
    # suivi du nom du conseil. Ce complément est une fonction, non un ministère.
    value = re.sub(r"\s+au\s+Conseil\s+d['’]administration\b.*$", "", value, flags=re.I)
    # Les titres sont capitalisés dans les PDF. Cette normalisation ne touche pas
    # les mots à l'intérieur de la dénomination du ministère.
    return value


def iso_date_from_filename(path: Path) -> str:
    match = re.search(r"(20\d{2})_(\d{2})_(\d{2})", path.stem)
    return "-".join(match.groups()) if match else ""


def iso_date_from_text(value: str) -> str:
    """Lit la date du conseil dans les premières pages si le fichier n'est pas daté."""
    match = re.search(
        r"\b(\d{1,2})\s+(janvier|f[é\uFFFD]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[é\uFFFD]cembre)\s+(20\d{2})\b",
        value,
        re.I,
    )
    if not match:
        return ""
    months = {
        "janvier": 1, "février": 2, "f\uFFFDvrier": 2, "mars": 3, "avril": 4,
        "mai": 5, "juin": 6, "juillet": 7, "août": 8, "septembre": 9,
        "octobre": 10, "novembre": 11, "décembre": 12, "d\uFFFDcembre": 12,
    }
    day, month_name, year = match.groups()
    month = months.get(month_name.lower())
    return f"{year}-{month:02d}-{int(day):02d}" if month else ""


def position_page(pages: list[tuple[int, str]], offset: int) -> int:
    total = 0
    for number, text in pages:
        if offset < total + len(text) + 1:
            return number
        total += len(text) + 1  # séparateur de page \f
    return pages[-1][0]


def text_before_first_marker(value: str) -> str:
    """Retire une éventuelle nouvelle rubrique absorbée à la fin d'un item."""
    markers = [
        r"\s+(?:[A-Z]|III\.\d+)\.\s+(?:AU\s+TITR\w*|MINISTERE)\b",
        r"\s+[A-Z]\.\s+(?:SECRETARIAT|PRESIDENCE|PRIMATURE|MINISTERE)\b",
        r"\s+(?:[IVXLCDM]+)\.\d+\.\s+NOMINATIONS?\b",
        r"\s+(?:[IVXLCDM]+|\d+)(?:\.\d+)?\.\s+(?:COMMUNICATIONS?|DIVERS|EXAMEN|ADOPTION)\b",
        r"\s+III\.\d+\.\s+NATURALISATIONS?\b",
        r"\s+(?:[IVXLCDM]+|\d+)\.\s+NATURALISATIONS?\b",
        r"[.;]\s*(?:\d+\s*)?Le\s+(?:premier|deuxième|second|troisième|quatrième|cinquième|sixième|même)\s+décret\b",
        r"\s+Le\s+(?:[a-zà-ÿ-]+)\s+(?:décret\s+)?(?:nomme|renouvelle|porte)\b",
        r"[.;]\s+Sont\s+nomm",
        # Fin de décision suivie d'une liste d'agents intégrés : ce n'est pas
        # le complément du poste de la personne extraite juste avant.
        r"[.;]\s+Sont\s+int\w*",
        r"[.;]\s+Les\s+personnes\s+dont(?:\s+les)?(?:\s+noms?)?\s+suivent\s+sont\s+nomm",
        r"[.;]\s+Les\s+personnes\b[^.:;]{0,160}\bsuivent\s+sont\s+nomm",
        r"[.;]\s+Les\s+enseignants\s+dont\s+les\s+noms?\s+suivent\s+sont\s+nomm",
        r"[.;]\s+Les\s+Greffiers\s+en\s+chef\s+dont\s+les\s+noms?\s+suivent\s+sont\s+nomm",
        r"[.;]\s+Les\s+Magistrats\s+dont\s+les\s+noms?\s+suivent\s+sont\s+nomm",
        r"[.;]\s+Sont\s+relev",
        # En-têtes internes d'une liste collective, placés après la dernière
        # personne de la sous-liste précédente.
        r"\s+MEMBRES?\s+(?:TITULAIRES?|SUPPLEANTS?)\b",
        r"[.;]\s+AU\s+TITRE\s+D(?:U|E\s+(?:LA|L['’\uFFFD])|ES)\b",
        r"[.;]\s+Pour\s+le\s+compte\b",
        r"[.;]\s+Nomination\s+des\s+membres\b",
        r"[.;]\s+ADMINISTRATEURS?\s+REPRESENTANT\b",
        # Sous-rubriques de listes collectives : sans cette borne, leur titre
        # est accidentellement rattaché au nom de la dernière personne.
        r"[.;]\s+REPR\w*\s+(?:DU|DES|DE|D['’\uFFFD]|[A-Z])\b",
        r"[.;]\s+MEMBRES?\s+(?:TITULAIRES?|SUPPLEANTS?)\b",
        r"[.;]\s+MINISTERE\b",
        r"[.;]\s+Pour\s+le\s+Ministre\b",
        r"[.;]\s+Le\s+Ministre\b",
    ]
    end = len(value)
    for marker in markers:
        found = re.search(marker, value, flags=re.I)
        if found:
            end = min(end, found.start())
    return value[:end].strip(" ;")


def split_after_matricule(value: str) -> tuple[str, str]:
    """Retourne le matricule, puis le reste descriptif de la nomination."""
    match = re.search(r"\bMle\s*\.?\s*([^,;]+?)\s*[,;]", value, flags=re.I)
    if not match:
        match = re.search(
            r"\bMle\s*\.?\s*([A-Z]?\s*\d(?:[\d\s]*\d)?(?:\s*[A-Z]|/[A-Z])?)\b\s*,?",
            value,
            flags=re.I,
        )
    if not match:
        return "", value.strip(" ,")
    matricule = re.sub(r"\s+", " ", match.group(1)).strip()
    matricule = re.sub(r"\s*\(\s*Mle\b[^)]*\)", "", matricule, flags=re.I).strip()
    return matricule, value[match.end() :].strip(" ,")


def parse_qualifications(value: str) -> tuple[str, str, str, str, str]:
    """Sépare emploi, grade, classe, échelon et éventuelle localisation."""
    value = value.strip(" ,.;")
    # Certains comptes rendus omettent « nommé » ("est Directeur") ou
    # comportent une ponctuation/OCR dégradé ("est nommé,", "en nommée").
    stop = re.search(
        r"\b(?:est\s+(?:nomm(?:[é\uFFFD]|e)\w*\s*,?\s*)?|en\s+nomm(?:[é\uFFFD]|e)\w*\s*,?\s*)",
        value,
        flags=re.I,
    )
    before_post = value[: stop.start()].strip(" ,") if stop else value

    grade_match = re.search(
        r"\b(?:\d+(?:er|ère|eme|ème)\s*grade|grade\s+(?:exceptionnel|terminale?|initial|intermédiaire))\b",
        before_post,
        flags=re.I,
    )
    classe_match = re.search(
        r"\b(?:classe\s+(?:exceptionnelle|terminale?|initiale?|intermédiaire)|\d+(?:er|ère|eme|ème)\s*classe|catégorie\s+[A-Z]\d+)\b",
        before_post,
        flags=re.I,
    )
    echelon_match = re.search(r"\b\d+(?:er|ère|eme|ème)\s*échelon\b", before_post, flags=re.I)
    qualifiers = [m for m in (grade_match, classe_match, echelon_match) if m]

    location_match = re.search(
        r",\s*((?:Région|Province|Département|Commune|Circonscription|District)\b.*)$",
        before_post,
        flags=re.I,
    )
    location = location_match.group(1).strip(" ,.;") if location_match else ""

    end_employment = len(before_post)
    if qualifiers:
        end_employment = min(end_employment, min(m.start() for m in qualifiers))
    if location_match:
        end_employment = min(end_employment, location_match.start())
    emploi = before_post[:end_employment].strip(" ,")
    return (
        emploi,
        grade_match.group(0) if grade_match else "",
        classe_match.group(0) if classe_match else "",
        echelon_match.group(0) if echelon_match else "",
        location,
    )


def appointment_from_bullet(
    bullet: str,
    document_id: str,
    date_conseil: str,
    ministere: str,
    group_post: str,
    page: int,
) -> dict[str, str] | None:
    bullet = re.sub(r"^-\s*", "", text_before_first_marker(clean(bullet)))
    # Les prolongements de listes collectives peuvent commencer par « de/du »
    # et décrire un organisme, non une personne nommée.
    if re.match(r"^(?:du|des|de(?:\s|['’])|au|aux|la|le|les|[Ll]['’])\b", bullet):
        return None
    person = re.match(r"(?:(Monsieur|Madame|Mademoiselle|Mme\.?)\s+)?(.+)", bullet, flags=re.I)
    if not person:
        return None
    civilite_raw = person.group(1).rstrip(".").lower() if person.group(1) else ""
    civilite = {"monsieur": "Monsieur", "madame": "Madame", "mademoiselle": "Mademoiselle", "mme": "Madame"}.get(civilite_raw, "")
    after_civilite = person.group(2)
    # Le premier séparateur après le nom est toujours une virgule; Mle peut être
    # absent pour quelques personnalités nommées dans les listes collectives.
    matricule_start = re.search(r"\s*,?\s*Mle\s*\.?\s*", after_civilite, flags=re.I)
    if matricule_start:
        nom = after_civilite[: matricule_start.start()]
        remainder = after_civilite[matricule_start.start() :]
    elif "," in after_civilite:
        nom, remainder = after_civilite.split(",", 1)
    elif group_post:
        # Une puce de liste collective peut ne contenir que le nom : le poste
        # est porté par la phrase introductive de la liste.
        nom = re.split(
            r"\s+(?:[A-Z]\.\s+)?Au\s+titre\b",
            after_civilite,
            maxsplit=1,
            flags=re.I,
        )[0].strip(" ;.")
        remainder = ""
    else:
        return None
    nom = nom.strip()
    matricule, details = split_after_matricule(remainder)
    representation = ""
    # Dans certaines listes de conseils, la qualité de représentant suit
    # l'emploi de la personne sans répéter le verbe de nomination.
    if group_post:
        role_match = re.search(
            r",\s*((?:Membre|Administrateur)\s+repr\w*\b.+)$",
            details,
            flags=re.I,
        )
        if role_match:
            representation = role_match.group(1).strip(" ;.")
            details = details[: role_match.start()].strip(" ,")
    emploi, grade, classe, echelon, location = parse_qualifications(details)

    post_match = re.search(
        r"\b(?:est\s+(?:nomm(?:[é\uFFFD]|e)\w*\s*,?\s*)?|en\s+nomm(?:[é\uFFFD]|e)\w*\s*,?\s*)(.+)$",
        bullet,
        flags=re.I,
    )
    if post_match:
        poste = post_match.group(1).strip(" ;.")
    elif group_post:
        poste = group_post.strip(" ;.")
        if representation:
            poste = f"{representation} — {poste}"
        if location:
            poste = f"{poste} — {location}"
    else:
        # Un item sans verbe de nomination ni rubrique collective ne peut pas être
        # identifié avec suffisamment de sûreté.
        return None

    return {
        "document_id": document_id,
        "date_conseil": date_conseil,
        "civilite": civilite,
        "nom": nom,
        "matricule": matricule,
        "emploi": emploi,
        "grade": grade,
        "classe": classe,
        "echelon": echelon,
        "ministere": ministere,
        "poste_nomination": poste,
        "page": str(page),
        "extrait_exact": bullet,
    }


def appointment_from_prose(
    sentence: str,
    document_id: str,
    date_conseil: str,
    ministere: str,
    page: int,
) -> dict[str, str] | None:
    """Traite les nominations aux conseils d'administration rédigées en prose."""
    sentence = text_before_first_marker(clean(sentence)).strip(" ;")
    # Dans quelques PDF, la dernière personne d'une liste sans ponctuation est
    # immédiatement suivie du décret suivant. On repart alors à ce décret pour
    # ne pas attribuer ses informations à la personne précédente.
    decrees = list(re.finditer(
        r"\bLe\s+[a-zà-ÿ-]+\s+(?:décret\s+)?(?:nomme|porte\s+nomination\s+de)\s+(?=(?:Monsieur|Madame|Mademoiselle)\b)",
        sentence,
        re.I,
    ))
    if decrees:
        start = decrees[0].start() if decrees[0].start() else 0
        end = decrees[1].start() if len(decrees) > 1 else len(sentence)
        sentence = sentence[start:end].strip(" ;:")
    if not re.search(r"\b(?:nomination|nomme|nommé|nommée|nomm\uFFFD|désigne|renouvel\w*)\b", sentence, re.I):
        return None
    person = re.search(r"\b(Monsieur|Madame|Mademoiselle)\s+(.+)", sentence, re.I)
    if not person:
        return None
    civilite = person.group(1).capitalize()
    content = person.group(2)
    matricule_start = re.search(r"\s*,?\s*Mle\s*\.?\s*", content, flags=re.I)
    if matricule_start:
        nom = content[: matricule_start.start()]
        remainder = content[matricule_start.start() :]
    elif "," in content:
        nom, remainder = content.split(",", 1)
    else:
        return None
    matricule, details = split_after_matricule(remainder)
    emploi, grade, classe, echelon, _ = parse_qualifications(details)

    # Dans ces phrases, la responsabilité de nomination suit généralement le
    # dernier emploi après une virgule (Administrateur, Président, Membre, etc.).
    role_match = re.search(
        r"(?:^|,\s*|\s+)((?:Administrateur\s+(?:représentant|au\s+titre|au\s+Conseil)|"
        r"Président|Présidente|Membre|Représentant|Directeur|Directrice)\b.+)$",
        details,
        re.I,
    )
    if role_match:
        poste = role_match.group(1).strip(" .;")
        emploi = details[: role_match.start(1)].strip(" ,.;")
    else:
        # Si aucun mot-clé de fonction n'est repéré, on conserve le reste afin de
        # ne pas perdre l'information dans le CSV.
        poste = details.strip(" .;")
    if not poste:
        return None
    return {
        "document_id": document_id,
        "date_conseil": date_conseil,
        "civilite": civilite,
        "nom": nom.strip(),
        "matricule": matricule,
        "emploi": emploi,
        "grade": grade,
        "classe": classe,
        "echelon": echelon,
        "ministere": ministere,
        "poste_nomination": poste,
        "page": str(page),
        "extrait_exact": sentence,
    }


def nomination_start_page(pages: list[tuple[int, str]]) -> int | None:
    """Repère le début des décisions de nomination, avec ou sans grand titre."""
    heading = r"\b(?:[IVXLCDM]+|\d+)(?:\s*[.:]\s*\d+)?\s*[.:-]\s*NOMINATIONS?\b"
    narrative = r"\bLe\s+Conseil\s+(?:a\s+)?(?:proc\w*|adopt\w*)[^.\f]{0,240}\b(?:nominations?|nomm\w*|d\w*signe)\b"
    individual = r"\b(?:Monsieur|Madame|Mademoiselle|Mme\.?)\s+[^.\f]{0,400}\best\s+nomm\w*\b"
    collective = (
        r"\b(?:Sont\s+(?:nomm|int[ée\uFFFD]gr|affect|promu|admis)"
        r"|Les\s+personnes\s+dont[^.\f]{0,120}\s+sont\s+nomm)"
    )
    for index, (_, text) in enumerate(pages):
        # III. NOMINATIONS, III.1. NOMINATION ou II.1. NOMINATIONS, ainsi que
        # les formules narratives de décision.
        if (
            re.search(heading, text, flags=re.I)
            or re.search(narrative, text, flags=re.I)
            or re.search(collective, text, flags=re.I)
        ):
            return index
        if re.search(individual, text, flags=re.I):
            # Une nomination isolée est souvent annoncée à la page précédente
            # par « le ministre de … a rendu compte ». Cette page fournit le
            # rattachement ministériel de la personne nommée.
            return max(0, index - 1)
    return None


def extract_from_pdf(path: Path, use_ocr: bool = False) -> tuple[list[dict[str, str]], int]:
    document = fitz.open(path)
    pages = []
    ocr_pages = 0
    for number, page in enumerate(document):
        text, used_ocr = extract_page_text(page, use_ocr)
        pages.append((number + 1, text))
        ocr_pages += used_ocr
    start_page = nomination_start_page(pages)
    if start_page is None:
        return [], ocr_pages
    # La première nomination peut se trouver sur la même page que le titre ou
    # la phrase introductive ; cette page doit donc être conservée.
    section_pages = pages[start_page:]
    if not section_pages:
        return [], ocr_pages

    separator = "\f"
    section = separator.join(text for _, text in section_pages)
    document_id = path.name
    # La date imprimée dans le compte rendu prévaut : un fichier peut avoir été
    # classé sous un nom erroné tout en conservant sa date officielle.
    date_conseil = iso_date_from_text(" ".join(text for _, text in pages[:2])) or iso_date_from_filename(path)
    rows: list[dict[str, str]] = []
    ministry = ""
    group_post = ""
    board_title_match = re.search(
        r"(?:\b(?:[IVXLCDM]+|\d+)(?:\s*[.:]\s*\d+)?\s*[.:-]\s*)?NOMINATIONS?\s+DANS\s+LES\s+CONSEILS",
        section,
        re.I,
    )

    events: list[tuple[int, str, re.Match[str]]] = []
    # Une rubrique individuelle utilise « AU TITRE DU MINISTERE ». Dans les
    # conseils d'administration elle est plus brève (« A. MINISTERE ... »).
    for match in re.finditer(
        r"(?:\b[A-Z][.-]\s*)?AU\s+TITRE\s+D(?:U|E\s+(?:LA|L['’\uFFFD])|ES)\s+([^.;\f]+?)(?=\s+-\s+(?:(?:Monsieur|Madame|Mademoiselle)\b|[A-ZÀ-Ý])|\s+(?:Sont\s+nomm|Les\s+personnes\s+dont(?:\s+les)?(?:\s+noms?)?\s+suivent|Pour\s+le\s+compte)\b|\f|$)",
        section,
        re.I,
    ):
        events.append((match.start(), "ministry", match))
    # Certains comptes rendus placent le nom juste après le titre du ministère,
    # sans puce ni deux-points.
    for match in re.finditer(
        r"(?:\b[A-Z][.-]\s*)?AU\s+TITRE\s+D(?:U|E\s+(?:LA|L['’\uFFFD])|ES)\s+([^.;\f]+?)(?=\s+(?:Monsieur|Madame|Mademoiselle|Mme\.?)\b)",
        section,
        re.I,
    ):
        events.append((match.start(), "ministry", match))
    # Certaines rubriques relèvent d'une autorité administrative plutôt que
    # d'un ministère; elle remplit le même champ de rattachement.
    for match in re.finditer(
        r"(?:\b[A-Z][.-]\s*)?AU\s+TITRE\s+DE\s+L.?\s*(AUTORITE\s+[^.;\f]+?)(?=\s+-\s+(?:(?:Monsieur|Madame|Mademoiselle)\b|[A-ZÀ-Ý])|\s+Sont\s+nomm|\f|$)",
        section,
        re.I,
    ):
        events.append((match.start(), "ministry", match))
    # Dans les nominations aux conseils, certains titres de ministère ne sont
    # pas précédés de « A. » ni de « Au titre du ».
    for match in re.finditer(
        r"(?:\b[A-Z][.-]\s*)?(?<!PREMIER )\b(MINISTERE\s+[^-]+?)(?=\s+Le\s+Conseil\s+(?:a|adopte)\b)",
        section,
        re.I,
    ):
        events.append((match.start(), "ministry", match))
    # Certains PDF conservent l'accent dans « Ministère », que l'OCR et les
    # anciens documents écrivent parfois sans accent. Les deux variantes sont
    # des intitulés de rattachement équivalents.
    for match in re.finditer(
        r"(?:\b[A-Z][.-]\s*)?(?<!PREMIER )\b(Minist[èe\uFFFD]re\s+[^-]+?)(?=\s+Le\s+Conseil\s+(?:a|adopte)\b)",
        section,
        re.I,
    ):
        events.append((match.start(), "ministry", match))
    for match in re.finditer(
        r"\b(PREMIER\s+MINISTERE|PRESIDENCE\s+DU\s+FASO|PRIMATURE)(?=\s+Le\s+Conseil\s+(?:a|adopte)\b)",
        section,
        re.I,
    ):
        events.append((match.start(), "ministry", match))
    # Une nomination isolée peut être précédée d'un compte rendu du ministre
    # concerné, sans sous-titre « Nominations ». On conserve ce rattachement
    # contextuel lorsqu'aucun intitulé plus précis ne le remplace ensuite.
    for match in re.finditer(
        r"\bLe\s+ministre\s+(de\s+(?:la\s+|l['’\uFFFD])?[^.;\f]+?)\s+a\s+(?:fait|rendu|inform\w*|pr[ée\uFFFD]sent\w*|soumis\w*|expos\w*)\b",
        section,
        re.I,
    ):
        events.append((match.start(), "narrative_ministry", match))
    for match in re.finditer(
        r"\b[A-Z][.-]\s+(MINISTERE\s+.+?)(?=\s+-\s+|\s+(?:Sont\s+nomm|Les\s+personnes\s+dont(?:\s+les)?(?:\s+noms?)?\s+suivent)\b|\s+Le\s+(?:Conseil|premier|second)\s+décret|\f|$)",
        section,
        re.I,
    ):
        events.append((match.start(), "ministry", match))
    # Certains comptes rendus omettent le préfixe ordinal ("A.") devant les
    # titres de ministère; la puce qui suit est alors le repère le plus fiable.
    for match in re.finditer(
        r"\b(MINISTERE\s+[^-\f]+?)(?=\s+(?:-\s+|Sont\s+nomm|Les\s+personnes\s+dont(?:\s+les)?(?:\s+noms?)?\s+suivent|Le\s+Conseil\s+(?:a|adopte)\b))",
        section,
        re.I,
    ):
        events.append((match.start(), "ministry", match))
    for match in re.finditer(
        r"Sont\s+nomm(?:[é\uFFFD](?:e|s|es)?|e(?:s)?)\s+((?:(?!\s+-\s+|\bSont\s+nomm).)+?)(?:,)?\s+les\s+personnes\s+dont(?:\s+les)?(?:\s+noms?)?\s+suivent(?:\s+pour\s+.+?)?\s*:",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    # La formule collective peut comporter une précision entre « suivent » et
    # les deux-points, par exemple « à compter du 25 juillet 2015 ».
    for match in re.finditer(
        r"\bSont\s+nomm(?:[é\uFFFD](?:e|s|es)?|e(?:s)?)\s+([^:\f]+?)\s+les\s+personnes\s+(?:dont(?:\s+les)?(?:\s+noms?)?\s+suivent|ci-apr[èe\uFFFD]s)\s*,?(?:\s+[^:\f]{0,240})?\s*:",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    # Certaines listes collectives ne répètent pas « les personnes dont les
    # noms suivent » : la fonction commune est directement suivie des deux
    # points, puis des puces (ex. « Sont nommés Conseillers au CSC : »).
    for match in re.finditer(
        r"\bSont\s+nomm(?:[é\uFFFD](?:e|s|es)?|e(?:s)?)\s+((?:(?!\bles\s+personnes\b)[^:\f])+?)\s*:",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    for match in re.finditer(
        r"Sont\s+nomm(?:[é\uFFFD](?:e|s|es)?|e(?:s)?)\s+(.+?)\s+les\s+personnes\s+ci-apr[èe\uFFFD]s(?:\s+pour\s+.+?)?\s*:",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    for match in re.finditer(
        r"Sont\s+nomm(?:\w|\uFFFD)*\s+((?:(?!\s+-\s+|\bSont\s+nomm).)+?)(?:,)?\s+(?:les\s+)?Administrateurs?\s+civils\s+dont\s+les\s+noms\s+suivent\s*:",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    for match in re.finditer(
        r"Les\s+personnes\s+ci-apr[èe\uFFFD]s\s+sont\s+nomm(?:[é\uFFFD](?:e|s|es)?|e(?:s)?)\s+(.+?)\s*:",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    for match in re.finditer(
        r"Les\s+personnes\s+dont(?:\s+les)?(?:\s+noms?)?\s+suivent\s+sont\s+nomm(?:[é\uFFFD](?:e|s|es)?|e(?:s)?)\s+((?:(?!\s+-\s+|\b(?:Les\s+personnes|Sont\s+nomm)).)+?)\s*[.:]",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    # Variantes fautives mais fréquentes dans les PDF : « dont les suivent »
    # ou « sont les noms suivent » à la place de « dont les noms suivent ».
    for match in re.finditer(
        r"\bLes\s+personnes\s+(?:(?:dont|sont)\s+)?(?:les\s+)?(?:noms?\s+)?suivent\s*,?\s+sont\s+nomm(?:[é\uFFFD]|e)\w*\s+([^:\f]+?)\s*:",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    for match in re.finditer(
        r"Les\s+Magistrats\s+dont\s+les\s+noms?\s+suivent\s*,?\s+sont\s+nomm\w*\s+((?:(?!\s+-\s+|\b(?:Les\s+Magistrats|Les\s+personnes|Sont\s+nomm)).)+?)\s*:",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    # Une rubrique peut annoncer simplement « Nomination des membres de… »,
    # puis détailler les représentants dans les puces suivantes.
    for match in re.finditer(
        r"\bNomination\s+des\s+((?:membres?|administrateurs?)\s+d(?:e\s+la\s+|u\s+|es\s+|['’\uFFFD])[^.\f]+?)(?=\s*[.:])",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    # Les intégrations, affectations et promotions peuvent également être
    # formulées sous forme de liste collective. Elles constituent des décisions
    # individuelles dans le corpus de référence, même sans verbe « nommer ».
    for match in re.finditer(
        r"\b(Sont\s+(?:int[ée\uFFFD]gr\w*|affect\w*|promu\w*|admis\w*)\s+[^:\f]+?)\s+les\s+personnes\s+(?:dont(?:\s+les)?(?:\s+noms?)?\s+suivent|ci-apr[èe\uFFFD]s)(?:\s+[^:\f]{0,240})?\s*:",
        section,
        re.I,
    ):
        events.append((match.start(), "group", match))
    # Certains conseils d'administration présentent les nommés sous forme de
    # liste, introduite par « nomme les personnes ci-après, Administrateurs… »
    # ou une variante de renouvellement de mandat. Ces formules jouent le même
    # rôle qu'une rubrique collective « Sont nommés ».
    for match in re.finditer(
        r"\b(?:"
        r"nomme\s+les\s+personnes\s+ci-apr[èe\uFFFD]s,?\s+|"
        r"(?:porte|portant)\s+nominations?\s+des\s+personnes\s+ci-apr[èe\uFFFD]s,?\s+|"
        r"(?:porte|portant)\s+nomination\s+d['’]Administrateurs?\s+des\s+personnes\s+ci-apr[èe\uFFFD]s,?\s+|"
        r"(?:porte|portant)\s+nomination\s+d['’]Administrateurs?\s+les\s+personnes\s+ci-apr[èe\uFFFD]s,?\s+|"
        r"(?:porte|portant)\s+nomination\s+des\s+personnes\s+ci-apr[èe\uFFFD]s,?\s+|"
        r"portant\s+nomination\s+des\s+personnes\s+ci-apr[èe\uFFFD]s,?\s+|"
        r"renouvelle\s+le\s+mandat\s+d(?:e\s+l['’]|['’])Administrateurs?\s+des\s+personnes\s+ci-apr[èe\uFFFD]s,?\s+"
        r")(.+?)(?=\s*(?:(?:[.:]\s*(?:Au\s+titre|[-]\s+))|[-]\s+|(?:Monsieur|Madame|Mademoiselle|Mme\.?)\b))",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    # Les renouvellements de mandat décrits comme listes collectives ont les
    # mêmes puces que les nominations mais emploient une syntaxe différente.
    # On conserve leur poste commun pour ne pas rejeter les personnes sans
    # verbe de nomination individuel.
    for match in re.finditer(
        r"\bdécret\s+porte\s+renouvellement\s+du\s+mandat\s+des\s+personnes\s+dont\s+les\s+noms\s+suivent\s*,?\s*(Administrateurs?\s+[^.\f]+?)(?=\s*\.)",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    for match in re.finditer(
        r"\bdécret\s+porte\s+renouvellement\s+de\s+mandat\s+des\s+personnes\s+ci-apr[èe\uFFFD]s\s*,?\s*((?:Administrateurs?|Membres?)\s+[^.\f]+?)(?=\s*\.)",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    for match in re.finditer(
        r"\bdécret\s+renouvelle\s+le\s+mandat\s+des\s+personnes\s+ci-apr[èe\uFFFD]s\s*,?\s*(Administrateurs?\s+[^.\f]+?)(?=\s*\.)",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    for match in re.finditer(
        r"\bdécret\s+renouvelle\s+le\s+mandat\s+des\s+(Membres?\s+ci-apr[èe\uFFFD]s\s+[^:\f]+?)(?=\s*:)",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    for match in re.finditer(
        r"\bdécret\s+(?:porte|portant)\s+renouvellement\s+de\s+mandat\s+d['’](Administrateurs?)(?=\s*,?\s+les\s+personnes\s+ci-apr[èe\uFFFD]s)",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    # Les sous-rubriques de certaines listes de conseils précisent la qualité
    # de représentation juste avant une puce.
    for match in re.finditer(
        r"\b((?:Administrateurs?|Membres?)\s+(?:re|pre)pr\w*(?:s)?\s+[^.:;\f]+?)(?=\s*:\s*|\s+Au\s+titre\b|\s+-\s+(?:Monsieur|Madame|Mademoiselle|Mme\.?)\b)",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    for match in re.finditer(
        r"\b(ADMINISTRATEURS?\s+REPRESENTANT\s+L['’]ETAT)\b",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    # De nombreux conseils annoncent la liste par « le premier décret porte
    # nomination d'Administrateurs… », sans employer « personnes ci-après ».
    # Cette phrase fournit le poste commun aux puces qui suivent.
    for match in re.finditer(
        r"\b(?:Le\s+(?:premier|deuxi[èe\uFFFD]me|troisi[èe\uFFFD]me|quatri[èe\uFFFD]me|cinqui[èe\uFFFD]me|sixi[èe\uFFFD]me)\s+)?(?:porte|portant)\s+nomination\s+d['’\uFFFD](Administrateurs?\s+[^.\f]+?)(?=\s*[:.])",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    for match in re.finditer(
        r"\b(?:Le\s+(?:premier|deuxi[èe\uFFFD]me|troisi[èe\uFFFD]me|quatri[èe\uFFFD]me|cinqui[èe\uFFFD]me|sixi[èe\uFFFD]me)\s+)?(?:décret\s+)?porte\s+renouvellement\s+de\s+mandat\s+d['’\uFFFD](Administrateurs?\s+[^.\f]+?)(?=\s*[:.])",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    for match in re.finditer(
        r"\b(?:Le\s+(?:premier|deuxi[èe\uFFFD]me|troisi[èe\uFFFD]me|quatri[èe\uFFFD]me|cinqui[èe\uFFFD]me|sixi[èe\uFFFD]me|même)\s+)?(?:décret\s+)?renouvelle\s+le\s+mandat\s+d['’\uFFFD](Administrateurs?)\s+des\s+personnes\s+ci-apr[èe\uFFFD]s",
        section,
        re.I,
    ):
        events.append((match.start(), "board_group", match))
    # Une rubrique principale clôt une éventuelle liste collective précédente.
    # Sans cette borne, une liste numérotée d'une décision ultérieure (grâce,
    # naturalisation, etc.) pourrait être prise pour des administrateurs.
    for match in re.finditer(
        # Les numéros simples (« 1. Monsieur… ») sont des éléments de liste,
        # non des titres : seuls les chiffres romains et les titres 1.2. sont
        # retenus comme séparateurs de rubrique.
        r"\b(?:[IVXLCD]{2,}(?:\.\d+)?|\d+\.\d+)\.\s+(?=[A-ZÀ-Ý])",
        section,
    ):
        events.append((match.start(), "section_break", match))
    if board_title_match:
        events.append((board_title_match.start(), "board_start", board_title_match))
        for match in re.finditer(
            r"\bLe\s+(?:premier|deuxième|second|troisième|quatrième|cinquième|sixième|même)\s+décret\b",
            section[board_title_match.start() :],
            re.I,
        ):
            events.append((board_title_match.start() + match.start(), "board_decree", match))
        # Dans quelques PDF, l'énumération ne met pas de tiret devant le nom.
        # On ajoute alors un événement de personne uniquement pour ce format.
        board_slice = section[board_title_match.start() :]
        for match in re.finditer(
            r"\bAu\s+titre\s+(?:DU\s+|DE\s+LA\s+|DE\s+L['’\uFFFD]\s*|DES\s+)([^.;\f]+?)(?=\s+(Monsieur|Madame|Mademoiselle|Mme\.?)\b)",
            board_slice,
            re.I,
        ):
            base = board_title_match.start()
            events.append((base + match.start(), "inline_ministry", match))
            events.append((base + match.start(2), "inline", match))
    # Certains comptes rendus insèrent directement le nom après un titre de
    # ministère, sans tiret ni deux-points. On ne retient que les cas où le
    # verbe de nomination est explicitement présent dans la même phrase.
    for match in re.finditer(
        r"\b(?:Monsieur|Madame|Mademoiselle|Mme\.?)\s+(?=[^.\f]{0,800}\best\s+nomm\w*\b)",
        section,
        re.I,
    ):
        prefix = section[max(0, match.start() - 12) : match.start()]
        if not re.search(r"(?:[-:;]\s*)$", prefix):
            events.append((match.start(), "inline", match))
    # Les renouvellements et certaines nominations individuelles sont rédigés
    # en prose, sans puce. Ils sont ajoutés comme événements séparés afin de
    # bénéficier du ministère actif à cet endroit du document.
    prose_patterns = [
        r"\bLe\s+Conseil\s+(?:a\s+)?adopt\w*[^.\f]{0,1600}\.",
        r"\bLe\s+\w+\s+d\w*cret\s+(?:nomme|porte\s+nomination|renouvel\w*)[^.\f]{0,1600}\.",
    ]
    for pattern in prose_patterns:
        for match in re.finditer(pattern, section, re.I):
            sentence = match.group(0)
            if re.search(r"\b(?:Monsieur|Madame|Mademoiselle)\b", sentence, re.I) and re.search(
                r"\b(?:nomination|nomm\w*|renouvel\w*)\b", sentence, re.I
            ):
                events.append((match.start(), "prose", match))
    # Les listes collectives utilisent tantôt une puce simple (« - »), tantôt
    # une puce numérotée (« 1- » ou « 1 - »).
    for match in re.finditer(r"(?:^|\s)(?:\d+\s*)?-\s+", section):
        events.append((match.start(), "bullet", match))
    # Certaines listes collectives ne mettent pas de tiret devant les personnes.
    # Les deux-points introduisent le premier nom, puis les points-virgules les
    # suivants; on les traite comme des puces sans dupliquer les listes à tirets.
    for match in re.finditer(
        r"(?:[:;])\s+((?:Monsieur|Madame|Mademoiselle|Mme\.?)\s+)",
        section,
        re.I,
    ):
        events.append((match.start(1), "inline", match))

    events.sort(
        key=lambda event: (
            event[0],
            {
                "board_start": 0,
                "board_decree": 1,
                "section_break": 2,
                "ministry": 3,
                "narrative_ministry": 4,
                "inline_ministry": 5,
                "group": 6,
                "board_group": 7,
                "prose": 8,
                "bullet": 9,
                "inline": 10,
            }[event[1]],
        )
    )
    for index, (start, kind, match) in enumerate(events):
        next_start = events[index + 1][0] if index + 1 < len(events) else len(section)
        if kind == "ministry":
            candidate = clean_ministry(match.group(1))
            # Une sous-rubrique « Au titre des Associations… » qualifie une
            # liste collective; elle n'est pas un nouveau ministère.
            is_ministry = bool(
                re.match(
                    r"^(?:MINIST(?:ERE|[ÈÉE\uFFFD]RE)|PREMIER\s+MINISTERE|PRESIDENCE|PRIMATURE|AUTORITE)\b",
                    candidate,
                    re.I,
                )
            )
            if is_ministry or not group_post:
                ministry = candidate
            # Dans une liste collective, les sous-rubriques ministérielles
            # changent le rattachement sans annuler le poste commun de la liste.
            if is_ministry and not group_post and (not board_title_match or start < board_title_match.start()):
                group_post = ""
        elif kind == "narrative_ministry":
            ministry = clean_ministry(f"MINISTERE {match.group(1).upper()}")
        elif kind == "board_start":
            group_post = ""
        elif kind == "board_decree":
            group_post = ""
        elif kind == "section_break":
            group_post = ""
        elif kind == "inline_ministry":
            ministry = clean_ministry(match.group(1))
        elif kind == "group":
            group_post = clean(match.group(1)).strip(" ,;.")
        elif kind == "board_group":
            group_post = clean(match.group(1))
            if re.fullmatch(r"ADMINISTRATEURS?\s+(?:RE|PRE)PR\w*\s+L['’]ETAT", group_post, re.I):
                group_post = "Administrateur représentant l’Etat"
            if re.match(r"(?:au|du)\s+Conseil\b", group_post, re.I):
                group_post = f"Administrateur {group_post}"
        elif kind == "prose":
            if board_title_match:
                continue
            row = appointment_from_prose(
                section[start:next_start],
                document_id,
                date_conseil,
                ministry,
                position_page(section_pages, start),
            )
            if row:
                rows.append(row)
        else:
            bullet = section[match.end() : next_start] if kind == "bullet" else section[start:next_start]
            row = appointment_from_bullet(
                bullet,
                document_id,
                date_conseil,
                ministry,
                group_post,
                position_page(section_pages, start),
            )
            if row:
                rows.append(row)

    # Les conseils d'administration sont souvent rédigés sous forme de phrase
    # plutôt que de puces. On examine chaque phrase de cette sous-section.
    if board_title_match:
        board_text = section[board_title_match.start() :]
        board_offset = board_title_match.start()
        current_ministry = ""
        chunks = re.split(r"(?<=[.;])\s+", board_text)
        cursor = board_offset
        for chunk in chunks:
            heading = re.search(
                r"(?:\b[A-Z]\.\s+)?(Minist[èe\uFFFD]re\s+.+?|PRIMATURE|PRESIDENCE\s+DU\s+FASO)(?=\s+Le\s+|$)",
                chunk,
                re.I,
            )
            if heading:
                current_ministry = clean_ministry(heading.group(1))
            if not re.search(r"\bpersonnes\s+ci-apr[èe\uFFFD]s\b", chunk, re.I):
                row = appointment_from_prose(
                    chunk,
                    document_id,
                    date_conseil,
                    current_ministry,
                    position_page(section_pages, cursor),
                )
                if row:
                    rows.append(row)
            cursor += len(chunk) + 1

    return rows, ocr_pages


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrait les nominations d'un dossier de PDF.")
    parser.add_argument("source", nargs="?", default="2015", help="Dossier contenant les PDF (défaut : 2015)")
    parser.add_argument("output", nargs="?", help="Nom du CSV de sortie")
    parser.add_argument("--ocr", action="store_true", help="Utilise Tesseract pour les pages sans texte exploitable")
    args = parser.parse_args()
    source = Path(args.source)
    output = Path(args.output) if args.output else Path(f"nominations_{source.name}.csv")
    if not source.is_dir():
        raise SystemExit(f"Dossier introuvable : {source}")
    if args.ocr and not shutil.which("tesseract"):
        raise SystemExit("Tesseract est introuvable. Installez-le ou retirez l'option --ocr.")

    rows = []
    ocr_counts = {}
    for path in sorted(source.glob("*.pdf")):
        extracted, ocr_pages = extract_from_pdf(path, use_ocr=args.ocr)
        rows.extend(extracted)
        ocr_counts[path.name] = ocr_pages

    # On protège le fichier contre les doublons qui peuvent provenir de textes
    # identiques (notamment le PDF du 28 septembre fourni en deux exemplaires).
    unique_rows = []
    seen = set()
    for row in rows:
        key = tuple(row[field] for field in FIELDS)
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)

    with output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(unique_rows)
    print(f"{len(unique_rows)} nominations extraites dans {output}")
    for path in sorted(source.glob("*.pdf")):
        count = sum(row["document_id"] == path.name for row in unique_rows)
        ocr_suffix = f" (OCR : {ocr_counts[path.name]} page(s))" if ocr_counts[path.name] else ""
        print(f"{path.name}: {count}{ocr_suffix}")


if __name__ == "__main__":
    main()
