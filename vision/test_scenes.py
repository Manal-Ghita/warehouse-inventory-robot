from pathlib import Path

import cv2
import numpy as np
import time

from lecteur import lire

ETIQ = Path(__file__).resolve().parent / "etiquettes"
MM_PX = 2                    # resolution du rayonnage virtuel
COTE_MM = 50                 # cote du qr imprime
L_MM, H_MM = 1000, 500       # morceau de rayonnage
W, H = 1920, 1080            # image de la gemini 335
FX = (W / 2) / np.tan(np.radians(86 / 2))
K = np.array([[FX, 0, W / 2], [0, FX, H / 2], [0, 0, 1]])


def rayonnage(codes):
    p = np.full((H_MM * MM_PX, L_MM * MM_PX, 3), 190, np.uint8)
    cote = COTE_MM * MM_PX
    poses = {}
    x, y = 40, 40
    for c in codes:
        e = cv2.imread(str(ETIQ / f"{c}.png"))
        # le qr fait toute la largeur : on le ramene a 5 cm
        e = cv2.resize(e, (cote, round(cote * e.shape[0] / e.shape[1])),
                       interpolation=cv2.INTER_AREA)
        h, w = e.shape[:2]
        if x + w > p.shape[1] - 40:
            x, y = 40, y + h + 60
        if y + h > p.shape[0] - 40:
            break
        p[y:y + h, x:x + w] = e
        poses[c] = (x + w / 2, y + cote / 2)   # centre du qr
        x += w + 70
    return p, poses


def homographie(d_mm, angle_deg):
    # camera a d_mm du rayonnage, tournee de angle_deg
    a = np.radians(angle_deg)
    R = np.array([[np.cos(a), 0, np.sin(a)],
                  [0, 1, 0],
                  [-np.sin(a), 0, np.cos(a)]])
    t = np.array([0, 0, d_mm])
    S = np.array([[1 / MM_PX, 0, -L_MM / 2],
                  [0, 1 / MM_PX, -H_MM / 2],
                  [0, 0, 1]])
    return K @ np.column_stack([R[:, 0], R[:, 1], t]) @ S


def degrader(img, flou_px, bruit, gain):
    if flou_px > 1:
        # flou de boge horizontal, le robot roule
        k = np.zeros((flou_px, flou_px))
        k[flou_px // 2, :] = 1 / flou_px
        img = cv2.filter2D(img, -1, k)
    img = img.astype(np.float32) * gain + np.random.normal(0, bruit, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8)


def essai(codes, d_mm, angle, flou, bruit, gain, sauver=None):
    p, poses = rayonnage(codes)
    Hm = homographie(d_mm, angle)
    img = cv2.warpPerspective(p, Hm, (W, H), borderValue=(120, 120, 120))
    img = degrader(img, flou, bruit, gain)
    if sauver:
        cv2.imwrite(sauver, img)

    # etiquettes vraiment dans le champ de la camera
    visibles = set()
    for c, (x, y) in poses.items():
        u, v = cv2.perspectiveTransform(np.array([[[x, y]]], np.float32), Hm)[0, 0]
        if 40 < u < W - 40 and 40 < v < H - 40:
            visibles.add(c)

    lus = {("E" if e["type"] == "emplacement" else "P") + "_" + e["code"]
           for e in lire(img)}
    return len(lus & visibles), len(visibles)


if __name__ == "__main__":
    codes = sorted(f.stem for f in ETIQ.glob("*.png"))[:24]
    conditions = [
        # nom, distance mm, angle, flou px, bruit, gain lumiere
        ("reference", 600, 0, 0, 0, 1.0),
        ("de biais 30", 600, 30, 0, 0, 1.0),
        ("loin 0,75 m", 750, 0, 0, 0, 1.0),
        ("flou reel 2 ms", 600, 0, 1, 0, 1.0),
        ("flou fort 15 ms", 600, 0, 5, 0, 1.0),
        ("bruit", 600, 0, 0, 12, 1.0),
        ("sombre", 600, 0, 0, 6, 0.4),
        ("tout ensemble", 650, 25, 4, 10, 0.6),
    ]
    debut = time.perf_counter()
    for nom, d, a, f, b, g in conditions:
        sauver = "scene_reference.png" if nom == "reference" else None
        lus, vis = essai(codes, d, a, f, b, g, sauver)
        print(f"{nom:15s} {lus:3d}/{vis:<3d} {100 * lus / max(vis, 1):5.0f} %")
        print(f"temps moyen par image : {(time.perf_counter() - debut) / len(conditions):.2f} s")