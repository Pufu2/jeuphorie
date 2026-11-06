# Les jeux offerts et les pages « Trouver un jeu »

## Ce qui existe

- `donnees/jeux-offerts.yml` : les jeux offerts hors fêtes, règles complètes, une page chacun (`/jeux-offerts/<id>/`).
- `donnees/jeux-fetes.yml` : les jeux offerts des fêtes (tâche du 20 du mois).
- `donnees/reperes-jeux.yml` : les repères (lieux, moments, énergie, matériel) des grands jeux et des jeux de fêtes.
- `donnees/trouver.yml` : les pages « Trouver un jeu » (`/trouver-un-jeu/<slug>/`) et les onglets du bas de page.
  Une page n'est publiée que si au moins 5 jeux lui correspondent : elle apparaît seule quand les jeux arrivent.

## La tâche automatique (chaque lundi) : deux nouveaux jeux offerts

1. Lire les jeux déjà présents : `donnees/jeux-offerts.yml`, `donnees/jeux-fetes.yml`, `donnees/jeux.yml`, les articles
   du blog, et la liste des jeux des kits payants (les noms des fiches, épreuves et ateliers dans les fichiers YAML de
   `jeuphorie-produits`). Un nouveau jeu ne doit reprendre **ni le nom ni le principe** d'un jeu déjà présent, et
   jamais un jeu d'un kit payant.
2. Choisir deux jeux qui comblent les manques : les pages de `trouver.yml` qui ont le moins de jeux, et les lieux,
   moments ou âges peu couverts (petits de 3-5 ans, intérieur calme, voiture, plage, forêt, jeux à deux, veillée…).
   Jeux traditionnels ou classiques de l'animation, décrits avec nos propres mots, ou jeux originaux.
3. Les écrire dans `donnees/jeux-offerts.yml`, au même format et au même niveau que les jeux existants :
   accroche, âges, joueurs, durée, repères (lieux, moments, energie, materiel_tags), but, matériel, une ou deux
   versions (lieu, espace, mise en place, déroulement), règles, adaptations par âge, sécurité quand il le faut, fin.
   `ajoute` : le mardi pour le premier jeu, le jeudi pour le second (le jeu reste caché jusque-là).
4. Une fois par mois au plus : si un nouveau croisement utile atteint 5 jeux (par exemple « jeux de plage pour les
   3-5 ans »), ajouter sa page dans `trouver.yml`, avec un texte propre (introduction, trois conseils, trois questions
   fréquentes), jamais un texte recopié d'une autre page en changeant un mot.
5. `python3 build.py --apercu` sans erreur, puis commit « Jeux offerts : <nom 1> et <nom 2> » (auteur Pufu2) et push.

## Les règles

- Vouvoiement, phrases simples, consignes concrètes, sécurité réelle. Pas de conseil médical.
- Fêtes chrétiennes bienvenues, jamais d'Halloween ; aucun personnage, marque ou musique sous droits.
- Personne n'est éliminé longtemps : un joueur sorti revient vite ou prend un autre rôle.
- Aucun jeu dangereux (strangulation, apnée, défis risqués, jeux d'évanouissement), aucun jeu humiliant.
