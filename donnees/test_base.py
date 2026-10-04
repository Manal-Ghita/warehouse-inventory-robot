from base import (connexion, ecarts, enregistrer, fermer_tournee,
                  initialiser, ouvrir_tournee)

con = connexion()
initialiser(con)

t = ouvrir_tournee(con, zone="A")
enregistrer(con, t, [
    ("A-14-13", "63KAC1", "conforme"),
    ("A-14-13", "M8W7TS", "conforme"),
    ("A-14-13", "ZZZZZZ", "inconnu"),
    ("A-14-13", "GPBMZJ", "manquant"),
    ("A-14-12", "EYEOXS", "conforme"),
    ("A-14-12", "TLFT43", "conforme"),
    ("A-14-12", "M8W7TS", "mal_range"),
    ("A-14-12", "YE890X", "manquant"),
    ("A-14-11", "4E0KXI", "conforme"),
    ("A-14-11", "O7TSVL", "conforme"),
    ("A-14-11", "TQBVRI", "manquant"),
])
fermer_tournee(con, t)

print(f"tournee {t}, ecarts :")
print(ecarts(con, t))