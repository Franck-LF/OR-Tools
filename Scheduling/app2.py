import streamlit as st
import json
import pandas as pd
import datetime

st.set_page_config(
    page_title="Outil de configuration des plannings",
    page_icon="📅",
    layout="wide"
)

st.title("📋 Outil de configuration des contraintes de planning")

# === Données de base ===
activities = ["Téléphone", "Renseignement", "Dérogation", "Impayés", "Libre"]
employees = [f"Employé {i+1}" for i in range(14)]
days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

today = datetime.date.today()
weeks = [today + datetime.timedelta(days=i) for i in range(28)]  # 4 semaines


# === Onglets Streamlit ===
tab1, tab2, tab3 = st.tabs(["⚙️ Contraintes générales", "👥 Disponibilités", "🧾 Résumé & Export"])

# ------------------------------------------------------------------------------------------
# 🧩 Onglet 1 : Contraintes générales
# ------------------------------------------------------------------------------------------
with tab1:
    st.header("⚙️ Contraintes par activité et par jour")
    st.markdown("Définis ici le **nombre minimum et maximum d’employés par jour** pour chaque activité.")

    day_names = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    min_max_constraints = {}

    for activity in activities:
        st.subheader(f"📍 {activity}")
        df = pd.DataFrame(index=day_names, columns=["Min", "Max"])
        for day in day_names:
            cols = st.columns(2)
            with cols[0]:
                min_val = st.number_input(
                    f"{day} – Min", min_value=0, max_value=100, value=1, step=1, key=f"{activity}_{day}_min"
                )
            with cols[1]:
                max_val = st.number_input(
                    f"{day} – Max", min_value=0, max_value=100, value=5, step=1, key=f"{activity}_{day}_max"
                )
            df.loc[day] = [min_val, max_val]
        min_max_constraints[activity] = df.to_dict()

    st.divider()
    st.header("📆 Jours consécutifs maximum par activité")
    max_consecutive_days = {}
    for activity in activities:
        max_consecutive_days[activity] = st.number_input(
            f"{activity} – Jours consécutifs max",
            min_value=1, max_value=14, value=5, step=1, key=f"jours_{activity}"
        )

    st.divider()
    st.header("🔄 Activités par employé")
    num_activities_per_employee = st.slider(
        "Nombre d’activités différentes par employé par semaine",
        min_value=1, max_value=len(activities), value=3
    )


# ------------------------------------------------------------------------------------------
# 👥 Onglet 2 : Disponibilités des employés
# ------------------------------------------------------------------------------------------
with tab2:
    st.header("👥 Disponibilités des employés sur les 4 prochaines semaines")

    st.markdown("Clique sur **Travail** ou **Congé** pour définir la présence de chaque employé sur chaque jour.")

    # Créer une grille vide
    schedule_data = {}
    for emp in employees:
        schedule_data[emp] = {}
        for i, date in enumerate(weeks):
            key = f"{emp}_{date}"
            work = st.radio(
                f"{emp} – {date.strftime('%a %d/%m')}",
                ["Travail", "Congé"],
                horizontal=True,
                key=key,
                index=0
            )
            schedule_data[emp][str(date)] = work

# ------------------------------------------------------------------------------------------
# 🧾 Onglet 3 : Résumé & Export
# ------------------------------------------------------------------------------------------
with tab3:
    st.header("🧾 Résumé des paramètres")

    parameters = {
        "effectifs_journaliers": min_max_constraints,
        "jours_consecutifs_max": max_consecutive_days,
        "activites_par_employe": num_activities_per_employee,
        "disponibilites": schedule_data,
    }

    st.json(parameters)

    if st.button("💾 Exporter les paramètres en JSON"):
        file_name = "parametres_planning.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(parameters, f, ensure_ascii=False, indent=4)
        st.success(f"Paramètres exportés dans `{file_name}` ✅")
