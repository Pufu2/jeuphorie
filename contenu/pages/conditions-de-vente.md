---
titre: Conditions générales de vente
url: /conditions-de-vente/
description: "Conditions générales de vente de Jeuphorie : produits numériques à télécharger et abonnement Jeuphorie Pro. Prix, commande, rétractation, résiliation, garanties, licence d'utilisation."
chapo: "Version du 18 octobre 2026. Ces conditions s'appliquent à tous les achats de produits Jeuphorie et à l'abonnement Jeuphorie Pro."
---

{% if not site.boutique.ventes_actives %}
> **La boutique n'est pas encore ouverte.** Ces conditions entreront en vigueur à l'ouverture des ventes.
{% endif %}

## 1. Qui vend

{% if site.editeur_ok %}Les kits sont vendus par {{ site.editeur.nom }}, {{ site.editeur.statut }}, {{ site.editeur.adresse }}, SIREN {{ site.editeur.siren }}, joignable à {{ site.email }} (ci-après « Jeuphorie »).{% else %}Les kits seront vendus par l'entreprise individuelle de Rafaël, créateur de Jeuphorie, joignable à {{ site.email }} (ci-après « Jeuphorie »). Son identité complète (nom, adresse, numéro SIREN) sera indiquée ici à l'ouverture des ventes.{% endif %}

Les paiements sont traités par **{{ site.plateforme_vente.nom }}** ({{ site.plateforme_vente.adresse }}), prestataire de paiement agréé.

## 2. Ce qui est vendu

Jeuphorie vend des **contenus numériques** : des fichiers de jeux et des kits d'animation au format PDF, des outils au format tableur, et un abonnement, Jeuphorie Pro, qui donne accès à une bibliothèque en ligne de fichiers à télécharger. Ils sont fournis par téléchargement, sans support matériel. Rien n'est envoyé par la poste.

Chaque fiche produit indique le contenu du kit, l'âge conseillé, le nombre de joueurs, la durée et le format des fichiers. Pour les utiliser, il faut un appareil capable d'ouvrir un PDF et, pour les imprimer, une imprimante ou un service de reprographie. Les outils au format tableur s'ouvrent avec Microsoft Excel, LibreOffice Calc ou Google Sheets.

## 3. Prix

Les prix sont indiqués en euros, toutes taxes comprises.{% if site.editeur_ok %} {{ site.editeur.tva }}{% endif %}

Le prix payé est celui affiché au moment de la commande.

## 4. Commande

Pour commander, vous cliquez sur le bouton d'achat du kit, puis vous suivez les étapes de la page de paiement sécurisée : adresse mail, carte bancaire, cases à cocher, puis validation. Avant de payer, vous pouvez vérifier le produit, son prix et corriger vos informations.

La commande est conclue au moment où vous validez le paiement. Une confirmation est envoyée à l'adresse mail indiquée : elle reprend le kit acheté, son prix et, le cas échéant, votre accord pour un accès immédiat (voir l'article 7).

## 5. Paiement

Le paiement se fait par carte bancaire, sur les pages sécurisées de Stripe. Jeuphorie n'a jamais accès à vos données bancaires. Une structure peut aussi payer par virement ou mandat administratif, sur devis et facture.

## 6. Téléchargement

Dès le paiement validé, vous arrivez sur la page de téléchargement de votre achat, dont le lien vous est aussi envoyé par mail. Pour un abonnement, vous recevez par mail le lien de votre bibliothèque. Si vous ne le recevez pas, vérifiez vos courriers indésirables puis écrivez à {{ site.email }} : nous vous renvoyons le kit.

## 7. Droit de rétractation

En principe, un consommateur dispose de 14 jours pour se rétracter après un achat à distance (article L. 221-18 du Code de la consommation).

**Ce droit ne s'applique pas aux contenus numériques téléchargés immédiatement**, si les trois conditions suivantes sont réunies (article L. 221-28, 13°, du Code de la consommation) :

1. avant de payer, vous avez demandé expressément à accéder au kit tout de suite, sans attendre la fin du délai de 14 jours ;
2. vous avez reconnu expressément qu'en accédant au kit, vous perdez votre droit de rétractation ;
3. Jeuphorie vous a confirmé cet accord par mail (article L. 221-13 du Code de la consommation).

Ces accords sont recueillis par des cases à cocher, non cochées par défaut, au moment de la commande.

**Si ces conditions ne sont pas réunies**, vous gardez votre droit de rétractation pendant 14 jours à compter de la commande. Pour l'exercer, utilisez le bouton « Me rétracter d'un achat » de la [page Contact](/contact/), ou envoyez à {{ site.email }} une déclaration claire, par exemple le modèle en fin de page. Vous êtes remboursé dans les 14 jours, par le moyen de paiement utilisé lors de l'achat.

## 8. Garantie légale de conformité

Les kits bénéficient de la garantie légale de conformité des contenus numériques (articles L. 224-25-12 et suivants du Code de la consommation). Si un fichier est illisible, incomplet ou ne correspond pas à sa description, signalez-le à {{ site.email }} : nous le corrigeons ou le remplaçons. Si ce n'est pas possible, vous êtes remboursé.

## 9. Ce que vous pouvez faire avec un fichier

