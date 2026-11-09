"""Envoie à chaque client le mail avec le lien de son achat (kit ou bibliothèque Pro), quelques minutes après le paiement.

Lancé toutes les 10 minutes par GitHub Actions (.github/workflows/livraison.yml). Il lit les paiements terminés des
deux derniers jours dans Stripe, envoie le mail par Brevo, puis marque le paiement (metadata mail_livraison) pour ne
jamais l'envoyer deux fois. Le lien est celui de la redirection après paiement : aucune adresse secrète n'est écrite ici.

Secrets GitHub : STRIPE_LIVRAISON_KEY (clé restreinte Stripe, « Checkout Sessions » en écriture) et BREVO_API_KEY.
Usage : python3 outils/livrer_mails.py [--essai]   (--essai affiche les mails sans rien envoyer ni marquer)
"""
import base64
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]


def stripe(methode, chemin, cle, **params):
    donnees = urllib.parse.urlencode(params, doseq=True)
    url = f"https://api.stripe.com/v1/{chemin}" + (f"?{donnees}" if methode == "GET" else "")
    req = urllib.request.Request(url, data=donnees.encode() if methode == "POST" else None, method=methode,
                                 headers={"Authorization": "Basic " + base64.b64encode(f"{cle}:".encode()).decode()})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def texte(page):
    """La version texte du mail (sans elle, les messageries le jugent plus volontiers indésirable)."""
    page = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', lambda m: f"{m.group(2)} : {html.unescape(m.group(1))}", page, flags=re.S)
    page = re.sub(r"<br\s*/?>", "\n", page)
    page = re.sub(r"</(p|tr|div)>", "\n\n", page)
    page = html.unescape(re.sub(r"<[^>]+>", "", page))
    return re.sub(r"\n\s*\n+", "\n\n", "\n".join(l.strip() for l in page.splitlines())).strip() + "\n"


def brevo(cle, corps):
    if corps.get("htmlContent") and not corps.get("textContent"):
        corps = {**corps, "textContent": texte(corps["htmlContent"])}
    req = urllib.request.Request("https://api.brevo.com/v3/smtp/email", data=json.dumps(corps).encode("utf-8"),
                                 headers={"api-key": cle, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"Brevo : {err.code} {err.read().decode('utf-8', 'replace')}") from None


def mail(nom_produit, lien, abonnement, portail):
    e = html.escape
    if abonnement:
        intro = f"Merci pour votre abonnement à <strong>{e(nom_produit)}</strong> ! Votre bibliothèque est ouverte :"
        bouton = "Ouvrir ma bibliothèque"
        suite = ("Tous les fichiers de votre formule y sont, et chaque nouveau dossier y arrive au fil des mois : "
                 "je vous préviens par mail. Gardez ce mail, le lien reste valable pendant tout l'abonnement.")
        if portail:
            suite += (f'</p><p>Pour changer de carte, retrouver vos reçus ou résilier : '
                      f'<a href="{portail}" style="color:#1A2340">gérer mon abonnement</a>.')
    else:
        intro = f"Merci pour votre achat ! Votre kit <strong>{e(nom_produit)}</strong> est prêt à être téléchargé :"
        bouton = "Télécharger mon kit"
        suite = ("Enregistrez le fichier sur votre ordinateur : il est à vous, imprimez-le autant de fois que vous le "
                 "voulez. Gardez ce mail, le lien reste valable.")
    return f"""<!doctype html><html lang="fr"><body style="margin:0;background:#FBFAF7">
<div style="max-width:600px;margin:0 auto;padding:24px 20px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.5;color:#1A2340">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right:10px;vertical-align:middle"><img src="https://jeuphorie.fr/img/logo-mail.png" width="40" height="40" alt="" style="display:block;border:0"></td><td style="vertical-align:middle;font-size:26px;font-weight:bold;font-family:Arial,Helvetica,sans-serif;color:#1A2340"><span style="color:#CF3424">Jeu</span>phorie</td></tr></table>
<p style="margin:18px 0 0">Bonjour,</p>
<p>{intro}</p>
<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:22px 0"><tr><td bgcolor="#CF3424" style="background:#CF3424;border-radius:24px;padding:12px 24px"><a href="{e(lien)}" style="color:#ffffff;text-decoration:none;font-weight:bold;font-family:Arial,Helvetica,sans-serif;font-size:16px">{bouton}</a></td></tr></table>
<p>{suite}</p>
<p>Une question ? Répondez simplement à ce mail, je vous réponds rapidement.</p>
<p style="margin-top:26px">Bonnes animations !<br>Rafaël, de Jeuphorie</p>
</div></body></html>"""


def main():
    essai = "--essai" in sys.argv
    config = yaml.safe_load((RACINE / "config.yml").read_text(encoding="utf-8"))
    cle_stripe = os.environ.get("STRIPE_LIVRAISON_KEY", "").strip()
    cle_brevo = os.environ.get("BREVO_API_KEY", "").strip()
    expediteur = config.get("lettre_expediteur")
    if not cle_stripe or not (cle_brevo or essai):
        print("Secrets STRIPE_LIVRAISON_KEY ou BREVO_API_KEY absents : rien n'est envoyé.")
        return 0
    kits = {k["id"]: k["titre"] for k in yaml.safe_load((RACINE / "donnees" / "kits.yml").read_text(encoding="utf-8"))["kits"]}
    formules = {f["id"]: f["nom"] for f in yaml.safe_load((RACINE / "donnees" / "abonnement.yml").read_text(encoding="utf-8"))["formules"]}
    portail = config.get("boutique", {}).get("portail_abonnes")
    depuis = int(time.time()) - 2 * 86400
    envoyes, apres = 0, None
    while True:
        params = {"status": "complete", "created[gte]": depuis, "limit": 100}
        if apres:
            params["starting_after"] = apres
        page = stripe("GET", "checkout/sessions", cle_stripe, **params)
        for s in page["data"]:
            meta = s.get("metadata") or {}
            email = (s.get("customer_details") or {}).get("email")
            lien = s.get("success_url") or ""
            if (meta.get("mail_livraison") or not email or "jeuphorie.fr/" not in lien
                    or s.get("payment_status") not in ("paid", "no_payment_required")):
                continue
            abonnement = "formule" in meta
            nom = formules.get(meta.get("formule")) if abonnement else kits.get(meta.get("kit"))
            nom = f"Jeuphorie {nom}" if abonnement and nom else nom or "Jeuphorie"
            sujet = f"Votre {'bibliothèque' if abonnement else 'kit'} Jeuphorie : {nom.replace('Jeuphorie ', '')}"
            if essai:
                print(f"[essai] {email} · {sujet} · {lien}")
                continue
            brevo(cle_brevo, {"sender": {"name": "Rafaël, de Jeuphorie", "email": expediteur},
                              "replyTo": {"email": config.get("email", expediteur)},
                              "to": [{"email": email}], "subject": sujet,
                              "htmlContent": mail(nom, lien, abonnement, portail), "tags": ["livraison"]})
            stripe("POST", f"checkout/sessions/{s['id']}", cle_stripe, **{"metadata[mail_livraison]": time.strftime("%Y-%m-%d %H:%M")})
            envoyes += 1
            print(f"Envoyé : {sujet}")
        if not page.get("has_more"):
            break
        apres = page["data"][-1]["id"]
    print(f"{envoyes} mail(s) de livraison envoyé(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
