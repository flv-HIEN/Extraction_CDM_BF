# Alias d'intitulés ministériels

`alias_ministeres.csv` est distinct de la table historique. Une ligne relie une variante complète à un intitulé de cette table. `fusion_denominations.py` applique ces alias avant la concordance. Casse, accents, apostrophes, ponctuation et espaces sont neutralisés pour comparer les titres ; aucun rapprochement flou n'est appliqué.

Seules les lignes de statut `verifie`, avec justification et référence documentaire, sont utilisées. Ces références identifient le compte rendu où la variante est observée ; elles ne constituent pas une nouvelle validation des attributions gouvernementales. Les trois alias initiaux concernent Aménangements/Aménagements, entreprenariat/entrepreneuriat et secondaires/secondaire. Ils ne créent pas de nouveaux rattachements institutionnels.

Une cible inconnue ou deux corrections contradictoires provoquent une erreur. Après modification du CSV, relancer le traitement dans un nouveau processus pour recharger les alias. Les colonnes `alias_ministere_applique` et `reference_alias_ministere` tracent les corrections. Une décision manuellement validée dans le dictionnaire reste prioritaire.

Retest de développement : 516 occurrences document/nom conservées ; 25 libellés après extraction corrigée et fusion, dont 7 titres historiques (39 lignes) conservés en attente d'examen des conventions. Les 13 lignes sans ministère correspondent à des institutions. Aucun intitulé ne reste non répertorié dans ce lot. Cela ne garantit pas la résolution des titres du reste du corpus.

Les sept cas sont dans `normalisation/fiabilisation_test_developpement_12_alias/correspondances_a_examiner.csv`. Il faut distinguer les vrais renommages des portefeuilles composites (sécurité, cohésion sociale, environnement, eau, transports, enseignement supérieur) : un simple alias ne permet pas d'attribuer un ministère composite à un ministère actuel unique. La table historique n'a pas été modifiée par cet ajout.
