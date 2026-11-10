"""Les visuels Canva des réseaux sociaux, préparés chaque dimanche par la tâche automatique de Claude.

  python3 outils/canva_semaine.py liste [--jours 7]
      Les publications Facebook et Instagram des prochains jours, chacune avec son style (six styles qui tournent),
      le texte à mettre et la consigne (« brief ») à donner à Canva pour le post et pour la Story.
  python3 outils/canva_semaine.py finir <image Canva> <nom du fichier> [--cadrage ajuster|centre|haut|bas]
                                        [--logo x,y,côté | --coin bas-gauche|bas-droite|haut-gauche|haut-droite|aucun]
      Met l'image exportée de Canva au format exact (1080 × 1350 ou 1080 × 1920), y pose le symbole du J (dans le
      carré laissé vide avec --logo, sinon dans un coin), et l'enregistre dans statique/img/reseaux-canva/ sous le nom
      attendu par la publication. --signature x0,y0,x1,y1[,#couleur] réécrit « Jeuphorie » dans cette zone si Canva
      l'a mal écrit (coordonnées de l'image finale).

Les visuels déposés dans statique/img/reseaux-canva/ remplacent les visuels maison (outils/reseaux.py) ; sans eux, la
publication part avec le visuel maison : rien n'est jamais bloqué.
"""
import datetime as dt
import json
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import reseaux  # noqa: E402
from styles import police  # noqa: E402

RACINE = ICI.parent
DOSSIER = RACINE / "statique" / "img" / "reseaux-canva"
SYMBOLE = RACINE / "statique" / "img" / "logo-1024.png"

COMMUN = (
    "Marque : Jeuphorie, site français de jeux et d'animations pour enfants à imprimer (jeuphorie.fr). "
    "Couleurs de la marque, à utiliser franchement : rouge #CF3424, jaune #F2B21B, vert #2D6A43, bleu #3D5BB8, "
    "bleu nuit #1A2340, crème #FBFAF7. Écrire en bas, en petit, le mot « Jeuphorie » en lettres épaisses et arrondies, "
    "comme un titre de bande dessinée, avec une petite vague soulignée. Laisser vide un petit carré dans le coin en bas "
    "à gauche (pour le logo). Aucune photo ni dessin réaliste d'enfant, aucun personnage connu, aucune marque. "
    "Aucun texte ni cadre coupé par les bords de l'image. Tout le texte en français, sans faute, lisible en une seconde sur un téléphone. Jamais d'Halloween."
)

STYLES = {
    "affiche": ("L'affiche choc",
                "Style affiche très graphique qui arrête le défilement : un fond d'une seule couleur vive, une question "
                "ou une accroche ÉNORME en typographie épaisse, une grande illustration simple et symbolique, beaucoup de "
                "contraste, peu de mots."),
    "infographie": ("L'infographie",
                    "Style infographie de magazine de parentalité : fond crème, une frise ou une liste numérotée en "
                    "étapes illustrées de petites icônes, de grosses pastilles colorées pour les numéros. Le genre de "
                    "publication qu'on enregistre."),
    "bd": ("La bande dessinée",
           "Style bande dessinée énergique : fond bleu nuit, un animal ou un objet illustré façon BD qui prend une pose "
           "drôle, des bulles et des éclairs, gros lettrage jaune comme un titre de BD."),
    "quiz": ("Le quiz",
             "Style quiz ou devinette : une grande question au centre (« Devinez… », « Vrai ou faux ? », « Vous "
             "connaissez ? »), deux ou trois réponses dans des cartes colorées, un point d'interrogation géant "
             "illustré. Donne envie de répondre en commentaire. La bonne réponse n'est écrite nulle part ailleurs sur "
             "l'image."),
    "carnet": ("Le carnet d'animateur",
               "Style carnet d'animateur fait main : page de cahier à petits carreaux, écriture manuscrite pour "
               "l'accroche, ruban adhésif, post-it jaune avec le conseil clé, petits dessins au feutre. Chaleureux et "
               "authentique."),
    "contraste": ("L'avant / après",
                  "Style avant / après : l'image coupée en deux, à gauche le problème (gris, terne, une phrase "
                  "courte), à droite la solution (couleurs vives, une phrase courte), une flèche qui relie les deux."),
}
ORDRE = ["affiche", "infographie", "bd", "quiz", "carnet", "contraste"]


