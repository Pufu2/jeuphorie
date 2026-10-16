# Ouvrir les ventes, étape par étape

Ce guide sert le jour où la micro-entreprise est déclarée. Tout le site est déjà prêt : les pages produits, les boutons d'achat, la page Pro et les conditions de vente n'attendent que vos réglages. Comptez une demi-journée.

Rien ne s'affiche à l'achat tant que `ventes_actives` reste à `false` dans `config.yml`. Vous pouvez donc préparer Payhip tranquillement, sans que les visiteurs voient quoi que ce soit.

## 1. Avant Payhip : les obligations

| À faire | Où | Ce que ça débloque |
|---|---|---|
| Déclarer la micro-entreprise | Guichet unique de l'INPI (formalites.entreprises.gouv.fr) | Le numéro SIREN |
| Choisir un médiateur de la consommation | Liste des médiateurs référencés sur economie.gouv.fr (rubrique médiation de la consommation) | Obligatoire pour vendre à des particuliers |
| Vérifier le régime de TVA | Service des impôts des entreprises (SIE) | La mention à écrire dans `config.yml` et sur les factures |
| Ouvrir un compte bancaire pour l'activité | Votre banque, ou une banque en ligne | Obligatoire au-delà de 10 000 € de chiffre d'affaires deux années de suite, conseillé dès le début |

Pour la TVA, posez au SIE une question précise : « Je suis en franchise en base. Je vends des PDF par Payhip, qui collecte la TVA européenne sur les ventes aux particuliers. Quelle mention dois-je porter sur mes factures aux associations et aux structures ? » Gardez la réponse écrite.

Pensez aussi à déclarer votre chiffre d'affaires à l'Urssaf chaque mois ou chaque trimestre, même quand il est nul.

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

Pour chaque kit, créez un produit numérique sur Payhip :

- **Titre et prix** : ceux du tableau ci-dessous (identiques à `donnees/kits.yml`).
- **Description** : copiez le texte de la page du kit sur le site (accroche, description, « Dans le fichier »).
- **Image** : `statique/img/kits/<identifiant>-couverture.jpg`.
- **Fichiers** : ceux du dossier privé des produits (jamais dans ce dépôt).
- Une fois le produit créé, copiez son code (la fin de `payhip.com/b/XXXX`) dans `donnees/kits.yml`, champ `payhip_id`, et passez `etat` à `en_vente`.

| Identifiant | Titre | Prix | Fichiers à joindre |
|---|---|---|---|
| olympiades-anniversaire | Les Olympiades d'anniversaire | 12 € | Jeuphorie-Olympiades-d-anniversaire.pdf |
| chasse-tresor-pirates | La chasse au trésor des pirates | 9,90 € | Jeuphorie-La-chasse-au-tresor-des-pirates.pdf |
| enquete-gateau-disparu | L'enquête du gâteau disparu | 12 € | Jeuphorie-L-enquete-du-gateau-disparu.pdf |
| safari-petits-explorateurs | Le safari des petits explorateurs | 9,90 € | Jeuphorie-Le-safari-des-petits-explorateurs.pdf |
| kit-toussaint | Le grand jeu de la forêt d'automne | 12 € | Jeuphorie-Le-grand-jeu-de-la-foret-d-automne.pdf |
| kit-noel | L'atelier du père Noël | 12 € | Jeuphorie-L-atelier-du-pere-Noel.pdf |
| kit-carnaval | Le grand bal du carnaval | 12 € | Jeuphorie-Le-grand-bal-du-carnaval.pdf |
| kit-paques | La grande quête des cloches | 12 € | Jeuphorie-La-grande-quete-des-cloches.pdf |
| kermesse-cle-en-main | La kermesse clé en main | 25 € | Kermesse-1-guide.pdf, Kermesse-2-a-imprimer.pdf, Kermesse-3-textes-a-modifier.docx |
| kit-du-directeur | Le kit du directeur d'accueil de loisirs | 29 € | Jeuphorie-Kit-du-directeur-guide.pdf, Jeuphorie-Kit-du-directeur-classeur.xlsx |
| pack-6-9 | Grands jeux 6-9 ans | 9,90 € | Vos fiches des grands jeux 6-9 ans, précédées de couv-pack-6-9.pdf |
| pack-10-13 | Grands jeux 10-13 ans | 9,90 € | Vos fiches 10-13 ans, précédées de couv-pack-10-13.pdf |
| pack-14-17 | Grands jeux 14-17 ans | 9,90 € | Vos fiches 14-17 ans, précédées de couv-pack-14-17.pdf |
| grand-fichier | Le grand fichier des jeux collectifs | 19,90 € | Les 34 fiches, précédées de couv-grand-fichier.pdf |

Vérifiez les titres exacts dans `donnees/kits.yml` avant de les recopier.

## 5. L'abonnement Jeuphorie Pro

Payhip propose des abonnements (**Products > Add new > Membership**). Créez un abonnement « Jeuphorie Pro » avec trois formules :

| Formule | Prix | Ce que l'abonné doit recevoir |
|---|---|---|
| Pro Animateur | 4,90 € par mois | Le dossier du mois en cours, puis chaque nouveau dossier ; le code de 30 % |
| Pro Animateur annuel | 39 € par an | Le grand fichier, tous les dossiers parus, puis chaque nouveau dossier ; le code de 30 % |
| Pro Structure | 119 € par an | Tout ce qui précède, plus les 4 kits des fêtes et le kit du directeur ; le code de 40 % |

Dans l'espace de l'abonnement, publiez un message par contenu, en choisissant à chaque fois les formules qui y ont accès :

1. **Bienvenue** (toutes les formules) : mode d'emploi, rappel de la licence, et le code de réduction de la formule.
2. **Le grand fichier** (annuel et Structure).
3. **Les kits des fêtes et le kit du directeur** (Structure).
4. **Un message par dossier du mois** (toutes les formules) : `Jeuphorie-Pro-Novembre-2026-Jours-de-pluie.pdf`, `Jeuphorie-Pro-Decembre-2026-Jeux-cooperatifs.pdf`, puis un nouveau chaque mois.

Copiez ensuite le code de chaque formule dans `donnees/abonnement.yml`, champ `payhip` de la formule. Les boutons « S'abonner » apparaissent alors sur la page `/pro/`.

## 6. Les codes de réduction

Dans **Coupons**, créez les deux codes que vous avez choisis pour les abonnés (30 % et 40 %), valables sur les kits uniquement, jamais sur l'abonnement. Ils ne sont donnés **que** dans le message de bienvenue de l'espace Pro : jamais sur le site, jamais dans ce dépôt.

Changez-les une fois par an : un code qui circule hors de l'espace Pro perd sa valeur.

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
