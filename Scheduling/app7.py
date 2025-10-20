import streamlit as st
import pandas as pd
import datetime
import json

st.set_page_config(page_title="Planning - Disponibilités", layout="wide")

st.title("👥 Disponibilités des employés (vue matrice compacte)")

# --- Données de base ---
employees = [f"Employé {i+1}" for i in range(14)]
today = datetime.date.today()
dates = [today + datetime.timedelta(days=i) for i in range(28)]

# --- Initialisation ---
if "availability_df" not in st.session_state:
    data = []
    for d in dates:
        row = {"Jour": d.strftime("%a %d/%m")}
        for e in employees:
            row[e] = "Travail"
        data.append(row)
    st.session_state.availability_df = pd.DataFrame(data)

df = st.session_state.availability_df

# --- Couleurs et affichage custom ---
color_map = {
    "Travail": "✅",
    "Congé": "❌"
}

# Conversion pour affichage
display_df = df.copy()
for e in employees:
    display_df[e] = display_df[e].map(color_map)

# --- Éditeur Streamlit ---
edited = st.data_editor(
    display_df,
    use_container_width=True,
    hide_index=True,
    disabled=["Jour"],
    key="editor",
    column_config={
        e: st.column_config.SelectboxColumn(
            label=e,
            options=["✅", "❌"],
            help="Clique pour basculer entre travail et congé"
        )
        for e in employees
    },
)

# --- Mise à jour de l'état interne ---
# Remet les valeurs '✅'/'❌' en 'Travail'/'Congé'
reverse_map = {"✅": "Travail", "❌": "Congé"}
for e in employees:
    st.session_state.availability_df[e] = edited[e].map(reverse_map)

# --- Export JSON ---
if st.button("💾 Exporter en JSON"):
    data_to_export = {}
    for _, row in st.session_state.availability_df.iterrows():
        date_label = row["Jour"]
        data_to_export[date_label] = {e: row[e] for e in employees}
    with open("disponibilites_compactes.json", "w", encoding="utf-8") as f:
        json.dump(data_to_export, f, ensure_ascii=False, indent=4)
    st.success("✅ Fichier 'disponibilites_compactes.json' exporté avec succès.")
