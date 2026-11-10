"""Les vraies vidéos du Reel du dimanche : des clips de la banque gratuite Pixabay (licence Pixabay), choisis à la main.

  python3 outils/clips.py chercher "neige forêt" "bougies noël" ...
      (dans GitHub Actions, avec le secret PIXABAY_API_KEY : workflow « Chercher des clips »)
      Affiche, pour chaque recherche, les clips trouvés (une ligne JSON par clip) : identifiant, durée, mots-clés, adresse
      de la petite version de la vidéo et de la page Pixabay.
  python3 outils/clips.py planche <fichier de lignes JSON> <image de sortie>
      Télécharge la petite version de chaque clip et en tire trois images (début, milieu, fin) sur une planche numérotée,
      pour vérifier qu'aucun clip ne montre d'enfant, de visage, de marque ou de texte.

Les clips retenus sont notés dans donnees/reel-clips.yml (date du dimanche → liste de clips). Le site les télécharge
le jour du Reel (outils/reel.py) ; sans clip noté, le Reel garde son fond animé.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
FICHIER = RACINE / "donnees" / "reel-clips.yml"
API = "https://pixabay.com/api/videos/"
AGENT = {"User-Agent": "Mozilla/5.0 (compatible; Jeuphorie/1.0; +https://jeuphorie.fr)"}


def _ouvrir(url, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers=AGENT), timeout=timeout)


def _copier(url, chemin):
    with _ouvrir(url, 120) as r, open(chemin, "wb") as f:
        while bloc := r.read(1 << 16):
            f.write(bloc)


def chercher(requete, combien=12):
    cle = os.environ.get("PIXABAY_API_KEY", "")
    if not cle:
        sys.exit("Le secret PIXABAY_API_KEY manque.")
    params = {"key": cle, "q": requete, "lang": "fr", "video_type": "film", "safesearch": "true",
              "per_page": max(3, min(combien, 200)), "order": "popular"}
    try:
        with _ouvrir(API + "?" + urllib.parse.urlencode(params)) as r:
            donnees = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Pixabay a refusé la recherche « {requete} » : {e.code} {e.read()[:200]!r}")
    clips = []
    for h in donnees.get("hits", []):
        v = h.get("videos", {})
        petit, moyen = v.get("tiny") or v.get("small") or {}, v.get("medium") or v.get("large") or {}
        if not moyen.get("url"):
            continue
        clips.append({"id": h["id"], "requete": requete, "duree": h.get("duration"), "mots": h.get("tags", ""),
                      "auteur": h.get("user", ""), "page": h.get("pageURL", ""), "apercu": petit.get("url", ""),
                      "url": moyen["url"], "taille": [moyen.get("width"), moyen.get("height")]})
    return clips


def planche(source, sortie):
    from PIL import Image, ImageDraw
    clips = [json.loads(l) for l in Path(source).read_text(encoding="utf-8").splitlines() if l.strip().startswith("{")]
    vignettes = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, c in enumerate(clips):
            fichier = Path(tmp) / f"{i}.mp4"
            try:
                _copier(c["apercu"] or c["url"], fichier)
            except Exception as e:  # noqa: BLE001
                print(f"{c['id']} : téléchargement impossible ({e})")
                continue
            duree = float(c.get("duree") or 10)
            images = []
            for k, t in enumerate((0.3, duree / 2, max(0.5, duree - 0.6))):
                img = Path(tmp) / f"{i}-{k}.jpg"
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(fichier),
                                "-frames:v", "1", "-vf", "scale=-2:200", str(img)], check=False)
                if img.exists():
                    images.append(Image.open(img).convert("RGB"))
            vignettes.append((i, c, images))
    largeur = 3 * 360 + 40
    planche = Image.new("RGB", (largeur, 250 * len(vignettes) + 10), "white")
    d = ImageDraw.Draw(planche)
    for rang, (i, c, images) in enumerate(vignettes):
        y = 10 + rang * 250
        d.text((10, y), f"#{i}  id {c['id']}  {c['duree']} s  {c['mots'][:70]}", fill="black")
        for k, im in enumerate(images):
            im.thumbnail((350, 200))
            planche.paste(im, (10 + k * 360, y + 20))
    planche.save(sortie, quality=85)
    print(f"{len(vignettes)} clips sur la planche {sortie}")


def musique_du_jour(jour, p):
    """Le morceau du Reel de ce dimanche (Kevin MacLeod, CC BY 4.0) : l'ambiance suit le sujet, le morceau change
    chaque semaine. Renvoie {titre, debut, url, credit}."""
    import urllib.parse
    d = yaml.safe_load((RACINE / "donnees" / "musiques.yml").read_text(encoding="utf-8"))
    if p.get("theme") == "noel" or jour.month == 12:
        ambiance = "noel"
    else:
        ambiance = "joyeux" if p.get("type") == "jeu" else "doux"
    liste = d["musiques"][ambiance]
    m = dict(liste[jour.isocalendar()[1] % len(liste)])
    m["url"] = d["source"] + urllib.parse.quote(m["titre"] + ".mp3")
    m["credit"] = (f"Musique : « {m['titre']} », Kevin MacLeod (incompetech.com), licence Creative Commons "
                   "Attribution 4.0 (creativecommons.org/licenses/by/4.0)")
    return m


def telecharger_musique(m, dossier):
    """Le fichier du morceau, ou None s'il est indisponible (le Reel garde alors sa musique composée)."""
    chemin = Path(dossier) / ("musique-" + m["titre"].replace(" ", "-") + ".mp3")
    try:
        Path(dossier).mkdir(parents=True, exist_ok=True)
        if not chemin.exists():
            _copier(m["url"], chemin)
        return chemin
    except Exception as e:  # noqa: BLE001
        print(f"Musique « {m['titre']} » indisponible ({e}) : musique composée à la place.")
        return None


def clips_du_jour(jour):
    """Les clips retenus pour le Reel de ce dimanche (liste vide sinon)."""
    if not FICHIER.exists():
        return []
    donnees = yaml.safe_load(FICHIER.read_text(encoding="utf-8")) or {}
    return (donnees.get("reels") or {}).get(jour.isoformat() if isinstance(jour, dt.date) else str(jour)) or []


def telecharger(clips, dossier):
    """Télécharge les clips retenus ; renvoie les chemins des fichiers obtenus (on saute ceux qui échouent)."""
    Path(dossier).mkdir(parents=True, exist_ok=True)
    chemins = []
    for c in clips:
        chemin = Path(dossier) / f"pixabay-{c['id']}.mp4"
        try:
            if not chemin.exists():
                _copier(c["url"], chemin)
            chemins.append(chemin)
        except Exception as e:  # noqa: BLE001
            print(f"Clip {c['id']} indisponible ({e}) : on continue sans lui.")
    return chemins


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["chercher"] and len(args) > 1:
        for q in args[1:]:
            for c in chercher(q):
                print(json.dumps(c, ensure_ascii=False))
    elif args[:1] == ["planche"] and len(args) == 3:
        planche(args[1], args[2])
    else:
        print(__doc__)
