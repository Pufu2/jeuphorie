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
import zlib
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
        if j.get("ajoute") and dt.date.fromisoformat(str(j["ajoute"])) > dt.date.today():
            continue  # pas encore paru
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


# ---------------------------------------------------------------- les messages du samedi (Facebook et Instagram)

MESSAGES_DEBUT = dt.date(2026, 10, 31)  # premier samedi des messages ; ne pas changer
MOTS_MESSAGES = "#animateur #animatrice #jeuxenfants #centredeloisirs #activiteenfant #bafa"


def message_du_jour(jour):
    """Le samedi, un message de Rafaël (donnees/messages-reseaux.yml), dans l'ordre ; None une fois la liste épuisée."""
    if jour.weekday() != 5 or jour < MESSAGES_DEBUT:
        return None
    n = (jour - MESSAGES_DEBUT).days // 7
    messages = _yaml(RACINE / "donnees" / "messages-reseaux.yml").get("messages", [])
    if n >= len(messages):
        return None
    m = messages[n]
    # sur le visuel, une phrase du message : le premier paragraphe qui n'est ni une salutation ni une liste
    paras = [x.strip() for x in m["texte"].strip().split("\n\n")]
    extrait = next((x for x in paras[1:] if not re.match(r"(\d\.|-) ", x)), paras[0])
    return {"id": f"message-{m['id']}", "type": "message", "titre": m["titre"], "surtitre": m["surtitre"],
            "texte": extrait, "url": m["url"], "couleur": ["fete", "plein-air", "pro", "saison"][n % 4],
            "variante": n % 3, "jour": jour, "mots": MOTS_MESSAGES, "mois": None, "theme": None,
            "message": m["texte"].strip()}


def publication_meta(jour):
    """Ce qui part sur Facebook et Instagram ce jour-là : le message du samedi, sinon le sujet du jour."""
    return message_du_jour(jour) or publication(jour)


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

INTROS = {
    "jeu": ["Une idée de jeu pour vos prochaines animations.", "Un jeu à ressortir cette semaine.",
            "Si vous cherchez un jeu qui fait bouger tout le monde, celui-ci est fait pour ça.",
            "Voici un jeu qui marche avec presque tous les groupes."],
    "article": ["Sur le blog cette semaine.", "Un article à garder sous le coude.", "À lire avant votre prochaine animation."],
    "univers": ["Un coin du site que vous ne connaissez peut-être pas encore.", "Si vous préparez une animation, c'est par ici."],
    "kit": ["Un kit prêt à imprimer.", "Pour ceux qui veulent tout avoir sous la main."],
}
QUESTIONS = {
    "jeu": ["Vous l'avez déjà essayé ?", "Vous le connaissiez sous un autre nom ?",
            "Si vous le testez, racontez-moi comment ça s'est passé.", "Vous le joueriez avec quel âge ?"],
    "article": ["Et chez vous, comment ça se passe ?", "Vous avez d'autres astuces ? Partagez-les en commentaire.",
                "Dites-moi si cet article vous a servi."],
    "univers": ["Dites-moi en commentaire ce que vous préparez en ce moment.", "Qu'aimeriez-vous y trouver d'autre ?"],
    "kit": ["Une question sur le kit ? Posez-la en commentaire."],
}


def _choisir(liste, p, sel=""):
    """Un choix qui varie d'une publication à l'autre, mais toujours le même pour une publication donnée."""
    return liste[zlib.crc32(f"{p['id']}{p.get('jour')}{sel}".encode()) % len(liste)]


def _lien_bio(texte, lien):
    """Sur Facebook, le lien est cliquable : « lien dans la bio » devient l'adresse."""
    texte = re.sub(r"\s*\((le )?lien (est )?dans la bio\)", f" ({lien})", texte)
    return re.sub(r"Le lien est dans la bio\.", f"Le lien : {lien}", texte)


