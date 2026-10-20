"""Prévient les moteurs de recherche (IndexNow : Bing, Qwant, DuckDuckGo, Yandex, Seznam) des pages publiées.

Lancé par la publication automatique, juste après la mise en ligne.
Usage : python3 outils/indexnow.py [--tout]
  sans option : seulement les pages dont la date (lastmod) est d'hier ou d'aujourd'hui (les nouveaux articles) ;
  --tout      : toutes les pages du plan du site (après une modification du site).
"""
import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import yaml

RACINE = Path(__file__).resolve().parents[1]


def main():
    config = yaml.safe_load((RACINE / "config.yml").read_text(encoding="utf-8"))
    cle, base = config.get("indexnow_cle"), config["url"].rstrip("/")
    if not cle:
        print("Pas de clé IndexNow dans config.yml : rien à faire.")
        return 0
    with urllib.request.urlopen(f"{base}/sitemap.xml", timeout=30) as r:
        plan = r.read().decode("utf-8")
    entrees = re.findall(r"<loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?", plan)
    if "--tout" in sys.argv:
        adresses = [loc for loc, _ in entrees]
    else:
        hier = (dt.date.today() - dt.timedelta(days=1)).isoformat()
        adresses = [loc for loc, date in entrees if date and date >= hier]
    if not adresses:
        print("Aucune nouvelle page à signaler.")
        return 0
    corps = json.dumps({"host": urlparse(base).netloc, "key": cle, "keyLocation": f"{base}/{cle}.txt",
                        "urlList": adresses[:10000]}).encode("utf-8")
    requete = urllib.request.Request("https://api.indexnow.org/indexnow", data=corps, method="POST",
                                     headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(requete, timeout=30) as r:
            print(f"IndexNow : {len(adresses)} page(s) signalée(s), réponse {r.status}.")
    except Exception as e:  # un refus ponctuel ne doit pas faire échouer la publication
        print(f"IndexNow n'a pas répondu correctement : {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
