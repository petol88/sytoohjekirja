import streamlit as st
import sys
import os

# 1. Page config
st.set_page_config(page_title="Onkologian Työpöytä", layout="wide")

# Add current directory to path so we can import oncology_helper
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 2. TUONNIT ONCOLOGY_HELPERISTÄ (Korvaa omat apufunktiot näillä)
from oncology_helper.data import Tietokanta, TNM_DATA
from oncology_helper.calculators import (
    laske_bsa, 
    laske_cockcroft_gault, 
    pyorista_tabletit, 
    laske_calvert,
    Sukupuoli,
    Potilas,
    laske_yksiloity_annos,
    EcogLuokka,
    hae_ecog_kuvaus,
    laske_ipi_pisteet,
    hae_ipi_riskiryhma,
    laske_cns_ipi_pisteet,
    hae_cns_ipi_riskiryhma,
    laske_mipi_pisteet,
    hae_mipi_riskiryhma,
    laske_flipi_pisteet,
    hae_flipi_riskiryhma,
    tarkista_gelf_kriteerit,
    hae_gelf_suositus,
    laske_cps_eg_pisteet,
    hae_cps_eg_ennuste
)
from oncology_helper.staging import (
    laske_stage_rintasyopa, 
    maarita_hoitosuunnitelma_rintasyopa,
    ReseptoriTila,
    Ki67Tila,
    Hoitolinja
)

# Load Data
@st.cache_data
def load_data():
    Tietokanta.lataa()
    return Tietokanta.data

YKSIKKO_OPTS_BASE = ("mg/m2", "mg/kg", "AUC", "mg")

try:
    Tietokanta.data = load_data()
except Exception as e:
    st.error(f"Virhe ladattaessa tietokantaa: {e}")

st.title("Onkologian Työpöytä v2.3 (Streamlit)")

view = st.sidebar.radio("Valitse näkymä", ["Sytostaattilaskuri", "Levinneisyys", "Pisteytykset", "Tietoa"])

