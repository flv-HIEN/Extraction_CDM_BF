# Dictionnaire des changements de dénomination des ministères au Burkina Faso (2015-2025)

## Objet et périmètre

Ce document suit les **dénominations des départements ministériels**, et non les
changements de personnes nommées ministres. Il couvre les compositions et
remaniements présents dans le dossier, complétés pour les étapes manquantes par
des décrets et publications institutionnelles disponibles en ligne, jusqu'au
31 décembre 2025.

Une différence de casse, d'accentuation ou de ponctuation n'est pas traitée comme
un changement. En revanche, l'ajout, le retrait, la fusion ou la scission d'un
domaine de compétence l'est. La qualité de « ministre d'État » et la fonction de
« porte-parole du Gouvernement » sont signalées seulement lorsqu'elles aident à
comprendre une restructuration : elles ne constituent pas, à elles seules, un
changement de nom du ministère.

## Format dictionnaire demandé

Le fichier exploitable est désormais
[`dictionnaires_ministeres_par_annee.py`](dictionnaires_ministeres_par_annee.py).
Chaque année où une dénomination évolue possède une variable dictionnaire :
`ministeres_2015`, `ministeres_2016`, …, `ministeres_2024`. Chaque dictionnaire
contient la liste complète des ministères pour la ou les dates concernées. Ainsi,
les deux remaniements de 2021 sont distingués par les clés `"2021-01-10"` et
`"2021-12-13"`, sans écraser l'une des deux compositions.

### Légende

- `→` : changement d'intitulé à périmètre principalement continu ;
- `+` : fusion de portefeuilles ;
- `↗` / `↘` : création / disparition (ou absorption) d'un portefeuille ;
- les intitulés sont reproduits sous la forme « Ministère de/des… », même lorsque
  le décret les présente sous la formule « Ministre de/des… ».

## Repères chronologiques utilisés

| Date de référence | Acte / gouvernement | Base principale |
|---|---|---|
| 19 juillet 2015 | Remaniement de la Transition, décret n° 2015-892 | D1 |
| 12 janvier 2016 | Composition du gouvernement Thiéba | D2, W1 |
| 20 février 2017 | Remaniement, décret n° 2017-075 | D3, W2 |
| 31 janvier 2018 | Remaniement, décret n° 2018-0035 | D4, W3 |
| 24 janvier 2019 | Premier gouvernement Dabiré | D5 |
| 10 janvier 2021 | Second gouvernement Dabiré | D6 |
| 13 décembre 2021 | Gouvernement Zerbo, décret n° 2021-1297 | D7, W4 |
| 5 mars 2022 | Gouvernement Albert Ouédraogo, décret n° 2022-053 | D8, W5 |
| 25 octobre 2022 | Gouvernement Kyélem de Tambèla, décret n° 2022-0927 | D9 |
| 17 décembre 2023 | Remaniement du gouvernement Kyélem de Tambèla | W6 |
| 1er août 2024 | Remaniement, décret n° 2024-0908 | D10, W7 |
| 8 décembre 2024 | Gouvernement Emmanuel Ouédraogo, décret n° 2024-1566 | W8, W9 |

Il n'apparaît pas de nouveau remaniement ministériel modifiant les intitulés au
cours de 2025. Le gouvernement nommé le 8 décembre 2024 est donc la dernière
référence de dénomination pour l'année 2025.

## Dictionnaire par domaine ministériel

### 1. Administration territoriale, décentralisation et sécurité

- **19 juillet 2015 → 12 janvier 2016** :
  *Ministère de l'Administration territoriale et de la Décentralisation* →
  *Ministère de l'Administration territoriale, de la Décentralisation et de la
  Sécurité intérieure* (`→`, intégration de la sécurité intérieure).
- **20 février 2017** :
  *Ministère de l'Administration territoriale, de la Décentralisation et de la
  Sécurité intérieure* → *Ministère de l'Administration territoriale et de la
  Décentralisation* ; `↗` *Ministère de la Sécurité* (`+` puis scission).
