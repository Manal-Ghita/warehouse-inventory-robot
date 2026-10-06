import numpy as np

COTE_QR_MM = 50
# demi-largeur d'un emplacement selon le niveau
DEMI_LARGEUR_MM = {1: 610, 2: 610, 3: 1830, 4: 1830}
HAUTEUR_MAX_MM = 600


def niveau(code):
    # a-14-30 -> 3
    return int(code.split("-")[2][0])


def px_par_mm(etiquette):
    # taille du qr en pixels, la distance n'importe pas
    c = etiquette["coins"]
    cote = np.mean([np.linalg.norm(c[i] - c[(i + 1) % 4]) for i in range(4)])
    return cote / COTE_QR_MM


def associer(etiquettes):
    """range chaque produit sous l'emplacement juste en dessous, dans sa largeur"""
    emps = [e for e in etiquettes if e["type"] == "emplacement"]
    prods = [e for e in etiquettes if e["type"] == "produit"]

    contenu = {e["code"]: set() for e in emps}
    orphelins = []
    for p in prods:
        px, py = p["centre"]
        candidats = []
        for e in emps:
            ex, ey = e["centre"]
            k = px_par_mm(e)
            dessous = 0 < ey - py < HAUTEUR_MAX_MM * k
            dedans = abs(px - ex) <= DEMI_LARGEUR_MM[niveau(e["code"])] * k
            if dessous and dedans:
                candidats.append((ey - py, abs(px - ex), e["code"], k))
        if not candidats:
            orphelins.append(p["code"])
            continue
        dy_min = min(c[0] for c in candidats)
        meme_lisse = [c for c in candidats if c[0] - dy_min < 150 * c[3]]
        contenu[min(meme_lisse, key=lambda c: c[1])[2]].add(p["code"])
    return contenu, orphelins