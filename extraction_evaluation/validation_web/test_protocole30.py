"""Contrôles sur copies temporaires du protocole des 30 PDF."""
import csv
import shutil
import tempfile
import unittest
from pathlib import Path
from serveur import ROOT, Store30

class Protocole30Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        project = Path(self.temp.name)
        (project / 'donnees').symlink_to(ROOT.parent / 'donnees', target_is_directory=True)
        self.root = project / 'extraction_evaluation'
        self.folder = self.root / 'lots'
        self.folder.mkdir(parents=True)
        for name in ('evaluation_30.csv', 'reference_30.csv', 'validation_30.csv'):
            shutil.copy2(ROOT / 'lots' / name, self.folder / name)
        self.store = Store30(self.root)
        self.ident = self.store.documents()[0]['document_id']

    def payload(self, rows, validate=True):
        return dict(document_id=self.ident, version=self.store.version(), rows=rows,
                    validate=validate, reviewed_all=True, reviewer='Test')

    def test_all_30_documents_accessible(self):
        self.assertEqual(len(self.store.documents()), 30)
        for doc in self.store.documents():
            data = self.store.load(doc['document_id'])
            self.assertTrue(data['pages'])
            self.assertTrue(self.store.source(doc, 'pdf').is_file())

    def test_empty_document_validation_and_reopening(self):
        self.store.save(self.payload([]))
        self.assertEqual(self.store.load(self.ident)['status'], 'valide')
        self.assertEqual(self.store.load(self.ident)['rows'], [])
        self.store.save(self.payload([], False))
        self.assertEqual(self.store.load(self.ident)['status'], 'a_relire')

    def test_prediction_deleted_not_reintroduced_and_conflict(self):
        folder = self.root / 'evaluation';folder.mkdir()
        (folder / 'extractions_pipeline_evaluation_30.csv').write_text(
            'document_id,nom\n' + self.ident + ',Proposition\n', encoding='utf-8')
        self.assertEqual(len(self.store.load(self.ident)['rows']), 1)
        stale = self.payload([])
        self.store.save(self.payload([], False))
        self.assertEqual(self.store.load(self.ident)['rows'], [])
        with self.assertRaises(RuntimeError):self.store.save(stale)

    def test_reference_compatible_with_evaluator(self):
        row = dict(nom='Nom test', page='1', date_conseil='2020-01-01',
                   extrait_exact='Extrait de test', fonction='Fonction test',
                   ministere='Ministère test', type_nomination='fonction_individuelle')
        self.store.save(self.payload([row]))
        data = self.store.load(self.ident)
        self.assertEqual(data['rows'][0]['statut_verification'], 'valide')
        self.assertEqual(data['status'], 'valide')
        with (self.folder / 'reference_30.csv').open(encoding='utf-8-sig') as f:
            self.assertEqual(next(csv.DictReader(f))['fonction'], 'Fonction test')
        self.assertTrue(list((self.folder / 'sauvegardes_validation').iterdir()))
        with self.assertRaises(ValueError):
            self.store.save({**self.payload([row]), 'reviewed_all':False})

if __name__=='__main__':unittest.main()
