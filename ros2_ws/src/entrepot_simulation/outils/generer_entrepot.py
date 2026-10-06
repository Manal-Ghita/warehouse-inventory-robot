"""genere une section de l'entrepot pour gazebo, a partir du dataset

2 allees, 3 rangees (a simple, b et c doubles), troncons 13 a 20
sortie : worlds/entrepot.world, materials/ (etiquettes qr), verite_terrain.csv
"""
import argparse
import random
from pathlib import Path

import pandas as pd
import qrcode
from PIL import Image, ImageDraw

PKG = Path(__file__).resolve().parent.parent
DATA = PKG.parents[2] / "data" / "processed"

POUCE = 0.0254
UNITE_X = 3 * POUCE           # 1 unite du dataset en x = 3 pouces
X_ORIGINE = 376               # bord du premier troncon, en unites

# plan dwg
ALLEE = 1.47
PROF = 0.76                   # un rayonnage, les doubles font 2 x 0.76
LISSES = {1: 0.23, 2: 1.37, 3: 2.51, 4: 4.42}
H_MONTANT = 6.2
LARG_POS = 16 * UNITE_X       # largeur d'une position (niveaux 1 et 2)
LARG_TRAVEE = 48 * UNITE_X

# rangees, en y : a [0, 0.76], allee 1, b [2.23, 3.75], allee 2, c [5.22, 6.74]
Y_A = (0.0, PROF)
Y_B = (PROF + ALLEE, PROF + ALLEE + 2 * PROF)
Y_C = (Y_B[1] + ALLEE, Y_B[1] + ALLEE + 2 * PROF)

# faces etiquetees : (zone, parite des troncons, y de la face, sens vers l'allee)
FACES = [("A", 0, Y_A[1], +1),
         ("B", 1, Y_B[0], -1),
         ("B", 0, Y_B[1], +1),
         ("C", 1, Y_C[0], -1)]
TRONCONS = {0: [14, 16, 18, 20], 1: [13, 15, 17, 19]}
CARTONS_PAR_EMP = 3


# ---------- etiquettes ----------

def image_etiquette(contenu, texte, chemin):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=2)
    qr.add_data(contenu)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    cote = img.size[0]
    fond = Image.new("RGB", (cote, cote + 50), "white")
    fond.paste(img, (0, 0))
    ImageDraw.Draw(fond).text((10, cote + 15), texte, fill="black")
    fond.save(chemin)


class Monde:
    def __init__(self):
        self.visuels = []
        self.materiaux = []
        self.n = 0

    def boite(self, nom, taille, pos, couleur=None, script=None, collision=True):
        self.n += 1
        x, y, z = pos
        sx, sy, sz = taille
        if script:
            mat = (f"<material><script><uri>file://materials/scripts</uri>"
                   f"<uri>file://materials/textures</uri><name>{script}</name></script></material>")
        else:
            r, g, b = (c / 255 for c in couleur)
            mat = (f"<material><ambient>{r:.3f} {g:.3f} {b:.3f} 1</ambient>"
                   f"<diffuse>{r:.3f} {g:.3f} {b:.3f} 1</diffuse></material>")
        geo = f"<geometry><box><size>{sx:.4f} {sy:.4f} {sz:.4f}</size></box></geometry>"
        bloc = (f"<visual name='v{self.n}_{nom}'><pose>{x:.4f} {y:.4f} {z:.4f} 0 0 0</pose>"
                f"{geo}{mat}</visual>")
        if collision:
            bloc += f"<collision name='c{self.n}_{nom}'><pose>{x:.4f} {y:.4f} {z:.4f} 0 0 0</pose>{geo}</collision>"
        self.visuels.append(bloc)


BLEU = (30, 70, 160)
ORANGE = (235, 110, 20)
GRILLE = (150, 150, 150)
CARTON = (190, 150, 100)


def x_monde(x_dataset):
    return (X_ORIGINE - x_dataset) * UNITE_X


