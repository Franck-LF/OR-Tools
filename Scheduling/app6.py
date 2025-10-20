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
# Onglet 1 : Contraintes (condensé)
# ------------------------------------------------------------------------------------------
with tab1:
    st.header("⚙️ Contraintes par activité et par jour (condensé)")
    st.markdown("Remplis les tableaux Min / Max pour chaque activité (7 jours).")

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
# Onglet 2 : Disponibilités — grille cliquable (CORRIGÉE)
# ------------------------------------------------------------------------------------------
with tab2:
    st.header("👥 Disponibilités des employés (cliquez une fois pour basculer)")
    st.markdown("🟩 => Travail | 🟥 => Congé — clic unique pour basculer, mise à jour immédiate.")

    # --- initialisation session_state (utiliser des clés string ISO pour stabilité)
    if "availability" not in st.session_state:
        st.session_state.availability = {
            emp: {d.isoformat(): "Travail" for d in dates} for emp in employees
        }

    # callback utilisé par st.button — met à jour l'état et force le rerun
    def toggle(emp: str, date_iso: str):
        cur = st.session_state.availability[emp][date_iso]
        st.session_state.availability[emp][date_iso] = "Congé" if cur == "Travail" else "Travail"

    # Affichage compact : pour chaque employé on affiche 4 lignes (une par semaine) de 7 boutons
    for emp in employees:
        with st.expander(emp, expanded=False):
            # Affiche les 4 semaines
            for week_idx in range(4):
                week_dates = dates[week_idx*7:(week_idx+1)*7]
                cols = st.columns(7)
                for i, d in enumerate(week_dates):
                    date_iso = d.isoformat()
                    state = st.session_state.availability[emp][date_iso]
                    emoji = "✅" if state == "Travail" else "❌"
                    # Choisir couleur CSS pour le texte de la description (Streamlit button n'accepte pas style)
                    # On garde un label explicite ; la couleur visuelle sera simulée par emoji + texte.
                    label = f"{emoji} {d.strftime('%a %d/%m')}"
                    key = f"btn_{emp}_{date_iso}"
                    # Utiliser on_click pour que le toggle s'exécute immédiatement et l'UI se mette à jour
                    if cols[i].button(label, key=key, on_click=toggle, args=(emp, date_iso)):
                        pass  # Le callback toggle fera le travail ; on ne fait rien ici

                # Petite séparation visuelle entre semaines
                st.markdown("---")

    st.caption("Astuce : utilise l'expander pour ouvrir/fermer chaque employé et éviter un écran surchargé.")

# ------------------------------------------------------------------------------------------
# Onglet 3 : Résumé & Export
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
