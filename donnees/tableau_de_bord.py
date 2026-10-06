import pandas as pd
import streamlit as st
from pathlib import Path

from base import connexion

st.set_page_config(page_title="Inventaire entrepot", layout="wide")
con = connexion(Path(__file__).resolve().parent / "serveur.db")

tournees = pd.read_sql_query(
    "SELECT id, debut, fin, zone FROM tournees ORDER BY id DESC", con)
if tournees.empty:
    st.info("Aucune tournée enregistrée.")
    st.stop()

st.title("Inventaire de l'entrepôt")

debuts = tournees.set_index("id")["debut"]
choix = int(st.selectbox("Tournée", tournees["id"],
                         format_func=lambda i: f"n° {i} du {debuts[i]}"))

res = pd.read_sql_query(
    "SELECT emplacement, produit, statut FROM resultats WHERE tournee_id = ?",
    con, params=(choix,))

# indicateurs de la tournee
c1, c2, c3 = st.columns(3)
c1.metric("Emplacements contrôlés", res["emplacement"].nunique())
c2.metric("Conformité", f"{(res['statut'] == 'conforme').mean() * 100:.1f} %")
c3.metric("Écarts", int((res["statut"] != "conforme").sum()))

st.subheader("Écarts")
statuts = ["manquant", "mal_range", "inconnu"]
filtre = st.multiselect("Statuts", statuts, default=statuts)
ec = res[res["statut"].isin(filtre)].sort_values(["emplacement", "statut"])
st.dataframe(ec, width="stretch", hide_index=True)
st.download_button("Télécharger le rapport (CSV)",
                   ec.to_csv(index=False).encode("utf-8"),
                   file_name=f"ecarts_tournee_{choix}.csv", mime="text/csv")

st.subheader("Évolution de la conformité")
hist = pd.read_sql_query(
    "SELECT tournee_id, AVG(statut = 'conforme') * 100 AS conformite "
    "FROM resultats GROUP BY tournee_id ORDER BY tournee_id", con)
st.line_chart(hist, x="tournee_id", y="conformite")