"""Affiche l'identifiant du compte Instagram relié à la page Facebook (il n'est pas secret).

Lancé à la main : onglet Actions > « Identifiant Instagram » > « Run workflow ». Le résultat s'affiche dans le journal.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]

config = yaml.safe_load((RACINE / "config.yml").read_text(encoding="utf-8"))
page = str(config.get("meta_page_id") or "")
jeton = os.environ.get("META_PAGE_TOKEN", "").strip()
if not (page and jeton):
    sys.exit("meta_page_id ou le secret META_PAGE_TOKEN manque.")
url = f"https://graph.facebook.com/{page}?" + urllib.parse.urlencode(
    {"fields": "name,instagram_business_account{id,username}", "access_token": jeton})
try:
    with urllib.request.urlopen(url, timeout=60) as r:
        d = json.loads(r.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    sys.exit(f"Erreur : {e.code} {e.read().decode('utf-8', 'replace')}")
ig = d.get("instagram_business_account")
print(f"Page : {d.get('name')}")
print(f"Instagram relié : {ig['username']} (identifiant {ig['id']})" if ig else "Aucun compte Instagram n'est relié à la page.")
