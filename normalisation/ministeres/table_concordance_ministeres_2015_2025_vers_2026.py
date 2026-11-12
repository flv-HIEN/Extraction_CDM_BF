"""Concordance des dénominations ministérielles (Burkina Faso, 2015-2025).

Le référentiel est la composition gouvernementale du 12 janvier 2026.  Cette
table est une concordance analytique : elle ne remplace jamais le libellé
historique figurant dans une source de nomination.

Chaque entrée donne :
- ``codes_ref_2026`` : un ou plusieurs codes du référentiel 2026 ;
- ``type_concordance`` : continuité, fusion, scission, etc. ;
- ``perimetres_non_couverts_2026`` : compétences pour lesquelles aucun
ministère de plein exercice équivalent n'apparaît dans la composition 2026.

Une liste de codes signale une scission ou un regroupement. Elle ne doit pas
servir à compter deux fois une même nomination dans un total global.
"""

try:
    from .dictionnaires_ministeres_par_annee import dictionnaires_par_annee
except ImportError:
    from dictionnaires_ministeres_par_annee import dictionnaires_par_annee


REFERENTIEL_2026 = {
    "DEFENSE": "Ministère de la Guerre et de la Défense patriotique",
    "AGRI_EAU_RAH": (
        "Ministère de l'Agriculture, de l'Eau, des Ressources animales et halieutiques"
    ),
    "ADMIN_MOBILITE": "Ministère de l'Administration territoriale et de la Mobilité",
    "ECONOMIE_FINANCES": "Ministère de l'Économie et des Finances",
    "SECURITE": "Ministère de la Sécurité",
    "AFFAIRES_ETRANGERES": "Ministère des Affaires étrangères",
    "SERVITEURS_PEUPLE": "Ministère des Serviteurs du Peuple",
    "COMMUNICATION_CULTURE_TOURISME": (
        "Ministère de la Communication, de la Culture, des Arts et du Tourisme"
    ),
    "FAMILLE_SOLIDARITE": "Ministère de la Famille et de la Solidarité",
    "JUSTICE": "Ministère de la Justice",
    "SANTE": "Ministère de la Santé",
    "TRANSITION_DIGITALE": (
        "Ministère de la Transition digitale, des Postes et des Communications électroniques"
    ),
    "INDUSTRIE_COMMERCE_ARTISANAT": "Ministère de l'Industrie, du Commerce et de l'Artisanat",
    "CONSTRUCTION_PATRIE": "Ministère de la Construction de la Patrie",
    "ENERGIE_MINES_CARRIERES": "Ministère de l'Énergie, des Mines et des Carrières",
    "EDUCATION_BASE": (
        "Ministère de l'Enseignement de base, de l'Alphabétisation et de la Promotion des langues nationales"
    ),
    "ENSEIGNEMENT_SECONDAIRE_FORMATION": (
        "Ministère de l'Enseignement secondaire et de la Formation professionnelle et technique"
    ),
    "ENSEIGNEMENT_SUP_RECHERCHE": (
        "Ministère de l'Enseignement supérieur, de la Recherche et de l'Innovation"
    ),
    "SPORTS_JEUNESSE_EMPLOI": "Ministère des Sports, de la Jeunesse et de l'Emploi",
}


CONCORDANCE_MINISTERES_2015_2025_VERS_2026 = {}


def _ajouter(libelles, codes_ref_2026, type_concordance, *, perimetres_non_couverts_2026=(), note=""):
    """Ajoute les lignes partageant la même règle de concordance."""
    for libelle in libelles:
        if libelle in CONCORDANCE_MINISTERES_2015_2025_VERS_2026:
            raise ValueError(f"Libellé dupliqué dans la concordance : {libelle}")
        CONCORDANCE_MINISTERES_2015_2025_VERS_2026[libelle] = {
            "codes_ref_2026": tuple(codes_ref_2026),
            "type_concordance": type_concordance,
            "perimetres_non_couverts_2026": tuple(perimetres_non_couverts_2026),
            "note": note,
        }


# Défense et sécurité.
_ajouter(
    (
        "Ministère de la Défense nationale et des Anciens Combattants",
        "Ministère de la Défense et des Anciens Combattants",
        "Ministère des Armées et des Anciens Combattants",
    ),
    ("DEFENSE",),
    "renommage",
)
_ajouter(("Ministère de la Sécurité",), ("SECURITE",), "continuité")


