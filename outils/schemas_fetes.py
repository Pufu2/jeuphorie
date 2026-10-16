"""Schémas de terrain des jeux de fêtes (donnees/jeux-fetes.yml), version « Dehors ».

Même repère et mêmes éléments que schemas.py (terrain de 100 x 60).
Ce fichier est propre au site : il n'est pas exporté depuis le dossier des produits.
"""
from schemas import dessiner

S = {}

S["ecureuils-reserve-hiver"] = [("legende", {"a": "écureuils rouges", "b": "écureuils bleus", "c": "écureuils verts", "n": "renard"}),
    ("cerceau", 6, 30, 4.4), ("txt", 6, 38, "nid", 2.6), ("cerceau", 94, 30, 4.4), ("txt", 94, 38, "nid", 2.6),
    ("cerceau", 50, 6, 4.4), ("txt", 50, 14, "nid", 2.6),
    *[("balle", x, y) for x, y in [(22, 14), (30, 44), (40, 24), (56, 40), (64, 18), (72, 50), (36, 52), (80, 12), (46, 34), (26, 30)]],
    ("j", 9, 24, "a"), ("j", 30, 40, "a"), ("j", 91, 24, "b"), ("j", 66, 22, "b"), ("j", 54, 8, "c"), ("j", 44, 30, "c"),
    ("j", 52, 46, "n", "R"), ("fleche", 32, 38, 11, 31), ("fleche", 64, 20, 89, 28),
    ("txt", 50, 57, "les ronds blancs sont les noisettes ; R = renard", 2.6)]

S["herissons-et-tas-de-feuilles"] = [("legende", {"d": "hérissons"}),
    *[("cerceau", x, y, 5) for x, y in [(18, 16), (50, 12), (82, 18), (28, 44), (70, 44)]],
    *[("j", x, y, "d") for x, y in [(34, 26), (40, 34), (58, 28), (62, 36), (12, 32), (86, 34), (48, 50), (20, 28)]],
    ("fleche", 36, 28, 46, 16), ("fleche", 60, 34, 68, 41),
    ("txt", 50, 57, "« Le vent se lève ! » : chacun court s'abriter dans un tas de feuilles", 2.6)]

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
