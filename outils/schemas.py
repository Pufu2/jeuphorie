"""Schémas de terrain des fiches Jeuphorie, dessinés en SVG.

Repère : terrain de 100 x 60. Équipes : a = rouge, b = bleu, c = vert, d = jaune.
Chaque schéma est une liste d'éléments simples ; dessiner() les transforme en SVG.
"""
from html import escape

COUL = {"a": "#CF3424", "b": "#3D5BB8", "c": "#2D6A43", "d": "#E0A100", "n": "#6B7590"}
CLAIR = {"a": "#FBE3DF", "b": "#E1E7F7", "c": "#DCEFE2", "d": "#FFF1C7", "n": "#EEF0F5",
         "mer": "#D6ECF7", "prison": "#EDE7DE"}
NOM_EQ = {"a": "rouges", "b": "bleus", "c": "verts", "d": "jaunes", "n": "assis"}


def _txt(x, y, t, taille=3.2, coul="#1A2340", ancre="middle", gras=False, italique=False):
    poids = ' font-weight="700"' if gras else ""
    style = ' font-style="italic"' if italique else ""
    return (f'<text x="{x}" y="{y}" font-size="{taille}" fill="{coul}" text-anchor="{ancre}"'
            f' font-family="Poppins, sans-serif"{poids}{style}>{escape(t)}</text>')


