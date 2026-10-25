"""Les compositions des visuels des réseaux sociaux, en plus de la composition classique de outils/reseaux.py.

Chaque composition a son propre univers (tableau noir, carnet, affiche, terrain de sport, ticket…), mais garde toujours
un repère de Jeuphorie : le logo « Jeuphorie », et souvent la guirlande de fanions aux quatre couleurs du site.
Chaque fonction reçoit la publication p, la taille, les deux couleurs de son thème et la phrase d'appel, et rend une image.
"""
import math
import random
import re
import zlib
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

POLICES = Path(__file__).resolve().parent / "polices-visuels"
ENCRE, PAPIER = "#1A2340", "#FBFAF7"
FANIONS = ["#CF3424", "#F2B21B", "#2D6A43", "#3D5BB8"]
ROUGE, JAUNE = "#CF3424", "#FFE36E"


# ---------------------------------------------------------------- outils communs

def police(nom, taille):
    return ImageFont.truetype(str(POLICES / nom), max(8, int(taille)))


def insecables(texte):
    """Jamais de retour à la ligne avant « : ; ? ! » » ni après « « » (espace insécable)."""
    return re.sub(r"« ", "«\u00a0", re.sub(r" ([:;?!»])", "\u00a0\\1", texte or ""))


def lignes(d, texte, f, largeur):
    out, cour = [], ""
    for m in (x for x in insecables(texte).split(" ") if x):
        essai = (cour + " " + m).strip()
        if d.textlength(essai, font=f) <= largeur or not cour:
            cour = essai
        else:
            out.append(cour)
            cour = m
    if cour:
        out.append(cour)
    return out


def ajuster(d, texte, nom, largeur, hauteur_max, t_max, t_min=20, interligne=1.12, lignes_max=6):
    """La plus grande taille de police pour que le texte tienne dans la boîte : (police, lignes, pas)."""
    t = int(t_max)
    while True:
        f = police(nom, t)
        ls = lignes(d, texte, f, largeur)
        if (len(ls) <= lignes_max and len(ls) * t * interligne <= hauteur_max) or t <= t_min:
            return f, ls[:lignes_max], int(t * interligne)
        t -= 2


def coupe(d, texte, f, largeur, n):
    """Au plus n lignes, avec des points de suspension si le texte est plus long."""
    ls = lignes(d, texte or "", f, largeur)
    if n <= 0:
        return []
    if len(ls) > n:
        ls = ls[:n]
        ls[-1] = ls[-1].rstrip(" ,.;:") + "…"
    return ls


def ecrire(d, ls, f, x, y, pas, couleur, centre=False, largeur=0):
    for l in ls:
        xx = x + (largeur - d.textlength(l, font=f)) / 2 if centre else x
        d.text((xx, y), l, font=f, fill=couleur)
        y += pas
    return y


def logo(d, x, y, taille, couleur, jeu=ROUGE, centre=False, largeur=0):
    f = police("Bricolage-800.ttf", taille)
    lw = d.textlength("Jeuphorie", font=f)
    if centre:
        x = x + (largeur - lw) / 2
    d.text((x, y), "Jeu", font=f, fill=jeu)
    d.text((x + d.textlength("Jeu", font=f), y), "phorie", font=f, fill=couleur)
    return lw


def guirlande(d, x0, x1, y, fil, n=14, couleurs=FANIONS, creux=0.0):
    """Les fanions du site ; creux > 0 fait pendre la ficelle."""
    pas = (x1 - x0) / n
    def yy(x):
        return y + creux * math.sin(math.pi * (x - x0) / max(1, x1 - x0))
    d.line([(x, yy(x)) for x in range(int(x0), int(x1) + 1, 8)], fill=fil, width=2)
    for i in range(n):
        xa, xb = x0 + i * pas + pas * 0.12, x0 + (i + 1) * pas - pas * 0.12
        xm = (xa + xb) / 2
        d.polygon([(xa, yy(xa)), (xb, yy(xb)), (xm, yy(xm) + pas * 0.72)], fill=couleurs[i % len(couleurs)])


