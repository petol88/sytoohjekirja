import streamlit as st
import sys
import os
from datetime import date, timedelta

# 1. Page config
st.set_page_config(page_title="Onkologian Työpöytä", layout="wide")

# Add current directory to path so we can import oncology_helper
current_dir = os.path.dirname(os.path.abspath(__file__))
onkohelper_dir = os.path.join(current_dir, "onkohelper")

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if os.path.exists(onkohelper_dir) and onkohelper_dir not in sys.path:
    sys.path.insert(0, onkohelper_dir)

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
    hae_cps_eg_ennuste,
    laske_ips_pisteet,
    hae_ips_ennuste,
    tarkista_hl_paikallinen_riskitekijat,
    hae_hl_paikallinen_riskiryhma,
    laske_child_pugh_pisteet,
    hae_child_pugh_luokka,
    laske_psadt,
    hae_psadt_tulkinta,
    laske_mascc_pisteet,
    hae_mascc_suositus,
    laske_qtc,
    hae_qtc_suositus,
    laske_antrasykliini_kertyma
)
from oncology_helper.staging import (
    laske_stage_rintasyopa, 
    maarita_hoitosuunnitelma_rintasyopa,
    laske_stage_suolistosyopa,
    maarita_hoitosuunnitelma_suolistosyopa,
    laske_stage_melanooma,
    maarita_hoitosuunnitelma_melanooma,
    laske_stage_keuhkosyopa,
    maarita_hoitosuunnitelma_keuhkosyopa,
    laske_riskiryhma_eturauhassyopa,
    maarita_hoitosuunnitelma_eturauhassyopa,
    laske_stage_munuaissyopa,
    maarita_hoitosuunnitelma_munuaissyopa,
    laske_stage_haimasyopa,
    maarita_hoitosuunnitelma_haimasyopa,
    ReseptoriTila,
    Ki67Tila,
    Hoitolinja,
    IsupLuokka,
    PsaTaso
)
from oncology_helper.guidelines import OHJEET

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

# Session state defaults (Jaettu tila)
if 'pituus' not in st.session_state or st.session_state['pituus'] < 100.0: st.session_state['pituus'] = 170.0
if 'paino' not in st.session_state: st.session_state['paino'] = 70.0
if 'ika' not in st.session_state: st.session_state['ika'] = 0
if 'krea' not in st.session_state: st.session_state['krea'] = 0.0
if 'sukupuoli' not in st.session_state: st.session_state['sukupuoli'] = "Mies"

view = st.sidebar.radio("Valitse näkymä", ["Sytostaattilaskuri", "Levinneisyys", "Pisteytykset", "Haittavaikutukset", "Ohjeet", "Tietoa"])

