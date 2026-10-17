# Le référencement de Jeuphorie

Ce document explique comment le site est construit pour être bien placé sur Google, et ce qui reste à faire.

## La stratégie en une phrase

Répondre mieux que les autres aux recherches précises des parents, des associations et des animateurs (« jeux d'anniversaire 6 ans à la maison », « organiser une kermesse d'école », « jeux de Noël en famille », « grand jeu centre de loisirs »), avec des pages utiles même sans rien acheter, qui renvoient naturellement vers le kit correspondant.

## Les quatre piliers

### 1. Des pages qui correspondent chacune à une recherche

| Type de page | Exemple | Recherches visées |
|---|---|---|
| Univers | /anniversaires/, /kermesse/ | « jeux d'anniversaire enfant à imprimer », « kermesse école clé en main » |
| Fête | /fetes/noel/ | « jeux de Noël enfants », « activités Toussaint centre de loisirs » |
| Produit | /boutique/kit-noel/ | « kit animation Noël à imprimer », « jeux arbre de Noël CSE » |
| Jeu offert | /fetes/paques/chasse-aux-oeufs-des-couleurs/ | « organiser une chasse aux œufs », « chasse aux œufs plusieurs âges » |
| Grand jeu offert | /jeux/poules-renards-viperes/ | « jeu des poules renards vipères », « règle gendarmes et voleurs » |
| Catalogue | /jeux/ | « grands jeux collectifs enfants », « jeux de cour par âge » |
| Article | /blog/... | Questions précises : « que faire à un anniversaire de 4 ans », « jeux quand il pleut » |

Les 3 grands jeux offerts et les 8 jeux de fêtes, publiés en entier, sont la « longue traîne » : chacun vise une recherche peu concurrentielle mais très ciblée (le nom d'un jeu, une règle). Les 31 autres grands jeux ne sont présentés que dans le catalogue (âge, joueurs, durée) : une page sans les règles décevrait les visiteurs venus de Google, et les règles restent réservées aux fiches vendues.

### 2. Le blog, un article par semaine

Chaque article répond à une vraie question, avec un contenu concret (déroulé, règles, matériel, astuces d'animateur) et renvoie vers une page d'univers, de fête ou de produit. Les articles sont écrits à l'avance et datés : le site se refabrique chaque matin et publie ceux dont la date est arrivée. Les règles de rédaction sont dans `docs/ECRIRE-UN-ARTICLE.md`.

Le calendrier suit les saisons, avec 4 à 6 semaines d'avance sur les recherches :

| Mois de publication | Sujets |
|---|---|
| Septembre, octobre | Toussaint et automne, anniversaires de rentrée, jeux d'intérieur |
| Novembre, décembre | Noël en famille, arbre de Noël du CSE, jeux coopératifs |
| Janvier, février | Carnaval, jeux calmes, galette des rois, anniversaires d'hiver |
| Mars, avril | Pâques et chasse aux œufs, grands jeux de printemps |
| Mai, juin | Kermesse et fête d'école, olympiades, jeux d'eau |
| Juillet, août | Grands jeux d'été, colonies, anniversaires au jardin |

### 3. La technique (déjà en place)

- Site statique, très rapide, sans publicité ni traceur.
- Une adresse canonique par page, un plan du site (`/sitemap.xml`) et un `robots.txt` créés à chaque publication.
- Les anciennes adresses redirigent vers les nouvelles (liste `REDIRECTIONS` dans `build.py`).
- Données structurées : organisation et site (accueil), fil d'Ariane (toutes les pages), article (blog), fiche « HowTo » (jeux), produit avec prix (quand le kit est en vente).
- Une image de partage par produit (1200 × 630) pour les réseaux sociaux, une image par défaut pour le reste du site.
- Des textes alternatifs sur les images, des dimensions déclarées, le chargement différé des images.
- Des titres de page qui reprennent la recherche visée, et des descriptions de 150 caractères environ.

### 4. La notoriété (liens et partages)

Google fait davantage confiance à un site cité par d'autres. Les pistes les plus efficaces pour Jeuphorie, par ordre de priorité :

1. **Pinterest.** C'est le premier moteur de recherche pour les activités d'enfants à imprimer. Créer un compte professionnel gratuit, puis épingler les images de partage des produits et des articles (`statique/img/kits/*-partage.jpg`), avec un lien vers la page. Une épingle par article et par kit.
2. **Les associations de parents d'élèves.** Proposer le jeu offert de la kermesse ou les 3 grands jeux offerts aux fédérations locales et aux groupes d'associations : un lien depuis leur site ou leur lettre d'information vaut beaucoup.
3. **Les réseaux d'animation.** Groupes d'animateurs et de directeurs (forums, groupes Facebook, réseaux de formation BAFA et BAFD) : partager les jeux offerts et les articles utiles, jamais de publicité directe.
4. **Les annuaires et sites de ressources éducatives** qui acceptent les ressources gratuites.

## Ce qu'il reste à faire (une seule fois)

1. **Google Search Console** (gratuit) : aller sur search.google.com/search-console, ajouter la propriété `jeuphorie.fr`. La vérification la plus simple pour un domaine OVHcloud est l'enregistrement DNS TXT (OVHcloud > Domaine > Zone DNS > Ajouter une entrée TXT). Sinon, choisir « balise HTML », copier la valeur `content` et la coller dans `config.yml` à la ligne `google_site_verification`.
2. Dans Search Console, envoyer le plan du site : `https://jeuphorie.fr/sitemap.xml`.
3. **Bing Webmaster Tools** (gratuit, alimente aussi Qwant et DuckDuckGo) : importer le site depuis Search Console en un clic, ou coller le code dans `bing_site_verification`.
4. Un mois plus tard, regarder dans Search Console les recherches qui amènent des visiteurs : ce sont les meilleurs sujets pour les prochains articles.

## Les règles à garder

- Une page = une recherche principale. Ne pas créer deux pages qui visent la même chose.
- Jamais de texte écrit pour les robots : chaque phrase doit servir le lecteur.
- Jamais de règles complètes des jeux payants sur le site : on montre ce qui donne envie et aide à choisir.
- Mettre à jour les dates (vacances, saisons) chaque année dans `donnees/saisons.yml`.
