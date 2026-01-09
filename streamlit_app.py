import streamlit as st
import sys
import os
import pandas as pd

# 1. Move set_page_config to the top
st.set_page_config(page_title="Onkologian Työpöytä", layout="wide")

# Add current directory to path so we can import oncology_helper
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add 'onkohelper' subdirectory to path because oncology_helper package is inside it
package_dir = os.path.join(current_dir, 'onkohelper')
if package_dir not in sys.path:
    sys.path.append(package_dir)

from oncology_helper.data import Tietokanta
from oncology_helper.logic import safe_float, laske_bsa, laske_cockcroft_gault, pyorista_tabletit

# Load Data
@st.cache_resource
def load_data():
    Tietokanta.lataa()

try:
    load_data()
except Exception as e:
    st.error(f"Virhe ladattaessa tietokantaa: {e}")

st.title("Onkologian Työpöytä v2.3 (Streamlit)")

# Sidebar for navigation
view = st.sidebar.radio("Valitse näkymä", ["Laskuri", "Tietoa"])

if view == "Laskuri":
    st.header("Sytostaattilaskuri")

    # Input section
    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Potilas", expanded=True):
            pituus = st.number_input("Pituus (cm)", min_value=0.0, step=1.0, format="%.1f")
            paino = st.number_input("Paino (kg)", min_value=0.0, step=0.1, format="%.1f")
            ika = st.number_input("Ikä", min_value=0, step=1)
            krea = st.number_input("Krea", min_value=0, step=1)
            sukupuoli = st.selectbox("Sukupuoli", ["Mies", "Nainen"])

            # Calculations
            bsa = laske_bsa(pituus, paino)
            gfr = laske_cockcroft_gault(ika, paino, krea, sukupuoli)

            st.metric("BSA", f"{bsa:.2f} m²")
            st.metric("GFR", f"{gfr:.0f} ml/min")

    with col2:
        st.subheader("Hoito")
        protokollat = list(Tietokanta.data.keys())
        valittu_protokolla = st.selectbox("Protokolla", [""] + protokollat)

        # Labs default value
        labrat_default = ""
        protokolla_data = None
        if valittu_protokolla and valittu_protokolla in Tietokanta.data:
            protokolla_data = Tietokanta.data[valittu_protokolla]
            labrat_default = protokolla_data.get('kontrollit', '')

        # Use key to force update when protocol changes
        labrat = st.text_input("Labrat", value=labrat_default, key=f"labrat_{valittu_protokolla}")

        if protokolla_data:
            st.subheader("Lääkkeet")

            laske_tulokset = []

            # Header
            cols = st.columns([3, 2, 2, 2, 2, 2])
            cols[0].markdown("**Lääke**")
            cols[1].markdown("**Annos**")
            cols[2].markdown("**Yks.**")
            cols[3].markdown("**Vahvuus**")
            cols[4].markdown("**Tulos (mg)**")
            cols[5].markdown("**Määräys**")

            for i, med in enumerate(protokolla_data['lääkkeet']):
                c = st.columns([3, 2, 2, 2, 2, 2])

                # Name
                c[0].write(med['nimi'])

                # 2. Fix sticky widget state issue by adding valittu_protokolla to keys

                # Dose (Annos)
                annos_val = med['annos']
                annos = c[1].number_input(f"Annos {i}", value=float(annos_val), step=10.0, label_visibility="collapsed", key=f"{valittu_protokolla}_annos_{i}")

                # Unit (Yksikkö)
                yksikkö_val = med.get('yksikkö', 'mg/m2')
                yksikkö_opts = ["mg/m2", "mg/kg", "AUC", "mg"]
                if yksikkö_val not in yksikkö_opts:
                    yksikkö_opts.append(yksikkö_val)
                # Ensure default is in options
                idx = yksikkö_opts.index(yksikkö_val) if yksikkö_val in yksikkö_opts else 0
                yksikkö = c[2].selectbox(f"Yks {i}", yksikkö_opts, index=idx, label_visibility="collapsed", key=f"{valittu_protokolla}_yks_{i}")

                # Strength (Vahvuus / Tablettikoot)
                tablettikoot = med.get("tablettikoot", [])
                vahvuus_str = "None"
                if tablettikoot:
                    vahvuus_str = c[3].selectbox(f"Vahv {i}", tablettikoot, label_visibility="collapsed", key=f"{valittu_protokolla}_vahv_{i}")
                else:
                    c[3].write("-")

                # Calculate Result
                mg = 0.0
                if yksikkö == "mg/m2":
                    mg = annos * bsa
                elif yksikkö == "mg/kg":
                    mg = annos * paino
                elif yksikkö == "AUC":
                     # Calvert formula: Dose = AUC * (GFR + 25)
                     # GFR cap is often 125 ml/min
                    mg = annos * (min(gfr, 125) + 25)
                else: # mg
                    mg = annos

                c[4].write(f"{mg:.0f}")

                # Final Amount (Määräys)
                fin = int(round(mg))
                if vahvuus_str and vahvuus_str != "None":
                    try:
                        strength = float(vahvuus_str.split()[0])
                        fin = pyorista_tabletit(mg, strength)
                    except:
                        pass

                # Use a session state key that includes the calculated value to force update if calculation changes
                # But to allow manual edit, we need to be careful.
                # A common pattern is:
                # If calculated value differs from stored calculated value, update 'maarays' state.

                state_key = f"{valittu_protokolla}_maar_{i}"
                calc_key = f"{valittu_protokolla}_calc_{i}"

                # Check if calculation changed since last run
                if calc_key not in st.session_state or st.session_state[calc_key] != fin:
                    st.session_state[state_key] = int(fin)
                    st.session_state[calc_key] = fin

                maarays = c[5].number_input(f"Määräys {i}", step=1, label_visibility="collapsed", key=state_key)

                laske_tulokset.append({
                    "med": med,
                    "annos": annos,
                    "yksikkö": yksikkö,
                    "vahvuus": vahvuus_str,
                    "tulos_mg": mg,
                    "maarays": maarays
                })

            # Report Generation
            st.subheader("Raportti")

            report_lines = []
            report_lines.append(f"PROTOKOLLA: {valittu_protokolla}")
            if "sykli" in protokolla_data:
                report_lines.append(f"Sykli: {protokolla_data['sykli']}")
            report_lines.append(f"Labrat: {labrat}")
            report_lines.append("-" * 40)

            for item in laske_tulokset:
                med = item['med']
                fin_val = item['maarays']

                report_lines.append(f"• {med['nimi']}: {fin_val} mg")

                ts = item['vahvuus']
                if ts and ts != "None" and fin_val > 0:
                    try:
                        strength = float(ts.split()[0])
                        count = fin_val / strength
                        report_lines.append(f"    -> {count:.1f} kpl ({ts})")
                    except:
                        pass

                if med.get('päivät'):
                    report_lines.append(f"   Ajoitus: {med['päivät']}")

            report_lines.append("-" * 40)
            report_lines.append(f"TUKIHOIDOT:\n{protokolla_data.get('esilääkitys', '-')}")

            report_text = "\n".join(report_lines)
            st.text_area("Kopioitava teksti", report_text, height=300)


elif view == "Tietoa":
    st.info("Tämä on Streamlit-versio Onkologian Työpöytä -sovelluksesta.")
