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
# ⚙️ Onglet 1 : Contraintes générales
# ------------------------------------------------------------------------------------------
with tab1:
    st.header("⚙️ Contraintes par activité et par jour")
    st.markdown("Définis ici le **nombre minimum et maximum d’employés par jour** pour chaque activité.")

    min_max_constraints = {}

    for activity in activities:
        st.subheader(f"📍 {activity}")
        df = pd.DataFrame(index=day_names, columns=["Min", "Max"])
        for day in day_names:
            df.loc[day, "Min"] = st.number_input(
                f"{activity} – {day} (min)",
                min_value=0, max_value=100, value=1, step=1,
                key=f"{activity}_{day}_min"
            )
            df.loc[day, "Max"] = st.number_input(
                f"{activity} – {day} (max)",
                min_value=0, max_value=100, value=5, step=1,
                key=f"{activity}_{day}_max"
            )
        min_max_constraints[activity] = df.to_dict()

    st.divider()
    st.header("📆 Jours consécutifs maximum")
    max_consecutive_days = {}
    for activity in activities:
        max_consecutive_days[activity] = st.number_input(
            f"{activity} – Jours consécutifs maximum",
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
    st.markdown("Clique sur les cellules pour indiquer si un employé **travaille (✅)** ou est en **congé (❌)**.")

    # Crée une DataFrame pour représenter la grille
    dates_str = [d.strftime("%a %d/%m") for d in dates]
    default_values = [["Travail" for _ in dates] for _ in employees]
    schedule_df = pd.DataFrame(default_values, index=employees, columns=dates_str)

    # Éditeur interactif
    edited_schedule = st.data_editor(
        schedule_df,
        use_container_width=True,
        height=600,
        column_config={
            col: st.column_config.SelectboxColumn(
                col,
                options=["Travail", "Congé"],
                required=True
            ) for col in schedule_df.columns
        },
        hide_index=False,
        key="schedule_editor"
    )

    st.caption("💡 Astuce : tu peux cliquer sur une cellule pour changer entre Travail et Congé.")

# ------------------------------------------------------------------------------------------
# 🧾 Onglet 3 : Résumé & Export
# ------------------------------------------------------------------------------------------
with tab3:
    st.header("🧾 Résumé des paramètres")

    parameters = {
        "effectifs_journaliers": min_max_constraints,
        "jours_consecutifs_max": max_consecutive_days,
        "activites_par_employe": num_activities_per_employee,
        "disponibilites": edited_schedule.to_dict(),
    }

    st.json(parameters)

    if st.button("💾 Exporter les paramètres en JSON"):
        file_name = "parametres_planning.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(parameters, f, ensure_ascii=False, indent=4)
        st.success(f"Paramètres exportés dans `{file_name}` ✅")
