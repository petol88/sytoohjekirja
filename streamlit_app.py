import streamlit as st
import sys
import os

# 1. Move set_page_config to the top
st.set_page_config(page_title="Onkologian Työpöytä", layout="wide")

# Add current directory to path so we can import oncology_helper
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add 'onkohelper' subdirectory to path because oncology_helper package is inside it
package_dir = os.path.join(current_dir, 'onkohelper')
if package_dir not in sys.path:
    sys.path.append(package_dir)

from oncology_helper.data import Tietokanta, TNM_DATA
import math

def safe_float(arvo, oletus=0.0):
    try:
        return float(arvo)
    except (ValueError, TypeError):
        return oletus

def laske_bsa(pituus_cm, paino_kg):
    # Lasketaan kehon pinta-ala Mostellerin kaavalla
    if pituus_cm <= 0 or paino_kg <= 0:
        return 0.0
    return math.sqrt((pituus_cm * paino_kg) / 3600.0)

def laske_cockcroft_gault(ika, paino_kg, krea_umol, sukupuoli):
    # Lasketaan kreatiniinipuhdistuma (Cockcroft-Gault)
    if ika <= 0 or paino_kg <= 0 or krea_umol <= 0:
        return 0.0
    # Peruskaava miehille (krea yksikössä umol/l)
    gfr = ((140 - ika) * paino_kg) / (0.814 * krea_umol)
    # Naisilla tulos kerrotaan kertoimella 0.85
    if sukupuoli.lower() == "nainen":
        gfr *= 0.85
    return gfr

def pyorista_tabletit(mg_maara, tabletin_vahvuus_mg):
    # Pyöristetään lääkeannos lähimpään tablettikokoon
    if tabletin_vahvuus_mg <= 0:
        return mg_maara
    kpl = round(mg_maara / tabletin_vahvuus_mg)
    return kpl * tabletin_vahvuus_mg

def laske_stage_rintasyopa(t, n, m):
    # Koska tarkka staging-logiikka poistettiin logic.py:n mukana, 
    # tässä on yksinkertaistettu varavaihtoehto, jotta sovellus ei kaadu.
    if "M1" in str(m): return "IV"
    return "Tuntematon (vaatii erillisen logiikan)"

def maarita_hoitosuunnitelma_rintasyopa(*args, **kwargs):
    # Placeholder poistetulle hoitosuunnitelman logiikalle
    return "Hoitosuunnitelmaa ei voida automaattisesti määrittää (logiikka poistettu)."


# Load Data
@st.cache_data
def load_data():
    Tietokanta.lataa()

    # Pre-calculate derived UI states to avoid O(N) operations on rerun
    _indikaatiot = set()
    _protokolla_map = {}

    for prot_nimi, prot_data in Tietokanta.data.items():
        tyypit = prot_data.get('syöpätyypit', [])

        # Build options set
        if tyypit:
            for t in tyypit:
                _indikaatiot.add(t)
        else:
            _indikaatiot.add("Ei määritelty")

        # Build mapping for quick filtering
        for t in tyypit or ["Ei määritelty"]:
            if t not in _protokolla_map:
                _protokolla_map[t] = []
            _protokolla_map[t].append(prot_nimi)

    # Also add "Kaikki" mapping
    _protokolla_map["Kaikki"] = list(Tietokanta.data.keys())

    syopatyyppi_opts = ["Kaikki"] + sorted(list(_indikaatiot))

    return Tietokanta.data, syopatyyppi_opts, _protokolla_map

YKSIKKO_OPTS_BASE = ("mg/m2", "mg/kg", "AUC", "mg")

try:
    # Always update Tietokanta.data with cached/loaded data
    _data, syopatyyppi_opts, protokolla_map = load_data()
    Tietokanta.data = _data
except Exception as e:
    st.error(f"Virhe ladattaessa tietokantaa: {e}")
    syopatyyppi_opts = ["Kaikki"]
    protokolla_map = {"Kaikki": []}

st.title("Onkologian Työpöytä v2.3 (Streamlit)")

# Sidebar for navigation
view = st.sidebar.radio("Valitse näkymä", ["Laskuri", "Levinneisyys", "Tietoa"])

