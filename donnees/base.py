import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
CHEMIN = RACINE / "donnees" / "inventaire.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tournees (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  debut TEXT NOT NULL,
  fin TEXT,
  zone TEXT
);
CREATE TABLE IF NOT EXISTS resultats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tournee_id INTEGER NOT NULL REFERENCES tournees(id),
  emplacement TEXT NOT NULL,
  produit TEXT NOT NULL,
  statut TEXT NOT NULL
    CHECK (statut IN ('conforme', 'mal_range', 'inconnu', 'manquant')),
  horodatage TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_resultats_tournee ON resultats(tournee_id);
"""


def maintenant():
    return datetime.now().isoformat(timespec="seconds")


def connexion(chemin=CHEMIN):
    con = sqlite3.connect(chemin)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def initialiser(con):
    con.executescript(SCHEMA)
    # referentiel de l'entrepot, recharge depuis le dataset
    pd.read_csv(RACINE / "data/processed/emplacements.csv").to_sql(
        "emplacements", con, if_exists="replace", index=False)
    pd.read_csv(RACINE / "data/processed/base_stock.csv").to_sql(
        "stock_attendu", con, if_exists="replace", index=False)


def attendu(con, emplacements):
    """produits attendus pour une liste d'emplacements"""
    marques = ",".join("?" * len(emplacements))
    lignes = con.execute(
        f"SELECT originalLocation, produit FROM stock_attendu "
        f"WHERE originalLocation IN ({marques})", list(emplacements)).fetchall()
    res = {e: set() for e in emplacements}
    for emp, prod in lignes:
        res[emp].add(prod)
    return res


def ouvrir_tournee(con, zone=None):
    cur = con.execute("INSERT INTO tournees (debut, zone) VALUES (?, ?)",
                      (maintenant(), zone))
    con.commit()
    return cur.lastrowid


def enregistrer(con, tournee_id, lignes):
    """lignes : liste de (emplacement, produit, statut)"""
    t = maintenant()
    con.executemany(
        "INSERT INTO resultats (tournee_id, emplacement, produit, statut, horodatage) "
        "VALUES (?, ?, ?, ?, ?)",
        [(tournee_id, e, p, s, t) for e, p, s in lignes])
    con.commit()


def fermer_tournee(con, tournee_id):
    con.execute("UPDATE tournees SET fin = ? WHERE id = ?", (maintenant(), tournee_id))
    con.commit()


def ecarts(con, tournee_id):
    """tout ce qui n'est pas conforme sur une tournee"""
    return pd.read_sql_query(
        "SELECT emplacement, produit, statut FROM resultats "
        "WHERE tournee_id = ? AND statut != 'conforme' "
        "ORDER BY emplacement, statut", con, params=(tournee_id,))