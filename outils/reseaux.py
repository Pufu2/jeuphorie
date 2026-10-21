"""Les réseaux sociaux de Jeuphorie, en automatique.

Chaque jour, le calendrier choisit un sujet du site (un article du blog, un jeu offert, une page d'univers, et les kits
quand les ventes sont ouvertes), en suivant les saisons. Pour chaque publication, ce module fabrique :
- un visuel vertical pour Pinterest (1000 × 1500) et un visuel pour Facebook et Instagram (1080 × 1350) ;
- la légende, écrite à partir des textes du site (titre, accroche) et de mots-clés choisis par thème ;
- les flux Pinterest (/flux/pinterest.xml et un flux par tableau thématique), que Pinterest lit tout seul ;
- le visuel de la Story Instagram (1080 × 1920) des jours de publication ;
- la page /reseaux/ (le « lien de la bio » d'Instagram), avec les dernières publications.

La publication sur Facebook et Instagram se fait par outils/publier_reseaux.py, lancé chaque matin par GitHub Actions.
Rien n'est à faire à la main : il suffit d'écrire des articles (déjà automatique) pour nourrir le calendrier.
"""
import datetime as dt
import functools
import html
import re
import textwrap
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
POLICES = Path(__file__).resolve().parent / "polices-visuels"

# premier jour du calendrier ; ne pas changer, sinon tout le calendrier se décale
DEBUT = dt.date(2026, 10, 14)
# jours de publication sur Facebook et Instagram (0 = lundi) ; Pinterest publie tous les jours
JOURS_META = {1, 3, 5}

COULEURS = {
    "fete": ("#CF3424", "#FDE6E1"),
    "plein-air": ("#2D6A43", "#DDEEE2"),
    "saison": ("#C2571A", "#FBEADF"),
    "soleil": ("#F2B21B", "#FFF2CC"),
    "pro": ("#1E2D5A", "#E2E8F6"),
}
ENCRE, PAPIER = "#1A2340", "#FBFAF7"

MOIS_FETES = {"toussaint": {9, 10}, "noel": {11, 12}, "carnaval": {1, 2}, "paques": {3, 4}}

# hashtags d'Instagram : des mots que les parents et les animateurs tapent vraiment, sans accent (les plus suivis),
# en mêlant des mots très suivis et des mots plus précis, où une publication reste visible plus longtemps
COMMUNS = "#activiteenfant #jeuxenfants #ideeactivite #animationenfant"
MOTS_CLES = {
    "anniversaires": "#anniversaireenfant #anniversaire #jeuxanniversaire #ideeanniversaire #gouteranniversaire",
    "grands-jeux": "#grandjeu #jeuxcollectifs #jeuxdexterieur #centredeloisirs #animateur",
    "fetes": "#fetes #activitemanuelle #mercredi #vacancesscolaires #centredeloisirs",
    "kermesse": "#kermesse #fetedecole #jeuxdekermesse #ape #ecole",
    "professionnels": "#animateur #bafa #bafd #accueildeloisirs #colo #directeuraccueil",
    "toussaint": "#toussaint #automne #vacancesdelatoussaint #activiteautomne #jeuxdautomne",
    "noel": "#noel #activitenoel #jeuxdenoel #noelenfants #animationnoel",
    "carnaval": "#carnaval #carnavalenfants #deguisement #mardigras #activitecarnaval",
    "paques": "#paques #chasseauxoeufs #activitepaques #printemps #jeuxdepaques",
}
for _k in MOTS_CLES:
    MOTS_CLES[_k] += " " + COMMUNS

# Pinterest : un tableau par thème, chacun nourri par son flux /flux/pinterest-<tableau>.xml ;
# les autres sujets restent dans le flux général /flux/pinterest.xml
TABLEAUX = {
    "noel": ("noel", "Jeux et activités de Noël pour enfants"),
    "toussaint": ("automne", "Activités d'automne et de la Toussaint"),
    "anniversaires": ("anniversaires", "Anniversaire enfant : jeux et idées"),
    "grands-jeux": ("grands-jeux", "Grands jeux et jeux collectifs"),
    "professionnels": ("animateurs", "Animateurs : BAFA, BAFD, accueil de loisirs"),
}
# ce que cherchent les gens sur Pinterest, ajouté au titre et à la description des épingles
RECHERCHES = {
    "noel": ("jeu de Noël pour enfants", "Activité de Noël pour enfants, à la maison, à l'école ou en centre de loisirs."),
    "toussaint": ("jeu d'automne pour enfants", "Activité d'automne pour les vacances de la Toussaint, dehors ou à l'intérieur."),
    "carnaval": ("jeu de carnaval pour enfants", "Activité de carnaval et de mardi gras pour enfants."),
    "paques": ("jeu de Pâques pour enfants", "Activité de Pâques pour enfants, avec ou sans chasse aux œufs."),
    "anniversaires": ("jeu d'anniversaire enfant", "Idée d'animation pour un anniversaire d'enfant à la maison."),
    "grands-jeux": ("grand jeu pour enfants", "Grand jeu collectif pour enfants, en centre de loisirs, en colo ou à l'école."),
    "kermesse": ("jeu de kermesse", "Idée de stand et de jeu pour la kermesse ou la fête de l'école."),
    "professionnels": ("animation enfants", "Pour les animateurs et directeurs d'accueil de loisirs, BAFA et BAFD."),
}


