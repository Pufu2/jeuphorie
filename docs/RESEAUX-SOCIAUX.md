# Les réseaux sociaux de Jeuphorie

> **Instagram** : le premier compte (jeuphorie_) a été désactivé par Instagram le 23 octobre 2026. Le nouveau compte `_jeuphorie_` est relié à la page depuis le même jour (`instagram_id` dans `config.yml`). Le lien de sa bio : `https://jeuphorie.fr/reseaux/`.

Tout est automatique. Chaque matin, le site choisit un sujet (le nouvel article du blog s'il en paraît un, sinon un jeu offert, une page d'univers et, quand les ventes seront ouvertes, un kit), en suivant les saisons. Il fabrique le visuel et la légende à partir des textes du site, puis :

- **Pinterest** : une épingle par jour, rangée dans le tableau de son thème (voir plus bas), avec un titre et une description écrits avec les mots que les gens cherchent ;
- **Facebook et Instagram** : une publication le mardi et le jeudi vers 12 h 15, le samedi vers 9 h 45, chacune reprise en Story Instagram ; un Reel le dimanche vers 19 h 30, lui aussi repris en Story. Les heures sont dans `.github/workflows/reseaux.yml` ;
- **la page `https://jeuphorie.fr/reseaux/`** : les dernières publications, à mettre en lien dans la bio Instagram.

Le calendrier se nourrit des articles écrits chaque mois par la tâche automatique : vous n'avez rien à écrire. Pour voir les trois prochaines semaines : `python3 outils/reseaux.py`.

Il reste trois réglages à faire **une seule fois**. Aucun mot de passe ni aucune clé ne doit être envoyé dans une conversation : les codes de vérification de Pinterest et de Google ne sont pas secrets (ils sont publiés dans les pages du site), mais les jetons Facebook, eux, se collent uniquement dans les secrets de GitHub.

## 1. Pinterest (10 minutes, le plus utile) · réglé le 20 octobre 2026

Pinterest est le premier moteur de recherche des parents et des animateurs qui cherchent des activités à imprimer.

