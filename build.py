#!/usr/bin/env python3
"""Fabrique le site Jeuphorie dans le dossier _site/.

Usage :
    python3 build.py              # version en ligne (adresses propres : /boutique/)
    python3 build.py --apercu     # version d'aperçu (liens relatifs vers index.html)

Dépendances : voir requirements.txt (Markdown, Jinja2, PyYAML).
Le site produit est fait de simples fichiers : il peut être hébergé
sur GitHub Pages ou chez n'importe quel hébergeur.
"""

import argparse
import datetime as dt
import html
import os
import posixpath
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent / "outils"))
from schemas import schema_svg  # noqa: E402
from jinja2 import Environment, FileSystemLoader, select_autoescape

RACINE = Path(__file__).resolve().parent
SORTIE = RACINE / "_site"

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


# ---------------------------------------------------------------- lecture

def lire_yaml(chemin):
    with open(chemin, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def lire_markdown(chemin):
    """Renvoie (entête, corps) d'un fichier Markdown avec entête YAML."""
    texte = Path(chemin).read_text(encoding="utf-8")
    if texte.startswith("---"):
        _, entete, corps = texte.split("---", 2)
        return yaml.safe_load(entete) or {}, corps.strip()
    return {}, texte.strip()


def convertir_markdown(texte):
    md = markdown.Markdown(extensions=["extra", "sane_lists", "smarty", "toc"],
                           extension_configs={
                               "smarty": {"substitutions": {
                                   "left-double-quote": "«&nbsp;",
                                   "right-double-quote": "&nbsp;»"}},
                               "toc": {"permalink": False}})
    rendu = md.convert(texte)
    # [[à compléter : ...]] devient une zone surlignée, bien visible
    rendu = re.sub(r"\[\[(.+?)\]\]",
                   r'<mark class="a-completer">\1</mark>', rendu)
    return rendu


# ---------------------------------------------------------------- outils

def date_fr(d):
    if isinstance(d, str):
        d = dt.date.fromisoformat(d)
    jour = "1er" if d.day == 1 else str(d.day)
    return f"{jour} {MOIS[d.month - 1]} {d.year}"


def temps_de_lecture(texte):
    mots = len(re.findall(r"\w+", texte))
    return max(1, round(mots / 220))


def fichier_de_sortie(url):
    """/boutique/ -> boutique/index.html ; /404.html -> 404.html"""
    if url.endswith("/"):
        return url.lstrip("/") + "index.html"
    return url.lstrip("/")


def faire_lien(depuis, vers, apercu, base=""):
    """Construit un lien. En aperçu, liens relatifs vers les fichiers."""
    if vers.startswith(("http://", "https://", "mailto:", "#")):
        return vers
    ancre = ""
    if "#" in vers:
        vers, ancre = vers.split("#", 1)
        ancre = "#" + ancre
    if not apercu:
        return base.rstrip("/") + vers + ancre
    dossier = posixpath.dirname(fichier_de_sortie(depuis))
    if vers == "/":
        return posixpath.relpath(".", dossier or ".").rstrip("/") + "/" + ancre
    cible = fichier_de_sortie(vers)
    return posixpath.relpath(cible, dossier or ".") + ancre


# ---------------------------------------------------------------- fabrique

class Site:
    def __init__(self, apercu=False):
        self.apercu = apercu
        self.config = lire_yaml(RACINE / "config.yml")
        self.donnees = {f.stem: lire_yaml(f) for f in (RACINE / "donnees").glob("*.yml")}
        self.env = Environment(loader=FileSystemLoader(RACINE / "gabarits"),
                               autoescape=select_autoescape(["html", "xml"]),
                               trim_blocks=True, lstrip_blocks=True)
        self.env.filters["date_fr"] = date_fr
        self.env.tests["contient"] = lambda liste, x: x in (liste or [])
        self.env.globals["schema"] = schema_svg
        self.pages = []  # (url, gabarit, contexte)
        self.articles = self.charger_articles()

    # -- contenus
    def charger_articles(self):
        articles = []
        aujourdhui = dt.date.today()
        for f in sorted((RACINE / "contenu" / "blog").glob("*.md")):
            entete, corps = lire_markdown(f)
            if entete.get("brouillon"):
                continue
            date = entete.get("date")
            if isinstance(date, str):
                date = dt.date.fromisoformat(date)
            if date and date > aujourdhui:
                continue  # programmé pour plus tard
            slug = entete.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem)
            articles.append({
                **entete,
                "date": date,
                "slug": slug,
                "url": f"/blog/{slug}/",
                "corps_md": corps,
                "lecture": temps_de_lecture(corps),
                "ages": entete.get("ages", []),
                "fetes": entete.get("fetes", []),
                "univers": entete.get("univers", []),
            })
        articles.sort(key=lambda a: a["date"], reverse=True)
        return articles

    def kits(self):
        return self.donnees.get("kits", {}).get("kits", [])

    def kit(self, ident):
        return next((k for k in self.kits() if k["id"] == ident), None)

    def jeux(self):
        jeux = self.donnees.get("jeux", {}).get("jeux", [])
        return sorted(jeux, key=lambda j: (j["age_min"], j["nom"].split(" ", 1)[-1].lower()))

    # -- déclaration des pages
    def declarer(self):
        d = self.donnees
        self.ajouter("/", "accueil.html", titre=None)
        self.ajouter("/boutique/", "boutique.html", titre="La boutique",
                     description="Grands jeux et jeux collectifs à télécharger et imprimer, par âge de 6 à 17 ans, et kits d'animation pour les fêtes, les écoles et les accueils de loisirs.")
        self.ajouter("/jeux/", "jeux.html", titre="Tous les grands jeux",
                     description="34 grands jeux et jeux collectifs pour enfants et ados : but du jeu, âge, nombre de joueurs, durée et matériel de chaque jeu.")
        for j in self.jeux():
            self.ajouter(f"/jeux/{j['id']}/", "jeu.html", titre=f"{j['nom']} : règles et organisation",
                         description=f"{j['nom']}, jeu collectif dès {j['age_min']} ans, de {j['joueurs'][0]} à {j['joueurs'][1]} joueurs, {j['duree']} min. {j['but']}"[:300],
                         jeu=j)
        for u in d["univers"]["univers"]:
            if u["id"] == "pro":
                continue
            self.ajouter(u["url"], "univers.html", titre=u["titre_page"],
                         description=u["description"], univers=u)
        pro = next(u for u in d["univers"]["univers"] if u["id"] == "pro")
        self.ajouter(pro["url"], "pro.html", titre=pro["titre_page"],
                     description=pro["description"], univers=pro)
        self.ajouter("/idees/", "idees.html", titre="Idées par âge et par fête",
                     description="Trouvez le bon jeu selon l'âge des enfants ou la fête à préparer : Halloween, Noël, carnaval, Pâques, fête de fin d'année.")
        for groupe in ("ages", "fetes"):
            for idee in d["idees"][groupe]:
                self.ajouter(f"/idees/{idee['slug']}/", "idee.html",
                             titre=idee["titre_page"], description=idee["description"],
                             idee=idee, groupe=groupe)
        self.ajouter("/jeux-gratuits/", "jeux-gratuits.html", titre="3 grands jeux offerts",
                     description="Recevez 3 grands jeux collectifs à imprimer, avec règles, variantes et schéma du terrain : Gendarmes et voleurs, Poules renards vipères, L'épervier gradé.")
        self.ajouter("/blog/", "blog.html", titre="Le carnet d'idées",
                     description="Conseils et idées de jeux pour les anniversaires, les fêtes et les grands jeux, écrits par un directeur d'animation.")
        for a in self.articles:
            self.ajouter(a["url"], "article.html", titre=a["titre"],
                         description=a.get("description", ""), article=a,
                         type_og="article")
        self.ajouter("/contact/", "contact.html", titre="Contact",
                     description="Une question sur un kit, une commande pour une association ou un centre de loisirs ? Écrivez-nous.")
        for f in sorted((RACINE / "contenu" / "pages").glob("*.md")):
            entete, corps = lire_markdown(f)
            self.ajouter(entete["url"], entete.get("gabarit", "page.html"),
                         titre=entete["titre"], description=entete.get("description", ""),
                         corps_md=corps, page_entete=entete)
        self.ajouter("/404.html", "404.html", titre="Page introuvable", indexer=False)

    def ajouter(self, url, gabarit, titre=None, description=None, indexer=True, **extra):
        self.pages.append({"url": url, "gabarit": gabarit, "titre": titre,
                           "description": description or self.config["description"],
                           "indexer": indexer, **extra})

    # -- rendu
    def rendre_page(self, page):
        apercu = self.apercu
        url_page = page["url"]

        def lien(vers):
            return faire_lien(url_page, vers, apercu,
                              self.config.get("chemin_de_base", ""))

        def statique(chemin):
            return lien("/" + chemin.lstrip("/"))

        contexte = {
            "site": self.config,
            "d": self.donnees,
            "page": page,
            "articles": self.articles,
            "kits": self.kits(),
            "jeux": self.jeux(),
            "produits": lambda u: [k for k in self.kits() if k["univers"] == u or u in k.get("aussi", [])],
            "kit": self.kit,
            "lien": lien,
            "statique": statique,
            "apercu": apercu,
            "annee": dt.date.today().year,
            "url_complete": self.config["url"].rstrip("/") + url_page.replace("index.html", ""),
        }
        # Pages en Markdown : le texte peut utiliser {{ site.… }}
        if "corps_md" in page:
            md_rendu = self.env.from_string(page["corps_md"]).render(**contexte)
            contexte["contenu"] = convertir_markdown(md_rendu)
        if page.get("article"):
            a = page["article"]
            contexte["contenu"] = convertir_markdown(
                self.env.from_string(a["corps_md"]).render(**contexte))
        if "contenu" in contexte:
            # liens internes écrits en Markdown, ex. [contact](/contact/)
            contexte["contenu"] = re.sub(
                r'href="(/[^"]*)"', lambda m: f'href="{lien(m.group(1))}"',
                contexte["contenu"])
        return self.env.get_template(page["gabarit"]).render(**contexte)

    def construire(self):
        if SORTIE.exists():
            shutil.rmtree(SORTIE)
        SORTIE.mkdir()
        shutil.copytree(RACINE / "statique", SORTIE, dirs_exist_ok=True)
        self.declarer()
        for page in self.pages:
            cible = SORTIE / fichier_de_sortie(page["url"])
            cible.parent.mkdir(parents=True, exist_ok=True)
            cible.write_text(self.rendre_page(page), encoding="utf-8")
        if not self.apercu:
            self.ecrire_fichiers_seo()
        nom_domaine = self.config.get("nom_de_domaine")
        if nom_domaine and not self.apercu:
            (SORTIE / "CNAME").write_text(nom_domaine + "\n", encoding="utf-8")
        (SORTIE / ".nojekyll").write_text("", encoding="utf-8")
        print(f"{len(self.pages)} pages fabriquées dans {SORTIE}"
              + (" (aperçu)" if self.apercu else ""))

    def ecrire_fichiers_seo(self):
        base = self.config["url"].rstrip("/")
        lignes = ['<?xml version="1.0" encoding="UTF-8"?>',
                  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for p in self.pages:
            if not p["indexer"]:
                continue
            lignes.append(f"  <url><loc>{html.escape(base + p['url'])}</loc></url>")
        lignes.append("</urlset>")
        (SORTIE / "sitemap.xml").write_text("\n".join(lignes) + "\n", encoding="utf-8")
        (SORTIE / "robots.txt").write_text(
            f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
        flux = self.env.get_template("flux.xml").render(
            site=self.config, articles=self.articles[:20],
            maintenant=dt.datetime.now(dt.timezone.utc))
        (SORTIE / "flux.xml").write_text(flux, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apercu", action="store_true",
                        help="liens relatifs, pour regarder le site sans serveur")
    args = parser.parse_args()
    Site(apercu=args.apercu).construire()


if __name__ == "__main__":
    sys.exit(main())