# ---------------------------------------------------------------- les sujets

def _yaml(chemin):
    return yaml.safe_load(Path(chemin).read_text(encoding="utf-8")) or {}


def _entete(chemin):
    texte = Path(chemin).read_text(encoding="utf-8")
    if texte.startswith("---"):
        _, entete, _ = texte.split("---", 2)
        return yaml.safe_load(entete) or {}
    return {}


def _propre(texte):
    return " ".join(str(texte or "").split())


def sujets(jour):
    """Tous les sujets publiables à la date donnée, dans un ordre stable."""
    return [s for s in _tous() if s["type"] != "article" or s["date"] <= jour]


@functools.lru_cache(maxsize=1)
def _tous():
    config = _yaml(RACINE / "config.yml")
    d = {f.stem: _yaml(f) for f in (RACINE / "donnees").glob("*.yml")}
    univers = {u["id"]: u for u in d["univers"]["univers"]}
    liste = []

    for f in sorted((RACINE / "contenu" / "blog").glob("*.md")):
        e = _entete(f)
        date = e.get("date")
        if isinstance(date, str):
            date = dt.date.fromisoformat(date)
        if e.get("brouillon") or not date:
            continue
        slug = e.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem)
        u = (e.get("univers") or ["fetes"])[0]
        fete = (e.get("fetes") or [None])[0]
        liste.append({"id": f"blog-{slug}", "type": "article", "date": date, "titre": e["titre"],
                      "texte": _propre(e.get("chapo") or e.get("description")), "url": f"/blog/{slug}/",
                      "surtitre": "Nouveau sur le blog", "couleur": univers.get(u, {}).get("couleur", "pro"),
                      "mots": MOTS_CLES.get(fete) or MOTS_CLES.get(u, MOTS_CLES["fetes"]), "mois": MOIS_FETES.get(fete),
                      "theme": fete if fete in MOIS_FETES else u,
                      "intertitres": re.findall(r"^## (.+)$", f.read_text(encoding="utf-8"), re.M)})

    for j in d.get("jeux-fetes", {}).get("jeux", []):
        liste.append({"id": f"fete-{j['id']}", "type": "jeu", "titre": j["nom"], "texte": _propre(j["accroche"]),
                      "url": f"/fetes/{j['fete']}/{j['id']}/", "surtitre": "Jeu offert, règles complètes",
                      "couleur": "saison", "mots": MOTS_CLES.get(j["fete"], MOTS_CLES["fetes"]),
                      "mois": MOIS_FETES.get(j["fete"]), "brut": j, "theme": j["fete"],
                      "detail": (f"Dès {j['age_min']} ans" if j["age_max"] >= 18 else f"{j['age_min']} à {j['age_max']} ans")
                      + f" · {j['joueurs'][0]} à {j['joueurs'][1]} joueurs"})

    for j in d.get("jeux", {}).get("jeux", []):
        if j.get("offert"):
            liste.append({"id": f"jeu-{j['id']}", "type": "jeu", "titre": j["nom"],
                          "texte": _propre(j.get("accroche") or ("Le but : " + j.get("but", "")[:1].lower() + j.get("but", "")[1:] + " " + " ".join(
                              re.split(r"(?<=[.!?]) ", _propre(j.get("organisation")))[:2]))),
                          "url": f"/jeux/{j['id']}/", "brut": j,
                          "detail": f"Dès {j['age_min']} ans · {j['joueurs'][0]} à {j['joueurs'][1]} joueurs · {j['duree']} min",
                          "surtitre": "Grand jeu offert, règles complètes", "couleur": "plein-air",
                          "mots": MOTS_CLES["grands-jeux"], "mois": None, "theme": "grands-jeux"})

    for u in univers.values():
        liste.append({"id": f"univers-{u['id']}", "type": "univers", "titre": u["titre_page"],
                      "texte": _propre(u["accroche"]), "url": u["url"], "surtitre": u.get("public", ""),
                      "couleur": u["couleur"], "mots": MOTS_CLES.get(u["id"], MOTS_CLES["fetes"]),
                      "mois": {2, 3, 4, 5, 6} if u["id"] == "kermesse" else None, "theme": u["id"]})

    if config.get("boutique", {}).get("ventes_actives"):
        for k in d["kits"]["kits"]:
            if k.get("etat") != "pret":
                continue
            u = univers.get(k.get("univers"), {})
            liste.append({"id": f"kit-{k['id']}", "type": "kit", "titre": k.get("titre_seo") or k["titre"],
                          "texte": _propre(k["accroche"]), "url": f"/boutique/{k['id']}/",
                          "surtitre": "Kit à imprimer", "couleur": u.get("couleur", "pro"),
                          "mots": MOTS_CLES.get(k.get("univers"), MOTS_CLES["fetes"]), "mois": None,
                          "theme": k.get("univers"),
                          "couverture": f"img/kits/{k['id']}-couverture.jpg"})
    return liste


