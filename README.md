# Jeuphorie

Site de la boutique Jeuphorie, « Jeux et animations clés en main ».

Le site est fait de simples fichiers HTML fabriqués par `build.py`. Il peut être hébergé gratuitement sur GitHub Pages, ou chez n'importe quel hébergeur : il suffit d'y copier le contenu du dossier `_site/`.

## Ce qu'on modifie le plus souvent

| Pour… | Modifier |
|---|---|
| Ouvrir les ventes, l'adresse de contact, les informations légales | `config.yml` |
| Ajouter ou mettre en vente un kit | `donnees/kits.yml` |
| Écrire un article | `contenu/blog/` (voir `docs/ECRIRE-UN-ARTICLE.md`) |
| Les textes des pages À propos et légales | `contenu/pages/` |
| Les idées par âge et par fête | `donnees/idees.yml` |
| Les couleurs et la mise en page | `statique/css/site.css` |

Dans les pages légales, tout ce qui est écrit `[[ainsi]]` apparaît surligné en jaune : ce sont les informations à compléter.

## Mettre un kit en vente

1. Créer le produit sur Payhip et noter son code (la fin de son adresse, par exemple `https://payhip.com/b/AbC12` → `AbC12`).
2. Dans `donnees/kits.yml`, pour ce kit : `etat: en_vente` et `payhip_id: "AbC12"`.
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

Les fichiers PDF des kits vendus : ils sont uniquement sur Payhip. Le dépôt est public.