if view == "Sytostaattilaskuri":
    st.header("Sytostaattilaskuri")

    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Potilas", expanded=True):
            if 'pituus' not in st.session_state: st.session_state['pituus'] = 0.0
            if 'paino' not in st.session_state: st.session_state['paino'] = 0.0
            if 'ika' not in st.session_state: st.session_state['ika'] = 0
            if 'krea' not in st.session_state: st.session_state['krea'] = 0
            if 'sukupuoli' not in st.session_state: st.session_state['sukupuoli'] = "Mies"

            pituus = st.number_input("Pituus (cm)", min_value=0.0, step=1.0, format="%.1f", key="pituus")
            paino = st.number_input("Paino (kg)", min_value=0.0, step=0.1, format="%.1f", key="paino")
            ika = st.number_input("Ikä", min_value=0, step=1, key="ika")
            krea = st.number_input("Krea", min_value=0.0, step=1.0, format="%.1f", key="krea")
            sukupuoli_str = st.selectbox("Sukupuoli", ["Mies", "Nainen"], key="sukupuoli")

            # MUUTOS: Käytetään Enumia
            sukupuoli_enum = Sukupuoli.MIES if sukupuoli_str == "Mies" else Sukupuoli.NAINEN

            # MUUTOS: Käytetään Potilas-luokkaa
            potilas = Potilas(
                pituus_cm=pituus,
                paino_kg=paino,
                ika=ika,
                krea=krea,
                sukupuoli=sukupuoli_enum
            )

            bsa = potilas.bsa()
            gfr = potilas.gfr()

            st.metric("BSA", f"{bsa:.2f} m²")
            st.metric("GFR", f"{gfr:.0f} ml/min")

    with col2:
        st.subheader("Hoito")
        
        indikaatiot = set()
        for prot_data in Tietokanta.data.values():
            tyypit = prot_data.get('syöpätyypit', [])
            if tyypit:
                for t in tyypit:
                    indikaatiot.add(t)
            else:
                indikaatiot.add("Ei määritelty")
        
        valittu_syopatyyppi = st.selectbox("Syöpätyyppi", ["Kaikki"] + sorted(list(indikaatiot)))
        
        if valittu_syopatyyppi == "Kaikki":
            protokollat = list(Tietokanta.data.keys())
        elif valittu_syopatyyppi == "Ei määritelty":
            protokollat = [
                nimi for nimi, data in Tietokanta.data.items() 
                if not data.get('syöpätyypit')
            ]
        else:
            protokollat = [
                nimi for nimi, data in Tietokanta.data.items() 
                if valittu_syopatyyppi in data.get('syöpätyypit', [])
            ]
            
        valittu_protokolla = st.selectbox("Protokolla", [""] + sorted(protokollat))

        labrat_default = ""
        protokolla_data = None

        if valittu_protokolla and valittu_protokolla in Tietokanta.data:
            protokolla_data = Tietokanta.data[valittu_protokolla]
            labrat_default = protokolla_data.get('kontrollit', '')

        labrat = st.text_input("Labrat", value=labrat_default, key=f"labrat_{valittu_protokolla}")

        if protokolla_data:
            st.subheader("Lääkkeet")

            laske_tulokset = []

            cols = st.columns([3, 2, 2, 2, 2, 2])
            cols[0].markdown("**Lääke**")
            cols[1].markdown("**Annos**")
            cols[2].markdown("**Yks.**")
            cols[3].markdown("**Vahvuus**")
            cols[4].markdown("**Tulos (mg)**")
            cols[5].markdown("**Määräys**")

            for i, med in enumerate(protokolla_data['lääkkeet']):
                c = st.columns([3, 2, 2, 2, 2, 2])
                c[0].write(med['nimi'])

                annos_val = med['annos']
                annos = c[1].number_input(f"Annos {i}", value=float(annos_val), step=10.0, label_visibility="collapsed", key=f"{valittu_protokolla}_annos_{i}")

                yksikkö_val = med.get('yksikkö', 'mg/m2')
                if yksikkö_val in YKSIKKO_OPTS_BASE:
                    yksikkö_opts = YKSIKKO_OPTS_BASE
                else:
                    yksikkö_opts = YKSIKKO_OPTS_BASE + (yksikkö_val,)
                idx = yksikkö_opts.index(yksikkö_val)
                yksikkö = c[2].selectbox(f"Yks {i}", yksikkö_opts, index=idx, label_visibility="collapsed", key=f"{valittu_protokolla}_yks_{i}")

                tablettikoot = med.get("tablettikoot", [])
                vahvuus_str = "None"
                if tablettikoot:
                    vahvuus_str = c[3].selectbox(f"Vahv {i}", tablettikoot, label_visibility="collapsed", key=f"{valittu_protokolla}_vahv_{i}")
                else:
                    c[3].write("-")

                # MUUTOS: Käytetään valmista funktiota annoksen laskemiseen
                mg = laske_yksiloity_annos(annos, yksikkö, bsa, paino, gfr)

                c[4].write(f"{mg:.0f}")

                fin = int(round(mg))
                strength_mg = None
                if vahvuus_str and vahvuus_str != "None":
                    try:
                        strength_mg = float(vahvuus_str.split()[0])
                        # MUUTOS: Käytetään pyorista_tabletit calculators.py:stä
                        fin = pyorista_tabletit(mg, strength_mg)
                    except (ValueError, IndexError, ZeroDivisionError):
                        pass

                state_key = f"{valittu_protokolla}_maar_{i}"
                calc_key = f"{valittu_protokolla}_calc_{i}"

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

                paivat = med.get('päivät')
                paivat_str = ""
                if paivat:
                    if isinstance(paivat, list):
                        paivat_str = f" pv {', '.join(str(p) for p in paivat)}"
                    else:
                        paivat_str = f" pv {paivat}"

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
            res_text += f"Levinneisyys (cTNM): {c1}{c2}{c3}"

            if tauti == "Rintasyöpä" and "?" not in (c1, c2, c3):
                try:
                    # MUUTOS: Käytetään funktiota staging.py:stä
                    st_val = laske_stage_rintasyopa(c1, c2, c3)
                    res_text += f"\nAnatominen levinneisyysryhmä: {st_val}"

                    # MUUTOS: Muunnetaan Streamlit-valinnat Enumeiksi
                    er_enum = ReseptoriTila.POSITIIVINEN if er_status == "Positiivinen" else ReseptoriTila.NEGATIIVINEN
                    her2_enum = ReseptoriTila.POSITIIVINEN if her2_status == "Positiivinen" else ReseptoriTila.NEGATIIVINEN
                    ki67_enum = Ki67Tila.MATALA if "Matala" in ki67_status else Ki67Tila.KORKEA
                    
                    hoito_enum = Hoitolinja.EI_VALITTU
                    if hoitolinja == "Neoadjuvantti": hoito_enum = Hoitolinja.NEOADJUVANTTI
                    elif hoitolinja == "Adjuvantti": hoito_enum = Hoitolinja.ADJUVANTTI

                    # MUUTOS: Käytetään funktiota staging.py:stä oikeilla tyypeillä
                    plan = maarita_hoitosuunnitelma_rintasyopa(
                        st_val, c1, c2, c3,
                        er_enum, her2_enum, ki67_enum,
                        hoito_enum
                    )
                    res_text += f"\n\n--- HOITOSUUNNITELMA ---\n{plan}"
                except Exception as e:
                    res_text += f"\nVirhe laskettaessa: {e}"

            res_text += "\n" + "-"*40 + "\n"
            if v1: res_text += f"• {d['L1_Label']}: {v1}\n"
            if v2: res_text += f"• {d['L2_Label']}: {v2}\n"
            if v3: res_text += f"• {d['L3_Label']}: {v3}\n"

        st.text_area("Lausunto", res_text, height=400)

