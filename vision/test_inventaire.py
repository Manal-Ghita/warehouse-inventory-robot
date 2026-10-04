from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import qrcode

import camera
from association import associer
from comparaison import comparer
from lecteur import lire

RACINE = Path(__file__).resolve().parent.parent
MM_PX = 2
L_MM, H_MM = 1200, 500    # trois positions de 40 cm
COTE = 50 * MM_PX         # qr de 5 cm
D_MM = 680                # distance camera-etiquettes


def qr_image(contenu):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=12, border=2)
    qr.add_data(contenu)
    qr.make(fit=True)
    img = np.array(qr.make_image(fill_color="black", back_color="white").convert("RGB"))
    return cv2.resize(img[:, :, ::-1], (COTE, COTE), interpolation=cv2.INTER_AREA)


def rayonnage(contenu):
    p = np.full((H_MM * MM_PX, L_MM * MM_PX, 3), 190, np.uint8)
    for i, (emp, prods) in enumerate(contenu.items()):
        x0 = (i * 400 + 40) * MM_PX
        # etiquette d'emplacement sur la lisse, au milieu de la position
        xe, ye = x0 + 160 * MM_PX, 380 * MM_PX
        p[ye:ye + COTE, xe:xe + COTE] = qr_image(f"E|{emp}")
        # cartons alignes au-dessus
        for j, prod in enumerate(prods):
            x, y = x0 + j * 110 * MM_PX, 150 * MM_PX
            p[y:y + COTE, x:x + COTE] = qr_image(f"P|{prod}")
    return p


if __name__ == "__main__":
    base = pd.read_csv(RACINE / "data/processed/base_stock.csv")
    emps = ["A-14-11", "A-14-12", "A-14-13"]

    # base de test : 3 cartons par emplacement
    attendu = {e: list(base.loc[base["originalLocation"] == e, "produit"])[:3]
               for e in emps}

    # rayonnage reel avec erreurs volontaires
    reel = {e: list(v) for e, v in attendu.items()}
    reel["A-14-11"].pop(0)                        # un carton manquant
    reel["A-14-12"][0] = attendu["A-14-13"][0]    # un carton mal range
    reel["A-14-13"][2] = "ZZZZZZ"                 # un carton inconnu

    img = camera.photographier(rayonnage(reel), D_MM, 0, L_MM, H_MM, MM_PX)
    cv2.imwrite("scene_inventaire.png", img)

    tol_px = 200 * camera.FX / D_MM   # 20 cm a la distance de lecture
    observe, orphelins = associer(lire(img), tol_px)

    lignes = comparer(observe,
                      {e: set(v) for e, v in attendu.items()},
                      set(base["produit"]))
    print(pd.DataFrame(lignes, columns=["emplacement", "produit", "statut"]))
    print("orphelins :", orphelins)