# Administration territoriale, mobilité et transports.
_ajouter(
    (
        "Ministère de l'Administration territoriale et de la Décentralisation",
        "Ministère de l'Administration territoriale et de la Mobilité",
    ),
    ("ADMIN_MOBILITE",),
    "continuité_ou_renommage",
)
_ajouter(
    (
        "Ministère de l'Administration territoriale, de la Décentralisation et de la Sécurité",
        "Ministère de l'Administration territoriale, de la Décentralisation et de la Sécurité intérieure",
    ),
    ("ADMIN_MOBILITE",),
    "rattachement_conventionnel",
    note="Convention de concordance : le portefeuille de sécurité est rattaché à ADMIN_MOBILITE.",
)
_ajouter(
    ("Ministère de l'Administration territoriale, de la Décentralisation et de la Cohésion sociale",),
    ("ADMIN_MOBILITE",),
    "rattachement_conventionnel",
    note="Convention de concordance : le portefeuille de cohésion sociale est rattaché à ADMIN_MOBILITE.",
)
_ajouter(
    ("Ministère des Transports, de la Mobilité urbaine et de la Sécurité routière",),
    ("ADMIN_MOBILITE",),
    "rattachement_fonctionnel",
    note="La mobilité est rattachée à l'Administration territoriale dans le référentiel 2026.",
)


# Relations extérieures.
_ajouter(
    (
        "Ministère des Affaires étrangères et de la Coopération régionale",
        "Ministère des Affaires étrangères et de la Coopération",
        "Ministère des Affaires étrangères, de la Coopération et des Burkinabè de l'Extérieur",
        "Ministère des Affaires étrangères, de la Coopération régionale et des Burkinabè de l'Extérieur",
        "Ministère des Affaires étrangères, de la Coopération, de l'Intégration africaine et des Burkinabè de l'Extérieur",
        "Ministère de l'Intégration africaine et des Burkinabè de l'Extérieur",
    ),
    ("AFFAIRES_ETRANGERES",),
    "regroupement",
)


# Économie, finances et prospective.
_ajouter(
    (
        "Ministère de l'Économie et des Finances",
        "Ministère de l'Économie, des Finances et du Développement",
        "Ministère de l'Économie, des Finances et du Plan",
        "Ministère de l'Économie, des Finances et de la Prospective",
        "Ministère de la Prospective et des Réformes structurelles",
    ),
    ("ECONOMIE_FINANCES",),
    "regroupement",
)


# Fonction publique, travail et protection sociale.
_ajouter(
    (
        "Ministère de la Fonction publique, du Travail et de la Sécurité sociale",
        "Ministère de la Fonction publique, du Travail et de la Protection sociale",
    ),
    ("SERVITEURS_PEUPLE",),
    "renommage_et_redefinition_de_perimetre",
    note="Rapprochement fonctionnel proposé ; vérifier les attributions précises si l'analyse porte sur le travail ou la protection sociale.",
)


# Justice, droits humains et promotion civique.
_ajouter(
    (
        "Ministère de la Justice, des Droits humains et de la Promotion civique, Garde des Sceaux",
        "Ministère de la Justice, Garde des Sceaux",
        "Ministère de la Justice et des Droits humains, chargée des Relations avec les institutions, Garde des Sceaux",
        "Ministère de la Justice et des Droits humains, chargé des Relations avec les institutions, Garde des Sceaux",
        "Ministère des Droits humains et de la Promotion civique",
    ),
    ("JUSTICE",),
    "regroupement",
)


# Santé.
_ajouter(
    (
        "Ministère de la Santé",
        "Ministère de la Santé et de l'Hygiène publique",
        "Ministère de la Santé, de l'Hygiène publique et du Bien-être",
    ),
    ("SANTE",),
    "continuité_ou_renommage",
)


# Agriculture, eau et ressources animales/halieutiques.
_ajouter(
    (
        "Ministère de l'Agriculture et des Aménagements hydrauliques",
        "Ministère de l'Agriculture et des Aménagements hydro-agricoles",
        "Ministère de l'Agriculture, des Aménagements hydro-agricoles et de la Mécanisation",
        "Ministère de l'Agriculture, des Aménagements hydro-agricoles, de la Mécanisation et des Ressources animales et halieutiques",
        "Ministère de l'Agriculture, des Ressources animales et halieutiques",
        "Ministère de l'Agriculture, des Ressources hydrauliques, de l'Assainissement et de la Sécurité alimentaire",
        "Ministère de l'Eau et de l'Assainissement",
        "Ministère des Ressources animales",
        "Ministère des Ressources animales et halieutiques",
    ),
    ("AGRI_EAU_RAH",),
    "regroupement",
)
_ajouter(
    ("Ministère de l'Environnement et des Ressources halieutiques",),
    ("AGRI_EAU_RAH",),
    "rattachement_fonctionnel",
    note="Convention de concordance : le portefeuille environnement est rattaché à AGRI_EAU_RAH.",
)
_ajouter(
    (
        "Ministère de l'Environnement, de l'Énergie, de l'Eau et de l'Assainissement",
        "Ministère de l'Environnement, de l'Eau et de l'Assainissement",
    ),
    ("AGRI_EAU_RAH",),
    "rattachement_conventionnel",
    note="Convention de concordance : les portefeuilles environnement, énergie, eau et assainissement sont rattachés à AGRI_EAU_RAH.",
)