if view == "Sytostaattilaskuri":
    st.header("Sytostaattilaskuri")

    col1, col2 = st.columns([1, 2])

    with col1:
        with st.expander("Potilas", expanded=True):
            pituus = st.number_input("Pituus (cm)", min_value=100.0, max_value=220.0, step=1.0, format="%.1f", key="pituus")
            paino = st.number_input("Paino (kg)", min_value=0.0, max_value=200.0, step=0.1, format="%.1f", key="paino")
            ika = st.number_input("Ikä", min_value=0, step=1, key="ika")
            krea = st.number_input("Krea", min_value=0.0, step=1.0, format="%.1f", key="krea")
            sukupuoli_str = st.selectbox("Sukupuoli", ["Mies", "Nainen"], key="sukupuoli")
            cap_bsa = st.checkbox("Max 2.2 m²", value=False, help="Rajoita BSA arvoon 2.2 m²", key="cap_bsa")

            if pituus < 140.0 or pituus > 200.0:
                st.warning("⚠️ Poikkeuksellinen pituus, tarkista syöte.")
            if paino > 0 and (paino < 40.0 or paino > 150.0):
                st.warning("⚠️ Poikkeuksellinen paino, tarkista syöte.")
            if ika > 90:
                st.warning("⚠️ Poikkeuksellisen korkea ikä, tarkista syöte.")

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

            cap = 2.2 if cap_bsa else None
            bsa = potilas.bsa(cap)
            gfr = potilas.gfr()

            st.metric("BSA", f"{bsa:.2f} m²")
            st.metric("GFR", f"{gfr:.0f} ml/min")
            
            if 0 < gfr < 20.0:
                st.warning("⚠️ Erittäin matala GFR (< 20), huomioi munuaistoksisuus ja annossäädöt.")

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
            
            if 0 < gfr < 60:
                report_lines.append(f"⚠️ YLEISVAROITUS: GFR on alentunut ({gfr:.0f} ml/min).")
                report_lines.append("  Harkitse annospudotusta munuaisteitse erittyville lääkkeille!\n")
                
            if cap_bsa and bsa == 2.2:
                report_lines.append("HUOM: BSA on rajoitettu maksimiarvoon 2.2 m².\n")

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

                yksikko_raw = item.get('yksikkö', '')
                lisamaare = ""
                if yksikko_raw and " " in yksikko_raw:
                    lisamaare = " " + yksikko_raw.split(" ", 1)[1]
                    
                kpl_lisamaare = lisamaare if "x" in lisamaare.lower() else ""

                reitti = med.get('reitti', '')
                reitti_str = f" {reitti}" if reitti else ""
                
                kesto = med.get('kesto', '')
                lisatieto = med.get('lisätieto', '')
                extra_info = []
                if kesto: extra_info.append(f"kesto: {kesto}")
                if lisatieto: extra_info.append(lisatieto)
                extra_str = f" ({', '.join(extra_info)})" if extra_info else ""

                report_lines.append(f"• {med['nimi']}{reitti_str} {fin_val} mg{lisamaare}{paivat_str}{extra_str}")

                ts = item['vahvuus']
                strength_mg = item.get('strength_mg')
                if ts and ts != "None" and fin_val > 0 and strength_mg:
                    try:
                        count = fin_val / strength_mg
                        report_lines.append(f"    -> {count:.1f} kpl{kpl_lisamaare} ({ts})")
                    except ZeroDivisionError:
                        pass
                        
                min_gfr = med.get('min_gfr')
                if min_gfr and 0 < gfr < min_gfr:
                    report_lines.append(f"    ⚠️ VAROITUS: Potilaan GFR ({gfr:.0f}) on lääkkeen ({med['nimi']}) suositusrajan ({min_gfr}) alapuolella!")

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
        isup_status = IsupLuokka.ISUP_1.value
        psa_status = PsaTaso.ALLE_10.value

        if tauti == "Rintasyöpä":
            st.markdown("---")
            st.markdown("**Biologiset tekijät**")
            er_status = st.selectbox("ER Status", ["Positiivinen", "Negatiivinen"])
            her2_status = st.selectbox("HER2 Status", ["Positiivinen", "Negatiivinen"])
            ki67_status = st.selectbox("Ki-67", ["Matala (<20%)", "Korkea (>=20%)"])
            st.markdown("---")
        elif tauti == "Eturauhassyöpä":
            st.markdown("---")
            st.markdown("**Eturauhassyövän lisätekijät (EAU-riskiluokitus)**")
            isup_status = st.selectbox("ISUP-luokka", [e.value for e in IsupLuokka])
            psa_status = st.selectbox("PSA-taso", [e.value for e in PsaTaso])
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

            elif tauti == "Suolistosyöpä" and "?" not in (c1, c2, c3):
                try:
                    st_val = laske_stage_suolistosyopa(c1, c2, c3)
                    res_text += f"\nAnatominen levinneisyysryhmä: {st_val}"
                    plan = maarita_hoitosuunnitelma_suolistosyopa(st_val, c1, c2, c3)
                    res_text += f"\n\n--- HOITOSUUNNITELMA ---\n{plan}"
                except Exception as e:
                    res_text += f"\nVirhe laskettaessa: {e}"

            elif tauti == "Melanooma" and "?" not in (c1, c2, c3):
                try:
                    st_val = laske_stage_melanooma(c1, c2, c3)
                    res_text += f"\nAnatominen levinneisyysryhmä: {st_val}"
                    plan = maarita_hoitosuunnitelma_melanooma(st_val, c1, c2, c3)
                    res_text += f"\n\n--- HOITOSUUNNITELMA ---\n{plan}"
                except Exception as e:
                    res_text += f"\nVirhe laskettaessa: {e}"

            elif tauti == "Keuhkosyöpä (NSCLC)" and "?" not in (c1, c2, c3):
                try:
                    st_val = laske_stage_keuhkosyopa(c1, c2, c3)
                    res_text += f"\nAnatominen levinneisyysryhmä: {st_val}"
                    plan = maarita_hoitosuunnitelma_keuhkosyopa(st_val, c1, c2, c3)
                    res_text += f"\n\n--- HOITOSUUNNITELMA ---\n{plan}"
                except Exception as e:
                    res_text += f"\nVirhe laskettaessa: {e}"

            elif tauti == "Eturauhassyöpä" and "?" not in (c1, c2, c3):
                try:
                    isup_enum = next((e for e in IsupLuokka if e.value == isup_status), IsupLuokka.ISUP_1)
                    psa_enum = next((e for e in PsaTaso if e.value == psa_status), PsaTaso.ALLE_10)
                    riski = laske_riskiryhma_eturauhassyopa(c1, c2, c3, isup_enum, psa_enum)
                    res_text += f"\nRiskiluokitus / Levinneisyys: {riski}"
                    plan = maarita_hoitosuunnitelma_eturauhassyopa(riski, c1, c2, c3)
                    res_text += f"\n\n--- HOITOSUUNNITELMA ---\n{plan}"
                except Exception as e:
                    res_text += f"\nVirhe laskettaessa: {e}"

            elif tauti == "Munuaissyöpä" and "?" not in (c1, c2, c3):
                st_val = laske_stage_munuaissyopa(c1, c2, c3)
                res_text += f"\nAnatominen levinneisyysryhmä: {st_val}"
                plan = maarita_hoitosuunnitelma_munuaissyopa(st_val, c1, c2, c3)
                res_text += f"\n\n--- HOITOSUUNNITELMA ---\n{plan}"

            elif tauti == "Haimasyöpä" and "?" not in (c1, c2, c3):
                st_val = laske_stage_haimasyopa(c1, c2, c3)
                res_text += f"\nAnatominen levinneisyysryhmä: {st_val}"
                plan = maarita_hoitosuunnitelma_haimasyopa(st_val, c1, c2, c3)
                res_text += f"\n\n--- HOITOSUUNNITELMA ---\n{plan}"

            res_text += "\n" + "-"*40 + "\n"
            if v1: res_text += f"• {d['L1_Label']}: {v1}\n"
            if v2: res_text += f"• {d['L2_Label']}: {v2}\n"
            if v3: res_text += f"• {d['L3_Label']}: {v3}\n"

        st.text_area("Lausunto", res_text, height=400)

