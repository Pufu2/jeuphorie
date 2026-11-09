"""Le 1er de chaque mois, prévient chaque abonné Jeuphorie Pro que le nouveau dossier du mois est dans sa bibliothèque.

Lancé par .github/workflows/dossier-du-mois.yml. Il lit le programme et les adresses des bibliothèques dans le dépôt
privé (JEUPHORIE_PRODUITS), les abonnements actifs dans Stripe, et envoie un mail par Brevo à chacun, une seule fois
par mois (metadata dossier_annonce sur l'abonnement). Si le dossier du mois n'existe pas, rien n'est envoyé.

Secrets GitHub : STRIPE_LIVRAISON_KEY (clé restreinte, avec « Subscriptions » et « Customers » en lecture,
« Checkout Sessions » en écriture) et BREVO_API_KEY.
Usage : python3 outils/annoncer_dossier.py [--essai]
"""
import datetime as dt
import html
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from livrer_mails import brevo, stripe  # noqa: E402

RACINE = Path(__file__).resolve().parents[1]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre",
        "décembre"]


def mail(mois, theme, angle, lien, portail):
    e = html.escape
    return f"""<!doctype html><html lang="fr"><body style="margin:0;background:#FBFAF7">
<div style="max-width:600px;margin:0 auto;padding:24px 20px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.5;color:#1A2340">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right:10px;vertical-align:middle"><img src="https://jeuphorie.fr/img/logo-mail.png" width="40" height="40" alt="" style="display:block;border:0"></td><td style="vertical-align:middle;font-size:26px;font-weight:bold;font-family:Arial,Helvetica,sans-serif;color:#1A2340"><span style="color:#CF3424">Jeu</span>phorie</td></tr></table>
<p style="margin:18px 0 0">Bonjour,</p>
<p>Le dossier de {e(mois)} est arrivé dans votre bibliothèque : <strong>{e(theme)}</strong>.</p>
<p>{e(angle)}</p>
<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:22px 0"><tr><td bgcolor="#CF3424" style="background:#CF3424;border-radius:24px;padding:12px 24px"><a href="{e(lien)}" style="color:#ffffff;text-decoration:none;font-weight:bold;font-family:Arial,Helvetica,sans-serif;font-size:16px">Ouvrir ma bibliothèque</a></td></tr></table>
<p>Une idée de thème pour les prochains dossiers ? Répondez simplement à ce mail.</p>
<p style="margin-top:26px">Bonnes animations !<br>Rafaël, de Jeuphorie</p>
<p style="font-size:13px;color:#4B5675;margin-top:22px">Vous recevez ce mail parce que vous êtes abonné à Jeuphorie Pro.
{f'<a href="{e(portail)}" style="color:#4B5675">Gérer mon abonnement</a>.' if portail else ''}</p>
</div></body></html>"""


def main():
    essai = "--essai" in sys.argv
    produits = Path(os.environ.get("JEUPHORIE_PRODUITS") or RACINE.parent / "jeuphorie-produits")
    config = yaml.safe_load((RACINE / "config.yml").read_text(encoding="utf-8"))
    cle_stripe = os.environ.get("STRIPE_LIVRAISON_KEY", "").strip()
    cle_brevo = os.environ.get("BREVO_API_KEY", "").strip()
    if not cle_stripe or not (cle_brevo or essai) or not (produits / "livraison.yml").exists():
        print("Secrets ou dépôt privé absents : rien n'est envoyé.")
        return 0
    jour = dt.date.today()
    cle_mois = f"{jour.year}-{jour.month:02d}"
    programme = yaml.safe_load((produits / "programme.yml").read_text(encoding="utf-8"))
    dossier = next((d for d in programme.get("dossiers", []) if str(d["mois"]) == cle_mois), None)
    nom_mois = MOIS[jour.month - 1]
    if not dossier or not list((produits / "pro" / "sortie").glob(f"*-{nom_mois.capitalize().replace('é', 'e').replace('û', 'u')}-{jour.year}-*.pdf")):
        print(f"Pas de dossier pour {cle_mois} : rien n'est envoyé.")
        return 0
    liv = yaml.safe_load((produits / "livraison.yml").read_text(encoding="utf-8"))
    portail = config.get("boutique", {}).get("portail_abonnes")
    envoyes, apres = 0, None
    while True:
        params = {"status": "active", "limit": 100, "expand[]": "data.customer"}
        if apres:
            params["starting_after"] = apres
        page = stripe("GET", "subscriptions", cle_stripe, **params)
        for s in page["data"]:
            meta = s.get("metadata") or {}
            code = liv.get("formules", {}).get(meta.get("formule"))
            email = (s.get("customer") or {}).get("email") if isinstance(s.get("customer"), dict) else None
            if not code or not email or meta.get("dossier_annonce") == cle_mois:
                continue
            lien = f"{config['url'].rstrip('/')}/bibliotheque/{code}/"
            sujet = f"Jeuphorie Pro : le dossier de {nom_mois} est arrivé"
            if essai:
                print(f"[essai] {email} · {sujet} · {lien}")
                continue
            brevo(cle_brevo, {"sender": {"name": "Rafaël, de Jeuphorie", "email": config.get("lettre_expediteur")},
                              "replyTo": {"email": config.get("email")}, "to": [{"email": email}], "subject": sujet,
                              "htmlContent": mail(nom_mois, dossier["theme"], dossier.get("angle", ""), lien, portail),
                              "tags": ["dossier-du-mois"]})
            stripe("POST", f"subscriptions/{s['id']}", cle_stripe, **{"metadata[dossier_annonce]": cle_mois})
            envoyes += 1
        if not page.get("has_more"):
            break
        apres = page["data"][-1]["id"]
    print(f"{envoyes} abonné(s) prévenu(s) du dossier de {nom_mois}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