# Énergie, mines et carrières.
_ajouter(
    (
        "Ministère des Mines et de l'Énergie",
        "Ministère de l'Énergie",
        "Ministère des Mines et des Carrières",
        "Ministère de l'Énergie, des Mines et des Carrières",
        "Ministère de la Transition énergétique, des Mines et des Carrières",
    ),
    ("ENERGIE_MINES_CARRIERES",),
    "regroupement",
)


# Numérique, postes et communications électroniques.
_ajouter(
    (
        "Ministère du Développement de l'Économie numérique et des Postes",
        "Ministère de l'Économie numérique, des Postes et de la Transformation digitale",
        "Ministère de la Transition digitale, des Postes et des Communications électroniques",
    ),
    ("TRANSITION_DIGITALE",),
    "continuité_ou_renommage",
)


# Industrie, commerce et artisanat.
_ajouter(
    (
        "Ministère de l'Industrie, du Commerce et de l'Artisanat",
        "Ministère du Commerce, de l'Industrie et de l'Artisanat",
        "Ministère du Développement industriel, du Commerce, de l'Artisanat et des Petites et Moyennes Entreprises",
    ),
    ("INDUSTRIE_COMMERCE_ARTISANAT",),
    "continuité_ou_renommage",
)


# Construction, infrastructures, urbanisme et habitat.
_ajouter(
    (
        "Ministère des Infrastructures",
        "Ministère des Infrastructures et du Désenclavement",
        "Ministère de l'Habitat et de l'Urbanisme",
        "Ministère de l'Urbanisme et de l'Habitat",
        "Ministère de l'Urbanisme, de l'Habitat et de la Ville",
        "Ministère du Développement urbain, de l'Habitat et de la Ville",
        "Ministère de l'Urbanisme, des Affaires foncières et de l'Habitat",
    ),
    ("CONSTRUCTION_PATRIE",),
    "fusion",
)
_ajouter(
    ("Ministère des Infrastructures, du Désenclavement et des Transports",),
    ("CONSTRUCTION_PATRIE",),
    "rattachement_conventionnel",
    note="Convention de concordance : le portefeuille des transports est rattaché à CONSTRUCTION_PATRIE.",
)


# Enseignement de base, secondaire et supérieur.
_ajouter(
    (
        "Ministère de l'Éducation nationale et de l'Alphabétisation",
        "Ministère de l'Éducation nationale, de l'Alphabétisation et de la Promotion des langues nationales",
        "Ministère de l'Enseignement de base, de l'Alphabétisation et de la Promotion des langues nationales",
    ),
    ("EDUCATION_BASE",),
    "continuité_ou_renommage",
)
_ajouter(
    ("Ministère de l'Enseignement secondaire, de la Formation professionnelle et technique",),
    ("ENSEIGNEMENT_SECONDAIRE_FORMATION",),
    "rattachement_fonctionnel",
)
_ajouter(
    (
        "Ministère de la Jeunesse, de la Formation professionnelle et de l'Emploi",
        "Ministère de la Jeunesse, de la Formation et de l'Insertion professionnelle",
        "Ministère de la Jeunesse, de la Formation et de l'Insertion professionnelles",
    ),
    ("SPORTS_JEUNESSE_EMPLOI",),
    "rattachement_conventionnel",
    note="Convention de concordance : le portefeuille de formation est rattaché à SPORTS_JEUNESSE_EMPLOI.",
)
_ajouter(
    (
        "Ministère de l'Enseignement supérieur, de la Recherche scientifique et de l'Innovation",
        "Ministère de l'Enseignement supérieur, de la Recherche et de l'Innovation",
        "Ministère de la Recherche scientifique et de l'Innovation",
    ),
    ("ENSEIGNEMENT_SUP_RECHERCHE",),
    "continuité_ou_renommage",
)
_ajouter(
    ("Ministère des Enseignements secondaire et supérieur",),
    ("ENSEIGNEMENT_SECONDAIRE_FORMATION",),
    "rattachement_conventionnel",
    note="Convention de concordance : le portefeuille d'enseignement supérieur est rattaché à ENSEIGNEMENT_SECONDAIRE_FORMATION.",
)