elif view == "Pisteytykset":
    st.header("Lääketieteelliset pisteytykset")
    
    laskuri_valinta = st.selectbox("Valitse laskuri", ["Valitse...", "ECOG-suorituskyky", "Kertyvä annos (Antrasykliinit)", "QTc-ajan korjauslaskuri (Bazett & Fridericia)", "MASCC-pisteytys (Kuumeinen neutropenia)", "IPI (International Prognostic Index)", "CNS-IPI (CNS International Prognostic Index)", "MIPI (Mantle Cell Lymphoma International Prognostic Index)", "FLIPI (Follicular Lymphoma International Prognostic Index)", "IPS (International Prognostic Score - Hodgkin lymfooma)", "Hodgkin lymfooma - Paikallisen taudin (Stage I-II) riskitekijät", "GELF-kriteerit (Follikulaarisen lymfooman hoidon aloitus)", "CPS+EG (Rintasyövän neoadjuvanttihoidon jälkeinen ennuste)", "Child-Pugh -luokitus (Maksan vajaatoiminta)", "PSA:n kahdentumisaika (PSADT)"], key="pisteytys_laskuri_valinta")
    
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
                
    elif laskuri_valinta == "Kertyvä annos (Antrasykliinit)":
        st.subheader("Kertyvän annoksen seuranta (Antrasykliinit)")
        st.write("Laskee antrasykliinien kumulatiivisen annoksen doksorubisiini-ekvivalentteina. Doksorubisiinin suositeltu elinikäinen maksimiannos on sydäntoksisuuden vuoksi 450–500 mg/m².")
        
        syotto_mode = st.radio("Syötettävien annosten yksikkö:", ["mg/m²", "Absoluuttinen (mg)"], horizontal=True, key="antr_mode")
        
        bsa = 1.0
        bsa_text = ""
        if syotto_mode == "Absoluuttinen (mg)":
            st.markdown("**Potilaan tiedot (BSA:n laskentaa varten):**")
            col_p, col_w = st.columns(2)
            with col_p:
                h = st.number_input("Pituus (cm)", min_value=100.0, max_value=220.0, step=1.0, format="%.1f", key="pituus")
            with col_w:
                w = st.number_input("Paino (kg)", min_value=0.0, max_value=200.0, step=0.1, format="%.1f", key="paino")
            bsa = laske_bsa(h, w)
            bsa_text = f" (BSA: {bsa:.2f} m²)"
            st.info(f"Laskettu BSA: {bsa:.2f} m²")
            unit_label = "mg"
        else:
            unit_label = "mg/m²"
            
        st.markdown(f"**Syötä potilaan aiemmin saamat kokonaisannokset ({unit_label}):**")
        col1, col2 = st.columns(2)
        with col1:
            doxo_input = st.number_input(f"Doksorubisiini ({unit_label})", min_value=0.0, step=10.0, value=0.0, key="antr_doxo")
            epi_input = st.number_input(f"Epirubisiini ({unit_label})", min_value=0.0, step=10.0, value=0.0, key="antr_epi")
        with col2:
            ida_input = st.number_input(f"Idarubisiini ({unit_label})", min_value=0.0, step=10.0, value=0.0, key="antr_ida")
            mito_input = st.number_input(f"Mitoksantroni ({unit_label})", min_value=0.0, step=10.0, value=0.0, key="antr_mito")
            
        doxo_mg = doxo_input / bsa if syotto_mode == "Absoluuttinen (mg)" else doxo_input
        epi_mg = epi_input / bsa if syotto_mode == "Absoluuttinen (mg)" else epi_input
        ida_mg = ida_input / bsa if syotto_mode == "Absoluuttinen (mg)" else ida_input
        mito_mg = mito_input / bsa if syotto_mode == "Absoluuttinen (mg)" else mito_input
        
        equiv, remaining, suositus = laske_antrasykliini_kertyma(doxo_mg, epi_mg, ida_mg, mito_mg)
        
        st.markdown("---")
        st.success(f"**Tulos{bsa_text}:** Doksorubisiini-ekvivalentti kertyvä annos: **{equiv:.0f} mg/m²**")
        
        rem_str = ""
        if remaining > 0:
            rem_str = "\n\n**Jäljellä oleva annos maksimirajaan (450 mg/m²) eri lääkkeinä:**\n"
            if syotto_mode == "Absoluuttinen (mg)":
                rem_str += f"- Doksorubisiini: {remaining:.0f} mg/m² (n. {remaining * bsa:.0f} mg)\n"
                rem_str += f"- Epirubisiini: {remaining / 0.5:.0f} mg/m² (n. {(remaining / 0.5) * bsa:.0f} mg)\n"
                rem_str += f"- Idarubisiini: {remaining / 3.0:.0f} mg/m² (n. {(remaining / 3.0) * bsa:.0f} mg)\n"
                rem_str += f"- Mitoksantroni: {remaining / 3.0:.0f} mg/m² (n. {(remaining / 3.0) * bsa:.0f} mg)"
            else:
                rem_str += f"- Doksorubisiini: {remaining:.0f} mg/m²\n"
                rem_str += f"- Epirubisiini: {remaining / 0.5:.0f} mg/m²\n"
                rem_str += f"- Idarubisiini: {remaining / 3.0:.0f} mg/m²\n"
                rem_str += f"- Mitoksantroni: {remaining / 3.0:.0f} mg/m²"
                
        if equiv >= 500 or equiv >= 450:
            st.error(f"**Tulkinta:** ⚠️ {suositus}")
        elif equiv >= 300:
            st.warning(f"**Tulkinta:** {suositus}{rem_str}")
        else:
            st.info(f"**Tulkinta:** {suositus}{rem_str}")
                
    elif laskuri_valinta == "QTc-ajan korjauslaskuri (Bazett & Fridericia)":
        st.subheader("QTc-ajan korjauslaskuri")
        st.write("Laskee sykekorjatun QT-ajan (QTc) Bazettin ja Friderician kaavoilla. Syöpähoidoissa (esim. TK-estäjät) suositellaan usein Friderician kaavaa.")
        
        col1, col2 = st.columns(2)
        with col1:
            qt_ms = st.number_input("Sähkökardiogrammin QT-aika (ms)", min_value=0.0, max_value=1000.0, value=400.0, step=1.0, key="qtc_qt")
        with col2:
            hr_bpm = st.number_input("Syke (bpm)", min_value=0.0, max_value=300.0, value=60.0, step=1.0, key="qtc_hr")
            
        if qt_ms > 0 and hr_bpm > 0:
            qtc_b, qtc_f = laske_qtc(qt_ms, hr_bpm)
            suositus = hae_qtc_suositus(qtc_f)
            
            st.markdown("---")
            st.success(f"**Tulos:** Bazett (QTcB): {qtc_b:.0f} ms  |  Fridericia (QTcF): {qtc_f:.0f} ms")
            
            if qtc_f > 500:
                st.error(f"**Tulkinta (Fridericia):** {suositus}")
            elif qtc_f > 480:
                st.warning(f"**Tulkinta (Fridericia):** {suositus}")
            else:
                st.info(f"**Tulkinta (Fridericia):** {suositus}")

    elif laskuri_valinta == "MASCC-pisteytys (Kuumeinen neutropenia)":
        st.subheader("MASCC (Multinational Association for Supportive Care in Cancer)")
        st.write("Arvioi komplikaatioriskiä potilaalla, jolla on kuumeinen neutropenia.")
        
        st.markdown("**Oireiden vaikeusaste (valitse yksi):**")
        mascc_oire_str = st.radio("Oireet", ["Lievät tai ei oireita (5 p)", "Kohtalaiset oireet (3 p)", "Vaikeat oireet (0 p)"], key="mascc_oire")
        
        if "Lievät" in mascc_oire_str: mascc_oire_val = 5
        elif "Kohtalaiset" in mascc_oire_str: mascc_oire_val = 3
        else: mascc_oire_val = 0
        
        st.markdown("**Muut kriteerit:**")
        mascc_hypo = st.checkbox("Ei hypotensiota (RR systolinen > 90 mmHg) (5 p)", key="mascc_hypo")
        mascc_copd = st.checkbox("Ei aktiivista COPD:tä (keuhkoahtaumatautia) (4 p)", key="mascc_copd")
        mascc_tumor = st.checkbox("Solidi tuumori TAI hematologinen syöpä ilman aiempaa sieni-infektiota (4 p)", key="mascc_tumor")
        mascc_dehydr = st.checkbox("Ei suonensisäisen nestehoidon tarvetta kuivumisen vuoksi (3 p)", key="mascc_dehydr")
        mascc_outpat = st.checkbox("Potilas on ollut avohoidossa kuumeen alkaessa (3 p)", key="mascc_outpat")
        mascc_age = st.checkbox("Ikä alle 60 vuotta (2 p)", key="mascc_age")
        
        pisteet = laske_mascc_pisteet(mascc_oire_val, mascc_hypo, mascc_copd, mascc_tumor, mascc_dehydr, mascc_outpat, mascc_age)
        suositus = hae_mascc_suositus(pisteet)
        
        st.markdown("---")
        if pisteet >= 21:
            st.success(f"**Tulos:** MASCC-pisteet: {pisteet} / 26\n\n**Suositus:** {suositus}")
        else:
            st.error(f"**Tulos:** MASCC-pisteet: {pisteet} / 26\n\n**Suositus:** {suositus}")

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
        
    elif laskuri_valinta == "IPS (International Prognostic Score - Hodgkin lymfooma)":
        st.subheader("IPS (International Prognostic Score)")
        st.write("Arvioi levinneen (Stage IIB-IV) Hodgkinin lymfooman ennustetta.")
        
        col1, col2 = st.columns(2)
        with col1:
            ips_alb = st.checkbox("Albumiini < 40 g/l", key="ips_alb")
            ips_hb = st.checkbox("Hemoglobiini < 105 g/l", key="ips_hb")
            ips_mies = st.checkbox("Mies-sukupuoli", key="ips_mies")
            ips_ika = st.checkbox("Ikä ≥ 45 vuotta", key="ips_ika")
        with col2:
            ips_stage = st.checkbox("Stage IV -tauti", key="ips_stage")
            ips_wbc = st.checkbox("Leukosyytit (WBC) ≥ 15.0 E9/l", key="ips_wbc")
            ips_lymf = st.checkbox("Lymfosyytit < 0.6 E9/l (tai < 8% WBC)", key="ips_lymf")
            
        pisteet = laske_ips_pisteet(ips_alb, ips_hb, ips_mies, ips_ika, ips_stage, ips_wbc, ips_lymf)
        ennuste = hae_ips_ennuste(pisteet)
        
        st.markdown("---")
        st.success(f"**Tulos:** IPS-pisteet: {pisteet} / 7")
        st.info(f"**Ennuste:** {ennuste}")
        
    elif laskuri_valinta == "Hodgkin lymfooma - Paikallisen taudin (Stage I-II) riskitekijät":
        st.subheader("Hodgkin lymfooma - Paikallisen taudin riskitekijät")
        st.write("Arvioi paikallisen (Stage I-II) Hodgkinin lymfooman riskiryhmää (EORTC/GHSG -kriteerit).")
        
        col1, col2 = st.columns(2)
        with col1:
            hl_med = st.checkbox("Iso mediastinumin tuumori (> 1/3 rintakehän leveydestä)", key="hl_med")
            hl_eks = st.checkbox("Tautia imusolmukkeen ulkopuolisessa elimessä (E-leesio)", key="hl_eks")
        with col2:
            hl_alue = st.checkbox("≥ 3 affisoitunutta imusolmukealuetta", key="hl_alue")
            hl_la = st.checkbox("La > 50 mm/t (Stage IA, IIA) TAI La > 30 mm/t (Stage IB, IIB)", key="hl_la")
            
        pisteet = tarkista_hl_paikallinen_riskitekijat(hl_med, hl_eks, hl_alue, hl_la)
        ryhma = hae_hl_paikallinen_riskiryhma(pisteet)
        
        st.markdown("---")
        st.success(f"**Tulos:** {pisteet} riskitekijä(ä) täyttyy.")
        st.info(f"**Riskiryhmä:** {ryhma}")
        
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
            st.info("""**Rintasyövän Stage-muistisääntö:**

* **Stage I:** T1 N0
* **Stage IIA:** T0-T1 N1 tai T2 N0
* **Stage IIB:** T2 N1 tai T3 N0
* **Stage IIIA:** T0-T2 N2 tai T3 N1-N2
* **Stage IIIB:** T4, mikä tahansa N
* **Stage IIIC:** Mikä tahansa T, N3

*(T1 ≤2cm, T2 2-5cm, T3 >5cm, T4 iho/rintakehä)*  
*(N1: 1-3 kainalo, N2: 4-9 kainalo/sis.rinta, N3: ≥10 kainalo/soliskuoppa)*""")
                    
        c_p = ["Stage I - IIA", "Stage IIB - IIIA", "Stage IIIB - IIIC"].index(cpseg_cstage_str)
        p_p = ["Stage 0 tai I", "Stage IIA - IIB", "Stage IIIA - IIIC"].index(cpseg_pstage_str)
        
        pisteet = laske_cps_eg_pisteet(c_p, p_p, cpseg_er, cpseg_grade)
        ennuste = hae_cps_eg_ennuste(pisteet)
        
        st.markdown("---")
        st.success(f"**Tulos:** CPS+EG -pisteet: {pisteet} / 6")
        st.info(f"**Ennuste:** {ennuste}")
        
        if pisteet >= 3:
            st.warning("**Huom:** Jos invasiivistä jäännöstautia, niin muista olaparibi-liitännäishoidon mahdollisuus ituradan BRCA-mutaation omaavilla vuoden ajaksi.")
            
    elif laskuri_valinta == "Child-Pugh -luokitus (Maksan vajaatoiminta)":
        st.subheader("Child-Pugh -luokitus")
        st.write("Arvioi kroonisen maksasairauden / kirroosin vakavuutta ja ennustetta.")
        
        col1, col2 = st.columns(2)
        with col1:
            cp_bili_str = st.radio("Bilirubiini (µmol/l)", ["< 34", "34 - 50", "> 50"], key="cp_bili")
            cp_alb_str = st.radio("Albumiini (g/l)", ["> 35", "28 - 35", "< 28"], key="cp_alb")
            cp_inr_str = st.radio("INR", ["< 1.7", "1.7 - 2.2", "> 2.2"], key="cp_inr")
        with col2:
            cp_ascites_str = st.radio("Askites", ["Ei", "Lievä / lääkityksellä hallinnassa", "Keskivaikea tai vaikea / huonosti reagoiva"], key="cp_ascites")
            cp_enk_str = st.radio("Enkefalopatia", ["Ei", "Aste I-II (Lievä / lääkityksellä hallinnassa)", "Aste III-IV (Vaikea / kooma)"], key="cp_enk")
            
        bili_p = ["< 34", "34 - 50", "> 50"].index(cp_bili_str) + 1
        alb_p = ["> 35", "28 - 35", "< 28"].index(cp_alb_str) + 1
        inr_p = ["< 1.7", "1.7 - 2.2", "> 2.2"].index(cp_inr_str) + 1
        ascites_p = ["Ei", "Lievä / lääkityksellä hallinnassa", "Keskivaikea tai vaikea / huonosti reagoiva"].index(cp_ascites_str) + 1
        enk_p = ["Ei", "Aste I-II (Lievä / lääkityksellä hallinnassa)", "Aste III-IV (Vaikea / kooma)"].index(cp_enk_str) + 1
            
        pisteet = laske_child_pugh_pisteet(bili_p, alb_p, inr_p, ascites_p, enk_p)
        luokka = hae_child_pugh_luokka(pisteet)
        
        st.markdown("---")
        st.success(f"**Tulos:** Child-Pugh -pisteet: {pisteet} / 15")
        st.info(f"**Luokitus:** {luokka}")

    elif laskuri_valinta == "PSA:n kahdentumisaika (PSADT)":
        st.subheader("PSA:n kahdentumisaika (PSADT)")
        st.write("Arvioi eturauhassyövän etenemistä mittaamalla aikaa, jossa PSA-arvo kaksinkertaistuu.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**1. mittaus**")
            pvm1 = st.date_input("Päivämäärä 1", value=date.today() - timedelta(days=90), key="psadt_pvm1")
            psa1 = st.number_input("PSA-arvo 1", min_value=0.0, step=0.1, value=5.0, key="psadt_psa1")
        with col2:
            st.markdown("**2. mittaus**")
            pvm2 = st.date_input("Päivämäärä 2", value=date.today(), key="psadt_pvm2")
            psa2 = st.number_input("PSA-arvo 2", min_value=0.0, step=0.1, value=10.0, key="psadt_psa2")
            
        if psa1 > 0 and psa2 > 0 and pvm2 > pvm1 and psa2 > psa1:
            psadt = laske_psadt(pvm1, psa1, pvm2, psa2)
            tulkinta = hae_psadt_tulkinta(psadt)
            
            st.markdown("---")
            st.success(f"**Tulos:** PSADT = {psadt:.1f} kuukautta")
            st.info(f"**Tulkinta:** {tulkinta}")
        elif pvm2 <= pvm1:
            st.warning("Jälkimmäisen päivämäärän on oltava ensimmäisen jälkeen.")
        elif psa2 <= psa1 and psa2 != 0:
            st.warning("Jälkimmäisen PSA-arvon on oltava suurempi kuin ensimmäisen, jotta kahdentumisaika voidaan laskea.")

