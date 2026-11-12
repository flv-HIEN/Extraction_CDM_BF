"""Contrôles des erreurs qui modifieraient les trajectoires individuelles."""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from fiabiliser_nominations import read_csv, run, write_csv


def nomination(nom="Alice TEST", matricule="001 234 A", poste="Directeur général", **changes):
    row = dict(document_id="CDM - 2020_01_08.pdf", date_conseil="2020-01-08",
               civilite="Madame", nom=nom, matricule=matricule, emploi="", grade="",
               classe="", echelon="", ministere="MINISTÈRE DE LA SANTÉ",
               poste_nomination=poste, page="3", extrait_exact=f"{nom} est nommé {poste}.")
    row.update(changes)
    return row


class PreparationTests(unittest.TestCase):
    def test_same_name_different_matricules_are_distinct_and_coherent(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, rows = self.prepare([
                nomination(), nomination(matricule="999999Z"),
            ], tmp)
            self.assertNotEqual(rows[0]["id_personne"], rows[1]["id_personne"])
            self.assertTrue(all(r["statut_identite"] == "coherent_nom_matricule" for r in rows))
            self.assertTrue(all(r["identite_eligible_strict"] == "1" for r in rows))

    def test_shared_matricule_remains_uncertain_despite_homonyms(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, rows = self.prepare([
                nomination(), nomination(matricule="999999Z"),
                nomination(nom="Benoit AUTRE"),
            ], tmp)
            self.assertEqual(rows[0]["statut_identite"], "a_verifier_matricule_partage")
            self.assertEqual(rows[2]["statut_identite"], "a_verifier_matricule_partage")
            self.assertEqual(rows[1]["statut_identite"], "coherent_nom_matricule")

    def prepare(self, rows, folder):
        source = Path(folder) / "source.csv"
        write_csv(source, rows, list(rows[0]))
        output = Path(folder) / "sorties"
        original = source.read_bytes()
        summary = run(source, output)
        self.assertEqual(source.read_bytes(), original)
        annotated = read_csv(output / "nominations_annotees.csv")
        for before, after in zip(rows, annotated):
            for field, value in before.items():
                self.assertEqual(after[field], value)
        return source, output, summary, annotated

    def test_institution_does_not_require_an_invented_ministry(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, rows = self.prepare([nomination(ministere="", institution="PRIMATURE")], tmp)
            self.assertEqual(rows[0]["ministere_harmonise"], "")
            self.assertEqual(rows[0]["institution"], "PRIMATURE")

    def test_consolidated_export_preserves_sources_and_harmonised_ministries(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output, _, annotated = self.prepare([
                nomination(), nomination(matricule="", ministere="ministère de la santé,"),
            ], tmp)
            consolidated = read_csv(output / "nominations_2015_2025_fiabilise.csv")
            original = read_csv(source)
            self.assertEqual(len(consolidated), len(original))
            self.assertEqual(consolidated, annotated)
            for before, after in zip(original, consolidated):
                self.assertTrue(all(after[k] == v for k, v in before.items()))
                self.assertTrue(after["id_personne"].isdigit())
                self.assertTrue(after["ministere_harmonise"])
                self.assertIn("statut_harmonisation_ministere", after)
            self.assertEqual(consolidated[0]["ministere_harmonise"], consolidated[1]["ministere_harmonise"])

    def test_sequential_ids_and_each_missing_matricule_is_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, output, _, rows = self.prepare([
                nomination(), nomination(date_conseil="2021-01-08"),
                nomination(matricule=""), nomination(matricule=""),
                nomination(nom="Benoit AUTRE", matricule="999999Z"),
            ], tmp)
            self.assertEqual(rows[0]["id_personne"], rows[1]["id_personne"])
            self.assertNotEqual(rows[2]["id_personne"], rows[3]["id_personne"])
            self.assertNotIn(rows[0]["id_personne"], [rows[2]["id_personne"], rows[3]["id_personne"]])
            self.assertEqual({r["id_personne"] for r in rows}, {"1", "2", "3", "4"})
            self.assertTrue((output / "dictionnaires/correspondance_ids_personnes.csv").exists())

    def test_same_matricule_different_people_are_not_merged(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, rows = self.prepare([nomination(), nomination(nom="Benoit AUTRE")], tmp)
            self.assertNotEqual(rows[0]["id_personne"], rows[1]["id_personne"])
            self.assertTrue(all(r["identite_eligible_strict"] == "0" for r in rows))

    def test_missing_matricule_is_only_a_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, output, _, rows = self.prepare([nomination(), nomination(matricule="")], tmp)
            self.assertNotEqual(rows[0]["id_personne"], rows[1]["id_personne"])
            reviews = read_csv(output / "identites_a_verifier.csv")
            self.assertEqual(reviews[0]["ids_candidats"], rows[0]["id_personne"])

    def test_only_equal_evidence_is_deduplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, summary, rows = self.prepare([
                nomination(), nomination(document_id="copie.pdf"),
                nomination(extrait_exact="Décision distincte, à vérifier."),
            ], tmp)
            self.assertEqual(sum(int(r["conserver_evenement"]) for r in rows), 2)
            self.assertEqual(summary["nombre_groupes_doublons"], 1)
            self.assertTrue(any(r["statut_doublon"] == "doublon_potentiel_a_verifier" for r in rows))

    def test_simultaneous_positions_not_collapsed_by_family(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, output, _, rows = self.prepare([
                nomination(poste="Directeur général de A"),
                nomination(poste="Directeur général de B"),
            ], tmp)
            self.assertEqual(rows[0]["fonction_harmonisee"], rows[1]["fonction_harmonisee"])
            self.assertNotEqual(rows[0]["id_poste"], rows[1]["id_poste"])
            self.assertTrue(all(r["conserver_evenement"] == "1" for r in rows))
            self.assertEqual(len(read_csv(output / "nominations_simultanees.csv")), 2)
            self.assertFalse(read_csv(output / "nominations_trajectoires_strictes.csv"))

    def test_dictionary_merges_known_historical_denominations(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, rows = self.prepare([
                nomination(), nomination(ministere="ministère de la santé,"),
                nomination(ministere="MINISTERE DE LA SANTE ET DE L'HYGIENE PUBLIQUE"),
            ], tmp)
            self.assertEqual(rows[0]["ministere_harmonise"], rows[1]["ministere_harmonise"])
            self.assertEqual(rows[0]["ministere_harmonise"], rows[2]["ministere_harmonise"])
            self.assertNotEqual(rows[0]["ministere_historique"], rows[2]["ministere_historique"])
            self.assertEqual(rows[2]["code_ministere_reference"], "SANTE")

    def test_ids_and_dictionary_edits_survive_rerun_and_reordering(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output, _, rows = self.prepare([nomination(), nomination(nom="Autre NOM", matricule="999999Z")], tmp)
            mapping = {r["nom"]: (r["id_personne"], r["id_ligne_source"]) for r in rows}
            path = output / "dictionnaires" / "postes.csv"
            dictionary = read_csv(path)
            dictionary[0]["fonction_harmonisee"] = "Libellé révisé"
            write_csv(path, dictionary, list(dictionary[0]))
            raw = read_csv(source)[::-1]
            write_csv(source, raw, list(raw[0]))
            run(source, output)
            after = read_csv(output / "nominations_annotees.csv")
            self.assertEqual(mapping, {r["nom"]: (r["id_personne"], r["id_ligne_source"]) for r in after})
            self.assertTrue(all(r["fonction_harmonisee"] == "Libellé révisé" for r in after))

    def test_manual_decision_cannot_merge_a_person_without_matricule(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output, _, rows = self.prepare([nomination(), nomination(matricule="")], tmp)
            decision = dict(id_ligne_source=rows[1]["id_ligne_source"], id_personne_valide=rows[0]["id_personne"],
                            justification="Ancien rattachement", reference_documentaire="PDF p. 3")
            path = output / "dictionnaires/decisions_identites.csv"
            write_csv(path, [decision], list(decision))
            run(source, output)
            after = read_csv(output / "nominations_annotees.csv")
            self.assertNotEqual(after[0]["id_personne"], after[1]["id_personne"])
            self.assertEqual(after[1]["statut_identite"], "provisoire_nom_seul")

    def test_manual_identity_decision_requires_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output, _, rows = self.prepare([nomination(), nomination(matricule="999999Z")], tmp)
            path = output / "dictionnaires" / "decisions_identites.csv"
            decision = dict(id_ligne_source=rows[1]["id_ligne_source"], id_personne_valide=rows[0]["id_personne"],
                            justification="Nom et identité vérifiés dans les pièces", reference_documentaire="PDF, p. 3")
            write_csv(path, [decision], list(decision))
            run(source, output)
            after = read_csv(output / "nominations_annotees.csv")
            self.assertEqual(after[0]["id_personne"], after[1]["id_personne"])
            self.assertEqual(after[1]["statut_identite"], "valide_manuellement")
            decision["reference_documentaire"] = ""
            write_csv(path, [decision], list(decision))
            with self.assertRaises(ValueError):
                run(source, output)

    def test_ambiguous_middle_event_does_not_create_a_false_jump(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, output, _, rows = self.prepare([
                nomination(),
                nomination(date_conseil="2021-01-08", document_id="CDM - 2021_01_09.pdf"),
                nomination(date_conseil="2022-01-08", document_id="CDM - 2022_01_08.pdf"),
            ], tmp)
            self.assertFalse(read_csv(output / "nominations_trajectoires_strictes.csv"))
            self.assertEqual(rows[0]["motifs_exclusion_stricte"], "autre_evenement_personne_a_verifier")

    def test_initial_zeros_and_atypical_matricules_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, _, rows = self.prepare([nomination(), nomination(matricule="ANPE 233")], tmp)
            self.assertEqual(rows[0]["matricule_normalise"], "001234A")
            self.assertEqual(rows[1]["matricule"], "ANPE 233")
            self.assertEqual(rows[1]["identite_eligible_strict"], "0")

    def test_unlinked_missing_matricule_cannot_create_a_false_jump(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, output, _, rows = self.prepare([
                nomination(),
                nomination(matricule="", date_conseil="2021-01-08", document_id="CDM - 2021_01_08.pdf"),
                nomination(date_conseil="2022-01-08", document_id="CDM - 2022_01_08.pdf"),
            ], tmp)
            self.assertFalse(read_csv(output / "nominations_trajectoires_strictes.csv"))
            self.assertEqual(rows[0]["motifs_exclusion_stricte"], "episode_candidat_non_rattache")


if __name__ == "__main__":
    unittest.main()