# Sports, jeunesse et emploi.
_ajouter(
    (
        "Ministère des Sports et des Loisirs",
        "Ministère des Sports, de l'Autonomisation des Jeunes et de l'Emploi",
        "Ministère des Sports, de la Jeunesse et de l'Emploi",
        "Ministère de la Jeunesse et de la Promotion de l'entrepreneuriat des jeunes",
        "Ministère de la Jeunesse, de la Promotion de l'Entrepreneuriat et de l'Emploi",
    ),
    ("SPORTS_JEUNESSE_EMPLOI",),
    "regroupement",
)


# Communication, culture, arts et tourisme.
_ajouter(
    (
        "Ministère de la Communication, chargée des Relations avec le Conseil national de la Transition",
        "Ministère de la Communication, chargé des Relations avec le Conseil national de la Transition",
        "Ministère de la Communication et des Relations avec le Parlement",
        "Ministère de la Communication, des Relations avec le Parlement, de la Culture, des Arts et du Tourisme",
        "Ministère de la Communication, de la Culture, des Arts et du Tourisme",
        "Ministère de la Culture et du Tourisme",
        "Ministère de la Culture, des Arts et du Tourisme",
    ),
    ("COMMUNICATION_CULTURE_TOURISME",),
    "fusion",
)


# Famille, genre, solidarité et action humanitaire.
_ajouter(
    (
        "Ministère de l'Action sociale et de la Solidarité nationale",
        "Ministère de la Femme, de la Solidarité nationale et de la Famille",
        "Ministère de la Femme, de la Solidarité nationale, de la Famille et de l'Action humanitaire",
        "Ministère de la Promotion de la Femme et du Genre",
        "Ministère du Genre, de la Solidarité nationale, de la Famille et de l'Action humanitaire",
        "Ministère de la Solidarité nationale et de l'Action humanitaire",
        "Ministère de la Solidarité, de l'Action humanitaire, de la Réconciliation nationale, du Genre et de la Famille",
        "Ministère du Genre et de la Famille",
        "Ministère de l'Action humanitaire et de la Solidarité nationale",
    ),
    ("FAMILLE_SOLIDARITE",),
    "regroupement",
)
_ajouter(
    (
        "Ministère auprès du Président du Faso, chargé de la Réconciliation nationale et de la Cohésion sociale",
        "Ministère auprès du Président du Faso, chargé de la Cohésion sociale et de la Réconciliation nationale",
    ),
    ("FAMILLE_SOLIDARITE",),
    "rapprochement_partiel",
    perimetres_non_couverts_2026=("réconciliation nationale",),
)


# Environnement : rattaché par convention à AGRI_EAU_RAH.
_ajouter(
    (
        "Ministère de l'Environnement, de l'Économie verte et du Changement climatique",
        "Ministère de la Transition écologique et de l'Environnement",
    ),
    ("AGRI_EAU_RAH",),
    "rattachement_fonctionnel",
    note="Convention de concordance : le portefeuille environnement est rattaché à AGRI_EAU_RAH.",
)


# Affaires religieuses et coutumières : rattachement conventionnel à l'administration territoriale.
_ajouter(
    ("Ministère des Affaires religieuses et coutumières",),
    ("ADMIN_MOBILITE",),
    "rattachement_fonctionnel",
    note="Convention de concordance : les affaires religieuses et coutumières sont rattachées à ADMIN_MOBILITE.",
)


def verifier_concordance():
    """Vérifie que chaque intitulé 2015-2025 a une règle de concordance."""
    libelles_historiques = {
        libelle
        for annee, compositions in dictionnaires_par_annee.items()
        if annee <= 2025
        for liste_ministeres in compositions.values()
        for libelle in liste_ministeres
    }
    libelles_non_couverts = libelles_historiques - set(CONCORDANCE_MINISTERES_2015_2025_VERS_2026)
    codes_inconnus = {
        code
        for regle in CONCORDANCE_MINISTERES_2015_2025_VERS_2026.values()
        for code in regle["codes_ref_2026"]
        if code not in REFERENTIEL_2026
    }
    if libelles_non_couverts or codes_inconnus:
        raise ValueError(
            "Concordance incomplète : "
            f"libellés non couverts={sorted(libelles_non_couverts)} ; "
            f"codes inconnus={sorted(codes_inconnus)}"
        )


verifier_concordance()
