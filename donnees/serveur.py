"""serveur de l'entrepot : recoit les tournees des robots en http et les range dans serveur.db"""
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

CHEMIN = Path(__file__).resolve().parent / "serveur.db"
PORT = 8090

SCHEMA = """
CREATE TABLE IF NOT EXISTS tournees (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  robot TEXT NOT NULL,
  id_robot INTEGER NOT NULL,
  debut TEXT,
  fin TEXT,
  zone TEXT,
  recue TEXT NOT NULL,
  UNIQUE (robot, id_robot)
);
CREATE TABLE IF NOT EXISTS resultats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tournee_id INTEGER NOT NULL REFERENCES tournees(id),
  emplacement TEXT NOT NULL,
  produit TEXT NOT NULL,
  statut TEXT NOT NULL,
  horodatage TEXT
);
"""


def ranger(p):
    """renvoie False si la tournee etait deja la (renvoi apres une coupure)"""
    con = sqlite3.connect(CHEMIN)
    try:
        with con:   # tout ou rien
            t = p["tournee"]
            cur = con.execute(
                "INSERT OR IGNORE INTO tournees (robot, id_robot, debut, fin, zone, recue) "
                "VALUES (?, ?, ?, ?, ?, datetime('now'))",
                (p["robot"], t["id"], t["debut"], t["fin"], t["zone"]))
            if cur.rowcount == 0:
                return False
            con.executemany(
                "INSERT INTO resultats (tournee_id, emplacement, produit, statut, horodatage) "
                "VALUES (?, ?, ?, ?, ?)",
                [(cur.lastrowid, r["emplacement"], r["produit"], r["statut"], r["horodatage"])
                 for r in p["resultats"]])
        return True
    finally:
        con.close()


class Reception(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/tournees":
            self.send_error(404)
            return
        try:
            p = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        except json.JSONDecodeError:
            self.send_error(400, "json invalide")
            return
        nouvelle = ranger(p)
        print(f"tournee {p['tournee']['id']} de {p['robot']} : "
              f"{'recue' if nouvelle else 'deja connue, ignoree'}")
        self.send_response(201 if nouvelle else 200)
        self.end_headers()

    def log_message(self, *args):
        pass   

if __name__ == "__main__":
    con = sqlite3.connect(CHEMIN)
    con.executescript(SCHEMA)
    con.close()
    print(f"serveur en ecoute sur le port {PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Reception).serve_forever()