def legende(p, reseau, base):
    lien = base.rstrip("/") + p["url"]
    if p["type"] == "message":
        if reseau == "instagram":
            return f"{p['message']}\n\n{p['mots']}"
        if reseau == "facebook":
            return _lien_bio(p["message"], lien)
        return _propre(f"{p['titre']}. {p['message']}")[:490]
    if reseau in ("facebook", "instagram"):
        intro = _choisir(INTROS[p["type"]], p, "intro")
        if p["type"] == "article" and p.get("date") == p.get("jour"):
            intro = "Nouvel article sur le blog."
        corps = f"{p['titre']}\n\n{intro} {p['texte']}"
        if p.get("detail"):
            corps += f"\n\n{p['detail']}"
        astuce = (p.get("brut") or {}).get("adapter")
        if astuce:  # les jeux de fêtes ont une adaptation par âge : un vrai conseil d'animateur
            a = _choisir(astuce, p, "astuce")
            corps += ("\n\nPetite astuce pour les " + a if re.match(r"\d", a) else "\n\nPetite astuce : " + a[:1].lower() + a[1:])
        question = _choisir(QUESTIONS[p["type"]], p, "question")
    else:
        corps = f"{p['titre']}\n\n{p['texte']}"
    if reseau == "instagram":
        suite = {"article": "L'article complet est sur jeuphorie.fr (lien dans la bio).",
                 "jeu": "Les règles complètes, gratuites, sont sur jeuphorie.fr (lien dans la bio).",
                 "univers": "Tout est sur jeuphorie.fr (lien dans la bio).",
                 "kit": "Le kit est sur jeuphorie.fr (lien dans la bio)."}[p["type"]]
        return f"{corps}\n\n{suite}\n\n{question}\n\n{p['mots']}"
    if reseau == "pinterest":
        sep = " " if p["titre"].rstrip()[-1:] in "?!." else ". "
        phrase = RECHERCHES.get(p.get("theme"), ("", ""))[1]
        detail = f" {p['detail']}." if p.get("detail") else ""
        signature = " Par Jeuphorie, jeux et animations pour enfants à imprimer."  # le nom, pour qu'on trouve les épingles
        return _propre(f"{p['titre']}{sep}{p['texte']}{detail} {phrase}")[:490 - len(signature)].rstrip() + signature
    suite = {"article": "À lire ici :", "jeu": "Les règles complètes, gratuites :", "univers": "C'est par ici :",
             "kit": "Le kit :"}[p["type"]]
    return f"{corps}\n\n{suite} {lien}\n\n{question}"


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


FANIONS = ["#CF3424", "#F2B21B", "#2D6A43", "#3D5BB8"]
# les mises en page : toutes gardent la guirlande, les polices et la signature du site, mais pas la même composition
MISES = ["classique", "bandeau", "carte", "pastille"]
PASTILLES = {"jeu": "Gratuit", "article": "Blog", "univers": "À découvrir", "kit": "À imprimer"}


def mise_en_page(p):
    """La composition du visuel : elle tourne d'une publication à l'autre (jamais deux fois la même à la suite)."""
    jour = p.get("jour") or DEBUT
    if jour.weekday() in JOURS_META:  # Facebook et Instagram : on compte les jours de publication
        rang = sum(1 for k in range((jour - DEBUT).days + 1) if (DEBUT + dt.timedelta(days=k)).weekday() in JOURS_META)
    else:
        rang = jour.toordinal()
    mise = MISES[rang % len(MISES)]
    if p["type"] == "message" and mise in ("classique", "pastille"):  # les messages de Rafaël : de grands guillemets
        mise = "citation"
    return mise


def _guirlande(d, largeur, y, fil, taille=14):
    pas = largeur / taille
    d.line([(0, y), (largeur, y)], fill=fil, width=2)
    for i in range(taille + 1):
        x = i * pas
        d.polygon([(x + 6, y), (x + pas - 6, y), (x + pas / 2, y + pas * 0.75)], fill=FANIONS[i % 4])


