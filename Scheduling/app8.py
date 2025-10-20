import streamlit as st
import pandas as pd
import datetime
import json

st.set_page_config(page_title="Planning demi-journée", layout="wide")
st.title("👥 Disponibilités par demi-journée")

# --- Paramètres ---
employees = [f"Employé {i+1}" for i in range(14)]
today = datetime.date.today()
dates = [today + datetime.timedelta(days=i) for i in range(28)]  # 4 semaines

# --- Initialisation session_state ---
if "availability_halfday" not in st.session_state:
    # Structure : {employé -> {date -> {"Matin": état, "Après-midi": état}}}
    st.session_state.availability_halfday = {
        emp: {d.strftime("%Y-%m-%d"): {"Matin": "Travail", "Après-midi": "Travail"} for d in dates}
        for emp in employees
    }

# --- Création de DataFrame pour afficher la grille par demi-journée ---
rows = []
for d in dates:
    row = {"Jour": d.strftime("%a %d/%m")}
    for emp in employees:
        # Afficher le matin et l'après-midi sous forme concaténée pour l'affichage
        val_m = st.session_state.availability_halfday[emp][d.strftime("%Y-%m-%d")]["Matin"]
        val_a = st.session_state.availability_halfday[emp][d.strftime("%Y-%m-%d")]["Après-midi"]
        row[f"{emp} - Matin"] = "✅" if val_m == "Travail" else "❌"
        row[f"{emp} - Après-midi"] = "✅" if val_a == "Travail" else "❌"
    rows.append(row)

df_display = pd.DataFrame(rows)

# --- Column config pour pouvoir sélectionner Trav/Conge directement ---
col_config = {}
for emp in employees:
    col_config[f"{emp} - Matin"] = st.column_config.SelectboxColumn(
        label=f"{emp} Matin",
        options=["✅", "❌"],
        help="Clique pour basculer Trav/Conge"
    )
    col_config[f"{emp} - Après-midi"] = st.column_config.SelectboxColumn(
        label=f"{emp} Après-midi",
        options=["✅", "❌"],
        help="Clique pour basculer Trav/Conge"
    )

edited = st.data_editor(
    df_display,
    use_container_width=True,
    hide_index=True,
    column_config=col_config,
    key="editor_halfday"
)

# --- Mise à jour session_state selon le résultat de l'éditeur ---
reverse_map = {"✅": "Travail", "❌": "Congé"}
for emp in employees:
    for i, d in enumerate(dates):
        st.session_state.availability_halfday[emp][d.strftime("%Y-%m-%d")]["Matin"] = reverse_map[edited.loc[i, f"{emp} - Matin"]]
        st.session_state.availability_halfday[emp][d.strftime("%Y-%m-%d")]["Après-midi"] = reverse_map[edited.loc[i, f"{emp} - Après-midi"]]

# --- Export JSON ---
if st.button("💾 Exporter demi-journées en JSON"):
    file_name = "disponibilites_demi_journee.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(st.session_state.availability_halfday, f, ensure_ascii=False, indent=4)
    st.success(f"✅ Fichier '{file_name}' exporté avec succès.")
