from pathlib import Path

import pandas as pd
import qrcode
from PIL import Image, ImageDraw

RACINE = Path(__file__).resolve().parent.parent
TAILLE_PX = 300  # cote du qr en pixels


def etiquette(contenu, texte, chemin):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=12, border=2)
    qr.add_data(contenu)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # bandeau blanc sous le qr pour le code en clair
    fond = Image.new("RGB", (TAILLE_PX, TAILLE_PX + 50), "white")
    fond.paste(img, (0, 0))
    ImageDraw.Draw(fond).text((10, TAILLE_PX + 15), texte, fill="black")
    fond.save(chemin)


if __name__ == "__main__":
    base = pd.read_csv(RACINE / "data/processed/base_stock.csv")

    # un echantillon : zone a, troncon 14
    ech = base[base["originalLocation"].str.startswith("A-14-")]

    sortie = RACINE / "vision/etiquettes"
    sortie.mkdir(exist_ok=True)

    for loc in ech["originalLocation"].unique():
        etiquette(f"E|{loc}", loc, sortie / f"E_{loc}.png")
    for prod in ech["produit"].unique():
        etiquette(f"P|{prod}", prod, sortie / f"P_{prod}.png")

    print(len(list(sortie.glob("*.png"))), "etiquettes generees")