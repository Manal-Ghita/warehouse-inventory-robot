"""sur le robot : envoie au serveur les tournees pas encore recues, et reessaie plus tard sinon"""
import argparse
import json
import time
import urllib.error
import urllib.request

from base import a_envoyer, connexion, marquer_envoyee, paquet

URL = "http://localhost:8090/tournees"
ROBOT = "robot-01"


def envoyer(p):
    req = urllib.request.Request(URL, data=json.dumps(p).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.status in (200, 201)


def synchroniser(con):
    for t in a_envoyer(con):
        try:
            ok = envoyer(paquet(con, t, ROBOT))
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            # pas de reseau : on garde tout, les suivantes attendront aussi
            print(f"tournee {t} : serveur injoignable, nouvel essai plus tard")
            return
        if ok:
            marquer_envoyee(con, t)
            print(f"tournee {t} envoyee")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--une-fois", action="store_true", help="un seul essai puis on quitte")
    ap.add_argument("--periode", type=float, default=30.0, help="secondes entre deux essais")
    args = ap.parse_args()

    con = connexion()
    while True:
        synchroniser(con)
        if args.une_fois:
            break
        time.sleep(args.periode)