def dessiner(elements, legende=True):
    out = []
    utilises = set()
    noms = dict(NOM_EQ)
    for el in elements:
        if el[0] == "legende":
            if el[1] is None:
                legende = False
            else:
                noms.update(el[1])
    defs = ('<defs><marker id="pointe" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" '
            'markerHeight="5" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#1A2340"/></marker></defs>')
    out.append('<rect x="0.5" y="0.5" width="99" height="59" rx="1.5" fill="#F4F7EF" stroke="#1A2340" stroke-width="0.6"/>')
    for e in elements:
        t = e[0]
        if t == "zone":
            _, x, y, w, h, s, lab = e
            fond = CLAIR.get(s, CLAIR["n"])
            bord = COUL.get(s, "#9AA3B8")
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fond}" stroke="{bord}" '
                       f'stroke-width="0.35" stroke-dasharray="1.2 0.8"/>')
            if lab:
                lignes = lab.split("\n")
                taille = min(2.9, (w - 1.6) / (max(len(l) for l in lignes) * 0.62))
                for i, l in enumerate(lignes):
                    out.append(_txt(x + w / 2, y + h / 2 + 1 + (i - (len(lignes) - 1) / 2) * (taille * 1.25), l, round(taille, 2),
                                    COUL.get(s, "#4B5675"), gras=True))
        elif t == "milieu":
            if e[1] == "v":
                out.append('<line x1="50" y1="1" x2="50" y2="59" stroke="#1A2340" stroke-width="0.45" stroke-dasharray="2 1.2"/>')
            else:
                out.append('<line x1="1" y1="30" x2="99" y2="30" stroke="#1A2340" stroke-width="0.45" stroke-dasharray="2 1.2"/>')
        elif t == "ligne":
            _, x1, y1, x2, y2 = e
            out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1A2340" stroke-width="0.45" stroke-dasharray="2 1.2"/>')
        elif t == "filet":
            out.append('<line x1="50" y1="2" x2="50" y2="58" stroke="#1A2340" stroke-width="1.1"/>')
            out.append(_txt(52, 6, "filet", 2.6, "#4B5675", "start", italique=True))
        elif t == "j":
            _, x, y, c = e[:4]
            lab = e[4] if len(e) > 4 else ""
            utilises.add(c)
            out.append(f'<circle cx="{x}" cy="{y}" r="2.1" fill="{COUL[c]}" stroke="#FFFFFF" stroke-width="0.5"/>')
            if lab:
                out.append(_txt(x, y + 1.05, lab, 2.4, "#FFFFFF", gras=True))
        elif t == "plot":
            _, x, y, c = e
            out.append(f'<polygon points="{x},{y-2.2} {x+1.9},{y+1.6} {x-1.9},{y+1.6}" fill="{COUL.get(c, "#E07B00")}" stroke="#1A2340" stroke-width="0.3"/>')
        elif t == "cerceau":
            _, x, y = e[:3]
            r = e[3] if len(e) > 3 else 2.6
            out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#E07B00" stroke-width="0.6"/>')
        elif t == "drapeau":
            _, x, y, c = e
            out.append(f'<line x1="{x}" y1="{y+3}" x2="{x}" y2="{y-3}" stroke="#1A2340" stroke-width="0.5"/>'
                       f'<polygon points="{x},{y-3} {x+4},{y-1.8} {x},{y-0.6}" fill="{COUL[c]}"/>')
        elif t == "balle":
            _, x, y = e
            out.append(f'<circle cx="{x}" cy="{y}" r="1.2" fill="#FFFFFF" stroke="#1A2340" stroke-width="0.45"/>')
        elif t == "fleche":
            _, x1, y1, x2, y2 = e
            out.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="#1A2340" stroke-width="0.45" fill="none" marker-end="url(#pointe)"/>')
        elif t == "courbe":
            _, x1, y1, cx, cy, x2, y2 = e
            out.append(f'<path d="M{x1} {y1} Q{cx} {cy} {x2} {y2}" stroke="#1A2340" stroke-width="0.45" fill="none" marker-end="url(#pointe)"/>')
        elif t == "txt":
            _, x, y, s = e[:4]
            taille = e[4] if len(e) > 4 else 3
            out.append(_txt(x, y, s, taille, "#1A2340", italique=True))
        elif t == "panier":
            _, x, y = e[:3]
            lab = e[3] if len(e) > 3 else ""
            out.append(f'<rect x="{x-3}" y="{y-0.5}" width="6" height="1" fill="#1A2340"/>'
                       f'<circle cx="{x}" cy="{y+2.2}" r="2" fill="none" stroke="#E07B00" stroke-width="0.7"/>')
            if lab:
                out.append(_txt(x, y - 2, lab, 2.7, "#1A2340", gras=True))
        elif t == "but":
            _, x, y, cote = e
            dx = -2.5 if cote == "g" else 2.5
            out.append(f'<rect x="{min(x, x+dx)}" y="{y-6}" width="2.5" height="12" fill="none" stroke="#1A2340" stroke-width="0.7"/>')
        elif t == "arbitre":
            _, x, y = e
            out.append(f'<circle cx="{x}" cy="{y}" r="2.1" fill="#1A2340"/>' + _txt(x, y + 5.4, "arbitre", 2.5, "#4B5675", italique=True))
        elif t == "base":
            _, x, y, lab = e
            out.append(f'<rect x="{x-2.4}" y="{y-2.4}" width="4.8" height="4.8" fill="#FFFFFF" stroke="#1A2340" stroke-width="0.5" transform="rotate(45 {x} {y})"/>')
            if lab:
                out.append(_txt(x, y + 6.2, lab, 2.5, "#4B5675", italique=True))
    leg = ""
    if legende and utilises:
        morceaux = [f'<span class="leg"><i style="background:{COUL[c]}"></i>{noms[c]}</span>' for c in sorted(utilises)]
        leg = '<div class="legende">' + "".join(morceaux) + "</div>"
    return (f'<svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg" role="img">{defs}'
            + "".join(out) + "</svg>" + leg)


def deux_camps(nb=5, marge=8):
    """Joueurs rouges à gauche, bleus à droite."""
    els = []
    for i in range(nb):
        y = 10 + i * (40 / max(1, nb - 1))
        els.append(("j", 50 - marge - (i % 2) * 9, y, "a"))
        els.append(("j", 50 + marge + (i % 2) * 9, y, "b"))
    return els


S = {}

S["balle-bouclier"] = [("milieu", "v"), ("drapeau", 5, 30, "a"), ("drapeau", 93, 30, "b"),
    *deux_camps(5, 10), ("zone", 44, 24, 12, 12, "n", "touchés"), ("arbitre", 50, 44),
    ("txt", 25, 57, "camp des rouges"), ("txt", 75, 57, "camp des bleus")]