def _signature(d, largeur, hauteur, marge, couleur, jeu="#CF3424"):
    bas = hauteur - int(hauteur * 0.1)
    d.line([(marge, bas - 24), (largeur - marge, bas - 24)], fill=couleur, width=2)
    f_marque = _police("Bricolage-800.ttf", int(largeur * 0.06))
    d.text((marge, bas), "Jeu", font=f_marque, fill=jeu)
    d.text((marge + d.textlength("Jeu", font=f_marque), bas), "phorie", font=f_marque, fill=couleur)
    f_main = _police("Gochi-400.ttf", int(largeur * 0.04))
    d.text((largeur - marge - d.textlength("jeuphorie.fr", font=f_main), bas + int(largeur * 0.012)), "jeuphorie.fr",
           font=f_main, fill=couleur)
    return bas


def _appel(d, p, largeur, x, y, couleur):
    appel = {"article": "À lire sur le blog", "jeu": "Règles complètes, gratuites", "univers": "Tout est sur le site",
             "kit": "Le kit à imprimer", "message": "Rafaël, de Jeuphorie"}[p["type"]]
    d.text((x, y), appel, font=_police("Gochi-400.ttf", int(largeur * 0.062)), fill=couleur)


def _titre(d, p, x, y, largeur_utile, largeur, couleur, echelle=1.0):
    taille = int(largeur * echelle * (0.1 if len(p["titre"]) < 45 else 0.085 if len(p["titre"]) < 70 else 0.072))
    f = _police("Bricolage-800.ttf", taille)
    for ligne in _lignes(d, p["titre"], f, largeur_utile)[:5]:
        d.text((x, y), ligne, font=f, fill=couleur)
        y += int(taille * 1.12)
    return y


