import unittest
from ministeres.fusion_denominations import fusionner

class FusionTests(unittest.TestCase):
    def test_known_renaming(self):
        a=fusionner('MINISTERE DE LA SANTE')
        b=fusionner("Ministère de la Santé et de l'Hygiène publique")
        self.assertEqual(a['ministere_reference'],b['ministere_reference'])
        self.assertEqual(b['code_ministere_reference'],'SANTE')
    def test_unknown_not_merged_by_similarity(self):
        self.assertEqual(fusionner('Ministère de la Santé et du Commerce imaginaire')['ministere_reference'],'')
    def test_convention_not_treated_as_renaming(self):
        r=fusionner("Ministère de l'Environnement, de l'Économie verte et du Changement climatique")
        self.assertEqual(r['statut_fusion_ministere'],'convention_a_verifier')
        self.assertEqual(r['ministere_reference'],'')
    def test_missing_preserved(self):
        self.assertEqual(fusionner('')['statut_fusion_ministere'],'sans_ministere')

    def test_verified_aliases_preserve_perimeters(self):
        r=fusionner("MINISTERE DE L'AGRICULTURE, DES AMENANGEMENTS HYDRO-AGRICOLES ET DE LA MECANISATION")
        self.assertEqual(r['code_ministere_reference'],'AGRI_EAU_RAH')
        self.assertTrue(r['reference_alias_ministere'])
        r=fusionner('Ministère des Enseignements secondaires et supérieur')
        self.assertEqual(r['statut_fusion_ministere'],'convention_a_verifier')
        self.assertTrue(r['alias_ministere_applique'])

if __name__=='__main__':unittest.main()
