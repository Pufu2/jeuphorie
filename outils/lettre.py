"""La lettre mensuelle de Jeuphorie, envoyée automatiquement par Brevo le premier mardi du mois.

Elle se compose toute seule à partir du site : le jeu offert le plus récent, les articles du blog parus depuis la
dernière lettre, et le kit de saison quand les ventes sont ouvertes. Aucun texte à écrire.

Réglages : config.yml (brevo_liste : numéro de la liste ; lettre_expediteur : adresse validée dans Brevo)
et le secret GitHub BREVO_API_KEY. Sans eux, rien n'est envoyé.
Usage : python3 outils/lettre.py [--apercu]   (--apercu écrit lettre-apercu.html sans rien envoyer)
"""
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre",
        "décembre"]


def lire(nom):
    return yaml.safe_load((RACINE / "donnees" / f"{nom}.yml").read_text(encoding="utf-8")) or {}


def articles_depuis(debut, fin):
    out = []
    for f in sorted((RACINE / "contenu" / "blog").glob("*.md")):
        texte = f.read_text(encoding="utf-8")
        e = yaml.safe_load(texte.split("---", 2)[1]) or {}
        date = e.get("date")
        if isinstance(date, str):
            date = dt.date.fromisoformat(date)
        if e.get("brouillon") or not date or not (debut <= date <= fin):
            continue
        slug = e.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem)
        out.append({"titre": e["titre"], "texte": e.get("description", ""), "url": f"/blog/{slug}/"})
    return out


def composer(jour):
    config = yaml.safe_load((RACINE / "config.yml").read_text(encoding="utf-8"))
    base = config["url"].rstrip("/")
    jeux = lire("jeux-fetes").get("jeux", [])
    fetes = {f["slug"]: f for f in lire("fetes").get("fetes", [])}
    recents = sorted([j for j in jeux if j.get("ajoute")], key=lambda j: str(j["ajoute"]), reverse=True)
    jeu = recents[0] if recents else None
    articles = articles_depuis(jour - dt.timedelta(days=35), jour)
    saison = next((s for s in lire("saisons").get("saisons", []) if jour.month in s["mois"]), None)
    kit = None
    if config.get("boutique", {}).get("ventes_actives") and saison and saison.get("kit"):
        kit = next((k for k in lire("kits").get("kits", []) if k["id"] == saison["kit"]), None)

    e = html.escape
    bouton = ('<a href="{u}" style="display:inline-block;background:#CF3424;color:#fff;text-decoration:none;'
              'font-weight:bold;padding:12px 22px;border-radius:999px">{t}</a>')
    blocs = []
    if jeu:
        url = f"{base}/fetes/{jeu['fete']}/{jeu['id']}/"
        blocs.append(f'<h2 style="font-size:20px;margin:28px 0 6px">Le jeu offert du mois : {e(jeu["nom"])}</h2>'
                     f'<p style="margin:0 0 6px">{e(jeu["accroche"])}</p>'
                     f'<p style="margin:0 0 14px;color:#4B5675">Dès {jeu["age_min"]} ans · {jeu["joueurs"][0]} à '
                     f'{jeu["joueurs"][1]} joueurs · {jeu["duree"]} minutes · {e(fetes.get(jeu["fete"], {}).get("nom", ""))}</p>'
                     + bouton.format(u=url, t="Les règles complètes"))
    if articles:
        items = "".join(f'<li style="margin:0 0 10px"><a href="{base}{a["url"]}" style="color:#1A2340;font-weight:bold">'
                        f'{e(a["titre"])}</a><br><span style="color:#4B5675">{e(a["texte"])}</span></li>' for a in articles)
        blocs.append(f'<h2 style="font-size:20px;margin:28px 0 8px">À lire sur le blog</h2><ul style="padding-left:18px;margin:0">{items}</ul>')
    if kit:
        blocs.append(f'<h2 style="font-size:20px;margin:28px 0 6px">{e(saison["titre"])}</h2>'
                     f'<p style="margin:0 0 14px">{e(kit["accroche"])}</p>'
                     + bouton.format(u=f"{base}/boutique/{kit['id']}/", t=f"Voir le kit, {kit['prix']} €"))
    if not blocs:
        return None
    mois = f"{MOIS[jour.month - 1]} {jour.year}"
    sujet = f"Jeuphorie, {MOIS[jour.month - 1]} : " + (jeu["nom"] if jeu else articles[0]["titre"])
    corps = f"""<!doctype html><html lang="fr"><body style="margin:0;background:#FBFAF7">
<div style="max-width:600px;margin:0 auto;padding:24px 20px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.5;color:#1A2340">
<p style="font-size:26px;font-weight:bold;margin:0"><span style="color:#CF3424">Jeu</span>phorie</p>
<p style="margin:2px 0 22px;color:#4B5675">La lettre de {mois}</p>
<p style="margin:0">Bonjour,</p>
<p style="margin:10px 0 0">Voici ce que je vous ai préparé ce mois-ci : de quoi animer un groupe d'enfants sans rien acheter, et quelques lectures utiles.</p>
{''.join(blocs)}
<p style="margin:30px 0 0">Bonnes animations !<br>Rafaël, de Jeuphorie</p>
<hr style="border:none;border-top:1px solid #E2DED5;margin:28px 0 14px">
<p style="font-size:13px;color:#4B5675;margin:0">Vous recevez cette lettre parce que vous vous êtes inscrit sur jeuphorie.fr.
<a href="{{{{ unsubscribe }}}}" style="color:#4B5675">Se désinscrire</a> en un clic.</p>
</div></body></html>"""
    return {"sujet": sujet, "html": corps, "nom": f"Lettre {mois}"}


def appel(chemin, cle, corps):
    req = urllib.request.Request(f"https://api.brevo.com/v3/{chemin}", data=json.dumps(corps).encode("utf-8"),
                                 headers={"api-key": cle, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            texte = r.read().decode("utf-8")
            return json.loads(texte) if texte else {}
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"{chemin} : {err.code} {err.read().decode('utf-8', 'replace')}") from None


def main():
    jour = dt.date.today()
    lettre = composer(jour)
    if not lettre:
        print("Rien de neuf à envoyer ce mois-ci.")
        return 0
    if "--apercu" in sys.argv:
        (RACINE / "lettre-apercu.html").write_text(lettre["html"], encoding="utf-8")
        print(f"Sujet : {lettre['sujet']}\nAperçu : lettre-apercu.html")
        return 0
    config = yaml.safe_load((RACINE / "config.yml").read_text(encoding="utf-8"))
    cle = os.environ.get("BREVO_API_KEY", "").strip()
    liste, expediteur = config.get("brevo_liste"), config.get("lettre_expediteur")
    if not (cle and liste and expediteur):
        print("Brevo n'est pas encore réglé (BREVO_API_KEY, brevo_liste, lettre_expediteur) : rien n'est envoyé.")
        return 0
    c = appel("emailCampaigns", cle, {"name": lettre["nom"], "subject": lettre["sujet"],
                                       "sender": {"name": "Rafaël de Jeuphorie", "email": expediteur},
                                       "htmlContent": lettre["html"], "recipients": {"listIds": [int(liste)]}})
    appel(f"emailCampaigns/{c['id']}/sendNow", cle, {})
    print(f"Lettre envoyée : « {lettre['sujet']} » (campagne {c['id']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