if view == "Laskuri":
    st.header("Sytostaattilaskuri")

    # Input section
    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Potilas", expanded=True):
            # 1. Alustetaan muuttujat session stateen, jos niitä ei vielä ole
            if 'pituus' not in st.session_state: st.session_state['pituus'] = 0.0
            if 'paino' not in st.session_state: st.session_state['paino'] = 0.0
            if 'ika' not in st.session_state: st.session_state['ika'] = 0
            if 'krea' not in st.session_state: st.session_state['krea'] = 0
            if 'sukupuoli' not in st.session_state: st.session_state['sukupuoli'] = "Mies"

            # 2. Käytetään "key"-parametria, jolloin Streamlit tallentaa arvot automaattisesti
            pituus = st.number_input("Pituus (cm)", min_value=0.0, step=1.0, format="%.1f", key="pituus")
            paino = st.number_input("Paino (kg)", min_value=0.0, step=0.1, format="%.1f", key="paino")
            ika = st.number_input("Ikä", min_value=0, step=1, key="ika")
            krea = st.number_input("Krea", min_value=0, step=1, key="krea")
            sukupuoli = st.selectbox("Sukupuoli", ["Mies", "Nainen"], key="sukupuoli")

            # Calculations
            bsa = laske_bsa(pituus, paino)
            gfr = laske_cockcroft_gault(ika, paino, krea, sukupuoli)

            st.metric("BSA", f"{bsa:.2f} m²")
            st.metric("GFR", f"{gfr:.0f} ml/min")

    with col2:
        st.subheader("Hoito")
        
        # 2. Luodaan syöpätyypin valikko (valmiiksi lasketulla listalla)
        valittu_syopatyyppi = st.selectbox("Syöpätyyppi", syopatyyppi_opts)
        
        # 3. Suodatetaan protokollat valitun syöpätyypin perusteella
        protokollat = protokolla_map.get(valittu_syopatyyppi, [])
            
        # 4. Protokollan valikko suodatetulla listalla
        valittu_protokolla = st.selectbox("Protokolla", [""] + sorted(protokollat))

        # Labs default value
        labrat_default = ""
        protokolla_data = None

        # HAETAAN VALITUN PROTOKOLLAN DATA TIETOKANNASTA
        if valittu_protokolla and valittu_protokolla in Tietokanta.data:
            protokolla_data = Tietokanta.data[valittu_protokolla]
            labrat_default = protokolla_data.get('kontrollit', '')

        # Use key to force update when protocol changes
        labrat = st.text_input("Labrat", value=labrat_default, key=f"labrat_{valittu_protokolla}")

        if protokolla_data:
            st.subheader("Lääkkeet")

            laske_tulokset = []

            # Pre-calculate GFR-related constant for AUC to avoid recalculation in loop
            auc_multiplier = None

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

                # Dose (Annos)
                annos_val = med['annos']
                annos = c[1].number_input(f"Annos {i}", value=float(annos_val), step=10.0, label_visibility="collapsed", key=f"{valittu_protokolla}_annos_{i}")

                # Unit (Yksikkö)
                yksikkö_val = med.get('yksikkö', 'mg/m2')
                if yksikkö_val in YKSIKKO_OPTS_BASE:
                    yksikkö_opts = YKSIKKO_OPTS_BASE
                else:
                    yksikkö_opts = YKSIKKO_OPTS_BASE + (yksikkö_val,)
                # Ensure default is in options
                idx = yksikkö_opts.index(yksikkö_val)
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
                    if auc_multiplier is None:
                        auc_multiplier = (min(gfr, 125) + 25)
                    mg = annos * auc_multiplier
                else: # mg
                    mg = annos

                c[4].write(f"{mg:.0f}")

                # Final Amount (Määräys)
                fin = int(round(mg))
                strength_mg = None
                if vahvuus_str and vahvuus_str != "None":
                    try:
                        strength_mg = float(vahvuus_str.split()[0])
                        fin = pyorista_tabletit(mg, strength_mg)
                    except (ValueError, IndexError, ZeroDivisionError):
                        pass

                # Use a session state key that includes the calculated value to force update if calculation changes
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
                    "strength_mg": strength_mg,
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

                # Muotoillaan lääkkeen päivät siistiksi merkkijonoksi
                paivat = med.get('päivät')
                paivat_str = ""
                if paivat:
                    if isinstance(paivat, list):
                        paivat_str = f" pv {', '.join(str(p) for p in paivat)}"
                    else:
                        paivat_str = f" pv {paivat}"

                # Lisätään kaikki samalle riville (esim. "• Dosetakseli: 126 mg pv 1")
                report_lines.append(f"• {med['nimi']}: {fin_val} mg{paivat_str}")

                ts = item['vahvuus']
                strength_mg = item.get('strength_mg')
                if ts and ts != "None" and fin_val > 0 and strength_mg:
                    try:
                        count = fin_val / strength_mg
                        report_lines.append(f"    -> {count:.1f} kpl ({ts})")
                    except ZeroDivisionError:
                        pass

            report_lines.append("-" * 40)
            report_lines.append(f"TUKIHOIDOT:\n{protokolla_data.get('esilääkitys', '-')}")

            report_text = "\n".join(report_lines)
            st.text_area("Kopioitava teksti", report_text, height=300)


