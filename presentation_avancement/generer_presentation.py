"""Génère une présentation PowerPoint modifiable et un PDF à partir du même dessin.

Dépendances : python-pptx et reportlab. Les données du projet sont uniquement lues.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Emplacement temporaire utilisé pour la génération initiale ; installation
# standard de python-pptx/reportlab également prise en charge.
if Path('/tmp/presentation_nominations_deps').is_dir():
    sys.path.insert(0, '/tmp/presentation_nominations_deps')

from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

OUT = Path(__file__).resolve().parent
A = json.loads((OUT / 'audit_projet.json').read_text())
B = A['bilan_fiabilisation']
W, H = 960, 540
P = {'bg':'F5F5EF','ink':'17332E','muted':'63736B','line':'DCE3D7',
     'white':'FFFFFF','green':'176A55','pale':'E7EFE1','gold':'AD7831',
     'sand':'F3EADB','red':'9C4C3B','dark':'142F29','light':'C0D2C1'}


def rgb(value):
    value = P.get(value, value)
    return RGBColor.from_string(value)


def pdfcolor(value):
    value = P.get(value, value)
    return tuple(int(value[i:i+2], 16)/255 for i in (0,2,4))


pdfmetrics.registerFont(TTFont('Body', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
prs = Presentation()
prs.slide_width, prs.slide_height = Pt(W), Pt(H)
prs.core_properties.title = 'Des comptes rendus aux trajectoires professionnelles — Avancement'
prs.core_properties.subject = A['objectif']
prs.core_properties.author = 'Projet de mémoire — extraction et analyse des nominations'
prs.core_properties.keywords = 'nominations, PDF, trajectoires professionnelles, avancement, 2015–2025'
pdf = Canvas(str(OUT / 'avancement_nominations_2026-10-16.pdf'), pagesize=(W,H))
pdf.setTitle(prs.core_properties.title)
pdf.setAuthor(prs.core_properties.author)
notes = []
all_text = []


class Slide:
    def __init__(self, chapter, title, subtitle='', source='', dark=False):
        self.slide = prs.slides.add_slide(prs.slide_layouts[6])
        self.index = len(prs.slides)
        self.title = title
        self.dark = dark
        self.texts = []
        self.rect(0,0,W,H,'dark' if dark else 'bg')
        self.text(48,25,864,15,chapter.upper(),9,'light' if dark else 'green',bold=True)
        if title:
            title_size=min(27,27*857/max(1,pdfmetrics.stringWidth(title,'Bold',27)))
            self.text(48,56,864,39,title,title_size,'white' if dark else 'ink',bold=True)
        if subtitle:
            self.text(48,104,864,34,subtitle,11,'light' if dark else 'muted')
        self.rect(48,502,864,.65,'green' if dark else 'line')
        self.text(48,510,810,18,source or 'Point d’avancement · 16 octobre 2026 · Corpus 2015–2025',7.1,'light' if dark else 'muted')
        self.text(866,508,46,18,f'{self.index:02d} / 18',8,'light' if dark else 'muted',align='right')

    def rect(self,x,y,w,h,fill='white',line=None,radius=0):
        shape = self.slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Pt(x),Pt(y),Pt(w),Pt(h))
        shape.fill.solid(); shape.fill.fore_color.rgb=rgb(fill)
        if line:
            shape.line.color.rgb=rgb(line);shape.line.width=Pt(.7)
        else:
            shape.line.fill.background()
        if radius:
            shape.adjustments[0]=.08
        pdf.setFillColorRGB(*pdfcolor(fill))
        if line: pdf.setStrokeColorRGB(*pdfcolor(line));pdf.setLineWidth(.7)
        if radius: pdf.roundRect(x,H-y-h,w,h,radius,stroke=int(bool(line)),fill=1)
        else: pdf.rect(x,H-y-h,w,h,stroke=int(bool(line)),fill=1)
        return shape

    def text(self,x,y,w,h,text,size=13,color='ink',bold=False,align='left',leading=None):
        font='Bold' if bold else 'Body'
        leading=leading or size*1.28
        lines=[]
        for para in str(text).split('\n'):
            lines.extend(simpleSplit(para,font,size,w) if para else [''])
        required=(len(lines)-1)*leading+size*1.15
        if required>h+.5:
            raise ValueError(f'Diapo {self.index} : texte trop haut ({required:.1f}>{h}) : {text[:100]}')
        if x<0 or y<0 or x+w>W+.5 or y+h>H+.5:
            raise ValueError(f'Diapo {self.index} : élément hors page')
        box=self.slide.shapes.add_textbox(Pt(x),Pt(y),Pt(w),Pt(h))
        tf=box.text_frame;tf.clear();tf.word_wrap=False
        tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
        from pptx.enum.text import PP_ALIGN
        for i,line in enumerate(lines):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
            p.text=line;p.font.name='DejaVu Sans';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color)
            p.space_before=p.space_after=Pt(0);p.line_spacing=Pt(leading)
            p.alignment={'left':PP_ALIGN.LEFT,'right':PP_ALIGN.RIGHT,'center':PP_ALIGN.CENTER}[align]
        pdf.setFillColorRGB(*pdfcolor(color));pdf.setFont(font,size)
        for i,line in enumerate(lines):
            tx=x
            if align=='center': tx=x+(w-pdfmetrics.stringWidth(line,font,size))/2
            elif align=='right':tx=x+w-pdfmetrics.stringWidth(line,font,size)
            pdf.drawString(tx,H-y-size*.95-i*leading,line)
        self.texts.append(str(text))
        return box

    def label(self,x,y,w,text,fill='pale',color='green'):
        self.rect(x,y,w,22,fill,radius=4)
        self.text(x+9,y+5,w-18,14,text,8.5,color,bold=True)

    def card(self,x,y,w,h,title,body,fill='white',number=None):
        self.rect(x,y,w,h,fill,'line',6)
        top=y+18
        if number:
            self.text(x+18,top,w-36,43,number,29,'green',bold=True);top+=48
        self.text(x+18,top,w-36,42,title,13,bold=True)
        self.text(x+18,top+48,w-36,max(20,h-(top-y)-62),body,11,'muted')

    def callout(self,text,fill='pale',color='green'):
        self.rect(48,459,864,33,fill,radius=5)
        size=min(10,10*834/max(1,pdfmetrics.stringWidth(text,'Bold',10)))
        self.text(61,468,838,18,text,size,color,bold=True)

    def bullets(self,x,y,w,items,size=12,gap=57):
        for i,(title,body) in enumerate(items):
            yy=y+i*gap
            self.rect(x,yy+4,4,15,'green')
            self.text(x+16,yy,w-16,25,title,size,bold=True)
            self.text(x+16,yy+27,w-16,gap-29,body,size-1,'muted')

    def finish(self,note):
        self.slide.notes_slide.notes_text_frame.text=note
        notes.append(f'{self.index:02d}. {self.title or "Page de titre"}\n{note}\n')
        all_text.append({'diapositive':self.index,'titre':self.title,'texte':self.texts,'notes':note})
        pdf.showPage()


# 01 — Objectif du mémoire.
s=Slide('Projet de mémoire · Conseil des ministres','',source='Présentation d’avancement · 16 octobre 2026 · Sources : fichiers et code du projet',dark=True)
s.text(48,84,825,144,'Des comptes rendus\naux trajectoires\nprofessionnelles',39,'white',True,leading=47)
s.text(50,257,760,62,'Construire un pipeline d’extraction des nominations dans les PDF,\npuis analyser les parcours professionnels observés.',16,'light',leading=23)
s.label(50,355,134,'CORPUS 2015–2025','green','white')
s.label(196,355,205,'POINT D’AVANCEMENT','green','white')
for x,n,label in [(50,'408','PDF disponibles'),(337,'22 038','lignes consolidées'),(624,'3 000','fiches de revue')]:
    s.text(x,407,255,38,n,27,'white',True)
    s.text(x,448,255,22,label,11,'light')
s.finish('L’objectif comporte deux volets : automatiser l’extraction des nominations, puis analyser les trajectoires professionnelles des personnes identifiées. La chaîne technique est largement développée, mais la qualité des données et les méthodes d’analyse doivent encore être validées. Les effectifs proviennent de l’inventaire local au 16 octobre 2026 et du bilan de fiabilisation. Une ligne consolidée est un enregistrement extrait, pas nécessairement une nomination distincte validée.')

# 02 — Périmètre.
s=Slide('01 · Finalité scientifique','Deux volets liés par la qualité des données','Passer du document administratif à une base d’événements, puis à des parcours comparables.','Sources : objectif du travail ; extraire_nominations_2015.py ; test3.ipynb')
s.card(48,153,420,229,'Extraire les nominations','Repérer les décisions dans les PDF.\nIdentifier la personne, la date, le poste et le rattachement.\nConserver la page et l’extrait pour revenir à la source.',number='01')
s.card(490,153,422,229,'Analyser les trajectoires','Reconstituer les successions de nominations observées.\nDécrire les mobilités et les délais entre événements.\nRechercher des parcours récurrents et comparables.',number='02')
s.text(61,406,835,36,'Question directrice : quels parcours peut-on documenter de façon fiable à partir des nominations publiées ?',13,'green',True)
s.callout('La source renseigne les nominations publiées ; elle ne décrit pas à elle seule des carrières complètes.')
s.finish('Le premier livrable attendu est une base de nominations structurée et traçable. Le second est une analyse de trajectoires professionnelles observées. Les comptes rendus ne renseignent pas nécessairement les sorties de poste, les activités intermédiaires, les personnes jamais nommées dans ces documents ni les carrières antérieures à la fenêtre étudiée. Il faut donc formuler les conclusions en fonction de ce périmètre observé.')

# 03 — Architecture.
s=Slide('02 · Architecture','Une chaîne développée par briques','L’orchestration complète et le contrôle scientifique restent à consolider.','Sources : scripts Python, notebooks, fichiers CSV et application revue_identites/')
steps=[('01','PDF sources','408 fichiers\n11 millésimes','Constitué'),('02','Extraction','Texte natif\nOCR en repli','Implémenté'),('03','Consolidation','CSV annuels\nCSV 2015–2025','À réconcilier'),('04','Fiabilisation','Identités, répétitions\nlibellés, alertes','Implémenté'),('05','Revue humaine','Fiches de conflit\ndécisions exportables','Prête à utiliser'),('06','Trajectoires','Séquences, distances\ngroupes de parcours','Exploratoire')]
for i,(n,title,body,status) in enumerate(steps):
    x=48+(i%3)*294;y=151+(i//3)*142
    s.rect(x,y,276,123,'white','line',5);s.text(x+14,y+12,31,23,n,12,'green',True);s.text(x+51,y+12,205,27,title,13,bold=True)
    s.text(x+15,y+45,245,35,body,11,'muted');s.label(x+15,y+89,245,status,'sand' if i in [2,4,5] else 'pale','gold' if i in [2,4,5] else 'green')
s.callout('Priorité : figer une version cohérente du corpus avant la validation et l’analyse finale.')
s.finish('Le projet dispose de composants pour chacune des étapes principales : extraction, fusion, préparation, revue et analyse exploratoire. Cela ne constitue pas encore une exécution entièrement orchestrée, mesurée et validée de bout en bout sur l’ensemble des documents. Le flux cible doit associer à chaque exécution un inventaire, une version de source, des journaux d’erreurs et les décisions de revue utilisées.')

# 04 — Inventaire.
s=Slide('03 · Corpus','408 PDF disponibles, une couverture inégale','Nombre de fichiers présents par dossier annuel ; ce décompte ne mesure pas l’exhaustivité des séances.','Source : inventaire donnees/2015 à donnees/2025 ; audit_projet.json')
chart_x,chart_y,chart_w,chart_h=63,167,619,222
for tick in [0,10,20,30,40,50]:
    yy=chart_y+chart_h-tick/50*chart_h;s.rect(chart_x,yy,chart_w,.5,'line');s.text(39,yy-5,20,15,str(tick),8,'muted',align='right')
for i,r in enumerate(A['inventaire_annuel']):
    x=chart_x+12+i*55;h=r['pdf']/50*chart_h
    s.rect(x,chart_y+chart_h-h,31,h,'gold' if r['annee']==2022 else 'green',radius=2)
    s.text(x-7,chart_y+chart_h-h-19,46,16,str(r['pdf']),10,'gold' if r['annee']==2022 else 'ink',True,align='center')
    s.text(x-7,chart_y+chart_h+10,46,18,str(r['annee']),8.5,'muted',align='center')
s.card(722,163,190,121,'Millésimes','2015 à 2025',number='11')
s.rect(722,301,190,123,'sand',radius=5)
s.text(738,317,157,27,'2022 : 7 PDF',16,'gold',True)
s.text(738,353,157,57,'Vérifier les sources disponibles avant d’interpréter la baisse des nominations.',11,'muted')
s.callout('35 PDF présents n’ont aucune ligne dans leur CSV annuel : absence réelle ou extraction à vérifier.')
s.finish('L’inventaire local compte 408 PDF, dont seulement 7 dans le dossier 2022. Il ne permet pas de calculer un taux de couverture des séances : le nombre officiel de séances et les documents manquants ne sont pas encore établis. Trente-cinq fichiers PDF présents n’ont pas de ligne correspondante dans le CSV de leur dossier annuel ; cela peut refléter une absence de nomination ou une extraction incomplète. Ce point doit être tranché par retour aux sources. Les duplications de fichiers doivent aussi être prises en compte dans le futur inventaire documentaire.')

# 05 — Extraction.
s=Slide('04 · Réalisé — extraction','Un extracteur à règles avec provenance','Le texte natif est préservé ; Tesseract peut être activé pour les pages sans texte exploitable.','Sources : extraire_nominations_2015.py ; extraire_nominations_2015.ipynb ; tests ponctuels du 16/10/2026')
for i,(title,body) in enumerate([('Lecture','PyMuPDF\npage par page'),('Repérage','Rubriques\nde nominations'),('Extraction','Puces, phrases\net listes collectives'),('Structuration','Personne, poste\net qualifications')]):
    x=48+i*220;s.rect(x,158,204,112,'white','line',5);s.text(x+15,172,174,25,title,14,bold=True);s.text(x+15,209,174,45,body,11,'muted')
s.text(49,293,511,27,'Un schéma de 13 colonnes',16,bold=True)
s.text(49,332,511,84,'Nom et matricule ; date du conseil ; poste et ministère ; emploi, grade, classe, échelon ; document, page et extrait ; civilité.',12,'muted')
s.rect(592,291,320,141,'pale',radius=6)
s.text(609,307,287,26,'Contrôles ponctuels exécutés',14,'green',True)
s.text(609,346,287,69,'07/01/2015 : 153 lignes extraites\n03/08/2022 : 477 lignes extraites\nSchéma de sortie conforme sur ces 2 PDF.',11,'ink',leading=18)
s.callout('Le fonctionnement technique est observé ; la précision et le rappel restent à mesurer.')
s.finish('L’extracteur implémente des règles pour les rubriques ministérielles, les nominations individuelles, les listes collectives et les conseils d’administration. La date imprimée dans les premières pages est privilégiée, puis le nom de fichier sert de repli. Les extraits sont nettoyés des artefacts de mise en page : ils ne sont pas une reproduction binaire du PDF. Deux appels sans OCR ont été exécutés dans memoire_env : 153 lignes pour le PDF du 7 janvier 2015, et 477 pour celui du 3 août 2022. Le schéma de 13 champs est respecté. Aucune comparaison exhaustive à une annotation manuelle de référence n’a été menée ; ces résultats ne mesurent pas la justesse des nominations.')

# 06 — Versions des données.
s=Slide('05 · Point de vigilance','La consolidation n’est pas synchronisée','Les fichiers annuels et le fichier consolidé ne représentent pas exactement le même état des données.','Sources : donnees/nominations_2015.csv à nominations_2025.csv ; nominations_2015_2025.csv')
s.card(48,164,274,158,'CSV annuels','Somme des onze fichiers annuels actuellement présents.',number=f"{A['lignes_annuelles']:,}".replace(',',' '))
s.card(342,164,274,158,'CSV consolidé utilisé','Source actuelle de la fiabilisation et de la revue.',number='22 038')
s.card(636,164,276,158,'Écart net','Différence d’effectifs ; elle ne suffit pas à localiser les divergences.',fill='sand',number=f"+{A['ecart_net']}")
s.text(49,348,864,36,f"Comparaison des lignes : {A['lignes_annuelles_absentes_consolide']} uniquement dans les annuels ; {A['lignes_consolide_absentes_annuels']} uniquement dans le consolidé.",12,'ink',True)
s.text(49,400,864,36,'À faire : choisir la source de référence, expliquer les écarts, puis régénérer les sorties avec une version figée.',12,'muted')
s.callout('Les deux copies du CSV consolidé sont identiques ; le décalage concerne leur correspondance avec les annuels.','sand','gold')
s.finish('Cette divergence a été constatée pendant l’audit de préparation de la présentation. Les CSV annuels totalisent 22 154 lignes ; les deux copies du consolidé en comptent 22 038 et ont la même empreinte SHA-256. Les différences ont été calculées comme des différences de multiensembles sur les treize colonnes : les doublons éventuels sont comptés. Il faut expliquer ces divergences avant de choisir une source canonique. Aucun fichier de données n’a été modifié pour réaliser cette présentation. Après changement de source, les décisions et fiches de revue doivent être réconciliées avec la nouvelle version, sans reprise silencieuse.')

# 07 — Fiabilisation.
s=Slide('06 · Réalisé — préparation','Une base annotée et des copies analytiques','Les valeurs sources sont conservées ; chaque exclusion et chaque alerte restent traçables.','Sources : fiabiliser_nominations.py ; fiabilisation/bilan_qualite.json ; nominations_annotees.csv')
metrics=[('22 038','lignes annotées','Source consolidée brute'),('562','répétitions écartées','Même événement et même extrait normalisé'),('21 463','événements conservés','Période 2015–2025, après dédoublonnage')]
for i,(value,title,body) in enumerate(metrics):s.card(48+i*294,155,276,184,title,body,number=value)
s.rect(48,359,420,76,'white','line',5);s.text(64,372,386,24,'466 groupes de simultanéité possible',14,bold=True);s.text(64,403,386,22,'Aucun ordre intrajournalier inventé.',11,'muted')
s.rect(490,359,422,76,'white','line',5);s.text(506,372,389,24,'513 discordances de dates',14,bold=True);s.text(506,403,389,22,'Date CSV ≠ date du nom de fichier : à vérifier.',11,'muted')
s.callout('13 lignes hors période sont conservées dans les annotations, puis exclues de la copie 2015–2025.')
s.finish('La préparation conserve les 22 038 lignes du fichier consolidé. La copie descriptive exclut les 13 lignes datées de 2010 et écarte 562 répétitions textuelles, d’où 21 463 événements conservés. Une répétition textuelle est une redondance selon une règle de rapprochement, pas une validation documentaire de chaque événement. Les 466 groupes de simultanéité et les 513 discordances avec les noms de fichiers sont des alertes. Une discordance ne prouve pas que la date du CSV est fausse, puisque le nom du PDF peut être erroné. Quatre-vingt-treize lignes ont un nom de fichier sans date reconnue ; elles sont également recensées dans les sorties.')

# 08 — Identités.
s=Slide('07 · Identités','Des identifiants déterministes, une revue ouverte','Le rapprochement automatique distingue les cas cohérents des cas ambigus ; il ne certifie pas l’identité.','Sources : referentiel_personnes.csv ; identites_a_verifier.csv ; dictionnaires/decisions_identites.csv')
s.card(48,156,274,164,'Identifiants construits','Inclut des identifiants provisoires et des cas à vérifier.',number='13 471')
s.card(342,156,274,164,'Lignes à vérifier','Plusieurs lignes peuvent correspondre à une même identité.',number='8 202')
s.card(636,156,276,164,'Décisions réintégrées','État du fichier de décisions manuelles au moment de l’audit.',fill='sand',number='0')
s.text(49,347,864,25,'Répartition des observations du corpus annoté',12,bold=True)
frac=13836/22038;s.rect(49,388,862*frac,20,'green');s.rect(49+862*frac,388,862*(1-frac),20,'gold')
s.text(49,419,530,22,'13 836 lignes : couple nom–matricule cohérent',11,'green')
s.text(595,419,317,22,'8 202 lignes : cas incertains',11,'gold',align='right')
s.callout('Les variantes douteuses ne sont pas fusionnées automatiquement ; les candidats sont proposés séparément.')
s.finish('Les 13 471 identifiants ne constituent pas un nombre certifié de personnes réelles. Les 13 836 lignes cohérentes et les 8 202 lignes à vérifier partitionnent les 22 038 lignes annotées. Les incertitudes comprennent les noms associés à plusieurs matricules, les matricules partagés, les matricules absents ou atypiques et les conflits multiples. Zéro décision est présent dans le fichier d’import : cela ne permet pas d’affirmer qu’aucune revue n’a été commencée dans un navigateur, car ces sauvegardes sont locales. Cela signifie qu’aucune validation n’est encore réintégrée dans ce fichier du projet.')

# 09 — Dictionnaires.
s=Slide('08 · Harmonisation','Les dictionnaires existent ; leur validation reste à mener','Les intitulés complets sont distincts des familles de fonctions et des domaines d’action.','Sources : fiabilisation/dictionnaires/postes.csv et ministeres.csv ; bilan_qualite.json')
rows=[('Ministères','1 068','844','Libellés complets ; restructurations non fusionnées'),('Postes','12 684','11 639','Variantes lexicales et grammaticales normalisées')]
for i,(label,raw,harm,desc) in enumerate(rows):
    y=158+i*99;s.rect(48,y,864,84,'white','line',5);s.text(65,y+16,160,25,label,15,bold=True);s.text(244,y+13,234,34,f'{raw}  →  {harm}',21,'green',True);s.text(500,y+16,392,49,desc,11,'muted')
s.rect(48,373,420,64,'sand',radius=5);s.text(64,385,389,20,'5 478 lignes : fonction « À qualifier »',13,'gold',True);s.text(64,410,389,17,'Soit 24,9 % du corpus annoté.',10,'muted')
s.rect(490,373,422,64,'pale',radius=5);s.text(506,385,388,20,'Validation documentaire à enregistrer',13,'green',True);s.text(506,410,388,17,'Aucune entrée marquée « valide_manuellement ».',10,'muted')
s.callout('844 libellés normalisés ne signifient pas 844 ministères distincts : erreurs et variantes restent possibles.')
s.finish('Les chiffres portent sur les libellés du corpus annoté, et non sur un nombre réel de ministères ou de postes administratifs uniques. Les dictionnaires conservent le texte original, la forme harmonisée et les règles proposées. Les familles de fonctions, niveaux et domaines restent des propositions lexicales. Il faut corriger les intitulés absorbant des fragments de texte, distinguer fonction exécutive, mandat de représentation et promotion de grade, et documenter les changements institutionnels. Toutes les entrées sont encore marquées normalisation_lexicale ; aucune n’est marquée valide_manuellement. Les 5 478 lignes à qualifier concernent la fonction proposée.')

# 10 — Outil.
s=Slide('09 · Réalisé — outil de revue','3 000 fiches pour décider à l’échelle du conflit','Une interface dédiée rassemble les variantes, les profils candidats et les observations sources.','Sources : revue_identites/dist/ ; donnees_revue.json ; appliquer_decisions_revue.py')
s.card(48,154,274,215,'Comparer','Noms et matricules côte à côte.\nDates, postes, extraits et pages sources.\nOuverture des PDF associés localement.',number='01')
s.card(342,154,274,215,'Décider','Une seule personne ; plusieurs personnes ; à revoir.\nAttribution possible observation par observation.\nJustification et référence conservées.',number='02')
s.card(636,154,276,215,'Réutiliser','CSV compatible avec la préparation.\nSauvegarde JSON pour reprendre la revue.\nFusion des décisions et recalcul.',number='03')
s.text(49,397,864,23,'8 862 observations avec le contexte candidat ; au maximum 36 observations par fiche.',12,'green',True)
s.text(49,429,864,20,'Application privée : revue-identites-nominations.espace-de-tr-6789.chatgpt.site',10,'muted')
s.callout('Le flux export → import → recalcul est testé ; l’utilisabilité de l’interface reste à vérifier en situation réelle.')
s.finish('L’application regroupe les conflits liés par des identifiants, des matricules ou des noms candidats. Une composante de conflit ne signifie jamais que tous ses membres sont une même personne : elle organise leur comparaison. Le dossier de revue comprend 3 000 fiches et 8 862 observations, dont le contexte candidat. Les données sont chargées dans le navigateur ; les PDF ne sont pas inclus dans le site. Le CSV exporté contient une décision par ligne source et peut être importé par appliquer_decisions_revue.py. La publication privée a été confirmée lors de sa création. Le parcours logique export/import est testé ; une recette visuelle et une revue réelle par l’utilisatrice restent nécessaires.')

# 11 — Tests.
s=Slide('10 · Vérification technique','26 tests passent ; la qualité d’extraction reste à mesurer','Les contrôles logiciels et l’évaluation scientifique répondent à des questions différentes.','Sources : test_fiabilisation.py ; test_import_decisions_revue.py ; revue_identites/test_core.cjs')
s.rect(48,155,420,271,'pale',radius=6);s.text(67,173,379,28,'Vérifié dans le projet',17,'green',True)
s.bullets(68,219,375,[('13 tests Python','Identités, répétitions, simultanéité et réimport.'),('13 tests JavaScript','Regroupement, partitions, CSV et sauvegardes.'),('2 PDF exécutés sans OCR','Lecture et schéma de sortie vérifiés ponctuellement.')],size=12,gap=65)
s.rect(490,155,422,271,'white','line',6);s.text(509,173,383,28,'Encore à évaluer',17,bold=True)
s.bullets(510,219,381,[('Précision et rappel','Annotation manuelle d’un échantillon de documents.'),('Robustesse de l’extraction','Années, formats, listes collectives et OCR.'),('Reproductibilité complète','Exécution intégrale et recette de l’interface.')],size=12,gap=65)
s.callout('Aucun taux de précision, de rappel ou de complétude n’est encore établi.')
s.finish('Les tests ont été relancés pour cet audit : dix tests de préparation, trois tests d’import incluant le parcours JavaScript → CSV → import Python → recalcul, et treize tests du cœur JavaScript. Ils vérifient des règles techniques sur des cas contrôlés ; ils ne prouvent pas l’exactitude de l’extraction dans le corpus réel. L’évaluation doit comparer les sorties à une annotation de référence et mesurer, au minimum, les nominations détectées à tort, les nominations manquées et la justesse des champs extraits. L’OCR et les variations de mise en page doivent être inclus dans cette évaluation.')

# 12 — Description.
s=Slide('11 · Analyse descriptive','Un socle exploratoire est déjà codé','Les sorties analytiques doivent être recalculées et interprétées sur une base validée.','Source : test3.ipynb, partie I ; sorties actuelles effacées pour réexécution propre')
s.card(48,158,420,254,'Déjà présent dans le notebook','Comptages mensuels et annuels.\nMoyenne mobile sur douze mois.\nDécomposition saisonnière.\nTests ADF/KPSS, ACF/PACF.\nRepérage exploratoire de valeurs atypiques.')
s.card(490,158,422,254,'À compléter pour répondre à l’étude','Distinguer personnes, nominations et documents.\nDécrire les fonctions et institutions harmonisées.\nPrésenter les valeurs manquantes et les dénominateurs.\nSéparer mois sans source et mois sans nomination.\nComparer les populations incluses et exclues.')
s.callout('Une variation du nombre de lignes peut refléter la collecte, l’extraction ou les nominations elles-mêmes.','sand','gold')
s.finish('La partie descriptive existe sous forme de code. Le notebook actuel n’a pas été exécuté intégralement pour cet audit ; aucune série ou conclusion statistique nouvelle n’est présentée comme acquise. Les tests de stationnarité ne valident pas la couverture documentaire. Les pourcentages devront préciser s’ils concernent des événements, des personnes ou des documents. Les représentations par civilité devront être décrites comme déduites de cette information, et non assimilées à une mesure démographique exhaustive. Les mois sans document exploitable ne doivent pas être automatiquement codés zéro.')

# 13 — Trajectoires.
s=Slide('12 · Trajectoires — état actuel','Un prototype de séquences, pas encore une typologie validée','Le sous-ensemble conservateur évite des successions créées par la suppression d’événements ambigus.','Sources : nominations_trajectoires_strictes.csv ; test3.ipynb, partie II')
for i,(v,title,body) in enumerate([('7 371','Lignes conservatrices','Événements éligibles selon les règles de préparation.'),('4 957','Profils concernés','Identifiants présents dans ce sous-ensemble.'),('522','Profils avec ≥ 3 dates','Population actuelle du prototype de séquences.')]):
    s.card(48+i*294,156,276,188,title,body,number=v)
s.text(49,371,864,25,'Déjà codé : visualisations TanaT, distances entre séquences et classification hiérarchique.',12,bold=True)
s.text(49,411,864,29,'À valider : représentation temporelle, distance, nombre de groupes et stabilité des résultats.',12,'muted')
s.callout('Le seuil de trois dates et les exclusions sélectionnent une population particulière : une analyse de sensibilité est nécessaire.')
s.finish('Les 7 371 lignes et les 4 957 profils sont recomptés dans le fichier de trajectoires strictes ; 522 profils ont au moins trois dates distinctes. Ce sous-ensemble ne constitue pas une population certifiée ni représentative de l’ensemble des personnes nommées. La partie II contient la construction de séquences d’états sous hypothèse de continuité, des distances d’édition et positionnelles et un clustering hiérarchique. Le paramètre de vingt groupes est actuellement fixé dans le code sans justification scientifique établie. La cohérence et la stabilité de cette typologie restent à évaluer après réexécution sur les données validées.')

# 14 — Définition des événements.
s=Slide('13 · Cadre méthodologique','Ce que les nominations permettent d’observer','L’événement est documenté ; la continuité d’occupation entre deux événements reste une hypothèse.','Sources : structure des comptes rendus ; calcul end_date dans test3.ipynb ; limites du bilan de préparation')
s.rect(81,222,791,3,'line')
for x,label,sub in [(120,'Nomination A','date connue'),(472,'Dernière nomination','date connue'),(824,'Fin d’observation','borne à documenter')]:
    s.rect(x-6,216,13,15,'green',radius=3);s.text(x-94,166,190,24,label,14,bold=True,align='center');s.text(x-94,250,190,25,sub,10,'muted',align='center')
s.text(218,199,164,20,'Délai observé',11,'green',True,align='center')
s.text(578,199,154,20,'Délai censuré',11,'gold',True,align='center')
s.card(48,303,274,131,'Pas de fin de poste certaine','La prochaine nomination ne prouve pas la fin de la fonction précédente.')
s.card(342,303,274,131,'Première date observée','Elle ne correspond pas nécessairement au début de la carrière.')
s.card(636,303,276,131,'Mobilité à définir','Renouvellement, cumul, mandat et changement de fonction sont à distinguer.')
s.callout('Privilégier d’abord les séquences d’événements ; justifier toute reconstruction de durées ou de niveaux de carrière.')
s.finish('Le point d’entrée le plus directement soutenu par les données est une succession d’événements de nomination. Le délai entre deux nominations observées ne peut pas être présenté comme une durée d’occupation sans preuve de sortie et de suivi complet. La dernière observation est censurée pour le délai jusqu’à la prochaine nomination observée, sous les hypothèses de suivi à documenter. Les nomenclatures devront distinguer nomination exécutive, représentation dans une instance, renouvellement, cumul et changement de grade. Une promotion ne doit être déduite que d’une hiérarchie explicite et défendable, et non d’un ordre supposé entre intitulés.')

# 15 — Plan de travail.
s=Slide('14 · Travail restant','Quatre jalons pour passer à des résultats défendables','Ordre proposé selon les dépendances ; aucune durée de réalisation n’est présumée.','Source : synthèse de l’audit du projet ; priorités proposées')
milestones=[('1','Figer le corpus','Inventaire des PDF et couverture.\nRéconciliation annuels/consolidé.\nVersion et empreinte de référence.','Livrable : corpus de référence'),('2','Valider les données','Revue des identités et dates.\nValidation des dictionnaires.\nÉvaluation précision/rappel.','Livrable : base documentée'),('3','Définir les trajectoires','Événements et simultanéités.\nPopulation et fenêtre temporelle.\nDistance et critères de regroupement.','Livrable : protocole analytique'),('4','Produire les résultats','Description actualisée.\nTransitions et parcours types.\nStabilité, sensibilité et rédaction.','Livrable : analyses reproductibles')]
for i,(n,title,body,deliverable) in enumerate(milestones):
    x=48+i*220;s.rect(x,159,204,267,'white','line',5);s.label(x+14,174,176,'JALON '+n)
    s.text(x+14,215,176,49,title,15,bold=True)
    s.text(x+14,280,176,86,body,11,'muted')
    s.text(x+14,384,176,33,deliverable,10,'green',True)
s.callout('Premier jalon immédiat : expliquer les divergences entre CSV avant de figer la version soumise à la revue.')
s.finish('Ce plan est un ordre de dépendances, pas un calendrier chiffré. La première priorité est la cohérence et la couverture des sources. La deuxième porte sur la qualité des données, mesurée sur un échantillon annoté et améliorée par la revue. La troisième fixe le protocole d’analyse des trajectoires. La dernière produit les résultats et leur validation. Les règles de comparaison, les seuils de sélection et les critères de qualité doivent être documentés avant l’interprétation finale, sans choisir les paramètres uniquement en fonction de résultats jugés attrayants.')

# 16 — Prochain point d’étape.
s=Slide('15 · Prochain point d’avancement','Les livrables attendus à la prochaine étape','L’avancement se mesurera par des preuves et des versions stables, plutôt que par un pourcentage global.','Source : synthèse et critères de sortie proposés pour les prochaines étapes')
s.bullets(50,156,857,[('Un corpus réconcilié et versionné','Origine de chaque PDF, dates vérifiées, lacunes connues et divergences expliquées.'),('Une évaluation documentée de l’extraction','Échantillon annoté, précision/rappel et erreurs par type de décision et par champ.'),('Une base de personnes et de fonctions révisée','Décisions importées, catégories validées et ambiguïtés conservées explicitement.'),('Un premier résultat analytique reproductible','Description de la population, transitions observées et sensibilité aux choix de préparation.')],size=14,gap=72)
s.callout('Le socle technique est disponible ; la priorité scientifique est désormais la validation des données et du protocole.')
s.finish('Le projet a progressé de l’extraction vers une chaîne de préparation, de revue et de réutilisation des décisions. Il reste à transformer ce socle technique en une base évaluée et un protocole analytique validé. Au prochain point d’étape, les preuves attendues sont une source stabilisée, un bilan d’erreurs d’extraction, des décisions de revue effectivement intégrées et un premier résultat descriptif reproductible. Aucun pourcentage global d’achèvement n’est proposé, car il mélangerait développement logiciel et validation scientifique.')

# 17 — Annexes de reproductibilité.
s=Slide('Annexe A · Repères dans le projet','Les fichiers qui matérialisent le travail','Code disponible, sorties produites et contrôles relançables.','Sources : inventaire local ; scripts et notebooks du projet ; audit_projet.json')
file_rows=[('Extraction','extraire_nominations_2015.py / .ipynb','Lecture PDF, règles, schéma et provenance'),('Fusion','donnees/fusionner_nominations.py','Contrôle du schéma et concaténation annuelle'),('Préparation','fiabiliser_nominations.py / .ipynb','Identités, libellés, répétitions et alertes'),('Revue','revue_identites/ ; appliquer_decisions_revue.py','Fiches, décisions, export et réintégration'),('Analyse','test3.ipynb','Description et trajectoires exploratoires'),('Contrôles','test_fiabilisation.py ; test_import_decisions_revue.py','Règles de préparation et cycle des décisions')]
s.rect(48,153,864,28,'green');
for x,w,label in [(62,130,'Brique'),(209,390,'Fichiers'),(615,280,'Rôle')]:s.text(x,161,w,17,label,9,'white',True)
for i,(label,path,role) in enumerate(file_rows):
    y=181+i*43;s.rect(48,y,864,43,'white' if i%2==0 else 'pale');s.text(62,y+12,130,25,label,10,bold=True);s.text(209,y+10,390,31,path,9);s.text(615,y+10,280,31,role,9,'muted')
s.text(49,452,864,33,'Environnement scientifique repéré : memoire_env · Python 3.11.16 · pandas 3.0.5 · TanaT 0.10.4 · PyMuPDF 1.28.2',9,'muted')
s.finish('Les versions Jupyter et les scripts Python coexistent. L’extracteur est aussi copié dans donnees/ ; ces deux scripts sont identiques au moment de l’audit, mais cette duplication devra être évitée ou contrôlée pour prévenir des divergences futures. Un environnement scientifique existant a été repéré dans miniconda3/envs/memoire_env. Il contient notamment pandas, NumPy, statsmodels, polars, TanaT et PyMuPDF. Les tests relançables sont documentés dans les fichiers cités. La présentation est générée depuis audit_projet.json et conserve ses notes d’oral dans le PowerPoint ainsi que dans un fichier texte séparé.')

# 18 — Définitions et limites.
s=Slide('Annexe B · Lecture des chiffres','Définitions, sources et limites de l’état présenté','Les effectifs décrivent des fichiers locaux au 16 octobre 2026, pas une population administrative exhaustive.','Source principale : audit_projet.json ; bilan_qualite.json ; recomptages CSV et inventaire des PDF')
s.bullets(49,157,864,[('Ligne, événement, identifiant et personne réelle','Une ligne extraite peut être redondante ; un identifiant peut être provisoire. Les unités sont distinguées.'),('Corpus annuel et consolidé','Les chiffres de fiabilisation proviennent du consolidé de 22 038 lignes ; les annuels ne sont pas synchronisés.'),('Validation humaine et qualité d’extraction','Zéro décision est réintégrée ; aucune performance d’extraction mesurée sur une référence annotée.'),('Analyse exploratoire et résultats établis','Le code d’analyse est présent ; l’exécution intégrale et la validation des conclusions restent à réaliser.')],size=13,gap=72)
s.callout('Les chiffres techniques servent à piloter le travail ; ils ne sont pas encore des conclusions sur les carrières.')
s.finish('Sources locales principales : inventaire des 408 PDF, treize colonnes des CSV annuels et consolidés, fiabilisation/bilan_qualite.json, fichiers d’alertes, dictionnaires, référentiel des personnes, sous-ensemble de trajectoires strictes, dossier de revue et code des tests. Les contrôles n’ont pas modifié les fichiers sources ou appliqué de décision à des personnes réelles. Les noms et matricules individuels ne sont pas exposés dans la présentation. Les nombres de fichiers, lignes, identifiants et fiches sont des unités différentes. Les réserves méthodologiques portent notamment sur la couverture, les identités, la nature des nominations, les hypothèses de continuité et la sélection des trajectoires.')

assert len(prs.slides)==18
prs.save(str(OUT / 'avancement_nominations_2026-10-16.pptx'))
pdf.save()
(OUT / 'notes_orateur.txt').write_text('PRÉSENTATION D’AVANCEMENT — 16 OCTOBRE 2026\n\n'+'\n'.join(notes),encoding='utf-8')
(OUT / 'contenu_diaporama.json').write_text(json.dumps(all_text,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('18 diapositives créées : PowerPoint, PDF et notes orateur.')