def melange(c, blanc=0.0, noir=0.0):
    r, g, b = (int(c.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (v + (255 - v) * blanc for v in (r, g, b))
    r, g, b = (v * (1 - noir) for v in (r, g, b))
    return "#%02X%02X%02X" % (int(r), int(g), int(b))


def vague(d, x, y, largeur, couleur, epaisseur=6, amplitude=7, periode=46):
    pts = [(x + t, y + amplitude * math.sin(t / periode * 2 * math.pi)) for t in range(0, int(largeur), 4)]
    d.line(pts, fill=couleur, width=epaisseur, joint="curve")


def fleche(d, x, y, longueur, couleur, epaisseur=5):
    """Une petite flèche dessinée à la main, qui pointe vers la droite."""
    pts = [(x + t, y - 0.18 * longueur * math.sin(math.pi * t / longueur)) for t in range(0, int(longueur), 3)]
    d.line(pts, fill=couleur, width=epaisseur, joint="curve")
    xe, ye = pts[-1]
    d.line([(xe - 22, ye - 16), (xe, ye), (xe - 24, ye + 12)], fill=couleur, width=epaisseur, joint="curve")


def etoile(d, cx, cy, r, couleur):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=couleur)


def hasard(p, sel=""):
    return random.Random(zlib.crc32(f"{p['id']}{p.get('jour')}{sel}".encode()))


def texte_sur(fond):
    """Blanc sur une couleur foncée, encre sur une couleur claire."""
    r, g, b = (int(fond.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return ENCRE if 0.299 * r + 0.587 * g + 0.114 * b > 170 else "#FFFFFF"


# ---------------------------------------------------------------- tableau noir

def tableau(p, w, h, vif, clair, appel):
    craie, pastels = (246, 243, 232), ["#F4A79D", "#F7D774", "#A8D5A2", "#A9BDF0"]
    im = Image.new("RGB", (w, h), "#2E4B3C")
    # le grain du tableau et les traces d'effaceur
    grain = Image.effect_noise((w, h), 50).point(lambda v: 22 if v > 205 else 0)
    im.paste(Image.new("RGB", (w, h), "#FFFFFF"), (0, 0), grain)
    calque = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(calque)
    rnd = hasard(p, "tableau")
    for _ in range(5):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        d.ellipse([x - w * 0.25, y - h * 0.05, x + w * 0.25, y + h * 0.05], fill=(255, 255, 255, 7))
    cadre = int(w * 0.04)
    m = cadre + int(w * 0.07)
    utile = w - 2 * m
    guirlande(d, cadre + 20, w - cadre - 20, cadre + int(h * 0.035), craie + (200,), n=12, couleurs=pastels,
              creux=h * 0.02)
    y = cadre + int(h * 0.12)
    d.text((m, y), p["surtitre"], font=police("Gochi-400.ttf", w * 0.05), fill=pastels[1])
    y += int(w * 0.09)
    f, ls, pas = ajuster(d, p["titre"], "Gochi-400.ttf", utile, h * 0.3, w * 0.115, lignes_max=4, interligne=1.08)
    y = ecrire(d, ls, f, m, y, pas, craie)
    vague(d, m, y + int(w * 0.02), w * 0.3, pastels[0], 6, 6)
    y += int(w * 0.08)
    bas = h - cadre - int(h * 0.23)
    ft = police("Gochi-400.ttf", w * 0.052)
    pas_t = int(w * 0.052 * 1.3)
    reserve = int(pas_t * 1.3) if p.get("detail") else 0
    y = ecrire(d, coupe(d, p["texte"], ft, utile, (bas - y - reserve) // pas_t), ft, m, y, pas_t, craie)
    if p.get("detail"):
        d.text((m, y + int(w * 0.01)), p["detail"], font=police("Gochi-400.ttf", w * 0.046), fill=pastels[2])
    # l'appel, avec une flèche à la craie
    ya = h - cadre - int(h * 0.19)
    fa = police("Gochi-400.ttf", w * 0.06)
    d.text((m, ya), appel, font=fa, fill=pastels[1])
    fleche(d, m + d.textlength(appel, font=fa) + 20, ya + w * 0.045, w * 0.12, pastels[1])
    yb = h - cadre - int(h * 0.085)
    logo(d, m, yb, w * 0.058, craie, pastels[0])
    fm = police("Gochi-400.ttf", w * 0.042)
    d.text((w - m - d.textlength("jeuphorie.fr", font=fm), yb + w * 0.012), "jeuphorie.fr", font=fm, fill=craie)
    # la craie n'est jamais pleine : on la rend granuleuse
    trou = Image.effect_noise((w, h), 70).point(lambda v: 255 if v > 80 else 140)
    calque.putalpha(ImageChops.multiply(calque.getchannel("A"), trou))
    im.paste(calque, (0, 0), calque)
    # le cadre en bois et le rebord à craie
    d = ImageDraw.Draw(im)
    bois, bois_f = "#9A6B3F", "#7A512C"
    for box in ([0, 0, w, cadre], [0, h - cadre, w, h], [0, 0, cadre, h], [w - cadre, 0, w, h]):
        d.rectangle(box, fill=bois)
    d.rectangle([cadre, cadre, w - cadre, h - cadre], outline=bois_f, width=4)
    for k in range(6):
        yy = rnd.uniform(4, cadre - 4)
        d.line([(0, yy), (w, yy)], fill=bois_f, width=1)
    d.rectangle([w * 0.62, h - cadre - 18, w * 0.72, h - cadre - 4], fill="#F6F3E8")
    return im


# ---------------------------------------------------------------- carnet à spirale et post-it

def carnet(p, w, h, vif, clair, appel):
    im = Image.new("RGB", (w, h), "#FFFDF6")
    d = ImageDraw.Draw(im)
    marge_rouge = int(w * 0.17)
    m = marge_rouge + int(w * 0.05)
    utile = w - m - int(w * 0.07)
    # en-tête : le surtitre souligné au surligneur, le titre
    y = int(h * 0.07)
    fs = police("Atkinson-700.ttf", w * 0.034)
    sur = p["surtitre"].upper()
    while d.textlength(sur, font=fs) > utile and fs.size > 18:
        fs = police("Atkinson-700.ttf", fs.size - 2)
    d.rectangle([m - 8, y + w * 0.012, m + d.textlength(sur, font=fs) + 8, y + w * 0.042], fill=melange(vif, 0.7))
    d.text((m, y), sur, font=fs, fill=ENCRE)
    y += int(w * 0.075)
    f, ls, pas = ajuster(d, p["titre"], "Bricolage-800.ttf", utile, h * 0.27, w * 0.092, lignes_max=4)
    titre_y = y
    y += len(ls) * pas + int(w * 0.03)
    # les lignes du cahier
    pas_l = int(w * 0.066)
    premiere = y + pas_l
    for yy in range(premiere, h, pas_l):
        d.line([(0, yy), (w, yy)], fill="#C9D9EF", width=2)
    d.line([(marge_rouge, 0), (marge_rouge, h)], fill="#E79A9A", width=3)
    ecrire(d, ls, f, m, titre_y, pas, ENCRE)
    # la spirale
    for yy in range(int(h * 0.04), h, int(w * 0.075)):
        d.ellipse([w * 0.045, yy, w * 0.085, yy + w * 0.04], fill="#E7E1D3")
        d.arc([w * 0.015, yy - w * 0.012, w * 0.075, yy + w * 0.03], 160, 360, fill="#8A8F9C", width=5)
    # le texte, écrit à la main sur les lignes
    post_h = int(w * 0.36)
    bas = h - post_h - int(h * 0.06)
    ft = police("Gochi-400.ttf", w * 0.05)
    n = max(0, (bas - premiere) // pas_l)
    ls_t = coupe(d, p["texte"], ft, utile, n - (1 if p.get("detail") else 0))
    yy = premiere
    for l in ls_t:
        d.text((m, yy - w * 0.058), l, font=ft, fill="#2B3A8C")
        yy += pas_l
    if p.get("detail"):
        fd = police("Gochi-400.ttf", w * 0.046)
        lw = d.textlength(p["detail"], font=fd)
        d.rectangle([m - 6, yy - w * 0.035, m + lw + 6, yy - 4], fill=melange("#F2B21B", 0.55))
        d.text((m, yy - w * 0.056), p["detail"], font=fd, fill=ENCRE)
    # le post-it, avec son morceau de scotch
    cote = post_h
    post = Image.new("RGBA", (cote + 40, cote + 40), (0, 0, 0, 0))
    dp = ImageDraw.Draw(post)
    dp.rectangle([26, 28, cote + 26, cote + 28], fill=(0, 0, 0, 40))
    dp.rectangle([20, 20, cote + 20, cote + 20], fill="#FFE97A")
    fa, ls_a, pas_a = ajuster(dp, appel, "Gochi-400.ttf", cote * 0.8, cote * 0.45, w * 0.06, lignes_max=3)
    ecrire(dp, ls_a, fa, 20 + cote * 0.1, 20 + cote * 0.16, pas_a, ENCRE)
    logo(dp, 20 + cote * 0.1, 20 + cote * 0.7, w * 0.05, ENCRE)
    dp.rectangle([cote * 0.35, 4, cote * 0.75, 44], fill=(255, 255, 255, 150))
    post = post.rotate(-4, resample=Image.BICUBIC, expand=True)
    im.paste(post, (w - post.width - int(w * 0.04), h - post.height - int(h * 0.04)), post)
    fm = police("Gochi-400.ttf", w * 0.042)
    d.text((m, h - int(h * 0.075)), "jeuphorie.fr", font=fm, fill="#2B3A8C")
    return im


# ---------------------------------------------------------------- affiche à rayons

def rayons(p, w, h, vif, clair, appel):
    clair_r = melange(vif, 0.16)
    im = Image.new("RGB", (w, h), vif)
    d = ImageDraw.Draw(im)
    cx, cy, R = w / 2, h * 0.5, max(w, h) * 1.2
    for k in range(28):
        if k % 2:
            a0, a1 = 2 * math.pi * k / 28, 2 * math.pi * (k + 1) / 28
            d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))],
                      fill=clair_r)
    autour = texte_sur(vif)
    guirlande(d, 0, w, 18, autour, n=14)
    # l'étiquette centrale
    x0, x1 = int(w * 0.08), int(w * 0.92)
    y0, y1 = int(h * 0.2), int(h * 0.74)
    d.rounded_rectangle([x0 + 12, y0 + 14, x1 + 12, y1 + 14], radius=40, fill=melange(vif, 0, 0.3))
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=PAPIER, outline=ENCRE, width=5)
    # le ruban du surtitre
    fs = police("Atkinson-700.ttf", w * 0.034)
    sur = p["surtitre"].upper()
    while d.textlength(sur, font=fs) > w * 0.7 and fs.size > 18:
        fs = police("Atkinson-700.ttf", fs.size - 2)
    lw = d.textlength(sur, font=fs) + w * 0.1
    ry, rh = y0 - w * 0.045, w * 0.09
    rx0, rx1 = cx - lw / 2, cx + lw / 2
    for s in (-1, 1):  # les queues du ruban
        bx = rx0 - w * 0.06 if s < 0 else rx1 + w * 0.06
        bord = rx0 + w * 0.02 if s < 0 else rx1 - w * 0.02
        d.polygon([(bord, ry + rh * 0.25), (bx, ry + rh * 0.25), (bx + s * -w * 0.03, ry + rh * 0.75),
                   (bx, ry + rh * 1.25), (bord, ry + rh * 1.25)], fill=melange(ENCRE, 0.2))
    d.rectangle([rx0, ry, rx1, ry + rh], fill=ENCRE)
    d.text((cx - d.textlength(sur, font=fs) / 2, ry + rh / 2 - fs.size * 0.62), sur, font=fs, fill="#FFFFFF")
    # le contenu, centré
    m = x0 + int(w * 0.07)
    utile = x1 - x0 - int(w * 0.14)
    y = y0 + int(w * 0.11)
    f, ls, pas = ajuster(d, p["titre"], "Bricolage-800.ttf", utile, (y1 - y0) * 0.45, w * 0.095, lignes_max=4)
    y = ecrire(d, ls, f, m, y, pas, ENCRE, centre=True, largeur=utile)
    y += int(w * 0.02)
    for i in range(4):
        d.ellipse([cx - 70 + i * 36, y, cx - 52 + i * 36, y + 18], fill=FANIONS[i])
    y += int(w * 0.06)
    ft = police("Atkinson-400.ttf", w * 0.044)
    pas_t = int(w * 0.044 * 1.4)
    reserve = int(w * 0.06) if p.get("detail") else 0
    y = ecrire(d, coupe(d, p["texte"], ft, utile, (y1 - int(w * 0.05) - reserve - y) // pas_t), ft, m, y, pas_t, ENCRE,
               centre=True, largeur=utile)
    if p.get("detail"):
        fd = police("Atkinson-700.ttf", w * 0.036)
        d.text((cx - d.textlength(p["detail"], font=fd) / 2, y + w * 0.01), p["detail"], font=fd, fill=vif if autour == "#FFFFFF" else ENCRE)
    fa = police("Gochi-400.ttf", w * 0.064)
    d.text((cx - d.textlength(appel, font=fa) / 2, y1 + h * 0.045), appel, font=fa, fill=autour)
    logo(d, 0, h - int(h * 0.1), w * 0.065, autour, JAUNE if autour == "#FFFFFF" else ROUGE, centre=True, largeur=w)
    return im


# ---------------------------------------------------------------- terrain de sport

def terrain(p, w, h, vif, clair, appel):
    im = Image.new("RGB", (w, h), "#3F8F4F")
    d = ImageDraw.Draw(im)
    bande = w / 7
    for k in range(0, 8, 2):
        d.rectangle([k * bande, 0, (k + 1) * bande, h], fill="#48995A")
    blanc = "#EEF5EC"
    b = int(w * 0.05)
    d.rectangle([b, b, w - b, h - b], outline=blanc, width=7)
    d.line([(b, h * 0.62), (w - b, h * 0.62)], fill=blanc, width=7)
    d.ellipse([w / 2 - w * 0.17, h * 0.62 - w * 0.17, w / 2 + w * 0.17, h * 0.62 + w * 0.17], outline=blanc, width=7)
    for cx, cy in ((b + 6, b + 6), (w - b - 6, b + 6), (b + 6, h - b - 6), (w - b - 6, h - b - 6)):
        c = w * 0.035
        d.polygon([(cx - c, cy + c), (cx + c, cy + c), (cx, cy - c * 1.4)], fill="#F07F1F")
        d.line([(cx - c * 0.5, cy + c * 0.1), (cx + c * 0.5, cy + c * 0.1)], fill="#FFFFFF", width=6)
    # le tableau d'affichage
    x0, x1 = int(w * 0.1), int(w * 0.9)
    y0 = int(h * 0.09)
    m = x0 + int(w * 0.055)
    utile = x1 - x0 - int(w * 0.11)
    f, ls, pas = ajuster(d, p["titre"], "Bricolage-800.ttf", utile, h * 0.24, w * 0.088, lignes_max=4)
    y1 = y0 + int(w * 0.13) + len(ls) * pas + int(w * 0.04)
    d.rounded_rectangle([x0 + 10, y0 + 12, x1 + 10, y1 + 12], radius=26, fill="#2C6B3A")
    d.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=ENCRE)
    for i, cx in enumerate((x0 + w * 0.06, x1 - w * 0.06)):  # les deux poteaux
        d.ellipse([cx - 9, y0 + w * 0.045, cx + 9, y0 + w * 0.045 + 18], fill=FANIONS[i * 2 + 1])
    fs = police("Atkinson-700.ttf", w * 0.032)
    sur = p["surtitre"].upper()
    while d.textlength(sur, font=fs) > utile - w * 0.1 and fs.size > 18:
        fs = police("Atkinson-700.ttf", fs.size - 2)
    d.text(((w - d.textlength(sur, font=fs)) / 2, y0 + w * 0.04), sur, font=fs, fill=JAUNE)
    ecrire(d, ls, f, m, y0 + int(w * 0.11), pas, "#FFFFFF", centre=True, largeur=utile)
    # la fiche posée sur la pelouse
    fy0 = y1 + int(h * 0.05)
    fy1 = h - int(h * 0.25)
    if fy1 - fy0 > w * 0.12:
        d.rounded_rectangle([x0, fy0, x1, fy1], radius=22, fill=PAPIER)
        ft = police("Atkinson-400.ttf", w * 0.044)
        pas_t = int(w * 0.044 * 1.4)
        reserve = int(w * 0.06) if p.get("detail") else 0
        yy = ecrire(d, coupe(d, p["texte"], ft, utile, (fy1 - fy0 - int(w * 0.08) - reserve) // pas_t), ft, m,
                    fy0 + int(w * 0.04), pas_t, ENCRE)
        if p.get("detail"):
            d.text((m, yy + w * 0.01), p["detail"], font=police("Atkinson-700.ttf", w * 0.036), fill="#2D6A43")
    fa = police("Gochi-400.ttf", w * 0.062)
    d.text((x0, h - int(h * 0.205)), appel, font=fa, fill="#FFFFFF")
    yb = h - int(h * 0.115)
    d.rounded_rectangle([x0 - 16, yb - 14, x0 + w * 0.42, yb + w * 0.085], radius=18, fill=PAPIER)
    logo(d, x0 + 4, yb, w * 0.058, ENCRE)
    fm = police("Gochi-400.ttf", w * 0.042)
    d.text((x1 - d.textlength("jeuphorie.fr", font=fm), yb + w * 0.015), "jeuphorie.fr", font=fm, fill="#FFFFFF")
    return im


# ---------------------------------------------------------------- un grand signe qui déborde

def signe(p):
    t = p["titre"]
    if p["type"] == "message":
        return "?" if "?" in t else "«"
    n = re.search(r"\b(\d{1,2})\b", t)
    if n and p["type"] == "article":
        return n.group(1)
    j = p.get("brut") or {}
    if j.get("age_min"):
        return f"{j['age_min']}+"
    return "!"


def geante(p, w, h, vif, clair, appel):
    im = Image.new("RGB", (w, h), clair)
    d = ImageDraw.Draw(im)
    s = signe(p)
    fg = police("Bricolage-800.ttf", h * (0.5 if len(s) == 1 else 0.4))
    gw = d.textlength(s, font=fg)
    d.text((w - gw * (0.82 if len(s) == 1 else 0.9), -h * 0.1), s, font=fg, fill=vif)
    m = int(w * 0.08)
    utile = int(w * 0.84)
    y = int(h * 0.27)
    # le surtitre en étiquette
    fs = police("Atkinson-700.ttf", w * 0.032)
    sur = p["surtitre"].upper()
    lw = d.textlength(sur, font=fs)
    d.rectangle([m - 14, y - 10, m + lw + 14, y + w * 0.05], fill=PAPIER)
    d.text((m, y), sur, font=fs, fill=ENCRE)
    y += int(w * 0.085)
    # le titre, une ligne par bande d'encre, comme des étiquettes collées
    f, ls, pas = ajuster(d, p["titre"], "Bricolage-800.ttf", utile - 40, h * 0.27, w * 0.085, lignes_max=4,
                         interligne=1.3)
    for l in ls:
        lw = d.textlength(l, font=f)
        d.rectangle([m - 16, y - f.size * 0.06, m + lw + 16, y + f.size * 1.12], fill=ENCRE)
        d.text((m, y), l, font=f, fill="#FFFFFF")
        y += pas
    y += int(w * 0.035)
    bas = h - int(h * 0.24)
    ft = police("Atkinson-400.ttf", w * 0.046)
    pas_t = int(w * 0.046 * 1.42)
    reserve = int(w * 0.06) if p.get("detail") else 0
    y = ecrire(d, coupe(d, p["texte"], ft, utile, (bas - y - reserve) // pas_t), ft, m, y, pas_t, ENCRE)
    if p.get("detail"):
        d.text((m, y + w * 0.01), p["detail"], font=police("Atkinson-700.ttf", w * 0.038), fill=melange(vif, 0, 0.25))
    fa = police("Gochi-400.ttf", w * 0.062)
    d.text((m, h - int(h * 0.2)), appel, font=fa, fill=melange(vif, 0, 0.25))
    yb = h - int(h * 0.1)
    for i in range(5):  # cinq fanions avant le logo
        x = m + i * w * 0.045
        d.polygon([(x, yb + 8), (x + w * 0.036, yb + 8), (x + w * 0.018, yb + 8 + w * 0.04)], fill=FANIONS[i % 4])
    logo(d, m + w * 0.25, yb, w * 0.058, ENCRE)
    fm = police("Gochi-400.ttf", w * 0.042)
    d.text((w - m - d.textlength("jeuphorie.fr", font=fm), yb + w * 0.012), "jeuphorie.fr", font=fm, fill=ENCRE)
    return im


# ---------------------------------------------------------------- confettis et petits dessins

def confettis(p, w, h, vif, clair, appel):
    im = Image.new("RGB", (w, h), PAPIER)
    d = ImageDraw.Draw(im)
    rnd = hasard(p, "confettis")
    zone = (w * 0.1, h * 0.15, w * 0.9, h * 0.8)
    posees = 0
    while posees < 46:
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        if zone[0] < x < zone[2] and zone[1] < y < zone[3] or w * 0.15 < x < w * 0.85 and y > h * 0.75:
            continue
        posees += 1
        c = rnd.choice(FANIONS)
        r = rnd.uniform(w * 0.012, w * 0.03)
        forme = rnd.choice(["rond", "triangle", "trait", "etoile", "vague"])
        a = rnd.uniform(0, math.pi * 2)
        if forme == "rond":
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        elif forme == "triangle":
            d.polygon([(x + r * math.cos(a + k * 2.094), y + r * math.sin(a + k * 2.094)) for k in range(3)], fill=c)
        elif forme == "trait":
            d.line([(x - r * math.cos(a), y - r * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a))], fill=c,
                   width=10)
        elif forme == "etoile":
            etoile(d, x, y, r * 1.2, c)
        else:
            vague(d, x - r * 1.5, y, r * 3, c, 6, r * 0.35, r * 1.2)
    m = int(w * 0.12)
    utile = w - 2 * m
    y = int(h * 0.17)
    fs = police("Atkinson-700.ttf", w * 0.034)
    sur = p["surtitre"].upper()
    d.text(((w - d.textlength(sur, font=fs)) / 2, y), sur, font=fs, fill=melange(vif, 0, 0.1))
    y += int(w * 0.075)
    f, ls, pas = ajuster(d, p["titre"], "Bricolage-800.ttf", utile, h * 0.3, w * 0.1, lignes_max=4)
    y = ecrire(d, ls, f, m, y, pas, ENCRE, centre=True, largeur=utile)
    vague(d, w / 2 - w * 0.12, y + int(w * 0.025), w * 0.24, vif, 7, 7, 40)
    y += int(w * 0.08)
    bas = h - int(h * 0.27)
    ft = police("Atkinson-400.ttf", w * 0.046)
    pas_t = int(w * 0.046 * 1.42)
    reserve = int(w * 0.06) if p.get("detail") else 0
    y = ecrire(d, coupe(d, p["texte"], ft, utile, (bas - y - reserve) // pas_t), ft, m, y, pas_t, ENCRE, centre=True,
               largeur=utile)
    if p.get("detail"):
        fd = police("Atkinson-700.ttf", w * 0.038)
        d.text(((w - d.textlength(p["detail"], font=fd)) / 2, y + w * 0.01), p["detail"], font=fd, fill=melange(vif, 0, 0.1))
    fa = police("Gochi-400.ttf", w * 0.066)
    aw = d.textlength(appel, font=fa)
    ya = h - int(h * 0.215)
    d.text(((w - aw) / 2, ya), appel, font=fa, fill=melange(vif, 0, 0.1))
    etoile(d, (w - aw) / 2 - w * 0.05, ya + w * 0.04, w * 0.022, "#F2B21B")
    etoile(d, (w + aw) / 2 + w * 0.05, ya + w * 0.04, w * 0.022, "#F2B21B")
    logo(d, 0, h - int(h * 0.11), w * 0.07, ENCRE, centre=True, largeur=w)
    return im


# ---------------------------------------------------------------- un ticket d'entrée

def ticket(p, w, h, vif, clair, appel):
    fond = ENCRE
    im = Image.new("RGB", (w, h), fond)
    d = ImageDraw.Draw(im)
    pas = int(w * 0.05)
    for x in range(pas // 2, w, pas):
        for y in range(pas // 2, h, pas):
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill="#2C3A62")
    guirlande(d, 0, w, 18, "#8C96B5", n=14)
    x0, x1 = int(w * 0.08), int(w * 0.92)
    y0, y1 = int(h * 0.11), int(h * 0.87)
    talon = y1 - int(h * 0.19)
    d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PAPIER)
    # la bande de couleur en haut du ticket
    bande = int(w * 0.11)
    d.rounded_rectangle([x0, y0, x1, y0 + bande], radius=28, fill=vif)
    d.rectangle([x0, y0 + bande - 30, x1, y0 + bande], fill=vif)
    fs = police("Atkinson-700.ttf", w * 0.032)
    sur = p["surtitre"].upper()
    while d.textlength(sur, font=fs) > (x1 - x0) * 0.86 and fs.size > 18:
        fs = police("Atkinson-700.ttf", fs.size - 2)
    d.text(((w - d.textlength(sur, font=fs)) / 2, y0 + bande / 2 - fs.size * 0.62), sur, font=fs, fill=texte_sur(vif))
    # les encoches et les pointillés du talon
    r = int(w * 0.045)
    for cx in (x0, x1):
        d.ellipse([cx - r, talon - r, cx + r, talon + r], fill=fond)
    for x in range(x0 + r + 10, x1 - r - 10, 28):
        d.line([(x, talon), (x + 14, talon)], fill="#9AA2B8", width=4)
    m = x0 + int(w * 0.07)
    utile = x1 - x0 - int(w * 0.14)
    y = y0 + bande + int(w * 0.06)
    f, ls, pas_t = ajuster(d, p["titre"], "Bricolage-800.ttf", utile, (talon - y) * 0.5, w * 0.09, lignes_max=4)
    y = ecrire(d, ls, f, m, y, pas_t, ENCRE)
    y += int(w * 0.03)
    ft = police("Atkinson-400.ttf", w * 0.044)
    pas_c = int(w * 0.044 * 1.42)
    reserve = int(w * 0.06) if p.get("detail") else 0
    y = ecrire(d, coupe(d, p["texte"], ft, utile, (talon - int(w * 0.05) - reserve - y) // pas_c), ft, m, y, pas_c, ENCRE)
    if p.get("detail"):
        d.text((m, y + w * 0.01), p["detail"], font=police("Atkinson-700.ttf", w * 0.036), fill=melange(vif, 0, 0.15))
    # le talon : l'appel et le logo
    fa = police("Gochi-400.ttf", w * 0.056)
    d.text((m, talon + int(w * 0.05)), appel, font=fa, fill=melange(vif, 0, 0.15))
    logo(d, m, y1 - int(w * 0.1), w * 0.055, ENCRE)
    numero = f"N° {zlib.crc32(p['id'].encode()) % 900 + 100}"
    fn = police("Gochi-400.ttf", w * 0.04)
    d.text((x1 - int(w * 0.07) - d.textlength(numero, font=fn), y1 - int(w * 0.09)), numero, font=fn, fill="#8A8F9C")
    fm = police("Gochi-400.ttf", w * 0.042)
    d.text(((w - d.textlength("jeuphorie.fr", font=fm)) / 2, y1 + (h - y1) * 0.3), "jeuphorie.fr", font=fm, fill="#FFFFFF")
    return im


STYLES = {"tableau": tableau, "carnet": carnet, "rayons": rayons, "terrain": terrain, "geante": geante,
          "confettis": confettis, "ticket": ticket}
