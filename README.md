# Jeuphorie

Site de la boutique Jeuphorie, « Jeux et animations clés en main ».

Le site est fait de simples fichiers HTML fabriqués par `build.py`. Il peut être hébergé gratuitement sur GitHub Pages, ou chez n'importe quel hébergeur : il suffit d'y copier le contenu du dossier `_site/`.

## Ce qu'on modifie le plus souvent

| Pour… | Modifier |
|---|---|
| Ouvrir les ventes (pas à pas : `docs/OUVRIR-LES-VENTES.md`), l'adresse de contact, les informations légales | `config.yml` |
| Ajouter ou mettre en vente un produit (chaque produit a sa page /boutique/<id>/) | `donnees/kits.yml` |
| Les formules d'abonnement | `donnees/abonnement.yml` |
| La partie publique des jeux | `donnees/jeux.yml` (exportée depuis le dossier privé des produits) |
| Écrire un article | `contenu/blog/` (voir `docs/ECRIRE-UN-ARTICLE.md`) |
| Les textes des pages Qui suis-je et légales | `contenu/pages/` |
| Les fêtes de l'année (Toussaint, Noël, carnaval, Pâques) | `donnees/fetes.yml` |
| La mise en avant « En ce moment » de l'accueil, selon le mois | `donnees/saisons.yml` |
| Les univers (menu, couleurs, textes d'en-tête) | `donnees/univers.yml` |
| Les jeux de fêtes offerts (Toussaint, Noël…), publiés en entier | `donnees/jeux-fetes.yml` (schémas dans `outils/schemas_fetes.py`) |
| Les couleurs et la mise en page | `statique/css/site.css` |
| Les dossiers du mois déjà prêts, montrés sur la page Pro | `donnees/abonnement.yml` (`dossiers_prets`, vignettes dans `statique/img/pro/`) |
| Le référencement Google (stratégie et étapes) | `docs/REFERENCEMENT.md` |

Dans les pages légales, tout ce qui est écrit `[[ainsi]]` apparaît surligné en jaune : ce sont les informations à compléter.

## Les images des produits

La couverture, les aperçus et l'image de partage de chaque produit sont dans `statique/img/kits/`. Ils sont exportés depuis le dossier privé des produits par `exporter_images.py`. Les aperçus sont en basse résolution : le texte des fiches y est illisible.

## Les anciennes adresses

Quand une page change d'adresse, ajoutez la correspondance dans `REDIRECTIONS`, en haut de `build.py` : une page de redirection est créée toute seule.

## Mettre un kit en vente

1. Créer le lien de paiement Stripe du produit (Claude le fait par l'accès programmable de Stripe, voir `docs/OUVRIR-LES-VENTES.md`).
2. Dans `donnees/kits.yml`, pour ce kit : `etat: en_vente` et `paiement: "https://buy.stripe.com/..."`.
3. Dans `config.yml` : `ventes_actives: true` (une seule fois, après la déclaration de la micro-entreprise).

## Fabriquer le site sur un ordinateur

```
pip install -r requirements.txt
python3 build.py            # version en ligne, dans _site/
python3 build.py --apercu   # version à ouvrir directement, sans serveur
```

## Publication automatique

À chaque modification envoyée sur la branche `main`, et chaque matin, GitHub refabrique et publie le site (`.github/workflows/publier.yml`). Les polices sont copiées sur le site lui-même pendant la fabrication : aucune requête n'est faite à Google.

## Adresse du site

Dans `config.yml` :

- `url` : l'adresse complète du site, par exemple `https://jeuphorie.fr`, ou `https://compte.github.io/jeuphorie` avant l'achat du domaine ;
- `chemin_de_base` : `"/jeuphorie"` si le site est dans un sous-dossier de github.io, sinon vide ;
- `nom_de_domaine` : `jeuphorie.fr` une fois le domaine relié (le fichier CNAME est alors créé tout seul).

## Ce qui ne va jamais dans ce dépôt

Le dépôt est public. Les PDF vendus et les règles complètes des jeux payants restent dans le dépôt GitHub privé `jeuphorie-produits` et dans votre dossier privé des grands jeux (avec `jeux.yml` et `fabriquer.py`). Seule la partie publique des jeux (but, âge, matériel, mise en place) est copiée ici par `exporter_site.py`.
