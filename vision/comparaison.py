def comparer(observe, attendu, produits_connus):
    """statut de chaque couple (emplacement, produit) vu ou attendu"""
    lignes = []
    for emp, vus in observe.items():
        prevus = attendu.get(emp, set())
        for p in sorted(vus & prevus):
            lignes.append((emp, p, "conforme"))
        for p in sorted(vus - prevus):
            lignes.append((emp, p, "mal_range" if p in produits_connus else "inconnu"))
        for p in sorted(prevus - vus):
            lignes.append((emp, p, "manquant"))
    return lignes