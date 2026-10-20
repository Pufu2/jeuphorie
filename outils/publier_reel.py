"""Publie un Reel de donnees/reels.yml sur Instagram (Reel) et sur la page Facebook (vidéo).

La vidéo doit déjà être en ligne : statique/videos/<id>.mp4, publiée avec le site.
Lancé à la demande par GitHub Actions : onglet Actions > « Publier le site » > « Run workflow », champ « reel ».
Usage : python3 outils/publier_reel.py <id> [--essai]
        python3 outils/publier_reel.py --auto [--essai]   (le Reel automatique du dimanche, voir outils/reseaux.py)
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
GRAPH = "https://graph.facebook.com"


def appel(chemin, methode="POST", **params):
    donnees = urllib.parse.urlencode(params)
    if methode == "GET":
        req = urllib.request.Request(f"{GRAPH}/{chemin}?{donnees}")
    else:
        req = urllib.request.Request(f"{GRAPH}/{chemin}", data=donnees.encode("utf-8"))
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{chemin} : {e.code} {e.read().decode('utf-8', 'replace')}") from None


def main():
    ident = next((a for a in sys.argv[1:] if not a.startswith("--")), "")
    config = yaml.safe_load((RACINE / "config.yml").read_text(encoding="utf-8"))
    base = config["url"].rstrip("/")
    if "--auto" in sys.argv:
        sys.path.insert(0, str(RACINE / "outils"))
        import datetime as dt
        import reseaux
        p = reseaux.reel_du_jour(dt.date.today())
        if not p:
            print("Pas de Reel automatique aujourd'hui.")
            return 0
        r = {"url": p["url"], "legende": reseaux.legende(p, "instagram", base)}
        video = f"{base}/{reseaux.nom_video(p)}"
    else:
        reels = yaml.safe_load((RACINE / "donnees" / "reels.yml").read_text(encoding="utf-8"))["reels"]
        r = next((x for x in reels if x["id"] == ident), None)
        if not r:
            print(f"Reel inconnu : « {ident} ». Reels disponibles : {', '.join(x['id'] for x in reels)}")
            return 1
        video = f"{base}/videos/{ident}.mp4"
    legende = r["legende"].strip()
    page_id, insta = str(config.get("meta_page_id") or ""), str(config.get("instagram_id") or "")
    jeton = os.environ.get("META_PAGE_TOKEN", "").strip()
    print(f"Reel : {video}")
    if "--essai" in sys.argv:
        print(legende)
        return 0
    if not jeton:
        print("Le secret META_PAGE_TOKEN n'est pas réglé : rien n'est publié.")
        return 1
    erreurs = []
    if insta:
        try:
            c = appel(f"{insta}/media", media_type="REELS", video_url=video, caption=legende,
                      share_to_feed="true", access_token=jeton)
            for _ in range(40):  # Instagram traite la vidéo : jusqu'à 10 minutes
                time.sleep(15)
                etat = appel(c["id"], "GET", fields="status_code,status", access_token=jeton)
                if etat.get("status_code") == "FINISHED":
                    break
                if etat.get("status_code") == "ERROR":
                    raise RuntimeError(f"traitement refusé : {etat.get('status')}")
            else:
                raise RuntimeError("le traitement de la vidéo a pris trop de temps")
            pub = appel(f"{insta}/media_publish", creation_id=c["id"], access_token=jeton)
            print(f"Instagram : Reel publié ({pub.get('id')}).")
        except Exception as e:
            erreurs.append(f"Instagram : {e}")
    if page_id:
        try:
            pub = appel(f"{page_id}/videos", file_url=video, description=legende.replace("(lien dans la bio)", base + r["url"]),
                        access_token=jeton)
            print(f"Facebook : vidéo publiée ({pub.get('id')}).")
        except Exception as e:
            erreurs.append(f"Facebook : {e}")
    if erreurs:
        print("\n".join(erreurs))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
