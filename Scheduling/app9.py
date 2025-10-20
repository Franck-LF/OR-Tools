import streamlit as st
import datetime

st.set_page_config(page_title="Planning demi-journée compact", layout="wide")
st.title("👥 Planning demi-journée compact")

# --- Paramètres ---
employees = [f"Emp {i+1}" for i in range(14)]
today = datetime.date.today()
dates = [today + datetime.timedelta(days=i) for i in range(28)]  # 4 semaines

# --- Initialisation session_state ---
if "availability_halfday" not in st.session_state:
    st.session_state.availability_halfday = {
        emp: {d.strftime("%Y-%m-%d"): {"Matin": "Travail", "Après-midi": "Travail"} for d in dates}
        for emp in employees
    }

# --- Grille compacte ---
st.markdown("Clique sur un carré pour basculer entre Travail (🟩) et Congé (🟥)")

# Largeur pour réduire le scroll vertical
for d in dates:
    cols = st.columns(len(employees) + 1)
    cols[0].markdown(f"**{d.strftime('%a %d/%m')}**")  # première colonne = date

    for i, emp in enumerate(employees):
        state_m = st.session_state.availability_halfday[emp][d.strftime("%Y-%m-%d")]["Matin"]
        state_a = st.session_state.availability_halfday[emp][d.strftime("%Y-%m-%d")]["Après-midi"]

        col = cols[i + 1]
        # Affichage de 2 boutons très petits côte à côte pour matin et après-midi
        c1, c2 = col.columns(2)

        def toggle(emp=emp, date=d, half="Matin"):
            cur = st.session_state.availability_halfday[emp][date.strftime("%Y-%m-%d")][half]
            st.session_state.availability_halfday[emp][date.strftime("%Y-%m-%d")][half] = \
                "Congé" if cur == "Travail" else "Travail"

        # Matin
        color_m = "green" if state_m == "Travail" else "red"
        if c1.button("", key=f"{emp}_{d}_M", on_click=toggle, args=(emp, d, "Matin")):
            pass

        # Après-midi
        color_a = "green" if state_a == "Travail" else "red"
        if c2.button("", key=f"{emp}_{d}_A", on_click=toggle, args=(emp, d, "Après-midi")):
            pass

        # Couleur des boutons via markdown hack
        c1.markdown(f"<div style='background-color:{color_m}; width:100%; height:20px; border-radius:4px'></div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='background-color:{color_a}; width:100%; height:20px; border-radius:4px'></div>", unsafe_allow_html=True)

# --- Export JSON ---
if st.button("💾 Exporter demi-journées en JSON"):
    file_name = "disponibilites_compactes.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(st.session_state.availability_halfday, f, ensure_ascii=False, indent=4)
    st.success(f"✅ Fichier '{file_name}' exporté avec succès.")