1. Créer un compte **professionnel** gratuit sur pinterest.fr (« Créer un compte professionnel »), au nom de Jeuphorie.
2. Créer un tableau, par exemple « Jeux et animations pour enfants ».
3. **Revendiquer le site** : Paramètres > Comptes revendiqués > Sites web > `jeuphorie.fr` > « Ajouter une balise HTML ». Copier le code qui suit `content="…"` et le coller dans `config.yml` à la ligne `pinterest_site_verification` (ou me l'envoyer). Après la publication du site, cliquer sur « Vérifier ».
4. **Publication automatique** : Paramètres > Créer des épingles en masse > Publier automatiquement > ajouter le flux `https://jeuphorie.fr/flux/pinterest.xml` et choisir le tableau.

C'est fini : Pinterest lit le flux tout seul et crée les nouvelles épingles.

## 2. Facebook et Instagram (20 minutes)

1. Créer une **page Facebook** « Jeuphorie » depuis votre compte (Pages > Créer une page). Mettre `https://jeuphorie.fr/` dans la section « Site web ».
2. Créer un compte **Instagram professionnel** « jeuphorie » et le **relier à la page** (Paramètres de la page > Comptes liés > Instagram). Mettre `https://jeuphorie.fr/reseaux/` comme lien de la bio.
3. Sur developers.facebook.com, créer une application de type « Entreprise » (aucune validation de Meta n'est nécessaire pour publier sur vos propres comptes). Lui ajouter les produits « Facebook Login for Business » et « Instagram ».
4. Dans l'**explorateur de l'API Graph** (Outils > Explorateur de l'API Graph), choisir l'application, cocher les autorisations `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`, puis « Générer un jeton d'accès » et accepter.
5. Transformer ce jeton en **jeton de longue durée** (Outils > Débogueur de jeton d'accès > « Prolonger le jeton d'accès »). Le copier.
6. Dans l'explorateur, coller ce jeton et lancer la requête `me/accounts` : la réponse donne l'`id` de la page et son `access_token`. Ce jeton de page, obtenu à partir d'un jeton de longue durée, **n'expire pas**.
7. Lancer la requête `<id de la page>?fields=instagram_business_account` : la réponse donne l'identifiant Instagram.
8. Sur GitHub, dépôt `Pufu2/jeuphorie` > Settings > Secrets and variables > Actions, créer le secret `META_PAGE_TOKEN` avec le jeton de la page (uniquement la suite qui commence par `EAA`, sans guillemets). Les identifiants de la page et du compte Instagram, qui ne sont pas secrets, sont déjà dans `config.yml` (`meta_page_id`, `instagram_id`).

**État : réglé le 20 octobre 2026.** Une publication d'essai est partie sur Facebook et sur Instagram. Pour publier à la demande : onglet Actions > « Publier le site » > « Run workflow », en cochant « Publier aussi le sujet du jour sur Facebook et Instagram ».

Dès le prochain mardi, jeudi ou samedi, la publication part toute seule. Si un jour le jeton est révoqué (changement de mot de passe Facebook, par exemple), GitHub vous envoie un e-mail « Run failed » : il suffit de refaire les étapes 4 à 8.

## Le ton des publications (réglé le 25 octobre 2026)

- **Mardi et jeudi** : le sujet du jour (jeu, article, page du site), avec une phrase d'introduction et une question de fin qui changent d'une publication à l'autre, et, pour les jeux de fêtes, une astuce d'adaptation à l'âge. Les phrases sont dans `INTROS` et `QUESTIONS` (outils/reseaux.py).
- **Samedi** : un message de Rafaël, sans rien à vendre : présentation, conseil d'animateur ou question aux abonnés. Douze messages, un par samedi à partir du 31 octobre 2026, dans `donnees/messages-reseaux.yml`. Une fois la liste épuisée (après le 16 janvier 2027), le samedi reprend le sujet du jour normal ; il suffit d'ajouter des messages à la fin du fichier pour continuer.
- **Les visuels** changent de composition d'une publication à l'autre (classique, bandeau de couleur, fiche posée sur un fond, pastille « Gratuit », grands guillemets pour les messages du samedi), en gardant la guirlande de fanions, les polices et la signature du site. Voir `MISES` et `mise_en_page()` (outils/reseaux.py).
- **Les Reels** ont une musique de fond composée pour chacun par `outils/musique.py` : marimba en automne, clochettes et grelots en hiver, guitare et frappes de mains au printemps et en été. Comme elle est fabriquée note par note, il n'y a aucun droit d'auteur, et Instagram ne peut pas couper le son.
- **Pinterest** ne change pas : les épingles restent des fiches pratiques, c'est ce qui y marche.
- Jamais d'anecdote inventée : les messages restent vrais quelle que soit la semaine.
- **Le plus important reste à faire à la main : répondre aux commentaires**, surtout le samedi, puisque chaque message pose une question.

## Les tableaux Pinterest

Chaque thème a son tableau, nourri par son propre flux (réglé le 21 octobre 2026). À ajouter une fois dans Pinterest : Paramètres > Créer des épingles en masse > Publier automatiquement > « Ajouter un flux RSS », en créant le tableau au passage.

| Tableau | Flux |
|---|---|
| Jeux et activités de Noël pour enfants | `https://jeuphorie.fr/flux/pinterest-noel.xml` |
| Activités d'automne et de la Toussaint | `https://jeuphorie.fr/flux/pinterest-automne.xml` |
| Anniversaire enfant : jeux et idées | `https://jeuphorie.fr/flux/pinterest-anniversaires.xml` |
| Grands jeux et jeux collectifs | `https://jeuphorie.fr/flux/pinterest-grands-jeux.xml` |
| Animateurs : BAFA, BAFD, accueil de loisirs | `https://jeuphorie.fr/flux/pinterest-animateurs.xml` |

Le premier flux, `https://jeuphorie.fr/flux/pinterest.xml`, reste relié au tableau « Jeux et animations pour enfants » : il reçoit les autres sujets (carnaval, Pâques, kermesse, fêtes de l'année). Les thèmes et les tableaux sont dans `TABLEAUX` (outils/reseaux.py).

## 3. Ce qui n'est pas automatisé, volontairement

- **Les groupes Facebook d'animateurs et de parents** : Facebook ne permet plus d'y publier par un programme, et les publicités déguisées y sont mal vues. Partager à la main, de temps en temps, un jeu offert ou un article utile reste le moyen le plus efficace de se faire connaître.
- **Les publicités payantes** : le choix actuel est 100 % gratuit.
- **TikTok, YouTube, LinkedIn** : ils demandent des vidéos ou une validation longue de Meta et LinkedIn. À envisager plus tard.

## Changer le rythme ou les sujets

- Jours Facebook et Instagram : `JOURS_META` dans `outils/reseaux.py`.
- Mots-clés (hashtags) : `MOTS_CLES` dans le même fichier.
- Les sujets viennent du site : un nouvel article, un nouveau jeu offert ou un nouveau kit entre tout seul dans le calendrier. Les kits n'apparaissent qu'une fois les ventes ouvertes (`ventes_actives: true`).