def structure(monde, y0, y1, centres_travees):
    """montants, lisses avant et arriere, platelages d'une rangee"""
    bords = []
    for c in centres_travees:
        bords += [c - LARG_TRAVEE / 2 - 0.075, c + LARG_TRAVEE / 2 + 0.075]
    for xb in sorted(set(round(b, 3) for b in bords)):
        for y in (y0 + 0.04, y1 - 0.04):
            monde.boite("montant", (0.08, 0.08, H_MONTANT), (xb, y, H_MONTANT / 2), BLEU)
    for c in centres_travees:
        for niv, h in LISSES.items():
            for y in (y0 + 0.03, y1 - 0.03):
                monde.boite("lisse", (LARG_TRAVEE, 0.06, 0.10), (c, y, h - 0.05), ORANGE)
            monde.boite("platelage", (LARG_TRAVEE, y1 - y0, 0.02), (c, (y0 + y1) / 2, h + 0.01), GRILLE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manquants", type=int, default=4)
    ap.add_argument("--mal_ranges", type=int, default=3)
    ap.add_argument("--inconnus", type=int, default=2)
    ap.add_argument("--graine", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.graine)

    emp = pd.read_csv(DATA / "emplacements.csv")
    stock = pd.read_csv(DATA / "base_stock.csv")
    morceaux = emp["originalLocation"].str.split("-", expand=True)
    emp["zone"], emp["troncon"] = morceaux[0], morceaux[1].astype(int)
    emp["niveau"] = morceaux[2].str[0].astype(int)

    # emplacements de la section et contenu attendu (3 premiers produits)
    lignes = []
    for zone, parite, y_face, sens in FACES:
        sel = emp[(emp["zone"] == zone) & emp["troncon"].isin(TRONCONS[parite])]
        for _, e in sel.iterrows():
            prods = list(stock.loc[stock["originalLocation"] == e["originalLocation"], "produit"])[:CARTONS_PAR_EMP]
            lignes.append(dict(code=e["originalLocation"], zone=zone, troncon=e["troncon"],
                               niveau=e["niveau"], x=x_monde(e["x"]), y_face=y_face, sens=sens,
                               attendu=prods))
    reel = {l["code"]: list(l["attendu"]) for l in lignes}
    connus = set(stock["produit"])

    # erreurs volontaires
    erreurs = []
    pleins = [c for c in reel if reel[c]]
    for c in random.sample(pleins, args.manquants):
        p = reel[c].pop(random.randrange(len(reel[c])))
        erreurs.append((c, p, "manquant"))
    for _ in range(args.mal_ranges):
        src, dst = random.sample([c for c in reel if reel[c]], 2)
        p = reel[src].pop(random.randrange(len(reel[src])))
        reel[dst].append(p)
        erreurs.append((src, p, "manquant"))
        erreurs.append((dst, p, "mal_range"))
    for i in range(args.inconnus):
        c = random.choice(pleins)
        reel[c].append(f"ZZ{i:04d}")
        erreurs.append((c, f"ZZ{i:04d}", "inconnu"))

    # verite terrain : statut de chaque couple vu ou attendu
    verite = []
    for l in lignes:
        att, vu = set(l["attendu"]), set(reel[l["code"]])
        for p in sorted(att & vu):
            verite.append((l["code"], p, "conforme"))
        for p in sorted(vu - att):
            verite.append((l["code"], p, "mal_range" if p in connus else "inconnu"))
        for p in sorted(att - vu):
            verite.append((l["code"], p, "manquant"))
    pd.DataFrame(verite, columns=["emplacement", "produit", "statut"]).to_csv(PKG / "verite_terrain.csv", index=False)

    # textures et script de materiaux
    tex = PKG / "materials" / "textures"
    scr = PKG / "materials" / "scripts"
    for d in (tex, scr):
        d.mkdir(parents=True, exist_ok=True)
        for f in d.iterdir():
            f.unlink()
    noms_mat = []

    def materiau(contenu, texte):
        nom = contenu.replace("|", "_")
        # un produit peut etre a deux endroits : une seule texture
        if nom not in noms_mat:
            image_etiquette(contenu, texte, tex / f"{nom}.png")
            noms_mat.append(nom)
        return f"etiquette/{nom}"

    monde = Monde()

    # structures des trois rangees
    centres = sorted({round(x_monde(x), 4) for x in emp.loc[
        (emp["zone"] == "A") & emp["troncon"].isin(TRONCONS[0]) & (emp["niveau"] == 3), "x"]})
    structure(monde, *Y_A, centres)
    structure(monde, *Y_B, centres)
    structure(monde, *Y_C, centres)

    # etiquettes d'emplacement sur les lisses, cartons et etiquettes produit
    for l in lignes:
        h = LISSES[l["niveau"]]
        larg = LARG_POS if l["niveau"] <= 2 else LARG_TRAVEE
        yf, s = l["y_face"], l["sens"]
        monde.boite("etiq_emp", (0.06, 0.003, 0.07), (l["x"], yf + s * 0.0015, h - 0.05),
                    script=materiau(f"E|{l['code']}", l["code"]), collision=False)
        prods = reel[l["code"]]
        pas = larg / max(len(prods), 1)
        for i, p in enumerate(prods):
            xc = l["x"] - larg / 2 + pas * (i + 0.5)
            sx, sz = min(0.4, pas - 0.06), 0.32
            yc = yf - s * (0.03 + 0.25)
            monde.boite("carton", (sx, 0.5, sz), (xc, yc, h + 0.02 + sz / 2), CARTON)
            monde.boite("etiq_prod", (0.06, 0.003, 0.07), (xc, yf - s * 0.03 + s * 0.0015, h + 0.02 + 0.05),
                        script=materiau(f"P|{p}", p), collision=False)

    with open(scr / "etiquettes.material", "w") as f:
        for nom in noms_mat:
            f.write(f"material etiquette/{nom}\n{{\n  technique\n  {{\n    pass\n    {{\n"
                    f"      ambient 1 1 1 1\n      diffuse 1 1 1 1\n"
                    f"      texture_unit\n      {{\n        texture {nom}.png\n"
                    f"        filtering trilinear\n      }}\n    }}\n  }}\n}}\n\n")

    monde_sdf = f"""<?xml version="1.0"?>
<sdf version="1.6">
  <world name="entrepot">
    <include><uri>model://sun</uri></include>
    <include><uri>model://ground_plane</uri></include>
    <scene><ambient>0.6 0.6 0.6 1</ambient><shadows>false</shadows></scene>
    <model name="rayonnages">
      <static>true</static>
      <link name="structure">
        {''.join(monde.visuels)}
      </link>
    </model>
  </world>
</sdf>
"""
    (PKG / "worlds").mkdir(exist_ok=True)
    (PKG / "worlds" / "entrepot.world").write_text(monde_sdf)

    print(f"{len(lignes)} emplacements, {sum(len(v) for v in reel.values())} cartons, "
          f"{len(noms_mat)} etiquettes, {len(erreurs)} erreurs injectees")
    print(f"longueur de la section : {max(centres) + LARG_TRAVEE / 2 + 0.15:.2f} m")


if __name__ == "__main__":
    main()
