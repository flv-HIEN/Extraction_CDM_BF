import tempfile
import unittest
import subprocess
import json
from pathlib import Path

from appliquer_decisions_revue import import_decisions, FIELDS
from fiabiliser_nominations import write_csv, read_csv
from fiabiliser_nominations import run
from test_fiabilisation import nomination


class ImportTests(unittest.TestCase):
    def test_browser_export_is_consumed_by_the_real_preparation(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            source = folder / "source.csv"
            raw = [nomination(), nomination(nom="Alice TESTS", date_conseil="2021-01-08", document_id="CDM - 2021_01_08.pdf")]
            write_csv(source, raw, list(raw[0]))
            output = folder / "fiabilisation"
            run(source, output)
            exported = folder / "decisions.csv"
            core = Path(__file__).resolve().parent / "revue_identites" / "dist" / "core.js"
            js = """
const fs=require('node:fs'),C=require(process.argv[1]);
const data=C.buildDataset(C.parseCSV(fs.readFileSync(process.argv[2],'utf8')));
const group=data.groups[0];
const decisions={[group.id]:{mode:'same',target:group.ids[0],extraTargets:[],justification:'Validation simulée sur données de test',reference:'source synthétique, p. 3'}};
fs.writeFileSync(process.argv[3],C.csv(C.compileExport(data,decisions)));
"""
            subprocess.run(["node", "-e", js, str(core), str(output / "nominations_annotees.csv"), str(exported)], check=True, capture_output=True, text=True)
            imported = import_decisions(exported, output)
            self.assertEqual(imported["total"], 2)
            run(source, output)
            result = read_csv(output / "nominations_annotees.csv")
            self.assertEqual(len({r["id_personne"] for r in result}), 1)
            self.assertTrue(all(r["statut_identite"] == "valide_manuellement" for r in result))

    def test_merge_and_explicit_replacement_with_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            write_csv(folder / "nominations_annotees.csv", [{"id_ligne_source": "L1"}, {"id_ligne_source": "L2"}], ["id_ligne_source"])
            target = folder / "dictionnaires" / "decisions_identites.csv"
            old = dict(id_ligne_source="L1", id_personne_valide="P1", justification="Vérifié", reference_documentaire="a.pdf p.1")
            new = dict(old, id_ligne_source="L2", id_personne_valide="P2")
            write_csv(target, [old], FIELDS)
            incoming = folder / "export.csv"
            write_csv(incoming, [new], FIELDS)
            result = import_decisions(incoming, folder)
            self.assertEqual(result["total"], 2)
            self.assertTrue(Path(result["sauvegarde"]).exists())
            previous = target.read_bytes()
            write_csv(incoming, [dict(old, id_personne_valide="CORRIGE")], FIELDS)
            with self.assertRaises(ValueError):
                import_decisions(incoming, folder)
            self.assertEqual(target.read_bytes(), previous)
            import_decisions(incoming, folder, replace=True)
            self.assertEqual(read_csv(target)[0]["id_personne_valide"], "CORRIGE")

    def test_unknown_and_duplicate_lines_never_modify_existing_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            write_csv(folder / "nominations_annotees.csv", [{"id_ligne_source": "L1"}], ["id_ligne_source"])
            incoming = folder / "export.csv"
            record = dict(id_ligne_source="AUTRE", id_personne_valide="P", justification="ok", reference_documentaire="p1")
            write_csv(incoming, [record], FIELDS)
            with self.assertRaises(ValueError):
                import_decisions(incoming, folder)
            record["id_ligne_source"] = "L1"
            write_csv(incoming, [record, record], FIELDS)
            with self.assertRaises(ValueError):
                import_decisions(incoming, folder)
            self.assertFalse((folder / "dictionnaires" / "decisions_identites.csv").exists())


if __name__ == "__main__":
    unittest.main()
