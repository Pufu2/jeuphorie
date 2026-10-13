#!/usr/bin/env python3
"""Copie les polices (installées par npm depuis Fontsource) dans statique/polices/
et écrit polices.css. Ainsi le site n'appelle jamais Google Fonts.
Si une police manque, le site utilise la police de secours prévue dans le CSS."""
from pathlib import Path
import shutil

RACINE = Path(__file__).resolve().parent.parent
MODULES = RACINE / "node_modules" / "@fontsource"
DEST = RACINE / "statique" / "polices"

POLICES = [
    # (paquet, famille, graisse, style)
    ("bricolage-grotesque", "Bricolage Grotesque", 600, "normal"),
    ("bricolage-grotesque", "Bricolage Grotesque", 700, "normal"),
    ("bricolage-grotesque", "Bricolage Grotesque", 800, "normal"),
    ("atkinson-hyperlegible", "Atkinson Hyperlegible", 400, "normal"),
    ("atkinson-hyperlegible", "Atkinson Hyperlegible", 400, "italic"),
    ("atkinson-hyperlegible", "Atkinson Hyperlegible", 700, "normal"),
    ("gochi-hand", "Gochi Hand", 400, "normal"),
]

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    regles = []
    for paquet, famille, graisse, style in POLICES:
        for sous_ensemble in ("latin", "latin-ext"):
            nom = f"{paquet}-{sous_ensemble}-{graisse}-{style}.woff2"
            source = MODULES / paquet / "files" / nom
            if not source.exists():
                print("absent :", nom)
                continue
            shutil.copy(source, DEST / nom)
            plage = ("U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2212"
                     if sous_ensemble == "latin" else
                     "U+0100-02AF, U+0304, U+0308, U+0329, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF")
            regles.append(
                "@font-face{font-family:'%s';font-style:%s;font-weight:%d;font-display:swap;"
                "src:url(./%s) format('woff2');unicode-range:%s}" % (famille, style, graisse, nom, plage))
    (DEST / "polices.css").write_text("\n".join(regles) + "\n", encoding="utf-8")
    print(len(regles), "polices prêtes")

if __name__ == "__main__":
    main()
