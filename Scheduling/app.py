import streamlit as st
import json

st.set_page_config(
    page_title="Paramètres des contraintes de planning",
    page_icon="📅",
    layout="centered"
)

st.title("📋 Configuration des contraintes de planning")
st.markdown("Définis ici les paramètres de ton moteur d’optimisation de planning.")

# --- Liste des activités ---
activities = ["Téléphone", "Renseignement", "Dérogation", "Impayés", "Libre"]

st.divider()
st.header("👥 Effectifs minimum et maximum par jour")

# --- Saisie des min/max par activité ---
min_max_constraints = {}
for activity in activities:
    with st.expander(f"⚙️ {activity}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            min_val = st.number_input(
                f"Nombre minimum d’employés pour {activity}",
                min_value=0, max_value=100, value=1, step=1, key=f"min_{activity}"
            )
        with col2:
            max_val = st.number_input(
                f"Nombre maximum d’employés pour {activity}",
                min_value=0, max_value=100, value=5, step=1, key=f"max_{activity}"
            )
        min_max_constraints[activity] = {"min": min_val, "max": max_val}

st.divider()
st.header("📆 Nombre maximum de jours consécutifs")

# --- Jours consécutifs max ---
max_consecutive_days = {}
for activity in activities:
    val = st.number_input(
        f"{activity} – Jours consécutifs maximum",
        min_value=1, max_value=14, value=5, step=1, key=f"jours_{activity}"
    )
    max_consecutive_days[activity] = val

st.divider()
st.header("🔄 Nombre d’activités différentes par employé")

num_activities_per_employee = st.slider(
    "Nombre d’activités différentes par employé par semaine",
    min_value=1, max_value=len(activities), value=3
)

# --- Résumé ---
st.divider()
st.subheader("🧾 Résumé des paramètres")

parameters = {
    "effectifs_journaliers": min_max_constraints,
    "jours_consecutifs_max": max_consecutive_days,
    "activites_par_employe": num_activities_per_employee
}

st.json(parameters)

# --- Export JSON ---
if st.button("💾 Exporter les paramètres en JSON"):
    file_name = "parametres_contraintes.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(parameters, f, ensure_ascii=False, indent=4)
    st.success(f"Paramètres exportés dans le fichier `{file_name}` ✅")