def contenu(p):
    """Le texte que la publication doit porter : accroche, points clés, appel à l'action."""
    points = [x for x in p.get("intertitres", []) if x][:4]
    appel = {"article": "À lire sur jeuphorie.fr", "jeu": "Règles complètes gratuites sur jeuphorie.fr",
             "univers": "Tout est sur jeuphorie.fr", "kit": "Le kit est sur jeuphorie.fr",
             "message": "Répondez en commentaire"}.get(p["type"], "jeuphorie.fr")
    return {"surtitre": p.get("surtitre", ""), "titre": p["titre"], "texte": p.get("texte", ""),
            "points": points, "appel": appel}


def _phrase(t):
    """Termine un texte par un seul signe de ponctuation."""
    t = t.strip()
    return t if t[-1:] in ".?!" else t + "."


def _idee(texte, limite=220):
    """Les premières phrases entières du texte, sans dépasser la limite."""
    import re
    phrases, idee = re.split(r"(?<=[.?!])\s+", texte.strip()), ""
    for ph in phrases:
        if idee and len(idee) + len(ph) > limite:
            break
        idee = (idee + " " + ph).strip()
    return _phrase(idee[:limite * 2])


def brief(p, style, format_):
    c = contenu(p)
    nom, description = STYLES[style]
    points = (" Points à faire apparaître, très courts : " + " ; ".join(c["points"]) + ".") if c["points"] else ""
    taille = ("Publication Instagram verticale 4:5 (1080 × 1350)." if format_ == "post"
              else "Story Instagram verticale 9:16 (1080 × 1920), le texte important au centre, rien dans les "
                   "200 pixels du haut et du bas.")
    return (f"{taille} {description} Sujet : {_phrase(c['titre'])} Accroche à réécrire en 3 à 8 mots percutants, sans "
            f"changer le sens : « {c['titre']} ». Idée à faire passer : {_idee(c['texte'])}{points} "
            f"Bouton ou bandeau d'appel : « {c['appel']} ». "
            + (COMMUN if format_ == "post" else COMMUN.replace("dans le coin en bas à gauche",
                                                                "en bas à gauche, au-dessus des 200 pixels du bas")))


