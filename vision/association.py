def associer(etiquettes, tol_x_px):
    """range chaque produit sous l'emplacement le plus proche en dessous"""
    emps = [e for e in etiquettes if e["type"] == "emplacement"]
    prods = [e for e in etiquettes if e["type"] == "produit"]

    contenu = {e["code"]: set() for e in emps}
    orphelins = []
    for p in prods:
        px, py = p["centre"]
        # emplacements sous le produit, dans la meme colonne
        sous = [e for e in emps
                if e["centre"][1] > py and abs(e["centre"][0] - px) < tol_x_px]
        if not sous:
            orphelins.append(p["code"])
            continue
        e = min(sous, key=lambda e: e["centre"][1] - py)
        contenu[e["code"]].add(p["code"])
    return contenu, orphelins