Le fichier acheté, ou téléchargé dans le cadre de l'abonnement, vous donne le droit de l'**imprimer et de l'utiliser autant de fois que vous le voulez** :

- **pour un particulier** : dans le cadre familial et amical ;
- **pour une association, une école ou une structure** : pour toutes les activités de cette structure, par toute son équipe (salariés, animateurs, enseignants, bénévoles). Une structure s'entend d'un établissement (un accueil de loisirs, une école, un club…) ou d'une association ; plusieurs établissements, une collectivité entière ou un réseau relèvent d'un devis.

Il est interdit de revendre un fichier, de le partager en ligne (site, réseau social, groupe de messagerie), de le transmettre à une autre structure ou de le modifier pour le diffuser. Les jeux, textes et illustrations restent la propriété de Jeuphorie ou de leurs auteurs.

## 10. Abonnement Jeuphorie Pro

**Les formules.** Jeuphorie Pro existe en trois formules, décrites sur la page [Jeuphorie Pro](/pro/) :

- **Pro Animateur mensuel**, 4,90 € par mois : le dossier du mois publié pendant chaque mois d'abonnement, et un code de réduction de 30 % sur les kits d'anniversaire, de fêtes, de kermesse et de grands jeux ;
- **Pro Animateur annuel**, 39 € par an : le grand fichier des grands jeux et tous les dossiers du mois, y compris ceux déjà parus, dès la souscription, puis les nouveaux dossiers, et un code de réduction de 30 % sur les kits d'anniversaire, de fêtes et de kermesse. Les outils pour les structures ne bénéficient pas de cette réduction ;
- **Pro Structure**, 149 € par an : pour une structure (un établissement ou une association, voir l'article 9), tous les produits de la boutique, tous les dossiers du mois, le calendrier d'animation de l'année et les produits publiés pendant l'abonnement, pour toute l'équipe de la structure, sans limite de nombre de personnes.

Les fichiers inclus dans une formule sont mis à disposition dans une bibliothèque en ligne, dont le lien est envoyé par mail à la souscription, puis à chaque nouveauté.

**Durée et renouvellement.** L'abonnement mensuel est conclu pour un mois, l'abonnement annuel pour un an. Chacun se renouvelle automatiquement pour la même durée, au prix payé à la souscription, jusqu'à sa résiliation : tant que l'abonnement est renouvelé sans interruption, son prix n'augmente pas. Pour les abonnements annuels, Jeuphorie vous prévient par mail, entre un et trois mois avant l'échéance, de la date de renouvellement et de la façon d'y mettre fin (article L. 215-1 du Code de la consommation).

**Résiliation.** Vous pouvez résilier à tout moment, gratuitement, en quelques clics, depuis le lien de gestion de l'abonnement envoyé avec chaque reçu, ou par mail à {{ site.email }} (article L. 215-1-1 du Code de la consommation). La résiliation arrête le renouvellement : vous gardez l'accès à votre bibliothèque jusqu'à la fin de la période payée, qui n'est pas remboursée.

**Après la fin de l'abonnement.** Les fiches que vous avez téléchargées ou imprimées pendant l'abonnement restent utilisables selon l'article 9. Les codes de réduction ne sont plus valables, et les nouveautés et mises à jour ne sont plus accessibles.

**Droit de rétractation.** La bibliothèque Pro est un contenu numérique fourni immédiatement : l'article 7 s'applique de la même façon à la souscription.

**Structures.** Une structure peut demander un devis et payer par virement. L'abonnement Pro Structure est alors conclu pour un an à compter du paiement, sans renouvellement automatique.

## 11. Responsabilité

Les jeux sont conçus pour être animés par un adulte, qui reste responsable de la sécurité des enfants. Chaque kit indique l'âge conseillé et le matériel nécessaire. Adaptez les épreuves à l'espace disponible et aux enfants présents.

## 12. Données personnelles

Les données nécessaires à la commande sont traitées comme décrit dans la page [confidentialité](/confidentialite/).

## 13. Réclamations et médiation

Pour toute réclamation, écrivez d'abord à {{ site.email }}. Nous répondons sous 48 heures ouvrées.

Si le désaccord persiste, vous pouvez recourir gratuitement au médiateur de la consommation dont relève Jeuphorie (article L. 612-1 du Code de la consommation) :

{% if site.mediateur_ok %}
- **{{ site.mediateur.nom }}**
- {{ site.mediateur.adresse }}
- {{ site.mediateur.site }}
{% else %}
- Le nom et les coordonnées du médiateur seront indiqués ici à l'ouverture des ventes.
{% endif %}

## 14. Droit applicable

Ces conditions sont soumises au droit français. En cas de litige, et à défaut d'accord amiable ou de médiation, les tribunaux français sont compétents. Si vous êtes consommateur dans un autre pays de l'Union européenne, vous gardez la protection des règles impératives de votre pays.

## Modèle de formulaire de rétractation

À utiliser uniquement si le droit de rétractation s'applique (voir l'article 7). Envoyez-le à {{ site.email }}.

> À l'attention de {{ site.editeur_nom }}, Jeuphorie, {{ site.email }} :
>
> Je vous notifie par la présente ma rétractation du contrat portant sur la vente du contenu numérique ci-dessous :
>
> - Kit commandé le : …
> - Nom du kit : …
> - Nom et adresse mail utilisés lors de la commande : …
> - Date : …
