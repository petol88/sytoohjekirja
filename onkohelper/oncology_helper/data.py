import json
import os
from typing import Dict, List, Optional, Any

# TNM Data for staging
TNM_DATA: Dict[str, Dict[str, Any]] = {
    "Rintasyöpä": {
        "Type": "TNM",
        "L1_Label": "T (Kasvain)", "L2_Label": "N (Imusolmukkeet)", "L3_Label": "M (Etäpesäkkeet)",
        "L1": [ # T
            "Tx: Ei arvioitavissa", "T0: Ei primaarikasvainta", "Tis: In situ (DCIS/LCIS)",
            "T1mi: ≤ 1 mm", "T1a: >1-5 mm", "T1b: >5-10 mm", "T1c: >10-20 mm",
            "T2: >20-50 mm", "T3: >50 mm",
            "T4a: Rintakehän seinämä", "T4b: Ihohaavauma/turvotus", "T4c: T4a+T4b", "T4d: Inflammatorinen"
        ],
        "L2": [ # N
            "Nx: Ei arvioitavissa", "N0: Ei levinneisyyttä", "N1mi: Mikrometastaasit",
            "N1: 1-3 kainaloimusolmuketta", "N2a: 4-9 kainaloimusolmuketta", "N2b: Sisäiset rintaimusolmukkeet",
            "N3a: ≥10 kainaloimusolmuketta", "N3b: Sisäiset + kainalo", "N3c: Soliskuoppa (supra)"
        ],
        "L3": [ # M
            "M0: Ei etäpesäkkeitä", "M1: Etäpesäke todettu"
        ]
    },
    "Lymfooma (Ann Arbor)": {
        "Type": "AnnArbor",
        "L1_Label": "Levinneisyysalueet", "L2_Label": "Oireet (A/B)", "L3_Label": "Lisämääreet",
        "L1": [
            "I: Yksi imusolmukealue TAI yksi rajoittunut ekstranodaalinen alue (IE)",
            "II: Kaksi tai useampia alueita samalla puolella palleaa",
            "III: Imusolmukealueita molemmin puolin palleaa",
            "IV: Diffuusi tai dissiminoitunut levinneisyys yhdessä tai useammassa ulkopuolisessa elimessä"
        ],
        "L2": [
            "A: Ei yleisoireita",
            "B: Yleisoireet (Kuume >38°C, yöhikoilu, painonlasku >10%)"
        ],
        "L3": [
            "-: Ei lisämääreitä",
            "E: Rajoittunut ekstranodaalinen leviäminen (paikallinen)",
            "S: Pernan affisio (Spleen)",
            "X: Kookas kasvainmassa (Bulky, esim >10cm tai >1/3 rintakehästä)"
        ]
    },
    "Eturauhassyöpä": {
        "Type": "TNM",
        "L1_Label": "T (Kasvain)", "L2_Label": "N (Imusolmukkeet)", "L3_Label": "M (Etäpesäkkeet)",
        "L1": ["T1c: Neulanäyte (PSA)", "T2a: ≤50% yksi lohko", "T2b: >50% yksi lohko", "T2c: Molemmat lohkot", "T3a: Kapselin läpi", "T3b: Rakkularauhanen", "T4: Invaasio ympäristöön"],
        "L2": ["N0: Ei imusolmukkeita", "N1: Alueellinen imusolmuke"],
        "L3": ["M0: Ei etäpesäkkeitä", "M1a: Ei-alueelliset imusolmukkeet", "M1b: Luusto", "M1c: Muu elin"]
    },
    "Keuhkosyöpä (NSCLC)": {
        "Type": "TNM",
        "L1_Label": "T (Kasvain)", "L2_Label": "N (Imusolmukkeet)", "L3_Label": "M (Etäpesäkkeet)",
        "L1": ["T1a: ≤1cm", "T1b: >1-2cm", "T1c: >2-3cm", "T2a: >3-4cm", "T2b: >4-5cm", "T3: >5-7cm", "T4: >7cm tai invaasio"],
        "L2": ["N0: Ei levinneisyyttä", "N1: Hilaariset/Peribronk.", "N2: Mediastinaaliset (sama puoli)", "N3: Vastakkainen puoli/Soliskupat"],
        "L3": ["M0: Ei etäpesäkkeitä", "M1a: Pleura/Perikardium", "M1b: Yksi etäpesäke", "M1c: Useita etäpesäkkeitä"]
    }
}

def luo_esimerkkidata() -> None:
    """Creates med_data.json with example data if it is missing."""
    esimerkkidata = {
        "R-CHOP (NHL)": {
            "sykli": "21 vrk",
            "kontrollit": "PVK, Krea, Alat, Afos, EKG, (Pre-phase tarvittaessa)",
            "esilääkitys": "Kortisoni iv/po, Antihistamiini, Parasetamoli. G-CSF tuki tarvittaessa.",
            "lääkkeet": [
                {"nimi": "Rituksimabi", "annos": 375, "yksikkö": "mg/m2", "reseptiohje": "iv (hidas tiputus)", "max_mg": None, "päivät": "d1"},
                {"nimi": "Syklofosfamidi", "annos": 750, "yksikkö": "mg/m2", "reseptiohje": "iv", "max_mg": None, "päivät": "d1"},
                {"nimi": "Doksorubisiini", "annos": 50, "yksikkö": "mg/m2", "reseptiohje": "iv", "max_mg": None, "päivät": "d1"},
                {"nimi": "Vinkristiini", "annos": 1.4, "yksikkö": "mg/m2", "reseptiohje": "iv (Max 2mg)", "max_mg": 2.0, "päivät": "d1"},
                {"nimi": "Prednisolon", "annos": 40, "yksikkö": "mg/m2", "tablettikoot": ["40 mg", "20 mg"], "reseptiohje": "po aamuisin", "max_mg": None, "päivät": "d1-5"}
            ]
        }
    }
    try:
        with open("med_data.json", "w", encoding="utf-8") as f:
            json.dump(esimerkkidata, f, indent=4)
    except Exception as e:
        print(f"Varoitus: Ei voitu luoda esimerkkidataa: {e}")

class Tietokanta:
    """Handles loading and accessing protocol data."""
    data: Dict[str, Any] = {}

    @classmethod
    def lataa(cls) -> None:
        """Loads data from med_data.json, creating it if necessary."""
        # Determines path relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(base_dir, "med_data.json")

        if not os.path.exists(filepath):
            # Fallback to current working directory if not found in package dir (e.g. dev environment)
            if os.path.exists("med_data.json"):
                filepath = "med_data.json"
            else:
                # Create in package dir
                filepath = os.path.join(base_dir, "med_data.json")
                try:
                    luo_esimerkkidata()
                    # luo_esimerkkidata writes to CWD by default, let's move it or rewrite it?
                    # Actually luo_esimerkkidata writes to "med_data.json". 
                    # Let's just fix luo_esimerkkidata to take a path or handle it here.
                    # For simplicity, we'll just check if CWD/med_data.json exists after call.
                    if os.path.exists("med_data.json") and filepath != "med_data.json":
                        os.rename("med_data.json", filepath)
                except:
                    pass
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                cls.data = json.load(f)
        except Exception as e:
            print(f"Virhe ladattaessa tietokantaa ({filepath}): {e}")
            cls.data = {}
