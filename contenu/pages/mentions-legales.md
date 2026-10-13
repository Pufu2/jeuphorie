---
titre: Mentions légales
url: /mentions-legales/
description: "Mentions légales du site Jeuphorie : éditeur, hébergeur, plateforme de vente, propriété intellectuelle."
---

{% if not site.boutique.ventes_actives %}
> **Site en préparation.** Aucune vente n'est réalisée sur ce site pour le moment. La boutique ouvrira après l'immatriculation de l'entreprise de l'éditeur.
{% endif %}

## Éditeur du site

Le site {{ site.url | replace('https://', '') }} est édité par :

- **Nom :** {{ site.editeur.nom }}
- **Statut :** {{ site.editeur.statut }}
- **Adresse :** {{ site.editeur.adresse }}
- **SIREN :** {{ site.editeur.siren }}
- **TVA :** {{ site.editeur.tva }}
- **Contact :** {{ site.email }}

**Directeur de la publication :** {{ site.editeur.nom }}.

## Hébergeur

Le site est hébergé par :

- **{{ site.hebergeur.nom }}**
- {{ site.hebergeur.adresse }}
- Téléphone : {{ site.hebergeur.telephone }}
- Site : {{ site.hebergeur.site }}

## Plateforme de vente

Les ventes et les téléchargements sont gérés par **{{ site.plateforme_vente.nom }}**, {{ site.plateforme_vente.adresse }} ({{ site.plateforme_vente.site }}). Le paiement est traité par Payhip et ses prestataires de paiement : l'éditeur du site n'a jamais accès à vos données bancaires.

## Propriété intellectuelle

Les textes, jeux, règles, mises en page et illustrations de ce site et des kits sont la propriété de l'éditeur, sauf mention contraire. Les illustrations réalisées par des tiers sont utilisées sous licence commerciale ; leurs auteurs sont crédités ci-dessous.

Toute reproduction ou diffusion, même partielle, sans autorisation écrite est interdite. L'usage des kits achetés est précisé dans les [conditions de vente](/conditions-de-vente/).

**Crédits des illustrations :** [[à compléter à chaque illustration sous licence : auteur, source, licence]]

## Données personnelles et cookies

Ce site ne dépose aucun cookie de mesure d'audience ni de publicité. Le traitement de vos données est décrit dans la page [confidentialité](/confidentialite/).

## Signaler un contenu

Pour signaler un contenu qui vous semble illicite, écrivez à {{ site.email }} en indiquant la page concernée et la raison de votre signalement.
