"""Fabrique un Reel (vidéo verticale 1080 × 1920) à partir d'une suite de cartes de texte, avec des feuilles qui tombent
et une musique de fond composée pour lui (outils/musique.py, sans droits d'auteur).

Les Reels sont décrits dans donnees/reels.yml ; la vidéo est enregistrée dans statique/videos/<id>.mp4.
Usage : python3 outils/reel.py <id>      (ffmpeg doit être installé)
"""
import math
import random
import subprocess
import sys
import zlib
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

RACINE = Path(__file__).resolve().parents[1]
POLICES = Path(__file__).resolve().parent / "polices-visuels"
W, H, IPS = 1080, 1920, 30
ENCRE, PAPIER = "#1A2340", "#FBF3EA"
MUSIQUES = {"feuilles": "feuilles", "flocons": "flocons", "confettis": "confettis"}
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


def cadre(couleur):
    """Le bandeau à fanions en haut et la signature en bas, posés sur la vidéo (RGBA)."""
    plein = fond_fixe(couleur).convert("RGBA")
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.paste(plein.crop((0, 0, W, 175)), (0, 0))
    im.paste(plein.crop((0, H - 250, W, H)), (0, H - 250))
    return im


def images_clips(clips, total):
    """Les images des clips, mis bout à bout, recadrés en vertical, sur « total » images (un clip trop court
    tourne en boucle)."""
    part = total // len(clips)
    taille = W * H * 3
    for i, clip in enumerate(clips):
        n = part if i < len(clips) - 1 else total - part * (len(clips) - 1)
        cmd = ["ffmpeg", "-loglevel", "error", "-stream_loop", "-1", "-i", str(clip), "-an",
               "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={IPS}",
               "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        derniere = None
        for _ in range(n):
            brut = p.stdout.read(taille)
            if len(brut) == taille:
                derniere = Image.frombytes("RGB", (W, H), brut)
            yield derniere if derniere is not None else Image.new("RGB", (W, H), PAPIER)
        p.stdout.close()
        p.wait()


def fabriquer_video(r, sortie, decor="feuilles", clips=None):
    """clips : vidéos à mettre en fond (outils/clips.py) ; sans elles, le fond animé (feuilles, flocons, confettis)."""
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
    # la musique de fond, composée pour ce Reel (outils/musique.py), selon le décor
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import musique
    son = sortie.with_suffix(".wav")
    musique.enregistrer(musique.composer(MUSIQUES.get(decor, "confettis"), total / IPS,
                                         zlib.crc32(sortie.name.encode())), son)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(IPS),
           "-i", "-", "-i", str(son), "-shortest", "-af", "lowpass=f=9000,loudnorm=I=-18:TP=-2",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "23", "-preset", "medium",
           "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-movflags", "+faststart", str(sortie)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fondu = int(0.35 * IPS)
    video = images_clips(clips, total) if clips else None
    if video:
        bord = cadre(couleur)
        voile = Image.new("RGB", (W, H), (20, 25, 45))
    pop = int(0.45 * IPS)  # la première carte arrive en grand, puis se pose : l'accroche de la première seconde
    for n in range(total):
        t = n / IPS
        if video:
            im = Image.blend(next(video), voile, 0.18)
            im.paste(bord, (0, 0), bord)
        else:
            im = fond.copy()
        d = ImageDraw.Draw(im)
        for j, f in enumerate([] if video else feuilles):
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
        if i == 0 and k < pop:
            e = 1 - (1 - k / pop) ** 3
            z = 1.35 - 0.35 * e
            grand = calque.resize((int(W * z), int(H * z)), Image.BILINEAR)
            calque = grand.crop(((grand.width - W) // 2, (grand.height - H) // 2,
                                 (grand.width - W) // 2 + W, (grand.height - H) // 2 + H))
            alpha = max(alpha, e)
        if alpha < 1:
            calque = calque.copy()
            calque.putalpha(calque.getchannel("A").point(lambda v: int(v * alpha)))
        im.paste(calque, (0, 0), calque)
        p.stdin.write(im.tobytes())
    p.stdin.close()
    p.wait()
    son.unlink(missing_ok=True)
    print(f"{sortie.name} : {total / IPS:.1f} s, {sortie.stat().st_size // 1024} Ko")


# ---------------------------------------------------------------- le Reel sur vraies vidéos (depuis novembre 2026)
# Très peu de mots, posés directement sur la vidéo (pas de cadre) ; un dégradé discret pour la lisibilité ;
# une guirlande fine en haut, le J et l'adresse du site sous le texte. Le texte reste dans la zone que l'interface
# d'Instagram ne recouvre pas (ni le haut, ni le bas, ni la colonne de boutons à droite).

BLANC = (255, 255, 255, 255)
SYMBOLE = RACINE / "statique" / "img" / "logo-1024.png"
DUREE_ECRAN = 3.2


def _ombre(calque, flou=12, force=235):
    from PIL import ImageFilter
    a = calque.getchannel("A").filter(ImageFilter.GaussianBlur(flou)).point(lambda v: min(255, v * force // 255))
    ombre = Image.new("RGBA", calque.size, (10, 14, 30, 0))
    ombre.putalpha(a)
    ombre.alpha_composite(calque)
    return ombre


def ecran(c, couleur):
    """Un écran de texte (RGBA plein cadre) : surtitre en pastille, titre en grandes lettres blanches, petite ligne."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    marge, largeur = 90, W - 2 * 90 - 60  # 60 de plus à droite : les boutons d'Instagram
    blocs, h = [], 0
    if c.get("surtitre"):
        f = police("Atkinson-700.ttf", 42)
        blocs.append(("pastille", c["surtitre"].upper(), f))
        h += 100
    taille = 112
    while True:
        f = police("Bricolage-800.ttf", taille)
        ls = [l for morceau in c["titre"].split(" · ") for l in lignes(d, morceau, f, largeur)]
        if len(ls) <= 3 or taille <= 64:
            break
        taille -= 6
    blocs.append(("titre", ls, f))
    h += int(len(ls) * taille * 1.08) + 46
    if c.get("petit"):
        f = police("Gochi-400.ttf", 64)
        blocs.append(("petit", c["petit"], f))
        h += 90
    y = int(H * 0.53 - h / 2)
    for genre, contenu, f in blocs:
        if genre == "pastille":
            lw = d.textlength(contenu, font=f)
            d.rounded_rectangle([marge, y, marge + lw + 52, y + 72], radius=36, fill=couleur)
            d.text((marge + 26, y + 13), contenu, font=f, fill=BLANC)
            y += 100
        elif genre == "titre":
            for l in contenu:
                d.text((marge, y), l, font=f, fill=BLANC)
                y += int(f.size * 1.08)
            y += 14
            d.rounded_rectangle([marge, y, marge + 150, y + 14], radius=7, fill=couleur)
            y += 32
        else:
            d.text((marge, y), contenu, font=f, fill=BLANC)
            y += 90
    return _ombre(im)


def habillage(couleur):
    """Le dégradé du bas, la guirlande fine en haut et la signature (symbole + adresse), en RGBA."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    haut = int(H * 0.22)
    for y in range(haut, H):
        t = (y - haut) / (H - haut)
        d.line([(0, y), (W, y)], fill=(16, 20, 40, int(215 * min(1, t * 1.25) ** 1.3)))
    # la guirlande : une ficelle qui pend, des fanions aux couleurs du site
    pts = [(x, 34 + 26 * math.sin(math.pi * x / W)) for x in range(0, W + 1, 10)]
    d.line(pts, fill=(255, 255, 255, 200), width=3)
    for i in range(11):
        x0 = 20 + i * (W - 40) / 11
        x1 = x0 + (W - 40) / 11 - 14
        y0 = 34 + 26 * math.sin(math.pi * (x0 + x1) / 2 / W)
        d.polygon([(x0 + 7, y0), (x1 + 7, y0), ((x0 + x1) / 2 + 7, y0 + 54)],
                  fill=["#CF3424", "#F2B21B", "#2D6A43", "#3D5BB8"][i % 4])
    # la signature, sous le texte
    cote = 76
    sym = Image.open(SYMBOLE).convert("RGBA").resize((cote, cote), Image.LANCZOS)
    f = police("Bricolage-800.ttf", 50)
    texte = "jeuphorie.fr"
    lw = d.textlength(texte, font=f)
    x = int((W - 60 - (cote + 20 + lw)) / 2)
    y = int(H * 0.775)
    im.alpha_composite(sym, (x, y))
    d.text((x + cote + 20, y + 8), texte, font=f, fill=BLANC)
    return im


def fabriquer_video_clips(cartes, couleur, sortie, clips, musique=None, debut=0.0, decor="feuilles"):
    """Le Reel sur vraies vidéos. musique : fichier du morceau (sinon la musique composée), debut : seconde de départ."""
    sortie = Path(sortie)
    ecrans = [ecran(c, couleur) for c in cartes]
    par = int(DUREE_ECRAN * IPS)
    total = par * len(ecrans)
    habit = habillage(couleur)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    if musique:
        son_entree = ["-ss", f"{debut:.2f}", "-i", str(musique)]
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import musique as compo
        son = sortie.with_suffix(".wav")
        compo.enregistrer(compo.composer(MUSIQUES.get(decor, "confettis"), total / IPS,
                                         zlib.crc32(sortie.name.encode())), son)
        son_entree = ["-i", str(son)]
    duree = total / IPS
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(IPS),
           "-i", "-", *son_entree, "-map", "0:v", "-map", "1:a", "-t", f"{duree:.2f}",
           "-af", f"afade=t=in:d=0.3,afade=t=out:st={duree - 1.4:.2f}:d=1.4,loudnorm=I=-16:TP=-1.5",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "21", "-preset", "medium",
           "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", str(sortie)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    video = images_clips(clips, total)
    entree, sortie_f, pop = int(0.32 * IPS), int(0.22 * IPS), int(0.45 * IPS)
    for n in range(total):
        im = next(video).convert("RGBA")
        im.alpha_composite(habit)
        i, k = divmod(n, par)
        calque, dy = ecrans[i], 0
        if i == 0 and k < pop:  # l'accroche : le titre arrive en grand puis se pose
            e = 1 - (1 - k / pop) ** 3
            z = 1.3 - 0.3 * e
            grand = calque.resize((int(W * z), int(H * z)), Image.BILINEAR)
            calque = grand.crop(((grand.width - W) // 2, (grand.height - H) // 2,
                                 (grand.width - W) // 2 + W, (grand.height - H) // 2 + H))
            alpha = e
        else:
            alpha = 1.0
            if k < entree:  # les écrans suivants montent doucement
                e = 1 - (1 - k / entree) ** 3
                alpha, dy = e, int(46 * (1 - e))
            if i < len(ecrans) - 1 and par - k <= sortie_f:
                alpha = min(alpha, (par - k) / sortie_f)
        if alpha < 1:
            calque = calque.copy()
            calque.putalpha(calque.getchannel("A").point(lambda v: int(v * alpha)))
        im.alpha_composite(calque, (0, dy) if dy >= 0 else (0, 0))
        p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    if not musique:
        son.unlink(missing_ok=True)
    print(f"{sortie.name} : {duree:.1f} s, {sortie.stat().st_size // 1024} Ko")


if __name__ == "__main__":
    fabriquer(sys.argv[1])