def _historique(jusqua):
    """Le calendrier complet, du premier jour à la date donnée : {jour: publication}.

    Le jour où un article paraît, c'est lui. Les autres jours, on prend parmi les sujets de saison celui qui attend
    depuis le plus longtemps : chaque sujet revient à tour de rôle, et sous un visuel différent (3 variantes)."""
    histo, dernier, fois = {}, {}, {}
    jour = DEBUT
    while jour <= jusqua:
        tous = sujets(jour)
        choix = next((s for s in tous if s["type"] == "article" and s["date"] == jour), None)
        if not choix:
            mois_suivant = jour.month % 12 + 1
            candidats = [s for s in tous if (s["type"] != "article" or (jour - s["date"]).days > 21)
                         and (not s["mois"] or jour.month in s["mois"] or mois_suivant in s["mois"])]
            if candidats:
                choix = min(candidats, key=lambda s: dernier.get(s["id"], DEBUT - dt.timedelta(days=9999)))
        if choix:
            n = fois.get(choix["id"], 0)
            histo[jour] = {**choix, "variante": n % 3, "jour": jour}
            fois[choix["id"]] = n + 1
            dernier[choix["id"]] = jour
        jour += dt.timedelta(days=1)
    return histo


def publication(jour):
    """La publication du jour, ou None."""
    return _historique(jour).get(jour)


def calendrier(jusqua, combien=60):
    """Les publications passées, de la plus récente à la plus ancienne."""
    histo = _historique(jusqua)
    return [histo[j] for j in sorted(histo, reverse=True)][:combien]


# ---------------------------------------------------------------- le Reel de la semaine

JOUR_REEL = 6  # dimanche
NOMS_FETES = {"toussaint": "Pour les vacances de la Toussaint", "noel": "Pour Noël", "carnaval": "Pour le carnaval",
              "paques": "Pour Pâques"}


def _phrases(texte, n):
    return " ".join(re.split(r"(?<=[.!?…]) ", _propre(texte))[:n])


def _court(liste, n, maxi=60):
    out = []
    for x in liste or []:
        x = _propre(x).split(" : ")[0].split(", ou")[0]
        if len(x) <= maxi:
            out.append("- " + x.rstrip("."))
        if len(out) == n:
            break
    return out


