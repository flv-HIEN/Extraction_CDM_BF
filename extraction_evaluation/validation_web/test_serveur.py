"""Tests de sauvegarde sur copies temporaires, jamais sur les annotations de travail."""
import shutil
import tempfile
import unittest
from pathlib import Path
from serveur import ROOT, FILES, Store


class SaveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        folder = root / 'evaluation'
        folder.mkdir()
        for name in (*FILES, 'lot_pilote_12_documents.csv'):
            source = ROOT / 'archives' / 'evaluations_historiques' / name
            if source.exists():
                shutil.copy2(source, folder / name)
        shutil.copytree(ROOT / 'archives' / 'evaluations_historiques' / 'textes', folder / 'textes')
        self.store = Store(root, folder=folder)
        self.ident = 'CDM - 2024_07_10.pdf'

    def payload(self, validate=False, ident=None):
        data = self.store.load(ident or self.ident)
        return dict(document_id=data['document']['document_id'], version=data['version'],
                    rows=data['rows'], validate=validate, reviewed_all=validate, reviewer='Test temporaire')

    def test_validate_then_reopen_preserves_other_documents(self):
        _, before = self.store.read(FILES[0])
        others = [x for x in before if x['document_id'] != self.ident]
        p = self.payload(True)
        p['rows'][0]['commentaire'] = 'Correction de test'
        result = self.store.save(p)
        self.assertTrue((self.store.root / result['backup'] / FILES[0]).exists())
        self.assertEqual(len([x for x in self.store.read(FILES[1])[1] if x['document_id'] == self.ident]), 16)
        self.assertEqual([x for x in self.store.read(FILES[0])[1] if x['document_id'] != self.ident], others)
        self.assertEqual(self.store.read(FILES[0]), self.store.read(FILES[2]))
        self.store.save(self.payload(False))
        self.assertFalse(any(x['document_id'] == self.ident for x in self.store.read(FILES[1])[1]))

    def test_conflict_rejected_without_changes(self):
        p = self.payload()
        self.store.save(p)
        version = self.store.version()
        with self.assertRaises(RuntimeError):
            self.store.save(p)
        self.assertEqual(version, self.store.version())

    def test_invalid_page_and_missing_confirmation(self):
        p = self.payload(True)
        p['rows'][0]['page'] = '9999'
        before = self.store.version()
        with self.assertRaises(ValueError):
            self.store.save(p)
        p = self.payload(True)
        p['reviewed_all'] = False
        with self.assertRaises(ValueError):
            self.store.save(p)
        self.assertEqual(before, self.store.version())

    def test_zero_nominations_can_be_validated(self):
        ident = 'CDM - 2016_01_16.pdf'
        self.store.save(self.payload(True, ident))
        self.assertTrue(self.store.states()[ident]['valide'])
        self.assertEqual(self.store.states()[ident]['nombre_lignes'], 0)
        self.assertEqual(self.store.load(ident)['status'], 'aucune_nomination_verifiee')

    def test_added_and_deleted_rows_persist(self):
        p = self.payload()
        removed = p['rows'].pop(0)
        added = dict(removed, nom='NOM DE TEST', extrait_exact='Extrait de test')
        p['rows'].append(added)
        self.store.save(p)
        rows = self.store.load(self.ident)['rows']
        self.assertIn('NOM DE TEST', [x['nom'] for x in rows])
        self.assertNotIn(removed, rows)


if __name__ == '__main__':
    unittest.main()
