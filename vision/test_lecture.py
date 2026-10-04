from pathlib import Path

import cv2

from lecteur import lire

DOSSIER = Path(__file__).resolve().parent / "etiquettes"

images = sorted(DOSSIER.glob("*.png"))
reussies = 0
for chemin in images:
    attendu = chemin.stem.split("_", 1)[1]   # E_A-14-11.png -> A-14-11
    lus = lire(cv2.imread(str(chemin)))
    if len(lus) == 1 and lus[0]["code"] == attendu:
        reussies += 1
    else:
        print("echec :", chemin.name, lus)

print(f"{reussies}/{len(images)} etiquettes lues")