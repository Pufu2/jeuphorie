# Écrire et publier un article du blog

Ce guide sert à la personne ou à la tâche automatique qui écrit l'article de la semaine.

## Où mettre l'article

Un fichier par article dans `contenu/blog/`, nommé `AAAA-MM-JJ-mots-cles.md`.
Exemple : `contenu/blog/2026-10-20-jeux-automne-centre-de-loisirs.md`.

La partie après la date devient l'adresse : `/blog/jeux-automne-centre-de-loisirs/`.
Elle reprend la recherche visée, en minuscules, sans accents, avec des tirets.

## L'entête obligatoire

```yaml
---
titre: "Jeux d'automne en centre de loisirs : 7 idées pour les vacances de la Toussaint"
description: "150 caractères au plus, avec la recherche visée, qui donnent envie de cliquer depuis Google."
chapo: "Deux ou trois phrases d'introduction, affichées en grand sous le titre."
date: 2026-10-20
ages: [6-8-ans]
fetes: [toussaint]
univers: [anniversaires]
kit: defi-des-champions
---
```

- `date` : un article dont la date est dans le futur reste caché ; il apparaît tout seul le matin de sa date (le site se refabrique chaque jour).
- `ages` : parmi `3-5-ans`, `6-8-ans`, `9-12-ans`, `13-17-ans` (sert au classement, sans page dédiée).
- `fetes` : parmi `toussaint`, `noel`, `carnaval`, `paques` (voir `donnees/fetes.yml`). L'article apparaît sur la page de la fête.
- `univers` : parmi `anniversaires`, `grands-jeux`, `fetes`, `kermesse`, `professionnels`. L'article apparaît sur la page de l'univers.
- `kit` : l'identifiant d'un kit de `donnees/kits.yml`, ou rien. La fiche du kit s'affiche à la fin de l'article.
- `brouillon: true` : l'article n'est pas publié.
- Mettre entre guillemets toute valeur qui contient « : ».

## Les règles de rédaction

- On vouvoie le lecteur, sur un ton chaleureux. Phrases courtes et concrètes.
- 800 à 1 300 mots. Un titre qui reprend la recherche des parents.
- Des intertitres `##` qui répondent aux questions qu'ils se posent : durée, nombre d'enfants, matériel, âge, erreurs à éviter.
- Au moins un élément concret de directeur d'animation : déroulé minuté, règle en une phrase, matériel de la maison, adaptation par âge.
- Lien vers une page du site quand c'est utile, par exemple `[nos jeux de Noël](/fetes/noel/)` ou `[le kit du défi des champions](/boutique/defi-des-champions/)`.
- Une seule fin commerciale, discrète : le dernier paragraphe peut présenter le kit associé.
- Jamais de nom, logo, photo ou document de la structure où travaille l'auteur. Jamais de photo d'enfant.
- Pas de copie d'autres sites. Les idées classiques (chasse au trésor, course en sac) sont réécrites avec nos propres règles.
- Fêtes (Toussaint, Noël, carnaval, Pâques) : l'article renvoie vers la page de la fête et son kit. Il n'annonce jamais un kit qui n'existe pas encore (voir `donnees/kits.yml`).
- Sécurité : préciser la surveillance d'un adulte pour l'eau, les yeux bandés, les objets à lancer.

## Publier

Ajouter le fichier sur la branche `main` du dépôt : le site se refabrique et se publie en deux minutes environ (onglet **Actions** sur GitHub pour suivre).

## La tâche automatique (une fois par mois)

Une tâche planifiée de Claude Code se lance le 20 de chaque mois et suit exactement cette procédure. Vous n'avez rien à faire. Pour changer le rythme ou les sujets, modifiez cette section : la tâche la relit à chaque fois.

1. Lister les articles de `contenu/blog/` et repérer le dernier mardi déjà couvert.
2. Écrire un article pour chaque mardi suivant, jusqu'au dernier mardi du mois prochain (en général 4 ou 5 articles).
3. Choisir les sujets dans le calendrier de `docs/REFERENCEMENT.md` (4 à 6 semaines d'avance sur la saison), sans reprendre un sujet déjà traité : chaque article vise une recherche différente.
4. Varier les publics d'un mois à l'autre : parents (anniversaires, fêtes en famille), écoles et associations (kermesse, carnaval, fêtes d'école), animateurs et directeurs (grands jeux, organisation, Jeuphorie Pro).
5. Relier chaque article à un kit existant de `donnees/kits.yml` (champ `kit`) quand le sujet s'y prête, et à des pages existantes du site (jeux offerts, fêtes, univers).
6. Ne jamais publier les règles complètes d'un jeu vendu dans un kit, ni annoncer un kit, un dossier Pro ou un jeu qui n'existe pas, ni parler de codes de réduction.
7. Lancer `python3 build.py --apercu` pour vérifier qu'il n'y a pas d'erreur.
8. Enregistrer avec l'auteur `Pufu2 <Pufu2@users.noreply.github.com>` et envoyer sur `main`. Rien d'autre n'est modifié dans le dépôt.
