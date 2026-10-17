# Ouvrir les ventes, étape par étape

Ce guide sert le jour où la micro-entreprise est déclarée. Tout le site est déjà prêt : les pages produits, les boutons d'achat, la page Pro et les conditions de vente n'attendent que vos réglages. Comptez une demi-journée.

Rien ne s'affiche à l'achat tant que `ventes_actives` reste à `false` dans `config.yml`. Vous pouvez donc préparer Payhip tranquillement, sans que les visiteurs voient quoi que ce soit.

## 1. Avant Payhip : la micro-entreprise

Tout est expliqué, réponse par réponse, dans `docs/CREER-LA-MICRO-ENTREPRISE.md` : l'autorisation de cumul si vous êtes agent public, la déclaration en ligne, le SIREN, le médiateur de la consommation et le compte bancaire.

## 2. Le compte Payhip

1. Créez un compte sur payhip.com avec l'adresse de contact de Jeuphorie (jamais votre adresse personnelle si vous ne voulez pas qu'elle apparaisse aux clients).
2. **Settings > Account** : devise en euros, nom de la boutique « Jeuphorie », logo `statique/img/logo.png`.
3. **Settings > Payment** : reliez Stripe (carte bancaire) et PayPal.
4. **Settings > Taxes** : activez la gestion de la TVA européenne.
5. **Settings > Checkout** (ou équivalent) : ajoutez le lien vers les conditions de vente, `https://jeuphorie.fr/conditions-de-vente/`, avec une case à cocher obligatoire si l'option existe.
6. Le forfait gratuit suffit pour commencer (Payhip prend une commission sur chaque vente, en plus des frais Stripe ou PayPal). Vérifiez les tarifs du moment sur la page Pricing de Payhip.

### La case de renonciation au droit de rétractation

Pour qu'un client ne puisse pas télécharger un kit puis demander un remboursement, la loi exige qu'il coche, avant de payer, une case par laquelle il demande l'accès immédiat et renonce à son droit de rétractation (article L. 221-28, 13°, du Code de la consommation). Les conditions de vente de Jeuphorie sont rédigées pour cela.

Vérifiez dans les réglages de Payhip si cette case existe (elle est parfois appelée « EU digital content waiver » ou « withdrawal waiver »). Si vous ne la trouvez pas, envoyez ce message au support de Payhip (support@payhip.com) :

> Hello,
>
> I sell digital downloads (PDF) to customers in France and the EU. Under EU consumer law (Directive 2011/83/EU, art. 16(m)), the 14-day right of withdrawal only ends if the customer, before payment, expressly consents to immediate access and acknowledges losing the right of withdrawal, and if this consent is confirmed in the order email.
>
> Does Payhip offer a mandatory checkbox at checkout for this, and is the consent included in the confirmation email? If so, how do I enable it?
>
> Thank you,
> Jeuphorie

Sans cette case, les conditions de vente restent valables : le client garde simplement son droit de rétractation pendant 14 jours. C'est un risque faible pour des kits à 10 ou 12 €.

## 3. Le cadeau d'inscription (possible tout de suite)

Le produit gratuit « 3 grands jeux offerts » ne demande aucun paiement : il peut être mis en ligne avant même la déclaration.

1. **Products > Add new > Digital product**, prix 0 €, titre « 3 grands jeux offerts ».
2. Fichier : le PDF des trois jeux offerts (gendarmes et voleurs, poules renards vipères, l'épervier gradé), tiré de votre dossier des grands jeux.
3. Copiez le code du produit, la fin de son adresse `payhip.com/b/XXXX`, dans `config.yml`, ligne `jeu_gratuit_payhip`.

Le bouton « Recevoir les 3 jeux » apparaît alors sur la page `/jeux-gratuits/`.

## 4. Les produits

Pour chaque produit de `donnees/kits.yml`, créez un produit numérique sur Payhip. **Tout est préparé dans le fichier `PAYHIP-A-COPIER.html` du dossier privé des produits** : pour chaque produit, le titre, le prix, le texte de description à coller, l'image de couverture et la liste des fichiers à joindre. Il suffit d'ouvrir ce fichier à côté de Payhip et de copier-coller.

Une fois un produit créé, envoyez-moi son adresse (`payhip.com/b/XXXX`) : je reporte le code dans `donnees/kits.yml` et je passe le produit en vente. Vous pouvez aussi le faire vous-même : champ `payhip_id`, et `etat: en_vente`.

## 5. L'abonnement Jeuphorie Pro

Créez un abonnement « Jeuphorie Pro » (**Products > Add new > Membership**) avec trois formules. Les textes de présentation et le message de bienvenue de chaque formule sont dans `PAYHIP-A-COPIER.html`.

| Formule | Prix | Ce que l'abonné doit recevoir |
|---|---|---|
| Pro Animateur | 4,90 € par mois | Le dossier du mois en cours, puis chaque nouveau dossier ; le code de 30 % |
| Pro Animateur annuel | 39 € par an | Le grand fichier, tous les dossiers parus, puis chaque nouveau dossier ; le code de 30 % |
| Pro Structure | 149 € par an | Tous les produits de la boutique, tous les dossiers, le calendrier d'animation, et chaque nouveauté |

Pour Pro Structure, deux façons de donner accès à toute la boutique :

1. **Si Payhip permet d'inclure des produits dans une formule** (option du type « free for members » ou « included in membership » dans les réglages du produit ou de l'abonnement) : cochez-la pour chaque produit et la formule Structure. C'est le plus simple, et les nouveaux produits s'ajoutent en une case.
2. **Sinon**, publiez dans l'espace de la formule Structure un message par univers (anniversaires, fêtes, kermesse, grands jeux, professionnels) avec les fichiers joints.

