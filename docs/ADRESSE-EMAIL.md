# Regrouper les e-mails dans la nouvelle boîte

Objectif : tout recevoir dans une seule boîte Gmail, celle créée pour les deux sites (Jeuphorie et Fil rouge anim). L'adresse de cette boîte n'est volontairement pas écrite ici : ce dépôt est public, et une adresse publiée attire le spam.

## Le principe

Sur les sites, on garde **contact@jeuphorie.fr**. C'est plus professionnel qu'une adresse Gmail, et l'adresse ne change jamais, même si la boîte change un jour. Elle est simplement **redirigée** vers la nouvelle boîte. Rien n'est à modifier dans le site.

## 1. Rediriger contact@jeuphorie.fr (5 minutes, chez OVH)

1. Sur ovh.com, Espace client > **Web Cloud** > **Noms de domaine** > `jeuphorie.fr` (ou **E-mails** > `jeuphorie.fr`).
2. Onglet **Redirection** (ou « Redirections e-mail »).
3. Si une redirection `contact@jeuphorie.fr` existe déjà vers l'ancienne adresse : la **modifier** et mettre la nouvelle adresse Gmail. Sinon, **Ajouter une redirection** : de `contact@jeuphorie.fr` vers la nouvelle adresse, en choisissant « Ne pas conserver de copie ».
4. Envoyer un e-mail de test à contact@jeuphorie.fr depuis un autre compte : il doit arriver dans la nouvelle boîte (pensez à regarder les spams la première fois).

Pour répondre **depuis** contact@jeuphorie.fr dans Gmail : Paramètres > Comptes et importation > « Envoyer des e-mails en tant que » > Ajouter une autre adresse. Il faut pour cela un vrai compte e-mail OVH (offre MX Plan, incluse avec certains domaines) ; sinon, répondez depuis la nouvelle adresse Gmail, c'est très bien aussi.

## 2. Changer l'adresse des comptes (chacun se fait sur le site concerné, avec votre mot de passe)

Ordre conseillé : d'abord les comptes qui servent à se connecter aux autres.

| Compte | Où changer l'adresse | Remarque |
|---|---|---|
| Google (Search Console) | Ajouter la nouvelle adresse comme **propriétaire** dans Search Console > Paramètres > Utilisateurs et autorisations | On ne change pas l'adresse d'un compte Gmail : on donne l'accès au nouveau compte |
| GitHub (Pufu2) | Settings > **Emails** > ajouter la nouvelle adresse, la confirmer, puis la choisir comme « Primary » | Laisser cochée l'option « Keep my email addresses private ». Les e-mails « Run failed » iront alors dans la nouvelle boîte |
| Facebook (compte qui gère la page) | Paramètres > Espace Comptes > Informations personnelles > Coordonnées | Le jeton de publication automatique n'est pas touché |
| Instagram `_jeuphorie_` | Profil > Modifier le profil > Coordonnées professionnelles, et Paramètres > Espace Comptes | |
| Pinterest | Paramètres > Gestion du compte > Adresse e-mail | |
| Brevo (lettre mensuelle) | Mon compte > Paramètres > Profil | L'expéditeur des lettres reste contact@jeuphorie.fr : rien à changer de ce côté |
| GoatCounter (statistiques) | Settings > User > Email | |
| Bing Webmaster Tools | Paramètres > Utilisateurs : ajouter le nouveau compte | Comme pour Google |
| OVH | Espace client > Mon compte > Mes informations | Garder un accès : c'est le compte du nom de domaine |
| Etsy | Paramètres > Compte > Adresse e-mail | |
| Supabase (Fil rouge anim) | Account > Preferences | |
| Claude | claude.ai > Paramètres | Puis reconnecter Gmail (voir plus bas) |

Les e-mails des deux sites pour les clients (contact, lettre, plus tard les ventes) partent tous de contact@jeuphorie.fr : une fois l'étape 1 faite, les réponses arrivent dans la nouvelle boîte.

## 3. Pour que Claude lise la nouvelle boîte

Sur https://claude.ai/customize/connectors : déconnecter Gmail et Google Agenda, puis les reconnecter en choisissant le nouveau compte. Démarrer ensuite une nouvelle conversation (les connecteurs sont chargés au début de chaque conversation). L'agenda de la routine est dans l'ancien compte : le plus simple est de partager cet agenda avec le nouveau compte (Google Agenda > Paramètres de l'agenda > Partager avec des personnes, droit « Apporter des modifications »).

Claude ne se connecte jamais lui-même à un compte et ne demande jamais de mot de passe : les connexions se font par vous, sur les pages officielles.