- **24 janvier 2019** :
  *Ministère de l'Administration territoriale et de la Décentralisation* →
  *Ministère de l'Administration territoriale, de la Décentralisation et de la
  Cohésion sociale*.
- **10 janvier 2021** : retrait de « Cohésion sociale » : retour au *Ministère
  de l'Administration territoriale et de la Décentralisation*.
- **13 décembre 2021** : ce dernier devient le *Ministère de l'Administration
  territoriale, de la Décentralisation et de la Sécurité* (`+` avec la Sécurité).
- **1er août 2024** : restructuration : *Ministère de l'Administration
  territoriale, de la Décentralisation et de la Sécurité* → *Ministère de
  l'Administration territoriale et de la Mobilité* ; `↗` *Ministère de la
  Sécurité*. La décentralisation disparaît de l'intitulé et la mobilité y entre.

### 2. Affaires étrangères, coopération, intégration et diaspora

- **19 juillet 2015 → 12 janvier 2016** : *Ministère des Affaires étrangères
  et de la Coopération régionale* → *Ministère des Affaires étrangères, de la
  Coopération et des Burkinabè de l'Extérieur*.
- **31 janvier 2018** : *Ministère des Affaires étrangères, de la Coopération
  et des Burkinabè de l'Extérieur* → *Ministère des Affaires étrangères et de
  la Coopération*.
- **24 janvier 2019** : séparation : *Ministère des Affaires étrangères et de
  la Coopération* + `↗` *Ministère de l'Intégration africaine et des Burkinabè
  de l'Extérieur*.
- **10 janvier 2021** : fusion : *Ministère des Affaires étrangères, de la
  Coopération, de l'Intégration africaine et des Burkinabè de l'Extérieur*.
- **13 décembre 2021** : retrait de l'intégration africaine : *Ministère des
  Affaires étrangères, de la Coopération et des Burkinabè de l'Extérieur*.
- **5 mars 2022** : ajout de la coopération régionale : *Ministère des Affaires
  étrangères, de la Coopération régionale et des Burkinabè de l'Extérieur*.
  Cet intitulé est maintenu jusqu'à la fin de 2025.

### 3. Défense et anciens combattants

- **20 février 2017** : le portefeuille jusque-là exercé par le Président du
  Faso est individualisé comme *Ministère de la Défense nationale et des Anciens
  combattants* (`↗` comme département ministériel autonome).
- **13 décembre 2021** : *Ministère de la Défense nationale et des Anciens
  combattants* → *Ministère des Armées et des Anciens Combattants*.