S["ballon-chasseur"] = [("legende", {"a": "chasseurs", "b": "joueurs libres"}), ("j", 30, 20, "a", "C"), ("j", 66, 40, "a", "C"), ("balle", 33, 18),
    *[("j", x, y, "b") for x, y in [(15, 10), (45, 12), (80, 15), (20, 45), (50, 30), (85, 48), (60, 52), (40, 48), (72, 25)]],
    ("fleche", 34, 19, 46, 28), ("txt", 50, 57, "C = chasseur : un joueur touché devient chasseur")]

S["ballon-prisonnier"] = [("zone", 2, 2, 12, 56, "prison", "prison\ndes bleus"), ("zone", 86, 2, 12, 56, "prison", "prison\ndes rouges"),
    ("ligne", 14, 1, 14, 59), ("ligne", 86, 1, 86, 59), ("milieu", "v"),
    *[("j", 22 + (i % 2) * 12, 10 + i * 10, "a") for i in range(5)],
    *[("j", 66 + (i % 2) * 12, 10 + i * 10, "b") for i in range(5)],
    ("j", 92, 22, "a"), ("j", 8, 40, "b"), ("balle", 46, 30), ("fleche", 40, 28, 62, 22)]

S["beret"] = [("ligne", 15, 1, 15, 59), ("ligne", 85, 1, 85, 59),
    *[("j", 9, 8 + i * 11, "a", str(i + 1)) for i in range(5)],
    *[("j", 91, 8 + i * 11, "b", str(5 - i)) for i in range(5)],
    ("plot", 50, 30, "d"), ("txt", 50, 37, "béret"), ("fleche", 12, 30, 45, 30), ("fleche", 88, 52, 55, 32),
    ("txt", 50, 8, "« Le 3 ! »", 3.4), ("txt", 50, 57, "au moins 10 m entre les deux camps")]

S["relais-des-epis"] = [*[e for k, y in enumerate([15, 45]) for e in (
        [("zone", 8, y - 5, 8, 10, "a" if k == 0 else "b", "boîte")]
        + [("j", 4, y + d, "a" if k == 0 else "b") for d in (-3, 3)]
        + [("plot", 26 + i * 7, y, "a" if k == 0 else "b") for i in range(10)])],
    ("fleche", 17, 15, 24, 15), ("fleche", 17, 45, 24, 45), ("txt", 19, 30, "5 à 10 m"), ("txt", 64, 30, "un épi tous les 2 m")]

S["ballon-anglais"] = [("milieu", "v"),
    *[("j", 14 + i * 5.5, 20, "a") for i in range(6)], *[("j", 58 + i * 5.5, 40, "b") for i in range(6)],
    ("j", 40, 48, "a", "L"), ("j", 60, 12, "b", "L"), ("courbe", 40, 45, 60, 30, 80, 46), ("courbe", 60, 15, 40, 26, 20, 14),
    ("txt", 50, 57, "L = lanceur ; chaque équipe fait passer le ballon reçu dans sa file", 2.7)]