def liste(jours=7, depuis=None):
    debut = depuis or dt.date.today()
    sortie, rang = [], 0
    for k in range(jours):
        jour = debut + dt.timedelta(days=k)
        if jour.weekday() not in reseaux.JOURS_META:
            continue
        p = reseaux.publication_meta(jour)
        if not p:
            continue
        # le style tourne d'une publication à l'autre, dans le même ordre d'une semaine à la suivante
        style = ORDRE[((jour - reseaux.DEBUT).days // 2 + rang) % len(ORDRE)]
        rang += 1
        fichiers = {f: Path(reseaux.nom_visuel(p, f)).name for f in ("post", "story")}
        sortie.append({"jour": jour.isoformat(), "id": p["id"], "type": p["type"], "style": style,
                       "nom_style": STYLES[style][0], "contenu": contenu(p), "fichiers": fichiers,
                       "deja_fait": {f: (DOSSIER / n).exists() for f, n in fichiers.items()},
                       "brief_post": brief(p, style, "post"), "brief_story": brief(p, style, "story")})
    return sortie


def signature(im, x0, y0, x1, y1, couleur="#F2B21B"):
    """Efface la zone (fond pris sur son pourtour) et y écrit « Jeuphorie » avec la vague, si Canva l'a mal écrit."""
    from PIL import ImageDraw
    import statistics
    bord = [im.getpixel((x, y)) for x in range(x0, x1, 6) for y in (y0, y1 - 1)] + \
           [im.getpixel((x, y)) for y in range(y0, y1, 6) for x in (x0, x1 - 1)]
    fond = tuple(int(statistics.median(c[i] for c in bord)) for i in range(3))
    d = ImageDraw.Draw(im)
    d.rectangle((x0, y0, x1, y1), fill=fond)
    h = y1 - y0
    taille = int(h * 0.55)
    while True:
        f = police("Bricolage-800.ttf", taille)
        l, t, r, b = d.textbbox((0, 0), "Jeuphorie", font=f)
        if r - l <= (x1 - x0) * 0.92 or taille < 12:
            break
        taille -= 2
    x = x0 + (x1 - x0 - (r - l)) // 2 - l
    y = y0 + int(h * 0.08) - t
    d.text((x, y), "Jeuphorie", font=f, fill=couleur)
    # la petite vague soulignée
    import math
    cx, cy, lw = (x0 + x1) // 2, y + b + int(h * 0.14), (r - l) * 0.42
    pts = [(cx - lw / 2 + k * lw / 40, cy + math.sin(k / 40 * 4 * math.pi) * h * 0.045) for k in range(41)]
    d.line(pts, fill=couleur, width=max(3, int(h * 0.05)), joint="curve")


def finir(source, nom, coin="bas-gauche", cadrage="ajuster", logo=None, sig=None):
    """cadrage : « ajuster » (toute l'image, bords prolongés en flou si besoin), « centre », « haut » ou « bas »
    (rogner). logo : (x, y, côté) en pixels de l'image finale, pour poser le symbole dans le carré laissé vide."""
    from PIL import Image
    w, h = (1080, 1920) if nom.endswith("-story.jpg") else (1080, 1350)
    im = Image.open(source).convert("RGB")
    r = w / h
    if cadrage == "ajuster":
        k = min(w / im.width, h / im.height)
        petit = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        # le fond : l'image elle-même, agrandie et floutée, pour que les bords se prolongent sans trait
        from PIL import ImageFilter
        k2 = max(w / im.width, h / im.height)
        fond = im.resize((round(im.width * k2), round(im.height * k2)), Image.LANCZOS)
        fond = fond.crop(((fond.width - w) // 2, (fond.height - h) // 2, (fond.width - w) // 2 + w,
                          (fond.height - h) // 2 + h)).filter(ImageFilter.GaussianBlur(18))
        fond.paste(petit, ((w - petit.width) // 2, (h - petit.height) // 2))
        im = fond
    else:
        if im.width / im.height > r:
            nw = int(im.height * r)
            im = im.crop(((im.width - nw) // 2, 0, (im.width - nw) // 2 + nw, im.height))
        else:
            nh = int(im.width / r)
            y0 = {"haut": 0, "bas": im.height - nh}.get(cadrage, (im.height - nh) // 2)
            im = im.crop((0, y0, im.width, y0 + nh))
        im = im.resize((w, h), Image.LANCZOS)
    if sig:
        signature(im, *sig)
    if logo:
        x, y, cote = logo
    elif coin != "aucun":
        cote, marge = 96, 34
        x = marge if "gauche" in coin else w - marge - cote
        y = marge if "haut" in coin else h - marge - cote - (150 if h == 1920 else 0)
    if logo or coin != "aucun":
        sym = Image.open(SYMBOLE).convert("RGBA").resize((cote, cote), Image.LANCZOS)
        im.paste(sym, (x, y), sym)
    DOSSIER.mkdir(parents=True, exist_ok=True)
    im.save(DOSSIER / nom, quality=90, optimize=True)
    print(f"{nom} : enregistré ({w} × {h}).")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["liste"]:
        n = int(args[args.index("--jours") + 1]) if "--jours" in args else 7
        print(json.dumps(liste(n), ensure_ascii=False, indent=1))
    elif args[:1] == ["finir"] and len(args) >= 3:
        def opt(nom, defaut=None):
            return args[args.index(nom) + 1] if nom in args else defaut
        logo = tuple(int(v) for v in opt("--logo").split(",")) if opt("--logo") else None
        sig = None
        if opt("--signature"):
            v = opt("--signature").split(",")
            sig = tuple(int(n) for n in v[:4]) + tuple(v[4:5])
        finir(args[1], args[2], opt("--coin", "bas-gauche"), opt("--cadrage", "ajuster"), logo, sig)
    else:
        print(__doc__)
