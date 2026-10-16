"""Schémas de terrain des jeux de fêtes (donnees/jeux-fetes.yml), version « Dehors ».

Même repère et mêmes éléments que schemas.py (terrain de 100 x 60).
Ce fichier est propre au site : il n'est pas exporté depuis le dossier des produits.
"""
from schemas import dessiner

S = {}

S["potion-de-la-sorciere"] = [("legende", {"a": "équipe rouge", "b": "équipe bleue", "n": "sorcière"}),
    ("zone", 38, 20, 24, 20, "n", ""), ("txt", 50, 25, "chaudrons", 2.8),
    ("cerceau", 44, 31, 3.2), ("cerceau", 56, 31, 3.2), ("j", 50, 37, "n", "S"),
    *[("plot", x, y, "a") for x, y in [(10, 10), (24, 50), (78, 8), (90, 46)]],
    *[("plot", x, y, "b") for x, y in [(14, 44), (30, 8), (70, 52), (88, 20)]],
    ("j", 22, 22, "a"), ("j", 76, 38, "a"), ("j", 66, 14, "b"), ("j", 30, 40, "b"),
    ("fleche", 24, 24, 41, 30), ("fleche", 64, 16, 55, 27),
    ("txt", 50, 57, "triangles = ingrédients cachés, de la couleur de chaque équipe", 2.6)]

S["reveil-des-fantomes"] = [("legende", {"b": "fantômes", "n": "gardien"}), ("ligne", 12, 1, 12, 59),
    ("txt", 7, 30, "départ", 2.6),
    *[("j", x, y, "b") for x, y in [(8, 10), (20, 18), (34, 28), (16, 36), (44, 44), (26, 50)]],
    ("j", 90, 30, "n", "G"), ("plot", 95, 30, "d"), ("txt", 90, 38, "dos tourné", 2.6),
    ("fleche", 36, 28, 60, 28), ("fleche", 46, 44, 66, 40),
    ("txt", 50, 57, "15 à 20 m ; G = gardien, le triangle jaune = la lanterne", 2.6)]

S["tournee-du-pere-noel"] = [("legende", {"a": "équipe rouge", "b": "équipe bleue"}),
    ("zone", 2, 18, 16, 24, "n", "traîneau"),
    ("j", 8, 24, "a"), ("j", 8, 36, "b"), ("j", 13, 24, "a"), ("j", 13, 36, "b"),
    *[e for x, y, lab in [(40, 10, "1"), (62, 22, "2"), (88, 12, "3"), (46, 46, "4"), (76, 48, "5"), (92, 32, "6")]
      for e in (("base", x, y, ""), ("txt", x, y + 1, lab, 2.6))],
    ("j", 34, 30, "a"), ("fleche", 20, 26, 58, 22), ("fleche", 20, 34, 72, 46),
    ("txt", 50, 57, "losanges = maisons numérotées, entre 5 et 20 m du traîneau", 2.6)]

S["mannequin-du-carnaval"] = [("legende", {"a": "équipe rouge", "b": "équipe bleue"}),
    ("ligne", 14, 1, 14, 59),
    *[("j", 6 + (i % 2) * 4, 8 + i * 3.2, "a") for i in range(5)], ("zone", 1, 26, 12, 6, "a", "malle"),
    *[("j", 6 + (i % 2) * 4, 38 + i * 3.2, "b") for i in range(5)], ("zone", 1, 52, 12, 6, "b", "malle"),
    *[("plot", x, 15, "a") for x in (28, 38, 48)], ("cerceau", 60, 15), ("j", 88, 15, "a", "M"),
    *[("plot", x, 45, "b") for x in (28, 38, 48)], ("cerceau", 60, 45), ("j", 88, 45, "b", "M"),
    ("fleche", 18, 13, 82, 15), ("fleche", 18, 43, 82, 45),
    ("txt", 50, 30, "slalom, puis un saut dans le cerceau", 2.8),
    ("txt", 50, 57, "M = mannequin, à 10 ou 15 m", 2.6)]

S["chasse-aux-oeufs-des-couleurs"] = [("legende", None),
    ("zone", 2, 2, 30, 56, "d", "les petits\n(œufs visibles)"), ("zone", 34, 2, 30, 56, "c", "les moyens"),
    ("zone", 66, 2, 32, 56, "b", "les grands\n(énigmes)"),
    ("txt", 17, 52, "côté maison", 2.6), ("plot", 82, 50, "d"), ("txt", 82, 56, "œuf d'or", 2.6)]

S["voleurs-de-nids"] = [("legende", {"a": "poules rouges", "b": "poules bleues", "c": "poules vertes", "d": "poules jaunes"}),
    ("cerceau", 50, 30, 4.6), ("txt", 50, 38, "panier", 2.6),
    *[("balle", 48 + dx, 29 + dy) for dx, dy in [(0, 0), (2.5, 1.5), (4, -1), (1, 2.5), (2.8, -2)]],
    *[e for x, y, c in [(12, 10, "a"), (88, 10, "b"), (12, 50, "c"), (88, 50, "d")]
      for e in (("cerceau", x, y, 4), ("j", x + (6 if x < 50 else -6), y, c))],
    ("fleche", 18, 12, 44, 27), ("fleche", 82, 48, 55, 33), ("fleche", 82, 12, 18, 48)]


def schema_fete(id_jeu):
    els = S.get(id_jeu)
    return dessiner(els) if els else ""
