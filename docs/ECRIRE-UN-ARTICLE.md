# Écrire et publier un article du carnet d'idées

Ce guide sert à la personne ou à la tâche automatique qui écrit l'article de la semaine.

## Où mettre l'article

Un fichier par article dans `contenu/blog/`, nommé `AAAA-MM-JJ-mots-cles.md`.
Exemple : `contenu/blog/2026-10-20-jeux-halloween-6-8-ans.md`.

La partie après la date devient l'adresse : `/blog/jeux-halloween-6-8-ans/`.
Elle reprend la recherche visée, en minuscules, sans accents, avec des tirets.

## L'entête obligatoire

```yaml
---
titre: "Jeux d'Halloween pour les 6-8 ans : 7 idées qui font frissonner sans faire peur"
description: "150 caractères au plus, avec la recherche visée, qui donnent envie de cliquer depuis Google."
chapo: "Deux ou trois phrases d'introduction, affichées en grand sous le titre."
date: 2026-10-20
ages: [6-8-ans]
fetes: [halloween]
univers: [anniversaires]
kit: olympiades-anniversaire
---
```

- `date` : un article dont la date est dans le futur reste caché ; il apparaît tout seul le matin de sa date (le site se refabrique chaque jour).
- `ages` : parmi `3-5-ans`, `6-8-ans`, `9-12-ans` (voir `donnees/idees.yml`).
- `fetes` : parmi `halloween`, `noel`, `carnaval`, `paques`, `fete-de-fin-d-annee`.
- `univers` : parmi `anniversaires`, `grands-jeux`, `kermesse`, `pro`.
- `kit` : l'identifiant d'un kit de `donnees/kits.yml`, ou rien. La fiche du kit s'affiche à la fin de l'article.
- `brouillon: true` : l'article n'est pas publié.
- Mettre entre guillemets toute valeur qui contient « : ».

## Les règles de rédaction

- On vouvoie le lecteur, sur un ton chaleureux. Phrases courtes et concrètes.
- 800 à 1 300 mots. Un titre qui reprend la recherche des parents.
- Des intertitres `##` qui répondent aux questions qu'ils se posent : durée, nombre d'enfants, matériel, âge, erreurs à éviter.
- Au moins un élément concret de directeur d'animation : déroulé minuté, règle en une phrase, matériel de la maison, adaptation par âge.
- Lien vers une page du site quand c'est utile, par exemple `[nos idées pour les 6-8 ans](/idees/6-8-ans/)`.
- Une seule fin commerciale, discrète : le dernier paragraphe peut présenter le kit associé.
- Jamais de nom, logo, photo ou document de la structure où travaille l'auteur. Jamais de photo d'enfant.
- Pas de copie d'autres sites. Les idées classiques (chasse au trésor, course en sac) sont réécrites avec nos propres règles.
- Fêtes (Halloween, Noël, Pâques…) : l'article donne des conseils et des jeux du catalogue à habiller. Il n'annonce jamais de kit ou de jeu à thème qui n'existe pas.
- Sécurité : préciser la surveillance d'un adulte pour l'eau, les yeux bandés, les objets à lancer.

## Publier

Ajouter le fichier sur la branche `main` du dépôt : le site se refabrique et se publie en deux minutes environ (onglet **Actions** sur GitHub pour suivre).