def cartes_reel(p):
    """Les cartes d'un Reel, tirées des données du site (jeu offert ou article du blog)."""
    j = p.get("brut")
    if j:
        detail = p.get("detail") or ""
        cartes = [{"surtitre": NOMS_FETES.get(j.get("fete"), "Un grand jeu offert"), "titre": p["titre"], "main": detail}]
        if j.get("histoire"):
            cartes.append({"surtitre": "L'histoire", "texte": [_phrases(j["histoire"], 2)]})
        cartes.append({"surtitre": "Le but", "texte": [_propre(j.get("but"))]})
        mat = _court(j.get("materiel"), 3)
        if mat:
            cartes.append({"surtitre": "Le matériel", "texte": mat})
        regles = _court(j.get("regles"), 3, 70)
        if regles:
            cartes.append({"surtitre": "Les règles d'or", "texte": regles})
        if j.get("adapter"):
            cartes.append({"surtitre": "Avec les plus jeunes", "texte": [_phrases(j["adapter"][0], 2)]})
        cartes.append({"surtitre": "C'est gratuit", "titre": "Les règles complètes et le schéma du terrain",
                       "main": "Sur jeuphorie.fr, lien dans la bio"})
        return cartes
    inter = [x for x in p.get("intertitres", []) if len(x) < 60][:4]
    cartes = [{"surtitre": "Sur le blog", "titre": p["titre"]},
              {"surtitre": "En deux mots", "texte": [_phrases(p["texte"], 2)]}]
    if inter:
        cartes.append({"surtitre": "Au sommaire", "texte": ["- " + x for x in inter]})
    cartes.append({"surtitre": "À lire en entier", "titre": "L'article complet, gratuit",
                   "main": "Sur jeuphorie.fr, lien dans la bio"})
    return cartes


def _historique_reels(jusqua):
    histo, dernier, type_avant = {}, {}, "article"
    jour = DEBUT
    while jour <= jusqua:
        if jour.weekday() == JOUR_REEL:
            mois_suivant = jour.month % 12 + 1
            candidats = [s for s in sujets(jour) if s["type"] in ("jeu", "article")
                         and (not s["mois"] or jour.month in s["mois"] or mois_suivant in s["mois"])]
            autre = [s for s in candidats if s["type"] != type_avant]  # un jeu, un article, à tour de rôle
            candidats = autre or candidats
            if candidats:
                choix = min(candidats, key=lambda s: dernier.get(s["id"], DEBUT - dt.timedelta(days=9999)))
                histo[jour] = {**choix, "jour": jour}
                dernier[choix["id"]] = jour
                type_avant = choix["type"]
        jour += dt.timedelta(days=1)
    return histo


def reel_du_jour(jour):
    """Le Reel du jour (le dimanche), ou None."""
    return _historique_reels(jour).get(jour)


def nom_video(p):
    return f"videos/auto-{p['id']}-{p['jour'].isoformat()}.mp4"


# ---------------------------------------------------------------- les légendes

def legende(p, reseau, base):
    lien = base.rstrip("/") + p["url"]
    debut = {"article": "", "jeu": "Un jeu à essayer cette semaine. ", "univers": "", "kit": ""}[p["type"]]
    corps = f"{p['titre']}\n\n{debut}{p['texte']}"
    if p.get("detail"):
        corps += f"\n\n{p['detail']}"
    if reseau == "instagram":
        suite = {"article": "L'article complet est sur jeuphorie.fr (lien dans la bio).",
                 "jeu": "Les règles complètes, gratuites, sont sur jeuphorie.fr (lien dans la bio).",
                 "univers": "Tout est sur jeuphorie.fr (lien dans la bio).",
                 "kit": "Le kit est sur jeuphorie.fr (lien dans la bio)."}[p["type"]]
        return f"{corps}\n\n{suite}\n\n{p['mots']}"
    if reseau == "pinterest":
        sep = " " if p["titre"].rstrip()[-1:] in "?!." else ". "
        phrase = RECHERCHES.get(p.get("theme"), ("", ""))[1]
        detail = f" {p['detail']}." if p.get("detail") else ""
        return _propre(f"{p['titre']}{sep}{p['texte']}{detail} {phrase}")[:490]
    suite = {"article": "À lire ici :", "jeu": "Les règles complètes, gratuites :", "univers": "C'est par ici :",
             "kit": "Le kit :"}[p["type"]]
    return f"{corps}\n\n{suite} {lien}"


# ---------------------------------------------------------------- les visuels

def _police(nom, taille):
    from PIL import ImageFont
    return ImageFont.truetype(str(POLICES / nom), taille)


def _lignes(dessin, texte, police, largeur):
    mots, lignes, cour = texte.split(), [], ""
    for m in mots:
        essai = (cour + " " + m).strip()
        if dessin.textlength(essai, font=police) <= largeur:
            cour = essai
        else:
            if cour:
                lignes.append(cour)
            cour = m
    if cour:
        lignes.append(cour)
    return lignes


