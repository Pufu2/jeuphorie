"""Fabrique un Reel (vidéo verticale 1080 × 1920) à partir d'une suite de cartes de texte, avec des feuilles qui tombent.

Les Reels sont décrits dans donnees/reels.yml ; la vidéo est enregistrée dans statique/videos/<id>.mp4.
Usage : python3 outils/reel.py <id>      (ffmpeg doit être installé)
"""
import math
import random
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

RACINE = Path(__file__).resolve().parents[1]
POLICES = Path(__file__).resolve().parent / "polices-visuels"
W, H, IPS = 1080, 1920, 30
ENCRE, PAPIER = "#1A2340", "#FBF3EA"
FEUILLES = ["#C2571A", "#E08A1E", "#B23A1E", "#D9A21B", "#8C5A2B"]


def police(nom, taille):
    return ImageFont.truetype(str(POLICES / nom), taille)


def lignes(d, texte, f, largeur):
    mots, out, cour = texte.split(), [], ""
    for m in mots:
        essai = (cour + " " + m).strip()
        if d.textlength(essai, font=f) <= largeur:
            cour = essai
        else:
            out.append(cour)
            cour = m
    if cour:
        out.append(cour)
    return out


def carte(c, couleur):
    """Le texte d'une carte, centré sur un fond clair (les feuilles passent derrière), en RGBA."""
    brouillon = _texte(c, couleur, 0)
    hauteur = brouillon[1]
    y0 = int((H - hauteur) / 2 - 40)
    im, _ = _texte(c, couleur, y0)
    fond = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(fond).rounded_rectangle([60, y0 - 60, W - 60, y0 + hauteur + 30], radius=36,
                                            fill=(251, 243, 234, 235))
    fond.alpha_composite(im)
    return fond


def _texte(c, couleur, y):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    marge = 110
    debut = y
    if c.get("surtitre"):
        f = police("Atkinson-700.ttf", 46)
        d.text((marge, y), c["surtitre"].upper(), font=f, fill=couleur)
        y += 90
    if c.get("titre"):
        t = 104 if len(c["titre"]) < 40 else 88
        f = police("Bricolage-800.ttf", t)
        for l in lignes(d, c["titre"], f, W - 2 * marge):
            d.text((marge, y), l, font=f, fill=ENCRE)
            y += int(t * 1.12)
        y += 40
        d.rectangle([marge, y, marge + 170, y + 12], fill=couleur)
        y += 70
    f = police("Atkinson-400.ttf", 56)
    for para in c.get("texte", []):
        puce = para.startswith("- ")
        para = para[2:] if puce else para
        for i, l in enumerate(lignes(d, para, f, W - 2 * marge - (50 if puce else 0))):
            if puce and i == 0:
                d.ellipse([marge, y + 26, marge + 20, y + 46], fill=couleur)
            d.text((marge + (50 if puce else 0), y), l, font=f, fill=ENCRE)
            y += 80
        y += 34
    if c.get("main"):
        f = police("Gochi-400.ttf", 76)
        for l in lignes(d, c["main"], f, W - 2 * marge):
            d.text((marge, y), l, font=f, fill=couleur)
            y += 96
    return im, y - debut


def fond_fixe(couleur):
    im = Image.new("RGB", (W, H), PAPIER)
    d = ImageDraw.Draw(im)
    pas = W / 12
    d.line([(0, 70), (W, 70)], fill="#4B5675", width=3)
    for i in range(13):
        x = i * pas
        d.polygon([(x + 8, 70), (x + pas - 8, 70), (x + pas / 2, 70 + pas * 0.8)],
                  fill=["#CF3424", "#F2B21B", "#2D6A43", "#3D5BB8"][i % 4])
    f = police("Bricolage-800.ttf", 64)
    y = H - 190
    d.line([(110, y - 40), (W - 110, y - 40)], fill=ENCRE, width=3)
    d.text((110, y), "Jeu", font=f, fill="#CF3424")
    d.text((110 + d.textlength("Jeu", font=f), y), "phorie", font=f, fill=ENCRE)
    g = police("Gochi-400.ttf", 52)
    d.text((W - 110 - d.textlength("jeuphorie.fr", font=g), y + 10), "jeuphorie.fr", font=g, fill=ENCRE)
    return im