Dans tous les cas, publiez dans l'espace de l'abonnement :

- **Bienvenue** (toutes les formules) : mode d'emploi, rappel de la licence, et le code de réduction pour les formules Animateur.
- **Le grand fichier** (formules annuelles).
- **Le calendrier d'animation** (Structure).
- **Un message par dossier du mois** (toutes les formules), puis un nouveau chaque mois.

Copiez ensuite le code de chaque formule dans `donnees/abonnement.yml`, champ `payhip` de la formule (ou envoyez-moi les liens). Les boutons « S'abonner » apparaissent alors sur la page `/pro/`.

## 6. Le code de réduction des abonnés Animateur

Dans **Coupons**, créez un code de 30 %, valable sur les produits uniquement, jamais sur l'abonnement. Il n'est donné **que** dans le message de bienvenue des formules Animateur : jamais sur le site, jamais dans ce dépôt. Changez-le une fois par an. Les structures n'en ont pas besoin : tout est inclus.

## 7. Les structures qui paient sur facture

Beaucoup d'écoles, de mairies et de CSE ne paient pas par carte. La page Contact propose déjà un mail de demande de devis. Pour y répondre :

1. Envoyez un devis (nom de la structure, formule, prix, durée d'un an, conditions de vente en lien).
2. Après accord, envoyez une facture. Mentions obligatoires d'une facture de micro-entrepreneur : numéro unique et chronologique, date, vos nom et adresse, SIREN, nom et adresse de la structure, désignation, prix, mention de TVA confirmée par le SIE, date d'échéance et pénalités de retard, indemnité forfaitaire de 40 € pour frais de recouvrement (clients professionnels).
3. Les structures publiques (mairies, écoles publiques) demandent souvent le dépôt de la facture sur Chorus Pro, le portail gratuit de facturation au secteur public.
4. À réception du virement ou du mandat, donnez l'accès : ajoutez la structure comme membre Pro Structure dans Payhip si l'option existe, ou envoyez-lui les fichiers par un lien de téléchargement, sans renouvellement automatique (comme prévu à l'article 10 des conditions de vente).

## 8. Les mentions légales

Dans `config.yml`, remplacez chaque valeur entre `[[ ]]` :

- `editeur` : nom, statut (« Entrepreneur individuel »), adresse (une domiciliation est possible si vous ne voulez pas afficher votre adresse personnelle), SIREN, mention de TVA ;
- `mediateur` : nom, adresse et site du médiateur choisi ;
- `boutique.payhip` : l'adresse de votre boutique Payhip.

Complétez aussi les zones surlignées des pages elles-mêmes :

- `contenu/pages/confidentialite.md` : vérifier que la décision d'adéquation de la Commission européenne pour le Royaume-Uni (Payhip) est toujours en vigueur, et que GitHub adhère toujours au cadre de protection des données UE–États-Unis (Data Privacy Framework) ;
- `contenu/pages/mentions-legales.md` : les crédits des illustrations, s'il y en a sous licence.

Relisez ensuite les pages `/mentions-legales/`, `/conditions-de-vente/` et `/confidentialite/` sur le site d'aperçu : il ne doit plus rester aucune zone surlignée.

## 9. Ouvrir

1. Dans `config.yml`, passez `ventes_actives` à `true`.
2. Lancez `python3 build.py --apercu` et vérifiez une page produit, la boutique et la page Pro.
3. Publiez (envoi sur `main`).
4. Faites un achat test avec un code à 100 % créé pour l'occasion, puis supprimez ce code.
5. Vérifiez le mail de confirmation : produit, prix, lien de téléchargement, et la mention de renonciation au droit de rétractation si la case existe.

Pour toute vente, le site n'a rien à faire de plus : Payhip encaisse, envoie les fichiers et la facture au client.