elif view == "Pisteytykset":
    st.header("Lääketieteelliset pisteytykset")
    
    laskuri_valinta = st.selectbox("Valitse laskuri", ["Valitse...", "ECOG-suorituskyky", "IPI (International Prognostic Index)", "CNS-IPI (CNS International Prognostic Index)", "MIPI (Mantle Cell Lymphoma International Prognostic Index)", "FLIPI (Follicular Lymphoma International Prognostic Index)", "GELF-kriteerit (Follikulaarisen lymfooman hoidon aloitus)", "CPS+EG (Rintasyövän neoadjuvanttihoidon jälkeinen ennuste)"], key="pisteytys_laskuri_valinta")
    
    if laskuri_valinta == "ECOG-suorituskyky":
        st.subheader("ECOG (Eastern Cooperative Oncology Group) -suorituskykyluokitus")
        st.write("Arvioi potilaan toimintakykyä ja päivittäisistä toiminnoista suoriutumista.")
        
        # Create a list of options formatted as "0 - Täysin aktiivinen..."
        ecog_vaihtoehdot = []
        for luokka in EcogLuokka:
            kuvaus = hae_ecog_kuvaus(luokka)
            ecog_vaihtoehdot.append(f"ECOG {luokka.value}: {kuvaus}")
            
        valittu_ecog_str = st.radio("Valitse potilasta parhaiten kuvaava tila:", ecog_vaihtoehdot, key="ecog_radio_valinta")
        
        # Extract just the number to show the result clearly
        if valittu_ecog_str:
            ecog_arvo = valittu_ecog_str.split(":")[0]
            st.success(f"**Tulos:** Potilaan suorituskyky on {ecog_arvo}.")
            
            # Additional logic based on score (optional, but good for context)
            arvo_int = int(ecog_arvo.replace("ECOG ", ""))
            if arvo_int >= 3:
                st.warning("Huom: ECOG 3 tai huonompi on usein vasta-aihe raskaalle solunsalpaajahoidolle.")

    elif laskuri_valinta == "IPI (International Prognostic Index)":
        st.subheader("IPI (International Prognostic Index)")
        st.write("Arvioi diffuusin suurisoluisen B-solulymfooman (DLBCL) ennustetta.")
        
        col1, col2 = st.columns(2)
        with col1:
            ipi_ika = st.checkbox("Ikä > 60 vuotta", key="ipi_ika")
            ipi_ldh = st.checkbox("LDH koholla (> viitealueen yläraja)", key="ipi_ldh")
            ipi_ecog = st.checkbox("ECOG-suorituskyky ≥ 2", key="ipi_ecog")
        with col2:
            ipi_stage = st.checkbox("Ann Arbor Stage III tai IV", key="ipi_stage")
            ipi_en = st.checkbox("Yli 1 ekstranodaalinen pesäke", key="ipi_en")
            
        pisteet = laske_ipi_pisteet(ipi_ika, ipi_ldh, ipi_ecog, ipi_stage, ipi_en)
        riskiryhma = hae_ipi_riskiryhma(pisteet)
        
        st.markdown("---")
        st.success(f"**Tulos:** IPI-pisteet: {pisteet} / 5")
        st.info(f"**Riskiryhmä:** {riskiryhma}")
        
    elif laskuri_valinta == "MIPI (Mantle Cell Lymphoma International Prognostic Index)":
        st.subheader("MIPI (Mantle Cell Lymphoma International Prognostic Index)")
        st.write("Arvioi manttelisolulymfooman ennustetta (yksinkertaistettu sMIPI).")
        
        col1, col2 = st.columns(2)
        with col1:
            mipi_ika_str = st.radio("Ikä (vuotta)", ["< 50", "50 - 59", "60 - 69", "≥ 70"], key="mipi_ika")
            mipi_ecog_str = st.radio("ECOG-suorituskyky", ["0 - 1", "≥ 2"], key="mipi_ecog")
        with col2:
            mipi_ldh_str = st.radio("LDH / viitealueen yläraja", ["< 0.67", "0.67 - 0.99", "1.00 - 1.49", "≥ 1.50"], key="mipi_ldh")
            mipi_wbc_str = st.radio("Leukosyytit (WBC, E9/l)", ["< 6.7", "6.7 - 9.9", "10.0 - 14.9", "≥ 15.0"], key="mipi_wbc")
            
        ika_p = ["< 50", "50 - 59", "60 - 69", "≥ 70"].index(mipi_ika_str)
        ecog_p = ["0 - 1", "≥ 2"].index(mipi_ecog_str)
        ldh_p = ["< 0.67", "0.67 - 0.99", "1.00 - 1.49", "≥ 1.50"].index(mipi_ldh_str)
        wbc_p = ["< 6.7", "6.7 - 9.9", "10.0 - 14.9", "≥ 15.0"].index(mipi_wbc_str)
            
        pisteet = laske_mipi_pisteet(ika_p, ecog_p, ldh_p, wbc_p)
        riskiryhma = hae_mipi_riskiryhma(pisteet)
        
        st.markdown("---")
        st.success(f"**Tulos:** sMIPI-pisteet: {pisteet}")
        st.info(f"**Riskiryhmä:** {riskiryhma}")
        
    elif laskuri_valinta == "CNS-IPI (CNS International Prognostic Index)":
        st.subheader("CNS-IPI (CNS International Prognostic Index)")
        st.write("Arvioi keskushermostorelapssin riskiä diffuusissa suurisoluisessa B-solulymfoomassa (DLBCL).")
        
        col1, col2 = st.columns(2)
        with col1:
            cns_ika = st.checkbox("Ikä > 60 vuotta", key="cns_ika")
            cns_ldh = st.checkbox("LDH koholla (> viitealueen yläraja)", key="cns_ldh")
            cns_ecog = st.checkbox("ECOG-suorituskyky ≥ 2", key="cns_ecog")
        with col2:
            cns_stage = st.checkbox("Ann Arbor Stage III tai IV", key="cns_stage")
            cns_en = st.checkbox("Yli 1 ekstranodaalinen pesäke", key="cns_en")
            cns_kidney = st.checkbox("Munuaisten ja/tai lisämunuaisten affisio", key="cns_kidney")
            
        pisteet = laske_cns_ipi_pisteet(cns_ika, cns_ldh, cns_ecog, cns_stage, cns_en, cns_kidney)
        riskiryhma = hae_cns_ipi_riskiryhma(pisteet)
        
        st.markdown("---")
        st.success(f"**Tulos:** CNS-IPI-pisteet: {pisteet} / 6")
        st.info(f"**Riskiryhmä:** {riskiryhma}")
        
    elif laskuri_valinta == "FLIPI (Follicular Lymphoma International Prognostic Index)":
        st.subheader("FLIPI (Follicular Lymphoma International Prognostic Index)")
        st.write("Arvioi follikulaarisen lymfooman ennustetta.")
        
        col1, col2 = st.columns(2)
        with col1:
            flipi_ika = st.checkbox("Ikä > 60 vuotta", key="flipi_ika")
            flipi_stage = st.checkbox("Ann Arbor Stage III tai IV", key="flipi_stage")
            flipi_hb = st.checkbox("Hemoglobiini < 120 g/l", key="flipi_hb")
        with col2:
            flipi_nodaali = st.checkbox("Yli 4 nodaalista aluetta", key="flipi_nodaali")
            flipi_ldh = st.checkbox("LDH koholla (> viitealueen yläraja)", key="flipi_ldh")
            
        pisteet = laske_flipi_pisteet(flipi_ika, flipi_stage, flipi_hb, flipi_nodaali, flipi_ldh)
        riskiryhma = hae_flipi_riskiryhma(pisteet)
        
        st.markdown("---")
        st.success(f"**Tulos:** FLIPI-pisteet: {pisteet} / 5")
        st.info(f"**Riskiryhmä:** {riskiryhma}")
        
    elif laskuri_valinta == "GELF-kriteerit (Follikulaarisen lymfooman hoidon aloitus)":
        st.subheader("GELF-kriteerit (Follikulaarinen lymfooma)")
        st.write("Arvioi aktiivihoidon indikaatiota follikulaarisessa lymfoomassa (indikaatio jos vähintään 1 täyttyy).")
        
        col1, col2 = st.columns(2)
        with col1:
            gelf_bulkki = st.checkbox("Bulkki > 7 cm tai ≥3 imusolmukealuetta > 3 cm", key="gelf_bulkki")
            gelf_perna = st.checkbox("Oireinen splenomegalia", key="gelf_perna")
            gelf_kompressio = st.checkbox("Elinkompressio, pleura- tai peritoneaalieffuusio", key="gelf_kompressio")
            gelf_ldh = st.checkbox("Kohonnut LDH tai β2-mikroglobuliini", key="gelf_ldh")
        with col2:
            gelf_leukemia = st.checkbox("Leukeeminen tauti (lymfosyytit > 5.0 E9/l)", key="gelf_leukemia")
            gelf_syto = st.checkbox("Sytopeniat (Neut < 1.0 tai Tromb < 100)", key="gelf_syto")
            gelf_b_oireet = st.checkbox("B-oireet", key="gelf_b_oireet")
            
        pisteet = tarkista_gelf_kriteerit(gelf_bulkki, gelf_perna, gelf_kompressio, gelf_ldh, gelf_leukemia, gelf_syto, gelf_b_oireet)
        suositus = hae_gelf_suositus(pisteet)
        
        st.markdown("---")
        st.success(f"**Tulos:** {pisteet} GELF-kriteeriä täyttyy.")
        st.info(f"**Suositus:** {suositus}")
        
    elif laskuri_valinta == "CPS+EG (Rintasyövän neoadjuvanttihoidon jälkeinen ennuste)":
        st.subheader("CPS+EG (Rintasyövän neoadjuvanttihoidon jälkeinen ennuste)")
        st.write("Arvioi rintasyövän ennustetta neoadjuvanttihoidon ja leikkauksen jälkeen.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            cpseg_cstage_str = st.radio("Kliininen levinneisyys (cTNM) ennen hoitoa:", ["Stage I - IIA", "Stage IIB - IIIA", "Stage IIIB - IIIC"], key="cpseg_cstage")
            cpseg_pstage_str = st.radio("Patologinen levinneisyys (ypTNM) leikkauksen jälkeen:", ["Stage 0 tai I", "Stage IIA - IIB", "Stage IIIA - IIIC"], key="cpseg_pstage")
            
            st.write("**Muut tekijät:**")
            cpseg_er = st.checkbox("Estrogeenireseptori (ER) negatiivinen (1 p)", key="cpseg_er")
            cpseg_grade = st.checkbox("Gradus 3 (1 p)", key="cpseg_grade")
            
        with col2:
            st.info("**Rintasyövän Stage-muistisääntö:**\n"
                    "• **Stage I:** T1 N0\n"
                    "• **Stage IIA:** T0-T1 N1 tai T2 N0\n"
                    "• **Stage IIB:** T2 N1 tai T3 N0\n"
                    "• **Stage IIIA:** T0-T2 N2 tai T3 N1-N2\n"
                    "• **Stage IIIB:** T4, mikä tahansa N\n"
                    "• **Stage IIIC:** Mikä tahansa T, N3\n\n"
                    "*(T1 ≤2cm, T2 2-5cm, T3 >5cm, T4 iho/rintakehä)*")
                    
        c_p = ["Stage I - IIA", "Stage IIB - IIIA", "Stage IIIB - IIIC"].index(cpseg_cstage_str)
        p_p = ["Stage 0 tai I", "Stage IIA - IIB", "Stage IIIA - IIIC"].index(cpseg_pstage_str)
        
        pisteet = laske_cps_eg_pisteet(c_p, p_p, cpseg_er, cpseg_grade)
        ennuste = hae_cps_eg_ennuste(pisteet)
        
        st.markdown("---")
        st.success(f"**Tulos:** CPS+EG -pisteet: {pisteet} / 6")
        st.info(f"**Ennuste:** {ennuste}")
        
        if pisteet >= 3:
            st.warning("**Huom:** Jos invasiivistä jäännöstautia, niin muista olaparibi-liitännäishoidon mahdollisuus ituradan BRCA-mutaation omaavilla vuoden ajaksi.")