S["gendarmes-voleurs"] = [("zone", 2, 2, 18, 56, "a", ""), ("txt", 11, 9, "banque"), ("zone", 80, 2, 18, 56, "a", "camp\ndes voleurs"),
    ("zone", 20, 2, 60, 56, "b", ""), ("txt", 50, 8, "zone des gendarmes"),
    *[("plot", 7 + (i % 3) * 4.5, 20 + (i // 3) * 8, "d") for i in range(9)],
    *[("cerceau", x, y) for x, y in [(33, 18), (45, 42), (55, 22), (66, 40), (38, 52)]],
    *[("j", x, y, "b") for x, y in [(30, 30), (50, 32), (62, 14), (72, 50), (44, 14)]],
    ("j", 24, 28, "a"), ("j", 45, 42, "a"), ("fleche", 26, 28, 43, 41), ("txt", 50, 57, "cerceaux = cachettes")]

S["six-planetes"] = [("milieu", "v"), *[("plot", 8, y, "a") for y in (14, 30, 46)], *[("plot", 92, y, "b") for y in (14, 30, 46)],
    *deux_camps(4, 12), ("balle", 50, 20), ("balle", 50, 42), ("fleche", 64, 26, 88, 16), ("txt", 50, 57, "3 planètes par équipe")]

S["passe-a-5"] = [*[("cerceau", 8 + (i % 8) * 12 + (6 if (i // 8) % 2 else 0), 8 + (i // 8) * 14) for i in range(31) if 8 + (i % 8) * 12 + (6 if (i // 8) % 2 else 0) < 96],
    ("j", 20, 8, "a"), ("j", 32, 22, "a"), ("j", 50, 36, "a"), ("j", 26, 22, "b"), ("j", 44, 36, "b"),
    ("j", 68, 22, "c"), ("j", 80, 36, "c"), ("j", 74, 8, "d"), ("j", 86, 22, "d"),
    ("fleche", 21, 10, 31, 20), ("fleche", 34, 24, 48, 34), ("txt", 50, 57, "plusieurs matchs en même temps, sur les mêmes cerceaux")]

S["poules-renards-viperes"] = [("legende", {"a": "poules", "b": "vipères", "c": "renards"}), ("zone", 40, 2, 20, 12, "a", "poules"), ("zone", 4, 44, 20, 12, "c", "renards"), ("zone", 76, 44, 20, 12, "b", "vipères"),
    ("courbe", 61, 9, 82, 18, 86, 42), ("txt", 86, 26, "attrapent", 2.8),
    ("courbe", 75, 52, 50, 60, 25, 52), ("txt", 50, 54, "attrapent", 2.8),
    ("courbe", 14, 43, 18, 18, 39, 9), ("txt", 14, 26, "attrapent", 2.8),
    ("j", 50, 26, "a"), ("j", 30, 36, "c"), ("j", 68, 34, "b")]

S["beret-4-equipes"] = [("plot", 46, 30, "d"), ("plot", 50, 26, "d"), ("plot", 54, 31, "d"),
    *[("j", 30 + i * 10, 6, "a", str(i + 1)) for i in range(5)], *[("j", 30 + i * 10, 54, "b", str(5 - i)) for i in range(5)],
    *[("j", 12, 12 + i * 9, "c", str(i + 1)) for i in range(5)], *[("j", 88, 12 + i * 9, "d", str(5 - i)) for i in range(5)],
    ("fleche", 50, 9, 50, 23), ("fleche", 50, 51, 50, 34), ("fleche", 15, 30, 42, 30), ("fleche", 85, 30, 58, 31)]

S["rapetou"] = [("milieu", "v"), ("plot", 8, 18, "a"), ("plot", 8, 42, "a"), ("plot", 92, 18, "b"), ("plot", 92, 42, "b"),
    ("j", 40, 30, "a"), ("j", 60, 30, "b"), ("j", 42, 14, "a"), ("j", 42, 46, "a"), ("j", 58, 14, "b"), ("j", 58, 46, "b"),
    ("fleche", 44, 14, 88, 17), ("fleche", 56, 46, 12, 42), ("txt", 25, 57, "les rouges défendent ici"), ("txt", 75, 57, "les bleus défendent ici")]

S["foot-quilles"] = [("milieu", "v"),
    *[e for y in (14, 30, 46) for e in (("cerceau", 7, y, 3.6), ("plot", 7, y, "a"), ("cerceau", 93, y, 3.6), ("plot", 93, y, "b"))],
    ("j", 30, 15, "a", "1"), ("j", 36, 22, "a", "1"), ("j", 64, 18, "b", "1"), ("j", 30, 40, "a", "2"), ("j", 66, 44, "b", "2"), ("j", 70, 38, "b", "2"),
    ("balle", 48, 18), ("balle", 52, 42), ("txt", 50, 57, "le ballon 1 n'est joué que par les groupes 1")]

S["six-quilles"] = [("milieu", "v"), *[("plot", 92, y, "a") for y in (14, 30, 46)], *[("plot", 8, y, "b") for y in (14, 30, 46)],
    *deux_camps(4, 11), ("fleche", 64, 16, 88, 14), ("txt", 25, 57, "défense des rouges"), ("txt", 75, 57, "défense des bleus")]

S["barre"] = [("zone", 6, 2, 88, 10, "a", "camp des rouges"), ("zone", 6, 48, 88, 10, "b", "camp des bleus"),
    ("zone", 80, 14, 16, 9, "prison", "prison"), ("zone", 4, 37, 16, 9, "prison", "prison"),
    ("j", 40, 40, "a"), ("j", 42, 22, "b"), ("courbe", 42, 38, 38, 26, 42, 14), ("fleche", 44, 24, 42, 37), ("txt", 64, 32, "le joueur défié a « barre » sur celui qui l'a défié", 2.6)]

S["duel-au-panier"] = [("legende", {"a": "avec un ballon", "b": "en attente"}), ("panier", 50, 6), ("ligne", 38, 22, 62, 22), ("txt", 70, 24, "lancers francs", 2.6),
    *[("j", 50, 28 + i * 6, "a" if i < 2 else "b", str(i + 1)) for i in range(5)], ("balle", 53, 27), ("balle", 53, 33),
    ("fleche", 47, 26, 49, 11)]

S["duel-au-panier-geant"] = [("legende", None), ("panier", 18, 10, "panier 1"), ("panier", 50, 10, "panier 2"), ("panier", 82, 10, "panier 3"),
    *[("j", x, 28 + k * 6, "a") for x in (18, 50, 82) for k in range(3)],
    ("fleche", 76, 50, 56, 50), ("txt", 66, 47, "monte", 2.8), ("fleche", 24, 56, 44, 56), ("txt", 34, 53, "descend", 2.8)]

S["balle-au-capitaine"] = [("milieu", "v"), ("cerceau", 6, 30, 4.2), ("j", 6, 30, "a", "K"), ("cerceau", 94, 30, 4.2), ("j", 94, 30, "b", "K"),
    *deux_camps(4, 14), ("balle", 68, 22), ("fleche", 70, 23, 90, 29), ("txt", 50, 57, "K = capitaine, qui reste dans son cerceau")]

S["epervier-grade"] = [("zone", 2, 2, 12, 56, "a", "camp\ndes rouges"), ("zone", 86, 2, 12, 56, "b", "camp\ndes bleus"),
    *[("j", 22 + (i % 2) * 6, 10 + i * 10, "a") for i in range(5)], *[("j", 78 - (i % 2) * 6, 10 + i * 10, "b") for i in range(5)],
    ("fleche", 30, 20, 70, 28), ("fleche", 70, 40, 30, 32), ("arbitre", 50, 50), ("txt", 50, 8, "chacun garde une carte secrète")]

_bases = [("zone", 2, 22, 12, 16, "a", "attente"), ("cerceau", 50, 30, 4.4), ("txt", 50, 37.5, "chien", 2.6),
    ("base", 22, 48, "frappe"), ("base", 82, 48, "base 1"), ("base", 82, 10, "base 2"), ("base", 22, 10, "base 3"),
    ("fleche", 27, 48, 77, 48), ("fleche", 82, 43, 82, 15), ("fleche", 77, 10, 27, 10), ("fleche", 22, 15, 22, 43),
    *[("j", x, y, "b") for x, y in [(40, 22), (64, 30), (56, 44), (70, 18), (36, 38)]], ("j", 50, 30, "b"), ("j", 18, 48, "a")]
S["theque"] = _bases
S["balle-brulee"] = _bases

S["basket"] = [("milieu", "v"), ("panier", 5, 27), ("panier", 95, 27), *deux_camps(4, 12)]
S["basket"] = [("milieu", "v"), ("zone", 1, 18, 16, 24, "n", ""), ("zone", 83, 18, 16, 24, "n", ""),
    ("but", 2, 30, "d"), ("but", 98, 30, "g"), ("txt", 9, 47, "panier", 2.6), ("txt", 91, 47, "panier", 2.6), *deux_camps(4, 12)]

S["rugby-au-toucher"] = [("zone", 1, 1, 10, 58, "a", "en-but\nrouge"), ("zone", 89, 1, 10, 58, "b", "en-but\nbleu"), ("milieu", "v"),
    *deux_camps(4, 13), ("balle", 36, 22), ("fleche", 34, 24, 28, 34), ("txt", 50, 57, "passes vers l'arrière uniquement")]

S["tennis-ballon"] = [("filet",), ("ligne", 4, 1, 4, 59), ("ligne", 96, 1, 96, 59),
    *[("j", x, y, "a") for x, y in [(18, 18), (30, 40), (40, 22)]], *[("j", x, y, "b") for x, y in [(62, 38), (72, 18), (84, 44)]],
    ("balle", 40, 18), ("courbe", 40, 18, 52, 2, 66, 30), ("txt", 16, 57, "ligne de fond", 2.6)]
S["volley"] = [("filet",), *[("j", x, y, "a") for x, y in [(15, 15), (15, 45), (32, 30), (42, 14), (42, 46)]],
    *[("j", x, y, "b") for x, y in [(85, 15), (85, 45), (68, 30), (58, 14), (58, 46)]], ("balle", 42, 10), ("courbe", 42, 10, 52, 0, 64, 24)]

_buts = [("milieu", "v"), ("zone", 1, 18, 12, 24, "n", ""), ("zone", 87, 18, 12, 24, "n", ""), ("but", 2, 30, "d"), ("but", 98, 30, "g"),
    ("txt", 7, 47, "zone", 2.6), ("txt", 93, 47, "zone", 2.6), *deux_camps(4, 13)]
S["handball"] = _buts + [("balle", 64, 22)]
S["hockey"] = _buts + [("balle", 64, 22), ("balle", 36, 40)]

S["ultimate"] = [("zone", 1, 1, 14, 58, "a", "en-but\ndes rouges"), ("zone", 85, 1, 14, 58, "b", "en-but\ndes bleus"),
    *deux_camps(4, 12), ("j", 90, 42, "a"), ("fleche", 62, 30, 88, 41), ("txt", 50, 57, "marquer = attraper le frisbee dans l'en-but adverse")]

S["drapeau-simple"] = [("legende", {"a": "attaquants", "b": "défenseurs", "c": "chevalier"}), ("zone", 2, 2, 16, 56, "a", "camp des\nattaquants"), ("plot", 86, 30, "n"), ("drapeau", 86, 26, "d"),
    *[("j", x, y, "b") for x, y in [(70, 14), (72, 46), (60, 30), (80, 40), (78, 20)]],
    *[("j", x, y, "a") for x, y in [(30, 16), (34, 44), (26, 30)]], ("j", 40, 30, "c", "Ch"), ("fleche", 32, 28, 82, 29),
    ("txt", 50, 57, "Ch = chevalier (chasuble d'une autre couleur)")]

S["balle-americaine"] = [("legende", None), *[("j", x, y, c) for (x, y), c in zip([(12, 12), (30, 40), (50, 18), (70, 46), (86, 14), (40, 52), (62, 30), (20, 30), (80, 32)], "abcdabcda")],
    ("balle", 50, 22), ("fleche", 52, 22, 61, 28), ("txt", 50, 57, "chacun joue pour soi")]
S["balle-assise"] = [("legende", {"a": "debout"}), *[("j", x, y, "a") for x, y in [(15, 15), (35, 40), (55, 18), (78, 44), (88, 15)]],
    *[("j", x, y, "n") for x, y in [(45, 30), (70, 26)]], ("balle", 40, 24), ("balle", 74, 40), ("txt", 57, 37, "assis", 2.6), ("txt", 80, 33, "assis", 2.6)]

S["carre-touche"] = [("legende", {"a": "chasseurs", "b": "joueurs chassés"}), ("ligne", 50, 1, 50, 59), ("ligne", 1, 30, 99, 30),
    *[("zone", x, y, 8, 4, "d", "porte") for x, y in [(21, 28), (71, 28)]], *[("zone", 48, y, 4, 8, "d", "") for y in (11, 41)],
    ("j", 25, 15, "a", "C"), ("j", 75, 15, "a", "C"), ("j", 25, 45, "a", "C"), ("j", 75, 45, "a", "C"),
    *[("j", x, y, "b") for x, y in [(12, 8), (38, 20), (62, 8), (88, 22), (12, 52), (40, 40), (60, 50), (88, 40)]],
    ("balle", 28, 13), ("fleche", 38, 18, 49, 13), ("txt", 50, 57.5, "C = chasseur, qui reste dans son carré", 2.6)]

# Pas de schéma : la disposition dépend du terrain (mer à tracer selon le lieu).
S["drapeau-double"] = None
S["drapeau-double-ruse"] = None


def schema_svg(id_jeu):
    els = S.get(id_jeu)
    if not els:
        return ""
    return dessiner(els)
