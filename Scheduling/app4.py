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
# ⚙️ Onglet 1 : Contraintes générales (VERSION CONDENSÉE)
# ------------------------------------------------------------------------------------------
with tab1:
    st.header("⚙️ Contraintes par activité et par jour")
    st.markdown("Renseigne ci-dessous les **effectifs min/max** par jour et activité dans les tableaux ci-dessous.")

    min_max_constraints = {}

    for activity in activities:
        st.subheader(f"📍 {activity}")

        # DataFrame condensée : 7 jours, deux lignes (Min / Max)
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
# 👥 Onglet 2 : Disponibilités des employés (inchangé)
# ------------------------------------------------------------------------------------------
with tab2:
    st.header("👥 Disponibilités des employés sur les 4 prochaines semaines")
    st.markdown("Clique sur les cellules pour indiquer si un employé **travaille (✅)** ou est en **congé (❌)**.")

    # Crée une DataFrame pour représenter la grille
    dates_str = [d.strftime("%a %d/%m") for d in dates]
    default_values = [["Travail" for _ in dates] for _ in employees]
    schedule_df = pd.DataFrame(default_values, index=employees, columns=dates_str)

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