- **5 mars 2022** : retour à *Ministère de la Défense et des Anciens
  Combattants*. Cet intitulé est conservé en 2025 (avec le rang de ministère
  d'État à partir de décembre 2024).

### 4. Justice, droits humains et promotion civique

- **24 janvier 2019** : scission du *Ministère de la Justice, des Droits humains
  et de la Promotion civique, Garde des Sceaux* en *Ministère de la Justice,
  Garde des Sceaux* + `↗` *Ministère des Droits humains et de la Promotion
  civique*.
- **10 janvier 2021** : refusion : *Ministère de la Justice, des Droits humains
  et de la Promotion civique, Garde des Sceaux*.
- **5 mars 2022** : *Ministère de la Justice et des Droits humains, chargé des
  Relations avec les institutions, Garde des Sceaux*. La promotion civique sort
  de l'intitulé ; les relations avec les institutions y entrent. Cette
  dénomination est maintenue jusqu'en 2025.

### 5. Économie, finances, développement, plan et prospective

- **19 juillet 2015 → 12 janvier 2016** : *Ministère de l'Économie et des
  Finances* → *Ministère de l'Économie, des Finances et du Développement*.
- **13 décembre 2021** : *Ministère de l'Économie, des Finances et du
  Développement* → *Ministère de l'Économie, des Finances et du Plan* ; `↗`
  *Ministère de la Prospective et des Réformes structurelles*.
- **5 mars 2022** : *Ministère de l'Économie, des Finances et du Plan* →
  *Ministère de l'Économie, des Finances et de la Prospective* ; le portefeuille
  autonome de la prospective et des réformes structurelles est alors absorbé.
- **1er août 2024** : *Ministère de l'Économie, des Finances et de la
  Prospective* → *Ministère de l'Économie et des Finances*, qui demeure le nom
  de 2025.

### 6. Agriculture, eau, ressources animales et halieutiques

- **19 juillet 2015 → 12 janvier 2016** : le très large *Ministère de
  l'Agriculture, des Ressources hydrauliques, de l'Assainissement et de la
  Sécurité alimentaire* est restructuré en *Ministère de l'Agriculture et des
  Aménagements hydrauliques* + `↗` *Ministère de l'Eau et de l'Assainissement*.
  Les ressources animales, déjà séparées en 2015, deviennent le *Ministère des
  Ressources animales et halieutiques*.
- **24 janvier 2019** : *Ministère de l'Agriculture et des Aménagements
  hydrauliques* → *Ministère de l'Agriculture et des Aménagements
  hydro-agricoles*.
- **10 janvier 2021** : ajout de la mécanisation : *Ministère de l'Agriculture,
  des Aménagements hydro-agricoles et de la Mécanisation*.
- **13 décembre 2021** : fusion avec les ressources animales et halieutiques :
  *Ministère de l'Agriculture, des Aménagements hydro-agricoles, de la
  Mécanisation et des Ressources animales et halieutiques*.
- **5 mars 2022** : simplification : *Ministère de l'Agriculture, des
  Ressources animales et halieutiques*. Ce nom reste en vigueur jusqu'en 2025.

### 7. Environnement, énergie, mines, eau et assainissement

- **19 juillet 2015 → 12 janvier 2016** : *Ministère des Mines et de
  l'Énergie* → *Ministère de l'Énergie, des Mines et des Carrières*.
- **19 juillet 2015 → 12 janvier 2016** : *Ministère de l'Environnement et des
  Ressources halieutiques* → *Ministère de l'Environnement, de l'Économie verte
  et du Changement climatique* ; les ressources halieutiques rejoignent les
  ressources animales.
- **20 février 2017** : *Ministère de l'Énergie, des Mines et des Carrières* →
  `↘` *Ministère de l'Énergie* + `↗` *Ministère des Mines et des Carrières*.
- **10 janvier 2021** : nouvelle fusion : *Ministère de l'Énergie, des Mines et
  des Carrières*.
- **13 décembre 2021** : *Ministère de l'Environnement, de l'Économie verte et
  du Changement climatique* → *Ministère de la Transition écologique et de
  l'Environnement* ; *Ministère de l'Énergie, des Mines et des Carrières* →
  *Ministère de la Transition énergétique, des Mines et des Carrières*.
- **5 mars 2022** : grand regroupement : *Ministère de la Transition écologique
  et de l'Environnement* + les portefeuilles de l'énergie et de l'eau →
  *Ministère de l'Environnement, de l'Énergie, de l'Eau et de
  l'Assainissement* ; `↗` *Ministère des Mines et des Carrières*.
- **25 octobre 2022** : nouvelle scission : *Ministère de l'Environnement, de
  l'Eau et de l'Assainissement* + *Ministère de l'Énergie, des Mines et des
  Carrières*. Ces deux noms sont conservés jusqu'en 2025.

### 8. Infrastructures, transports, désenclavement et mobilité

- **19 juillet 2015 → 12 janvier 2016** : *Ministère des Infrastructures, du
  Désenclavement et des Transports* est scindé en *Ministère des
  Infrastructures* + *Ministère des Transports, de la Mobilité urbaine et de la
  Sécurité routière*.
- **10 janvier 2021** : *Ministère des Infrastructures* → *Ministère des
  Infrastructures et du Désenclavement*.
- **1er août 2024** : le premier redevient *Ministère des Infrastructures* ; le
  portefeuille autonome des transports cesse d'apparaître sous ce nom, tandis que
  « Mobilité » entre dans le *Ministère de l'Administration territoriale et de
  la Mobilité*.
- **8 décembre 2024** : *Ministère des Infrastructures* → *Ministère des
  Infrastructures et du Désenclavement*. Ce dernier changement est explicitement
  confirmé par le compte rendu officiel du Conseil des ministres du 12 mars 2025.

### 9. Industrie, commerce, artisanat et PME

- **19 juillet 2015 → 12 janvier 2016** : *Ministère de l'Industrie, du
  Commerce et de l'Artisanat* → *Ministère du Commerce, de l'Industrie et de
  l'Artisanat*.
- **10 janvier 2021** : retour de l'ordre *Ministère de l'Industrie, du
  Commerce et de l'Artisanat*.
- **13 décembre 2021** : *Ministère du Développement industriel, du Commerce,
  de l'Artisanat et des Petites et Moyennes Entreprises*.
- **1er août 2024** : retrait de « Développement » et des PME : *Ministère de
  l'Industrie, du Commerce et de l'Artisanat*, maintenu en 2025.

### 10. Numérique, postes et communications électroniques

- **10 janvier 2021** : *Ministère du Développement de l'Économie numérique et
  des Postes* → *Ministère de l'Économie numérique, des Postes et de la
  Transformation digitale*.
- **13 décembre 2021** : *Ministère de la Transition digitale, des Postes et
  des Communications électroniques*. Cette dénomination demeure inchangée
  jusqu'en 2025.

### 11. Éducation, enseignement supérieur, recherche et formation

- **19 juillet 2015 → 12 janvier 2016** : *Ministère des Enseignements
  secondaire et supérieur* + *Ministère de la Recherche scientifique et de
  l'Innovation* → *Ministère de l'Enseignement supérieur, de la Recherche
  scientifique et de l'Innovation*. Le *Ministère de l'Éducation nationale et
  de l'Alphabétisation* demeure séparé.
- **24 janvier 2019** : *Ministère de l'Éducation nationale et de
  l'Alphabétisation* → *Ministère de l'Éducation nationale, de
  l'Alphabétisation et de la Promotion des langues nationales*.
- **13 décembre 2021** : *Ministère de l'Enseignement supérieur, de la
  Recherche scientifique et de l'Innovation* → *Ministère de l'Enseignement
  supérieur, de la Recherche et de l'Innovation*.
- **1er août 2024** : scission de l'éducation : *Ministère de l'Éducation
  nationale, de l'Alphabétisation et de la Promotion des langues nationales* →
  *Ministère de l'Enseignement de base, de l'Alphabétisation et de la Promotion
  des langues nationales* + `↗` *Ministère de l'Enseignement secondaire, de la
  Formation professionnelle et technique*. Ces deux ministères, ainsi que celui
  de l'enseignement supérieur, conservent leurs noms en 2025.

### 12. Solidarité, genre, famille, jeunesse et sports

- **19 juillet 2015 → 12 janvier 2016** : *Ministère de l'Action sociale et de
  la Solidarité nationale* + *Ministère de la Promotion de la Femme et du Genre*
  → *Ministère de la Femme, de la Solidarité nationale et de la Famille*.
- **19 juillet 2015 → 12 janvier 2016** : *Ministère de la Jeunesse, de la
  Formation professionnelle et de l'Emploi* → *Ministère de la Jeunesse, de la
  Formation et de l'Insertion professionnelle*.
- **24 janvier 2019** : ajout de l'action humanitaire : *Ministère de la Femme,
  de la Solidarité nationale, de la Famille et de l'Action humanitaire*.
- **13 décembre 2021** : *Ministère du Genre, de la Solidarité nationale, de la
  Famille et de l'Action humanitaire* ; le *Ministère de la Jeunesse, de la
  Promotion de l'Entrepreneuriat et de l'Emploi* + le *Ministère des Sports et
  des Loisirs* deviennent le *Ministère des Sports, de l'Autonomisation des
  Jeunes et de l'Emploi*.
- **5 mars 2022** : scission de la solidarité : *Ministère de la Solidarité
  nationale et de l'Action humanitaire* + `↗` *Ministère du Genre et de la
  Famille* ; le portefeuille sport-jeunesse devient le *Ministère des Sports, de
  la Jeunesse et de l'Emploi*.
- **25 octobre 2022** : refusion : *Ministère de la Solidarité, de l'Action
  humanitaire, de la Réconciliation nationale, du Genre et de la Famille*.
- **1er août 2024** : *Ministère de l'Action humanitaire et de la Solidarité
  nationale* (retrait de la réconciliation nationale, du genre et de la famille).
  Le *Ministère des Sports, de la Jeunesse et de l'Emploi* reste inchangé en
  2025.

### 13. Santé, urbanisme, habitat, communication et culture

- **19 juillet 2015 → 12 janvier 2016** : *Ministère de la Communication,
  chargé des Relations avec le Conseil national de la Transition* → *Ministère
  de la Communication et des Relations avec le Parlement* ; le rattachement de
  porte-parole du Gouvernement est une fonction associée, non un ministère
  distinct.
- **19 juillet 2015 → 12 janvier 2016** : *Ministère de la Culture et du
  Tourisme* → *Ministère de la Culture, des Arts et du Tourisme*.
- **19 juillet 2015 → 12 janvier 2016** : *Ministère de l'Habitat et de
  l'Urbanisme* → *Ministère de l'Urbanisme et de l'Habitat*.
- **13 décembre 2021** : *Ministère de la Santé* → *Ministère de la Santé, de
  l'Hygiène publique et du Bien-être* ; *Ministère de l'Urbanisme, de l'Habitat
  et de la Ville* → *Ministère du Développement urbain, de l'Habitat et de la
  Ville* ; *Ministère de l'Environnement, de l'Économie verte et du Changement
  climatique* change comme indiqué à la section 7.
- **13 décembre 2021** : fusion de la culture dans la communication :
  *Ministère de la Communication et des Relations avec le Parlement* +
  *Ministère de la Culture, des Arts et du Tourisme* → *Ministère de la
  Communication, des Relations avec le Parlement, de la Culture, des Arts et du
  Tourisme*.
- **5 mars 2022** : *Ministère de la Santé, de l'Hygiène publique et du
  Bien-être* → *Ministère de la Santé et de l'Hygiène publique* ; *Ministère du
  Développement urbain, de l'Habitat et de la Ville* → *Ministère de
  l'Urbanisme, des Affaires foncières et de l'Habitat* ; le portefeuille de la
  communication devient le *Ministère de la Communication, de la Culture, des
  Arts et du Tourisme*.
- **1er août 2024** : *Ministère de la Santé et de l'Hygiène publique* →
  *Ministère de la Santé* ; *Ministère de l'Urbanisme, des Affaires foncières et
  de l'Habitat* → *Ministère de l'Urbanisme et de l'Habitat*. Le ministère de
  la Communication, de la Culture, des Arts et du Tourisme garde son intitulé
  (son ministre reçoit aussi le rang de ministre d'État et la fonction de
  porte-parole).

### 14. Fonction publique, travail et protection sociale

- **19 juillet 2015 → 12 janvier 2016** : *Ministère de la Fonction publique,
  du Travail et de la Sécurité sociale* → *Ministère de la Fonction publique, du
  Travail et de la Protection sociale*. Cette dénomination est ensuite stable sur
  la période étudiée.

### 15. Portefeuilles ponctuels à ne pas assimiler à un simple renommage

- **5 mars 2022** : `↗` *Ministère des Affaires religieuses et coutumières*.
  Cet intitulé ne figure plus dans la composition du 25 octobre 2022 (`↘`).
- **24 janvier 2019** : `↗` *Ministère des Droits humains et de la Promotion
  civique* et *Ministère de l'Intégration africaine et des Burkinabè de
  l'Extérieur* : ils résultent de scissions et sont réintégrés, respectivement,
  en janvier 2021.

## Contrôles utiles pour réutiliser le dictionnaire

1. Ne pas coder comme « changement de nom » le seul remplacement d'un ministre.
2. Pour 2022 et 2024, préserver les relations de fusion/scission : elles
   modifient le périmètre du département, pas seulement son libellé.
3. Pour les séries statistiques ou les entretiens, rattacher chaque observation à
   la **date de l'acte** ci-dessus, et non à l'année civile seule.
4. Les ministres délégués et secrétaires d'État n'ont pas été intégrés à ce
   dictionnaire, sauf lorsqu'ils éclairent une fusion de portefeuille.

## Sources

### Dossier `remaniement` (sources de travail)

- **D1** — `remaniemnent19-07-2015.docx`, décret n° 2015-892/PRES-TRANS/PM.
- **D2** — `formationGouv2016.pdf`, décret n° 2016-006/PRES/PM/SGG-CM du
  6 février 2016 (attributions des membres du Gouvernement).
- **D3** — `decret_remaniement2017.pdf`, décret n° 2017-075/PRES/PM du
  20 février 2017.
- **D4** — `remaniement31-01-2018.docx`.
- **D5** — `remaniement2019.docx`.
- **D6** — `remaniement2021.docx` et `remaniementII-2021.docx`.
- **D7** — `composition_gouvernement_zerbo_13-12-21.pdf`.
- **D8** — `decret-composition-du-gouvernement03-03-2022.pdf`.
- **D9** — `Composition-du-nouveau-gouvernement-de-la-transition-Kyelem25-10-22.pdf`.
- **D10** — `Remaniement-aout-2024.pdf` (doublon : `remaniement_aout_2024-2.pdf`).

### Vérifications en ligne

- **W1** — [Composition du gouvernement Thiéba du 12 janvier 2016](https://lepays.bf/gouvernement-paul-kaba-thieba-la-liste-des-membres/).
- **W2** — [Décret n° 2017-075 hébergé par le ministère des Affaires étrangères](https://www.mae.gov.bf/fileadmin/user_upload/storages/fichier/decret_remaniement2.pdf).
- **W3** — [Composition issue du remaniement du 31 janvier 2018](https://lefaso.net/?id_article=81741&page=impression).
- **W4** — [Décret n° 2021-1297 : gouvernement Zerbo](https://www.sidwaya.info/wp-content/uploads/2021/12/Album-gourvernement-Lassina-Zerbo.pdf).
- **W5** — [Présidence du Faso : équipe formée le 5 mars 2022](https://www.presidencedufaso.bf/rentree-gouvernementale-le-president-du-faso-appelle-a-lintegrite-et-a-la-loyaute-dans-la-conduite-des-affaires-de-letat/).
- **W6** — [Présidence du Faso : gouvernement issu du remaniement du 17 décembre 2023](https://www.presidencedufaso.bf/composition-du-gouvernement/).
- **W7** — [SIG : référence au décret n° 2024-0908 du 1er août 2024](https://www.sig.gov.bf/fileadmin/user_upload/CONSEIL_DES_MINISTRES_N__034_DU_23_OCTOBRE_2024.pdf).
- **W8** — [Décret n° 2024-1566 du 8 décembre 2024](https://www.aib.media/wp-content/uploads/2024/12/Gouvernement-Emmanuel-Ouedraogo-.pdf).
- **W9** — [RTB : confirmation officielle du retour de « Désenclavement » en 2025](https://www.rtb.bf/2025/03/12/compte-rendu-du-conseil-des-ministres-du-12-mars-2025/).
