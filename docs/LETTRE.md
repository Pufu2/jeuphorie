# La lettre de Jeuphorie et la mesure d'audience

## 1. La liste d'e-mails (Brevo, gratuit jusqu'à 300 envois par jour)

Le site est prêt : dès que le formulaire Brevo est branché, la page « Jeux gratuits » propose de recevoir les 3 jeux offerts par e-mail et de s'inscrire à la lettre. Le téléchargement direct reste possible, sans inscription. Chaque mois, le premier mardi, une lettre part toute seule : le jeu offert du mois, les articles parus, et le kit de saison une fois les ventes ouvertes. Aucun texte à écrire.

À faire **une seule fois** :

1. Créer un compte gratuit sur brevo.com, au nom de Jeuphorie.
2. **Expéditeur** : Paramètres > Expéditeurs, domaines et IP dédiées > ajouter `contact@jeuphorie.fr` et cliquer sur le lien reçu.
3. **Liste** : Contacts > Listes > « Créer une liste », nommée « Lettre Jeuphorie ». Noter son numéro (#2, #3…) et me l'envoyer : ce n'est pas un secret.
4. **Formulaire** : Contacts > Formulaires > « Créer un formulaire d'inscription », choisir la liste ci-dessus, cocher la **double confirmation** (« double opt-in »). Pages de redirection :
   - après l'inscription : `https://jeuphorie.fr/jeux-gratuits/merci/`
   - après la confirmation : `https://jeuphorie.fr/jeux-gratuits/bienvenue/`
5. À l'étape « Partager », choisir « Code HTML » et me copier uniquement l'adresse qui suit `action="…"` (elle commence par `https://` et contient `sibforms.com`). Elle n'est pas secrète : elle va dans `config.yml`, à la ligne `brevo_formulaire`.
6. **Clé d'API** : Paramètres > SMTP et API > Clés API > « Générer une nouvelle clé ». Ne pas me l'envoyer : la coller dans GitHub, dépôt `Pufu2/jeuphorie` > Settings > Secrets and variables > Actions > « New repository secret », nom `BREVO_API_KEY`.

Pour voir la prochaine lettre sans l'envoyer : `python3 outils/lettre.py --apercu` (fichier `lettre-apercu.html`). Pour l'envoyer à la main : onglet Actions > « Lettre mensuelle » > « Run workflow ».

## 2. La mesure d'audience (GoatCounter, gratuit, sans cookie)

GoatCounter compte les visites sans cookie et sans donnée personnelle : pas de bandeau de consentement à afficher.

1. Créer un compte sur goatcounter.com avec le code **jeuphorie** (l'adresse devient `jeuphorie.goatcounter.com`).
2. Me dire que c'est fait : la ligne `goatcounter: "jeuphorie"` est ajoutée dans `config.yml`, et les visites s'affichent sur votre tableau de bord.

## 3. Les témoignages

Quand un client raconte son animation (bouton « Racontez-moi comment ça s'est passé » sur les pages des kits, actif une fois les ventes ouvertes), son avis s'ajoute dans `donnees/temoignages.yml`, seulement avec son accord écrit. Jamais de nom de structure ni de photo d'enfant : un prénom et une fonction suffisent (« Julie, animatrice »).
