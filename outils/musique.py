"""Compose la musique de fond des Reels : une boucle simple et joyeuse, fabriquée note par note, donc sans droits d'auteur.

Trois ambiances, selon le décor du Reel : « feuilles » (automne, marimba tranquille), « flocons » (hiver, clochettes et
grelots), « confettis » (printemps et été, guitare pincée et frappes de mains). La mélodie change d'un Reel à l'autre
(graine), mais reste toujours dans la même gamme et sur les mêmes accords : le résultat est doux, jamais faux.
Usage : python3 outils/musique.py <ambiance> <durée en secondes> <sortie.wav> [graine]
"""
import sys
import wave

import numpy as np

SR = 44100
# les accords (en demi-tons au-dessus de la tonique) : I, IV, vi, V, puis I, vi, IV, V
GRILLE = [(0, 4, 7), (5, 9, 12), (9, 12, 16), (7, 11, 14), (0, 4, 7), (9, 12, 16), (5, 9, 12), (7, 11, 14)]
PENTA = [0, 2, 4, 7, 9]
AMBIANCES = {
    "feuilles": {"tempo": 92, "tonique": 53, "arpege": "marimba", "melodie": "marimba", "batterie": "douce"},
    "flocons": {"tempo": 100, "tonique": 55, "arpege": "cloche", "melodie": "cloche", "batterie": "grelots"},
    "confettis": {"tempo": 116, "tonique": 52, "arpege": "pince", "melodie": "pince", "batterie": "mains"},
}


def hz(note):
    return 440.0 * 2 ** ((note - 69) / 12)


def instrument(nom, f, duree):
    t = np.arange(int(duree * SR)) / SR
    if nom == "marimba":
        son = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 18)
        env = np.exp(-t * 5.5)
    elif nom == "cloche":
        son = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2.0 * f * t) * np.exp(-t * 3) \
            + 0.15 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 6)
        env = np.exp(-t * 2.6)
    elif nom == "pince":
        son = sum(np.sin(2 * np.pi * k * f * t) * np.exp(-t * (3 + 4 * k)) / k for k in range(1, 6))
        env = np.exp(-t * 2.5)
    elif nom == "basse":
        son = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 2 * f * t)
        env = np.exp(-t * 2.2)
    else:  # nappe : un son tenu, très doux
        son = np.sin(2 * np.pi * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
        env = np.minimum(1, t / 0.4) * np.minimum(1, (duree - t) / 0.4)
    attaque = np.minimum(1, t / 0.004)  # pas de clic au début de la note
    return son * env * attaque


def bruit(duree, decroissance, rnd):
    t = np.arange(int(duree * SR)) / SR
    return rnd.uniform(-1, 1, len(t)) * np.exp(-t * decroissance)


def poser(piste, son, debut, volume, pan=0.0):
    i = int(debut * SR)
    n = min(len(son), len(piste) - i)
    if n > 0:
        piste[i:i + n, 0] += son[:n] * volume * (1 - pan) / 2 * 2 ** 0.5
        piste[i:i + n, 1] += son[:n] * volume * (1 + pan) / 2 * 2 ** 0.5


def composer(ambiance, duree, graine=0):
    a = AMBIANCES.get(ambiance, AMBIANCES["confettis"])
    rnd = np.random.default_rng(graine)
    temps = 60 / a["tempo"]
    piste = np.zeros((int((duree + 2) * SR), 2))
    tonique = a["tonique"]
    # un motif de deux mesures, répété (c'est la répétition qui fait une mélodie), avec une variation de temps en temps
    rythmes = [[1, 1, 2], [2, 1, 1], [1.5, 0.5, 2], [1, 1, 1, 1], [3, 1]]
    motif = [rythmes[rnd.integers(len(rythmes))] for _ in range(2)]
    motif_notes = [[int(rnd.integers(len(PENTA))) for _ in r] for r in motif]
    arpege = [[0, 1, 2, 1], [0, 2, 1, 2], [0, 1, 2, 3]][int(rnd.integers(3))]
    mesure, t0 = 0, 0.0
    while t0 < duree:
        accord = GRILLE[mesure % len(GRILLE)]
        racine = tonique + accord[0]
        # la basse et la nappe
        poser(piste, instrument("basse", hz(racine - 12), temps * 2), t0, 0.32)
        poser(piste, instrument("basse", hz(racine - 12 + (7 if mesure % 2 else 0)), temps * 2), t0 + 2 * temps, 0.26)
        for k, n in enumerate(accord):
            poser(piste, instrument("nappe", hz(tonique + n), temps * 4), t0, 0.05, pan=(k - 1) * 0.5)
        # l'arpège, en croches
        for c in range(8):
            n = (list(accord) + [accord[0] + 12])[arpege[c % 4]]
            poser(piste, instrument(a["arpege"], hz(tonique + 12 + n), temps * 1.5), t0 + c * temps / 2,
                  0.11 if c % 2 else 0.14, pan=-0.35)
        # la mélodie (pas sur les deux premières mesures : l'oreille s'installe)
        if mesure >= 2:
            r, notes = motif[mesure % 2], motif_notes[mesure % 2]
            if mesure % 8 >= 6 and rnd.random() < 0.6:  # une petite variation en fin de phrase
                notes = [min(len(PENTA) - 1, x + 1) for x in notes]
            t = t0
            for longueur, idx in zip(r, notes):
                note = tonique + 24 + PENTA[idx]
                # la note la plus proche dans l'accord, pour rester juste sur le premier temps
                if t == t0:
                    note = min((tonique + 24 + x for x in accord), key=lambda x: abs(x - note))
                poser(piste, instrument(a["melodie"], hz(note), temps * longueur + 0.6), t, 0.19, pan=0.3)
                t += temps * longueur
        # la batterie
        for b in range(4):
            tb = t0 + b * temps
            if a["batterie"] in ("douce", "mains") and b in (0, 2):
                tt = np.arange(int(0.25 * SR)) / SR
                poser(piste, np.sin(2 * np.pi * (50 + 70 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14), tb, 0.38)
            if a["batterie"] == "mains" and b in (1, 3):
                poser(piste, bruit(0.15, 28, rnd), tb, 0.09, pan=0.15)
            if a["batterie"] == "grelots":
                for s in range(2):  # des grelots : un bruit aigu et bref, en croches
                    g = np.diff(bruit(0.08, 60, rnd), prepend=0)
                    poser(piste, g, tb + s * temps / 2, 0.018 if s else 0.03, pan=0.4)
            if a["batterie"] == "douce":
                poser(piste, bruit(0.04, 120, rnd), tb + temps / 2, 0.04, pan=0.3)
        mesure += 1
        t0 += 4 * temps
    piste = piste[:int(duree * SR)]
    # un fondu à l'entrée et à la sortie, et un volume de fond (la musique accompagne, elle ne couvre rien)
    t = np.arange(len(piste)) / SR
    env = np.minimum(1, t / 0.8) * np.minimum(1, (duree - t) / 2.5)
    piste *= env[:, None]
    piste *= 0.5 / max(1e-9, np.abs(piste).max())
    return piste


def enregistrer(piste, chemin):
    donnees = (np.clip(piste, -1, 1) * 32767).astype("<i2")
    with wave.open(str(chemin), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(donnees.tobytes())


if __name__ == "__main__":
    enregistrer(composer(sys.argv[1], float(sys.argv[2]), int(sys.argv[4]) if len(sys.argv) > 4 else 0), sys.argv[3])
