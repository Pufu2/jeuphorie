---
titre: Mentions légales
url: /mentions-legales/
description: "Mentions légales du site Jeuphorie : éditeur, hébergeur, plateforme de vente, propriété intellectuelle."
---

{% if not site.boutique.ventes_actives %}
> **Site en préparation.** Aucune vente n'est réalisée sur ce site pour le moment. La boutique ouvrira après l'immatriculation de l'entreprise de l'éditeur.
{% endif %}

## Éditeur du site

{% if site.editeur_ok %}
Le site {{ site.url | replace('https://', '') }} est édité par :

- **Nom :** {{ site.editeur.nom }}
- **Statut :** {{ site.editeur.statut }}
- **Adresse :** {{ site.editeur.adresse }}
- **SIREN :** {{ site.editeur.siren }}
- **TVA :** {{ site.editeur.tva }}
- **Contact :** {{ site.email }}

**Directeur de la publication :** {{ site.editeur.nom }}.
{% else %}
Le site {{ site.url | replace('https://', '') }} est édité à titre non professionnel par Rafaël, créateur de Jeuphorie, joignable à {{ site.email }}. Conformément à l'article 6, III, 2 de la loi n° 2004-575 du 21 juin 2004, ses coordonnées ont été communiquées à l'hébergeur. Elles figureront ici à l'ouverture de la boutique.

**Directeur de la publication :** Rafaël, créateur de Jeuphorie.
{% endif %}

## Hébergeur

Le site est hébergé par :

- **{{ site.hebergeur.nom }}**
- {{ site.hebergeur.adresse }}
- Téléphone : {{ site.hebergeur.telephone }}
- Site : {{ site.hebergeur.site }}

## Plateforme de vente

Les paiements sont traités par **{{ site.plateforme_vente.nom }}**, {{ site.plateforme_vente.adresse }} ({{ site.plateforme_vente.site }}). L'éditeur du site n'a jamais accès à vos données bancaires.

## Propriété intellectuelle

Les textes, jeux, règles, mises en page et illustrations de ce site et des kits sont la propriété de l'éditeur, sauf mention contraire. Les illustrations réalisées par des tiers sont utilisées sous licence commerciale ; leurs auteurs sont crédités ci-dessous.

Toute reproduction ou diffusion, même partielle, sans autorisation écrite est interdite. L'usage des kits achetés est précisé dans les [conditions de vente](/conditions-de-vente/).

**Crédits des illustrations :** les illustrations du site et des kits sont créées pour Jeuphorie. Si une illustration sous licence est un jour utilisée, son auteur et sa licence seront indiqués ici.

## Données personnelles et cookies

Ce site ne dépose aucun cookie de mesure d'audience ni de publicité. Le traitement de vos données est décrit dans la page [confidentialité](/confidentialite/).

## Signaler un contenu

Pour signaler un contenu qui vous semble illicite, écrivez à {{ site.email }} en indiquant la page concernée et la raison de votre signalement.