elif view == "Ohjeet":
    st.header("Ohjeet ja Protokollat")
    
    ohje_valinta = st.selectbox("Valitse ohje", ["Valitse..."] + list(OHJEET.keys()))
    
    if ohje_valinta and ohje_valinta != "Valitse...":
        st.markdown("---")
        # Näytetään Markdown-muotoiltu teksti siististi
        st.markdown(OHJEET[ohje_valinta])

elif view == "Haittavaikutukset":
    st.header("Haittavaikutusten hallinta")
    st.write("Valitse tablettilääke ja kyseisen lääkkeen tyyppihaitta nähdäksesi valmisteyhteenvedon mukaiset annosreduktio- ja tauotusohjeet.")
    
    from oncology_helper.toxicity import HAITTAVAIKUTUKSET
    
    col1, col2 = st.columns(2)
    with col1:
        laake = st.selectbox("Valitse lääkeaine", ["Valitse..."] + sorted(list(HAITTAVAIKUTUKSET.keys())))
        
    with col2:
        haitat = ["Valitse..."] + sorted(list(HAITTAVAIKUTUKSET[laake].keys())) if laake and laake != "Valitse..." else ["Valitse lääke ensin"]
        haitta = st.selectbox("Valitse haittavaikutus", haitat)
        
    if laake and laake != "Valitse..." and haitta and haitta not in ["Valitse...", "Valitse lääke ensin"]:
        st.markdown("---")
        st.subheader(f"Toimenpideohjeet: {laake} – {haitta}")
        
        ohjeet = HAITTAVAIKUTUKSET[laake][haitta]
        for gradus, ohje in ohjeet.items():
            st.markdown(f"**{gradus}:**")
            st.info(ohje)