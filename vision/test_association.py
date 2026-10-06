import numpy as np

from association import associer


def etiquette(type_, code, x, y, cote_px=50):
    # qr carre de cote_px pixels centre en (x, y)
    d = cote_px / 2
    coins = np.array([[x - d, y - d], [x + d, y - d], [x + d, y + d], [x - d, y + d]], float)
    return {"type": type_, "code": code, "coins": coins, "centre": np.array([x, y], float)}


# 1 px par mm 
scene = [
    # niveau 3 : une travee entiere, cartons jusqu'a 1,2 m de l'etiquette
    etiquette("emplacement", "A-14-30", 2000, 1000),
    etiquette("produit", "LOIN_G", 800, 880),
    etiquette("produit", "CENTRE", 2000, 880),
    etiquette("produit", "LOIN_D", 3200, 880),
    # niveau 1 : deux positions de 1,22 m cote a cote
    etiquette("emplacement", "A-14-11", 1000, 3000),
    etiquette("emplacement", "A-14-12", 2220, 3000),
    etiquette("produit", "P11", 1400, 2880),
    etiquette("produit", "P12", 1900, 2880),
    # carton dont l'etiquette d'emplacement est hors de l'image
    etiquette("produit", "SANS_ETIQ", 3500, 2880),
]

contenu, orphelins = associer(scene)
attendu = {"A-14-30": {"LOIN_G", "CENTRE", "LOIN_D"}, "A-14-11": {"P11"}, "A-14-12": {"P12"}}

print("contenu   :", contenu)
print("orphelins :", orphelins)
print("OK" if contenu == attendu and orphelins == ["SANS_ETIQ"] else "ECHEC")