def _corps(im, d, p, x, y, largeur_utile, bas, largeur, couleur, accent, main=False):
    """Le texte (ou la couverture d'un kit) et le détail, entre y et bas."""
    from PIL import Image
    couverture = p.get("couverture") and (RACINE / "statique" / p["couverture"])
    if couverture and couverture.exists():
        c = Image.open(couverture).convert("RGB")
        h = min(bas - y, int(c.height * (largeur * 0.62) / c.width))
        w = int(c.width * h / c.height)
        im.paste(c.resize((w, h)), (x + (largeur_utile - w) // 2, y))
        return y + h
    taille = int(largeur * (0.056 if main else 0.05))
    f_txt = _police("Gochi-400.ttf" if main else "Atkinson-400.ttf", taille)
    interligne = int(taille * (1.3 if main else 1.42))
    detail = p.get("detail")
    lignes = _lignes(d, p["texte"], f_txt, largeur_utile)
    maxi = max(0, (bas - y - (int(interligne * 1.8) if detail else 0)) // interligne)
    if len(lignes) > maxi:
        lignes = lignes[:maxi]
        if lignes:
            lignes[-1] = lignes[-1].rstrip(" ,.;:") + "…"
    for ligne in lignes:
        d.text((x, y), ligne, font=f_txt, fill=couleur)
        y += interligne
    if detail:
        y += int(largeur * 0.02)
        d.text((x, y), detail, font=_police("Atkinson-700.ttf", int(largeur * 0.038)), fill=accent)
        y += int(largeur * 0.05)
    return y


def visuel(p, largeur, hauteur, chemin):
    from PIL import Image, ImageDraw
    vif, clair = COULEURS.get(p["couleur"], COULEURS["pro"])
    sombre_sur_vif = p["couleur"] == "soleil"  # le jaune est trop clair pour du texte blanc
    sur_vif = ENCRE if sombre_sur_vif else "#FFFFFF"
    var = p.get("variante", 0)
    mise = mise_en_page(p)
    marge = int(largeur * 0.08)
    utile = largeur - 2 * marge
    f_sur = _police("Atkinson-700.ttf", int(largeur * 0.034))
    pied = hauteur - int(hauteur * 0.1) - int(largeur * 0.16)  # là où commence l'appel écrit à la main

    if mise == "bandeau":
        # un grand bandeau de couleur en haut avec le titre, le texte sur fond clair en dessous
        haut_c = [vif, ENCRE, vif][var]
        texte_haut = "#FFFFFF" if haut_c == ENCRE else sur_vif
        fond = [PAPIER, clair, PAPIER][var]
        im = Image.new("RGB", (largeur, hauteur), fond)
        d = ImageDraw.Draw(im)
        essai = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        y_t = _titre(essai, p, marge, int(hauteur * 0.06) + int(largeur * 0.13), utile, largeur, texte_haut)
        limite = y_t + int(largeur * 0.06)
        d.rectangle([0, 0, largeur, limite], fill=haut_c)
        y = int(hauteur * 0.06)
        d.text((marge, y + int(largeur * 0.05)), p["surtitre"].upper(), font=f_sur,
               fill="#FFE36E" if haut_c == ENCRE else texte_haut)
        _titre(d, p, marge, int(hauteur * 0.06) + int(largeur * 0.13), utile, largeur, texte_haut)
        _guirlande(d, largeur, limite, texte_haut)
        y = limite + int(largeur * 0.13)
        _corps(im, d, p, marge, y, utile, pied - int(largeur * 0.03), largeur, ENCRE, vif if not sombre_sur_vif else ENCRE)
        _appel(d, p, largeur, marge, pied, vif if not sombre_sur_vif else ENCRE)
        _signature(d, largeur, hauteur, marge, ENCRE)

    elif mise == "carte":
        # une fiche claire posée sur un fond de couleur, comme une fiche de jeu sur une table
        fond = [vif, clair, ENCRE][var]
        autour = ENCRE if fond == clair else ("#FFFFFF" if fond == ENCRE else sur_vif)
        im = Image.new("RGB", (largeur, hauteur), fond)
        d = ImageDraw.Draw(im)
        _guirlande(d, largeur, 18, autour)
        x0, y0 = int(largeur * 0.06), int(hauteur * 0.1)
        x1, y1 = largeur - x0, pied - int(largeur * 0.04)
        d.rounded_rectangle([x0 + 10, y0 + 12, x1 + 10, y1 + 12], radius=34, fill=tuple(max(0, int(fond.lstrip("#")[i:i + 2], 16) - 28) for i in (0, 2, 4)))
        d.rounded_rectangle([x0, y0, x1, y1], radius=34, fill=PAPIER)
        dedans = int(largeur * 0.07)
        y = y0 + dedans
        accent = vif if not sombre_sur_vif else ENCRE
        d.text((x0 + dedans, y), p["surtitre"].upper(), font=f_sur, fill=accent)
        y = _titre(d, p, x0 + dedans, y + int(largeur * 0.07), x1 - x0 - 2 * dedans, largeur, ENCRE, 0.85)
        y += int(largeur * 0.025)
        d.rectangle([x0 + dedans, y, x0 + dedans + int(largeur * 0.14), y + 8], fill=accent)
        y += int(largeur * 0.055)
        _corps(im, d, p, x0 + dedans, y, x1 - x0 - 2 * dedans, y1 - dedans // 2, largeur, ENCRE, accent)
        _appel(d, p, largeur, marge, pied + int(largeur * 0.01), autour)
        _signature(d, largeur, hauteur, marge, autour, "#FFE36E" if autour == "#FFFFFF" else "#CF3424")

    elif mise in ("pastille", "citation"):
        # fond uni, une pastille ronde (ou de grands guillemets pour les messages) qui attire l'œil
        fond = [PAPIER, clair, PAPIER][var] if mise == "pastille" else [clair, PAPIER, clair][var]
        im = Image.new("RGB", (largeur, hauteur), fond)
        d = ImageDraw.Draw(im)
        _guirlande(d, largeur, 18, "#4B5675")
        accent = vif if not sombre_sur_vif else ENCRE
        y = int(hauteur * 0.13)
        if mise == "pastille":
            r = int(largeur * 0.1)
            cx, cy = largeur - marge - int(r * 0.6), int(hauteur * 0.09) + int(r * 0.4)
            pastille = Image.new("RGBA", (2 * r + 4, 2 * r + 4), (0, 0, 0, 0))
            dp = ImageDraw.Draw(pastille)
            dp.ellipse([2, 2, 2 * r, 2 * r], fill=vif)
            mot = PASTILLES[p["type"]]
            fp = _police("Gochi-400.ttf", int(r * (0.52 if len(mot) < 8 else 0.36)))
            dp.text((r + 1 - dp.textlength(mot, font=fp) / 2, r - fp.size * 0.62), mot, font=fp, fill=sur_vif)
            pastille = pastille.rotate(12, resample=Image.BICUBIC)
            im.paste(pastille, (cx - r, cy - r), pastille)
            place, f = cx - r * 1.15 - marge, f_sur  # le surtitre s'arrête avant la pastille
            while d.textlength(p["surtitre"].upper(), font=f) > place and f.size > 18:
                f = _police("Atkinson-700.ttf", f.size - 2)
            d.text((marge, y), p["surtitre"].upper(), font=f, fill=accent)
            y += int(largeur * 0.125)
        else:
            d.text((marge - int(largeur * 0.015), y - int(largeur * 0.07)), "«",
                   font=_police("Bricolage-800.ttf", int(largeur * 0.24)), fill=vif)
            d.text((marge + int(largeur * 0.2), y + int(largeur * 0.035)), p["surtitre"].upper(), font=f_sur, fill=accent)
            y += int(largeur * 0.165)
        y = _titre(d, p, marge, y, utile, largeur, ENCRE)
        y += int(largeur * 0.03)
        _guirlande_petite = [(marge + i * 34, y) for i in range(4)]
        for i, (x, yy) in enumerate(_guirlande_petite):  # quatre petits points aux couleurs des fanions
            d.ellipse([x, yy, x + 18, yy + 18], fill=FANIONS[i])
        y += int(largeur * 0.07)
        _corps(im, d, p, marge, y, utile, pied - int(largeur * 0.03), largeur, ENCRE, accent, main=mise == "citation")
        _appel(d, p, largeur, marge, pied, accent)
        _signature(d, largeur, hauteur, marge, ENCRE)

    else:  # classique : la composition d'origine
        fond = [PAPIER, clair, vif][var]
        texte_c = sur_vif if var == 2 else ENCRE
        accent = sur_vif if var == 2 else (vif if not sombre_sur_vif else ENCRE)
        im = Image.new("RGB", (largeur, hauteur), fond)
        d = ImageDraw.Draw(im)
        _guirlande(d, largeur, 18, "#4B5675" if var != 2 else texte_c)
        y = int(hauteur * 0.13)
        d.text((marge, y), p["surtitre"].upper(), font=f_sur, fill=accent)
        y = _titre(d, p, marge, y + int(largeur * 0.075), utile, largeur, texte_c)
        y += int(largeur * 0.03)
        d.rectangle([marge, y, marge + int(largeur * 0.16), y + 8], fill=accent if var != 1 else vif)
        y += int(largeur * 0.06)
        _corps(im, d, p, marge, y, utile, pied - int(largeur * 0.03), largeur, texte_c, accent)
        _appel(d, p, largeur, marge, pied, accent if var != 1 else vif)
        _signature(d, largeur, hauteur, marge, texte_c, "#CF3424" if var != 2 else "#FFE36E")

    chemin = Path(chemin)
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
    im = Image.new("RGB", (1080, 1920), post.getpixel((5, 1430)))
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
    for i in range(3):  # le message du samedi : son visuel et sa Story
        m = message_du_jour(aujourdhui - dt.timedelta(days=i))
        if m:
            visuel(m, 1080, 1350, Path(sortie) / nom_visuel(m, "post"))
            visuel_story(m, Path(sortie) / nom_visuel(m, "story"))
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
