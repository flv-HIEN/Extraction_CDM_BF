import tempfile
import unittest
from pathlib import Path
from extraire_nominations_2015 import context_resolver, detect_rattachements, extract_from_pdf, fitz

class RattachementTests(unittest.TestCase):
    def test_title_stops_before_person_and_next_heading(self):
        text = "II. NOMINATIONS\nA. AU TITRE DU MINISTERE DE LA SANTE\nMonsieur Alpha, est nommé Directeur.\nB. AU TITRE DU MINISTERE DE LA JUSTICE\nMadame Beta, est nommée Directrice."
        resolve=context_resolver(text)
        self.assertEqual(resolve(text.index('Monsieur'))['ministere'],'MINISTERE DE LA SANTE')
        self.assertEqual(resolve(text.index('Madame'))['ministere'],'MINISTERE DE LA JUSTICE')

    def test_representation_is_not_a_ministry(self):
        text="AU TITRE DU MINISTERE DE LA SANTE\nLe Conseil adopte.\nAu titre des usagers de l'eau\n- Monsieur Alpha"
        c=context_resolver(text)(text.index('Monsieur'))
        self.assertEqual(c['ministere'],'MINISTERE DE LA SANTE')
        self.assertEqual(c['categorie_representation'],"usagers de l'eau")
        text="Au titre du personnel\n- Monsieur Alpha"
        c=context_resolver(text)(text.index('Monsieur'))
        self.assertEqual(c['ministere'],'')
        self.assertEqual(c['categorie_representation'],'personnel')
        self.assertTrue(c['alerte_extraction_ministere'])

    def test_institution_and_reset(self):
        text="II. NOMINATIONS\nAU TITRE DE LA PRIMATURE\n- Monsieur Alpha\nIII. COMMUNICATIONS\nMonsieur Beta"
        resolve=context_resolver(text)
        c=resolve(text.index('Monsieur Alpha'))
        self.assertEqual(c['institution'],'PRIMATURE')
        self.assertEqual(c['ministere'],'')
        c=resolve(text.index('Monsieur Beta'))
        self.assertEqual(c['institution'],'')
        self.assertTrue(c['alerte_extraction_ministere'])

    def test_multiline_and_nomination_boundary(self):
        text="A. MINISTERE DE L'ECONOMIE,\nDES FINANCES ET DU DEVELOPPEMENT\nSont nommés directeurs les personnes suivantes :\nMonsieur Alpha"
        heading=detect_rattachements(text)[0]
        self.assertEqual(heading['label'],"MINISTERE DE L'ECONOMIE, DES FINANCES ET DU DEVELOPPEMENT")

    def test_no_narrative_inference(self):
        text="Le ministre de la santé a informé le Conseil. Monsieur Alpha est nommé directeur."
        self.assertEqual(context_resolver(text)(text.index('Monsieur'))['ministere'],'')

    def test_real_pdf_pipeline_preserves_context_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'CDM - 2020_01_08.pdf'
            with fitz.open() as doc:
                page=doc.new_page()
                page.insert_text((50,50),"II. NOMINATIONS\nA. AU TITRE DU MINISTERE DE LA SANTE\n- Monsieur Alpha TEST, Mle 123456A, est nomme Directeur general.")
                doc.save(p)
            rows,_=extract_from_pdf(p)
            self.assertTrue(rows)
            self.assertTrue(all(r['ministere']=='MINISTERE DE LA SANTE' for r in rows))
            self.assertTrue(all(r['type_rattachement']=='ministere' for r in rows))

    def test_multiline_board_list_and_ministry_are_both_recognised(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'CDM - 2020_01_08.pdf'
            text=("II. NOMINATIONS DANS LES CONSEILS\n"
                  "A. MINISTERE DE LA SANTE\n"
                  "Le premier decret nomme les personnes ci-apres, Administrateurs\n"
                  "au Conseil d'administration de l'Agence de test :\n"
                  "- Monsieur Alpha TEST, Mle 123456A, Ingenieur ;\n"
                  "- Madame Beta TEST, Mle 123457A, Ingenieur.\n")
            # Accent nécessaire à la formule ci-après de la règle existante.
            text=text.replace('ci-apres','ci-après')
            with fitz.open() as doc:
                page=doc.new_page();page.insert_text((50,50),text);doc.save(path)
            rows,_=extract_from_pdf(path)
            self.assertEqual({r['nom'] for r in rows},{'Alpha TEST','Beta TEST'})
            self.assertTrue(all(r['ministere']=='MINISTERE DE LA SANTE' for r in rows))
            self.assertTrue(all('Administrateur' in r['poste_nomination'] for r in rows))

    def test_collective_intro_does_not_cross_next_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'CDM - 2020_01_08.pdf'
            text=("II. NOMINATIONS\nA. MINISTERE DE LA SANTE\n"
                  "Sont nommes Administrateurs\n"
                  "B. MINISTERE DE LA JUSTICE\n"
                  "les personnes ci-après :\n"
                  "- Monsieur Alpha TEST, Mle 123456A, Ingenieur.\n")
            with fitz.open() as doc:
                page=doc.new_page();page.insert_text((50,50),text);doc.save(path)
            rows,_=extract_from_pdf(path)
            self.assertFalse(rows)

    def test_arcop_is_not_part_of_ministry_title(self):
        text=("Au titre du ministère des Infrastructures et du désenclavement "
              "au Conseil de régulation de l'Autorité de régulation de la Commande publique "
              "(ARCOP) pour un premier mandat de trois ans : Monsieur Alpha")
        heading=detect_rattachements(text)[0]
        self.assertEqual(heading['label'], 'ministère des Infrastructures et du désenclavement')
        self.assertNotIn('ARCOP',heading['label'])
        for conseil in ["au Conseil d'orientation et de contrôle de l'ANAM", "au Conseil d’administration de l'Agence"]:
            heading=detect_rattachements("Au titre du ministère de la Santé " + conseil + " : Monsieur Alpha")[0]
            self.assertEqual(heading['label'],'ministère de la Santé')

if __name__=='__main__':unittest.main()