elif view == "Levinneisyys":
    st.header("Levinneisyys & Luokitus")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Määritys")

        tauti = st.selectbox("Syöpätyyppi", list(TNM_DATA.keys()))
        d = TNM_DATA[tauti]

        hoitolinja = st.selectbox("Hoitolinja", ["-", "Neoadjuvantti", "Adjuvantti"])

        # Breast Cancer Specifics
        er_status = "Positiivinen"
        her2_status = "Negatiivinen"
        ki67_status = "Matala (<20%)"

        if tauti == "Rintasyöpä":
            st.markdown("---")
            st.markdown("**Biologiset tekijät**")
            er_status = st.selectbox("ER Status", ["Positiivinen", "Negatiivinen"])
            her2_status = st.selectbox("HER2 Status", ["Positiivinen", "Negatiivinen"])
            ki67_status = st.selectbox("Ki-67", ["Matala (<20%)", "Korkea (>=20%)"])
            st.markdown("---")

        st.markdown("**Levinneisyys**")
        v1 = st.selectbox(f"{d['L1_Label']}", [""] + d['L1'])
        v2 = st.selectbox(f"{d['L2_Label']}", [""] + d['L2'])
        v3 = st.selectbox(f"{d['L3_Label']}", [""] + d['L3'])

    with col2:
        st.subheader("Tulos")

        res_text = f"Diagnoosi: {tauti}\n"

        # Parse codes
        c1 = v1.split(":")[0] if v1 else "?"
        c2 = v2.split(":")[0] if v2 else "?"
        c3 = v3.split(":")[0] if v3 else "?"

        if d['Type'] == "AnnArbor":
            stage_base = c1
            symptoms = c2 if c2 in ["A", "B"] else ""
            modifiers = c3 if c3 not in ["-", "?"] else ""

            full_stage = f"{stage_base}{symptoms}"
            if modifiers: full_stage += f" {modifiers}"

            res_text += f"Ann Arbor levinneisyys: {full_stage}\n"
            res_text += "-"*40 + "\n"
            if v1: res_text += f"• Levinneisyys: {v1}\n"
            if v2: res_text += f"• Oireet: {v2}\n"
            if v3 and c3 != "-": res_text += f"• Lisämääre: {v3}\n"

        else:
            # TNM Logic
            res_text += f"Levinneisyys (cTNM): {c1}{c2}{c3}"

            if tauti == "Rintasyöpä" and "?" not in (c1, c2, c3):
                try:
                    st_val = laske_stage_rintasyopa(c1, c2, c3)
                    res_text += f"\nAnatominen levinneisyysryhmä: {st_val}"

                    plan = maarita_hoitosuunnitelma_rintasyopa(
                        st_val, c1, c2, c3,
                        er_status, her2_status, ki67_status,
                        hoitolinja if hoitolinja != "-" else None
                    )
                    res_text += f"\n\n--- HOITOSUUNNITELMA ---\n{plan}"
                except Exception as e:
                    res_text += f"\nVirhe laskettaessa: {e}"

            res_text += "\n" + "-"*40 + "\n"
            if v1: res_text += f"• {d['L1_Label']}: {v1}\n"
            if v2: res_text += f"• {d['L2_Label']}: {v2}\n"
            if v3: res_text += f"• {d['L3_Label']}: {v3}\n"

        st.text_area("Lausunto", res_text, height=400)

elif view == "Tietoa":
    st.info("Tämä on Streamlit-versio Onkologian Työpöytä -sovelluksesta.")