def visuel(p, largeur, hauteur, chemin):
    from PIL import Image, ImageDraw
    vif, clair = COULEURS.get(p["couleur"], COULEURS["pro"])
    var = p.get("variante", 0)
    fond = [PAPIER, clair, vif][var]
    texte_c = "#FFFFFF" if var == 2 else ENCRE
    accent = "#FFFFFF" if var == 2 else vif
    im = Image.new("RGB", (largeur, hauteur), fond)
    d = ImageDraw.Draw(im)
    marge = int(largeur * 0.08)
    # la guirlande de fanions du site
    fanions = ["#CF3424", "#F2B21B", "#2D6A43", "#3D5BB8"]
    pas = largeur / 14
    d.line([(0, 18), (largeur, 18)], fill="#4B5675" if var != 2 else "#FFFFFF", width=2)
    for i in range(15):
        x = i * pas
        d.polygon([(x + 6, 18), (x + pas - 6, 18), (x + pas / 2, 18 + pas * 0.75)], fill=fanions[i % 4])
    y = int(hauteur * 0.13)
    # surtitre
    f_sur = _police("Atkinson-700.ttf", int(largeur * 0.034))
    d.text((marge, y), p["surtitre"].upper(), font=f_sur, fill=accent)
    y += int(largeur * 0.075)
    # image de couverture d'un kit, sinon un grand titre
    couverture = p.get("couverture") and (RACINE / "statique" / p["couverture"])
    taille_titre = int(largeur * (0.1 if len(p["titre"]) < 45 else 0.085 if len(p["titre"]) < 70 else 0.072))
    f_titre = _police("Bricolage-800.ttf", taille_titre)
    for ligne in _lignes(d, p["titre"], f_titre, largeur - 2 * marge)[:5]:
        d.text((marge, y), ligne, font=f_titre, fill=texte_c)
        y += int(taille_titre * 1.12)
    y += int(largeur * 0.03)
    d.rectangle([marge, y, marge + int(largeur * 0.16), y + 8], fill=accent if var != 1 else vif)
    y += int(largeur * 0.06)
    reste = hauteur - y - int(hauteur * 0.24)
    if couverture and couverture.exists():
        c = Image.open(couverture).convert("RGB")
        h = min(reste, int(c.height * (largeur * 0.62) / c.width))
        w = int(c.width * h / c.height)
        c = c.resize((w, h))
        im.paste(c, ((largeur - w) // 2, y))
    else:
        f_txt = _police("Atkinson-400.ttf", int(largeur * 0.05))
        interligne = int(largeur * 0.05 * 1.42)
        lignes = _lignes(d, p["texte"], f_txt, largeur - 2 * marge)
        maxi = max(1, (reste - (int(interligne * 1.8) if p.get("detail") else 0)) // interligne)
        if len(lignes) > maxi:
            lignes = lignes[:maxi]
            lignes[-1] = lignes[-1].rstrip(" ,.;:") + "…"
        for ligne in lignes:
            d.text((marge, y), ligne, font=f_txt, fill=texte_c)
            y += interligne
        if p.get("detail"):
            y += int(largeur * 0.02)
            d.text((marge, y), p["detail"], font=_police("Atkinson-700.ttf", int(largeur * 0.038)), fill=accent)
    # l'appel, écrit à la main
    appel = {"article": "À lire sur le blog", "jeu": "Règles complètes, gratuites", "univers": "Tout est sur le site",
             "kit": "Le kit à imprimer"}[p["type"]]
    f_appel = _police("Gochi-400.ttf", int(largeur * 0.062))
    bas = hauteur - int(hauteur * 0.1)
    d.text((marge, bas - int(largeur * 0.16)), appel, font=f_appel, fill=accent if var != 1 else vif)
    # signature
    d.line([(marge, bas - 24), (largeur - marge, bas - 24)], fill=texte_c, width=2)
    f_marque = _police("Bricolage-800.ttf", int(largeur * 0.06))
    d.text((marge, bas), "Jeu", font=f_marque, fill="#CF3424" if var != 2 else "#FFE36E")
    d.text((marge + d.textlength("Jeu", font=f_marque), bas), "phorie", font=f_marque, fill=texte_c)
    f_main = _police("Gochi-400.ttf", int(largeur * 0.04))
    site = "jeuphorie.fr"
    d.text((largeur - marge - d.textlength(site, font=f_main), bas + int(largeur * 0.012)), site, font=f_main, fill=texte_c)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    im.save(chemin, quality=86, optimize=True)


def titre_epingle(p):
    """Le titre de l'épingle : le titre du site, complété par ce que les gens cherchent (100 caractères au plus)."""
    cle = RECHERCHES.get(p.get("theme"), ("", ""))[0]
    titre = p["titre"]
    if p["type"] == "jeu" and cle and cle.split(" ")[0].lower() not in titre.lower():
        titre = f"{titre} : {cle}"
    return titre if len(titre) <= 100 else p["titre"][:100]


def visuel_story(p, chemin):
    """Le visuel d'une Story Instagram (1080 × 1920) : le visuel du post, centré, loin des bords que l'appli recouvre."""
    from PIL import Image
    tmp = Path(chemin).with_suffix(".tmp.jpg")
    visuel(p, 1080, 1440, tmp)
    post = Image.open(tmp).convert("RGB")
    im = Image.new("RGB", (1080, 1920), post.getpixel((5, 700)))
    im.paste(post, (0, 240))
    tmp.unlink()
    chemin.parent.mkdir(parents=True, exist_ok=True)
    im.save(chemin, quality=86, optimize=True)


def nom_visuel(p, format_):
    return f"img/reseaux/{p['id']}-{p['variante']}-{format_}.jpg"


# ---------------------------------------------------------------- fabrication (appelée par build.py)

def fabriquer(sortie, base, aujourdhui=None):
    """Fabrique les visuels, le flux Pinterest ; renvoie les publications récentes pour la page /reseaux/."""
    aujourdhui = aujourdhui or dt.date.today()
    pubs = calendrier(aujourdhui)
    faits = set()
    for p in pubs:
        for fmt, (w, h) in {"pin": (1000, 1500), "post": (1080, 1350)}.items():
            rel = nom_visuel(p, fmt)
            if rel not in faits:
                visuel(p, w, h, Path(sortie) / rel)
                faits.add(rel)
    for p in pubs[:3]:  # la Story ne sert que le jour même
        if p["jour"].weekday() in JOURS_META:
            visuel_story(p, Path(sortie) / nom_visuel(p, "story"))
    base = base.rstrip("/")
    flux = {"": []}  # le flux général, déjà relié à Pinterest, existe toujours
    for p in pubs:
        tableau = TABLEAUX.get(p.get("theme"), ("", ""))[0]
        flux.setdefault(tableau, []).append(p)
    (Path(sortie) / "flux").mkdir(parents=True, exist_ok=True)
    for tableau, liste in flux.items():
        nom = f"pinterest-{tableau}.xml" if tableau else "pinterest.xml"
        (Path(sortie) / "flux" / nom).write_text(_flux(liste, base), encoding="utf-8")
    for theme, (tableau, _) in TABLEAUX.items():  # un tableau pas encore servi : ses sujets, pour démarrer
        if tableau not in flux:
            depart = [{**s, "variante": 0, "jour": DEBUT} for s in sujets(aujourdhui) if s.get("theme") == theme][:3]
            for p in depart:
                visuel(p, 1000, 1500, Path(sortie) / nom_visuel(p, "pin"))
            (Path(sortie) / "flux" / f"pinterest-{tableau}.xml").write_text(_flux(depart, base), encoding="utf-8")
    vus, recentes = set(), []
    for p in pubs:
        if p["id"] not in vus:
            vus.add(p["id"])
            recentes.append({**p, "image": nom_visuel(p, "post")})
    return recentes[:12]


def _flux(pubs, base):
    items = []
    for p in pubs:
        image = f"{base}/{nom_visuel(p, 'pin')}"
        items.append(f"""  <item>
    <title>{html.escape(titre_epingle(p))}</title>
    <link>{base}{p['url']}</link>
    <guid isPermaLink="false">{p['id']}-{p['jour'].isoformat()}</guid>
    <pubDate>{p['jour'].strftime('%a, %d %b %Y 07:00:00 +0000')}</pubDate>
    <description>{html.escape(legende(p, 'pinterest', base))}</description>
    <enclosure url="{image}" length="0" type="image/jpeg"/>
    <media:content url="{image}" medium="image" type="image/jpeg"/>
  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
<channel>
  <title>Jeuphorie : jeux et animations clés en main</title>
  <link>{base}/</link>
  <description>Jeux pour enfants, fêtes, anniversaires et grands jeux, par un directeur adjoint d'accueil de loisirs.</description>
  <language>fr-FR</language>
{chr(10).join(items)}
</channel>
</rss>
"""


if __name__ == "__main__":
    # aperçu du calendrier des 3 prochaines semaines
    jour = dt.date.today()
    histo = _historique(jour + dt.timedelta(days=40))
    for i in range(40):
        j = jour + dt.timedelta(days=i)
        p = histo.get(j)
        meta = "FB/IG" if j.weekday() in JOURS_META else "     "
        print(j.isoformat(), meta, p["id"] if p else "-")
