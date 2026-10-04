import cv2
import numpy as np
from pyzbar.pyzbar import ZBarSymbol, decode


_clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))


def lire(image):
    """liste des etiquettes lues dans une image bgr, en plusieurs passes"""
    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # image brute, image agrandie (biais), contraste renforce (sombre)
    versions = [
        (gris, 1.0),
        (cv2.resize(gris, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC), 2.0),
        (_clahe.apply(gris), 1.0),
    ]

    trouves = []
    for img, echelle in versions:
        for s in decode(img, symbols=[ZBarSymbol.QRCODE]):
            texte = s.data.decode("utf-8", errors="ignore")
            if "|" not in texte:
                continue
            genre, code = texte.split("|", 1)
            if genre not in ("E", "P"):
                continue
            # coins ramenes a l'echelle de l'image d'origine
            coins = np.array([(p.x, p.y) for p in s.polygon], np.float32) / echelle
            centre = coins.mean(axis=0)

            # deja trouvee au meme endroit par une autre passe
            if any(t["texte"] == texte and np.linalg.norm(t["centre"] - centre) < 20
                   for t in trouves):
                continue

            trouves.append({
                "texte": texte,
                "type": "emplacement" if genre == "E" else "produit",
                "code": code,
                "coins": coins,
                "centre": centre,
            })
    return trouves