"""Publie la publication du jour sur la page Facebook et le compte Instagram de Jeuphorie.

Lancé par GitHub Actions (.github/workflows/reseaux.yml) à l'heure où le public regarde son téléphone.
Publie aussi une Story Instagram qui renvoie vers la publication.
Les jours de publication sont JOURS_META dans outils/reseaux.py (mardi, jeudi, samedi).

Les identifiants de la page et du compte Instagram sont dans config.yml (meta_page_id, instagram_id).
Le jeton d'accès de la page, lui, est un secret du dépôt (Settings > Secrets and variables > Actions) :
  META_PAGE_TOKEN  le jeton « permanent » de la page, voir docs/RESEAUX-SOCIAUX.md
Sans ce secret, il ne fait rien : Pinterest, lui, se nourrit tout seul du flux /flux/pinterest.xml.

Usage : python3 outils/publier_reseaux.py [--essai]   (--essai affiche sans rien publier)
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reseaux  # noqa: E402

GRAPH = "https://graph.facebook.com"


def appel(chemin, **params):
    donnees = urllib.parse.urlencode(params).encode("utf-8")
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{GRAPH}/{chemin}", data=donnees), timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{chemin} : {e.code} {e.read().decode('utf-8', 'replace')}") from None


def main():
    essai = "--essai" in sys.argv
    jour = dt.date.today()
    if jour.weekday() not in reseaux.JOURS_META:
        print("Pas de publication Facebook ni Instagram aujourd'hui.")
        return 0
    p = reseaux.publication(jour)
    if not p:
        print("Aucun sujet aujourd'hui.")
        return 0
    config = yaml.safe_load((reseaux.RACINE / "config.yml").read_text(encoding="utf-8"))
    base = config["url"].rstrip("/")
    image = f"{base}/{reseaux.nom_visuel(p, 'post')}"
    page_id = os.environ.get("META_PAGE_ID", "").strip() or str(config.get("meta_page_id") or "")
    insta = os.environ.get("INSTAGRAM_ID", "").strip() or str(config.get("instagram_id") or "")
    jeton = os.environ.get("META_PAGE_TOKEN", "").strip()
    print(f"Sujet du jour : {p['id']} ({image})")
    if essai:
        print("--- Facebook\n" + reseaux.legende(p, "facebook", base))
        print("--- Instagram\n" + reseaux.legende(p, "instagram", base))
        return 0
    if not (page_id and jeton):
        print("Le secret META_PAGE_TOKEN n'est pas encore réglé : rien n'est publié.")
        return 0
    erreurs = []
    try:
        r = appel(f"{page_id}/photos", url=image, caption=reseaux.legende(p, "facebook", base), access_token=jeton)
        print(f"Facebook : publié ({r.get('post_id') or r.get('id')}).")
    except Exception as e:
        erreurs.append(f"Facebook : {e}")
    if insta:
        try:
            media = appel(f"{insta}/media", image_url=image, caption=reseaux.legende(p, "instagram", base),
                          access_token=jeton)
            time.sleep(20)  # Instagram prépare l'image avant de la publier
            r = appel(f"{insta}/media_publish", creation_id=media["id"], access_token=jeton)
            print(f"Instagram : publié ({r.get('id')}).")
        except Exception as e:
            erreurs.append(f"Instagram : {e}")
        try:  # la Story renvoie les abonnés vers la publication
            story = appel(f"{insta}/media", media_type="STORIES", image_url=f"{base}/{reseaux.nom_visuel(p, 'story')}",
                          access_token=jeton)
            time.sleep(20)
            r = appel(f"{insta}/media_publish", creation_id=story["id"], access_token=jeton)
            print(f"Instagram : Story publiée ({r.get('id')}).")
        except Exception as e:
            print(f"Instagram : Story non publiée ({e}).")  # sans gravité : la publication est partie
    if erreurs:
        print("\n".join(erreurs))
        print("Le plus souvent, le jeton a expiré ou a été révoqué : voir docs/RESEAUX-SOCIAUX.md.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
