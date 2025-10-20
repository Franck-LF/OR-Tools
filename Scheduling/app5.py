import streamlit as st
import json
import pandas as pd
import datetime

st.set_page_config(
    page_title="Configuration de planning",
    page_icon="📅",
    layout="wide"
)

st.title("📋 Outil de configuration des contraintes de planning")

# === Données de base ===
activities = ["Téléphone", "Renseignement", "Dérogation", "Impayés", "Libre"]
employees = [f"Employé {i+1}" for i in range(14)]
day_names = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

today = datetime.date.today()
dates = [today + datetime.timedelta(days=i) for i in range(28)]  # 4 semaines


# === Onglets ===
tab1, tab2, tab3 = st.tabs(["⚙️ Contraintes générales", "👥 Disponibilités", "🧾 Résumé & Export"])

# ------------------------------------------------------------------------------------------
# ⚙️ Onglet 1 (identique à la version condensée précédente)
# ------------------------------------------------------------------------------------------
with tab1:
    st.header("⚙️ Contraintes par activité et par jour")
    st.markdown("Renseigne les **effectifs min/max** par jour et activité.")

    min_max_constraints = {}
    for activity in activities:
        st.subheader(f"📍 {activity}")
        data = pd.DataFrame(
            [[1] * 7, [5] * 7],
            index=["Min", "Max"],
            columns=day_names
        )
        edited = st.data_editor(
            data,
            use_container_width=True,
            height=150,
            key=f"grid_{activity}",
            num_rows="fixed"
        )
        min_max_constraints[activity] = edited.to_dict()

    st.divider()
    st.header("📆 Jours consécutifs maximum")
    max_consecutive_days = {}
    cols = st.columns(len(activities))
    for i, activity in enumerate(activities):
        with cols[i]:
            max_consecutive_days[activity] = st.number_input(
                f"{activity}",
                min_value=1, max_value=14, value=5, step=1, key=f"jours_{activity}"
            )

    st.divider()
    st.header("🔄 Activités par employé")
    num_activities_per_employee = st.slider(
        "Nombre d’activités différentes par employé par semaine",
        min_value=1, max_value=len(activities), value=3
    )

# ------------------------------------------------------------------------------------------
# 👥 Onglet 2 : Nouvelle grille interactive colorée
# ------------------------------------------------------------------------------------------
with tab2:
    st.header("👥 Disponibilités des employés")
    st.markdown("Clique sur une case pour basculer entre **Travail (🟩)** et **Congé (🟥)**.")

    # Initialisation dans la session
    if "availability" not in st.session_state:
        st.session_state.availability = {
            emp: {str(date): "Travail" for date in dates} for emp in employees
        }

    # Fonction de bascule
    def toggle(emp, date):
        current = st.session_state.availability[emp][str(date)]
        st.session_state.availability[emp][str(date)] = (
            "Congé" if current == "Travail" else "Travail"
        )

    # Affichage de la grille
    for emp in employees:
        with st.expander(emp, expanded=False):
            cols = st.columns(7)
            for i, date in enumerate(dates):
                col = cols[i % 7]
                day_label = date.strftime("%a %d/%m")
                state = st.session_state.availability[emp][str(date)]

                color = "green" if state == "Travail" else "red"
                emoji = "✅" if state == "Travail" else "❌"
                style = f"""
                    background-color:{color};
                    color:white;
                    border:none;
                    border-radius:8px;
                    padding:0.4em 0.8em;
                    width:100%;
                    cursor:pointer;
                """

                if col.button(f"{emoji} {day_label}", key=f"{emp}_{date}", use_container_width=True):
                    toggle(emp, date)

                # Saut de ligne chaque semaine
                if (i + 1) % 7 == 0 and i < len(dates) - 1:
                    cols = st.columns(7)

# ------------------------------------------------------------------------------------------
# 🧾 Onglet 3 : Résumé & Export
# ------------------------------------------------------------------------------------------
with tab3:
    st.header("🧾 Résumé des paramètres")

    parameters = {
        "effectifs_journaliers": min_max_constraints,
        "jours_consecutifs_max": max_consecutive_days,
        "activites_par_employe": num_activities_per_employee,
        "disponibilites": st.session_state.availability,
    }

    st.json(parameters)

    if st.button("💾 Exporter les paramètres en JSON"):
        file_name = "parametres_planning.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(parameters, f, ensure_ascii=False, indent=4)
        st.success(f"Paramètres exportés dans `{file_name}` ✅")