def feuille(d, x, y, r, angle, c):
    pts = []
    for k in range(24):
        t = 2 * math.pi * k / 24
        px, py = r * math.cos(t), r * 0.45 * math.sin(t) * (1 + 0.3 * math.cos(t))
        ca, sa = math.cos(angle), math.sin(angle)
        pts.append((x + px * ca - py * sa, y + px * sa + py * ca))
    d.polygon(pts, fill=c)
    d.line([(x - r * math.cos(angle), y - r * math.sin(angle)), (x + r * math.cos(angle), y + r * math.sin(angle))],
           fill="#6B3A12", width=3)


def fabriquer(ident):
    reels = yaml.safe_load((RACINE / "donnees" / "reels.yml").read_text(encoding="utf-8"))["reels"]
    r = next(x for x in reels if x["id"] == ident)
    fabriquer_video(r, RACINE / "statique" / "videos" / f"{ident}.mp4")


def decor_saison(mois):
    if mois in (9, 10):
        return "feuilles"
    if mois in (11, 12, 1, 2):
        return "flocons"
    return "confettis"


def fabriquer_video(r, sortie, decor="feuilles"):
    sortie = Path(sortie)
    couleur = r.get("couleur", "#C2571A")
    cartes = [carte(c, couleur) for c in r["cartes"]]
    duree_carte = r.get("duree_carte", 3.6)
    fond = fond_fixe(couleur)
    rnd = random.Random(7)
    feuilles = [{"x": rnd.uniform(0, W), "y": rnd.uniform(-H, H), "r": rnd.uniform(22, 44), "v": rnd.uniform(90, 170),
                 "a": rnd.uniform(0, 6.28), "va": rnd.uniform(-1.2, 1.2), "o": rnd.uniform(0.5, 1.6),
                 "c": rnd.choice(FEUILLES)} for _ in range(16)]
    total = int(len(cartes) * duree_carte * IPS)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(IPS),
           "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "23", "-preset", "medium",
           "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", str(sortie)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fondu = int(0.35 * IPS)
    for n in range(total):
        t = n / IPS
        im = fond.copy()
        d = ImageDraw.Draw(im)
        for j, f in enumerate(feuilles):
            y = (f["y"] + f["v"] * t) % (H + 200) - 100
            x = f["x"] + 40 * math.sin(t * f["o"] + f["a"])
            if decor == "flocons":
                rr = f["r"] * 0.55
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=["#A9C4EA", "#C9D9F2", "#8FB0E0"][j % 3])
            elif decor == "confettis":
                a = f["a"] + f["va"] * t * 2
                w, h = f["r"] * 0.5, f["r"] * 0.22
                pts = [(x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a))
                       for px, py in [(-w, -h), (w, -h), (w, h), (-w, h)]]
                d.polygon(pts, fill=["#CF3424", "#F2B21B", "#2D6A43", "#3D5BB8"][j % 4])
            else:
                feuille(d, x, y, f["r"], f["a"] + f["va"] * t, f["c"])
        i, k = divmod(n, int(duree_carte * IPS))
        i = min(i, len(cartes) - 1)
        alpha = min(1.0, k / fondu) if i > 0 or k < fondu else 1.0
        if i == 0:
            alpha = min(1.0, (k + 1) / fondu)
        reste = int(duree_carte * IPS) - k
        if i < len(cartes) - 1 and reste < fondu:
            alpha = min(alpha, reste / fondu)
        calque = cartes[i]
        if alpha < 1:
            calque = calque.copy()
            calque.putalpha(calque.getchannel("A").point(lambda v: int(v * alpha)))
        im.paste(calque, (0, 0), calque)
        p.stdin.write(im.tobytes())
    p.stdin.close()
    p.wait()
    print(f"{sortie.name} : {total / IPS:.1f} s, {sortie.stat().st_size // 1024} Ko")


if __name__ == "__main__":
    fabriquer(sys.argv[1])
