# Ouvrir les ventes, étape par étape

Les paiements passent par **Stripe**, sans autre plateforme. Stripe a un accès programmable : Claude crée lui-même les produits, les prix, les liens de paiement et les abonnements, et branche le site. Votre part se limite aux démarches qui demandent votre identité.

Rien ne s'affiche à l'achat tant que `ventes_actives` reste à `false` dans `config.yml`.

## 1. La micro-entreprise

Tout est expliqué, réponse par réponse, dans `docs/CREER-LA-MICRO-ENTREPRISE.md` : l'autorisation de cumul si vous êtes agent public, la déclaration en ligne, le SIREN, le médiateur de la consommation et le compte bancaire.

## 2. Votre part (environ 20 minutes, une seule fois)

1. **Créer le compte Stripe** sur dashboard.stripe.com/register. Le mode test fonctionne tout de suite ; pour encaisser pour de vrai, Stripe demande votre identité, votre IBAN et le SIREN.
2. **Dans Stripe**, réglages du compte : nom public « Jeuphorie », libellé sur le relevé bancaire « JEUPHORIE », adresse de contact, et l'adresse des conditions de vente `https://jeuphorie.fr/conditions-de-vente/` (Paramètres > Paramètres publics de l'entreprise).
3. **Donner l'accès à Claude** : dans les réglages de l'environnement Claude (menu de l'environnement dans la barre de titre d'une session, puis Edit) :
   - Network access : ajouter `api.stripe.com` aux domaines autorisés ;
   - Network secrets : ajouter la clé secrète Stripe (Développeurs > Clés API) sous le nom `STRIPE_SECRET_KEY`. D'abord la clé de test (`sk_test_…`), puis la clé réelle (`sk_live_…`) le jour de l'ouverture. Ne jamais coller une clé dans la conversation.
4. **Permettre au site de lire les fichiers du dépôt privé** au moment de la mise en ligne : sur GitHub, créer un jeton « fine-grained » (Settings > Developer settings > Personal access tokens) limité au dépôt `jeuphorie-produits`, en lecture seule sur « Contents », puis l'ajouter dans le dépôt `jeuphorie` (Settings > Secrets and variables > Actions) sous le nom `PRODUITS_TOKEN`.
5. Ouvrir une nouvelle session Claude avec les dépôts `jeuphorie` et `jeuphorie-produits`.

## 3. Ce que Claude fait ensuite

- Crée dans Stripe les produits, les prix et un lien de paiement par produit, avec la case obligatoire de renonciation au droit de rétractation (article L. 221-28, 13°, du Code de la consommation) et le rappel de cet accord dans la confirmation.
- Crée les trois abonnements (4,90 € par mois, 39 € et 149 € par an) et active l'espace de gestion où l'abonné résilie lui-même.
- Crée un code de 30 % pour les formules Animateur, limité aux kits d'anniversaire, de fêtes, de kermesse et de grands jeux.
- Prépare la livraison : après le paiement, le client arrive sur une page de téléchargement à adresse secrète. Les fichiers viennent du dépôt privé et ne sont jamais dans le dépôt public.
- Prépare les bibliothèques des abonnés (une par formule), dont le lien est envoyé par mail à la souscription, puis chaque mois avec le nouveau dossier. Quand un abonné résilie, l'adresse change et seuls les abonnés actifs reçoivent la nouvelle.
- Reporte les liens dans `donnees/kits.yml` et `donnees/abonnement.yml` (champ `paiement`) et vous fait faire un achat d'essai en mode test.

## 4. Les structures qui paient sur facture

Beaucoup d'écoles, de mairies et de CSE ne paient pas par carte. La page Contact propose un mail de demande de devis. Pour y répondre :

1. Envoyez un devis (nom de la structure, formule, prix, durée d'un an, conditions de vente en lien). Stripe peut aussi émettre la facture.
2. Mentions obligatoires d'une facture de micro-entrepreneur : numéro unique et chronologique, date, vos nom et adresse, SIREN, nom et adresse de la structure, désignation, prix, « TVA non applicable, article 293 B du CGI » en franchise, date d'échéance et pénalités de retard, indemnité forfaitaire de 40 € pour frais de recouvrement (clients professionnels).
3. Les structures publiques (mairies, écoles publiques) demandent souvent le dépôt de la facture sur Chorus Pro, le portail gratuit de facturation au secteur public.
4. À réception du virement ou du mandat, envoyez le lien de la bibliothèque Pro Structure, pour un an, sans renouvellement automatique (article 10 des conditions de vente).

## 5. Les mentions légales

Dans `config.yml`, remplacez chaque valeur entre `[[ ]]` (ou envoyez les informations à Claude) :

- `editeur` : nom, statut (« Entrepreneur individuel »), adresse (une domiciliation est possible si vous ne voulez pas afficher votre adresse personnelle), SIREN, mention de TVA ;
- `mediateur` : nom, adresse et site du médiateur choisi.

Complétez aussi les zones surlignées des pages elles-mêmes :

- `contenu/pages/confidentialite.md` : vérifier que GitHub adhère toujours au cadre de protection des données UE–États-Unis (Data Privacy Framework) ;
- `contenu/pages/mentions-legales.md` : les crédits des illustrations, s'il y en a sous licence.

Relisez ensuite les pages `/mentions-legales/`, `/conditions-de-vente/` et `/confidentialite/` sur le site d'aperçu : il ne doit plus rester aucune zone surlignée.

## 6. Ouvrir

1. Remplacer la clé de test par la clé réelle dans les réglages de l'environnement ; Claude recrée les liens en mode réel.
2. Dans `config.yml`, passer `ventes_actives` à `true`, vérifier l'aperçu, publier.
3. Faire un vrai achat à petit prix (un code à 100 % créé pour l'occasion, puis supprimé) et vérifier le mail : produit, prix, lien de téléchargement, rappel de la renonciation au droit de rétractation.
