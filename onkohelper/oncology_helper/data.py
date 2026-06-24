import json
import os
from pathlib import Path
from typing import Dict, Any

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
    },
    "Suolistosyöpä": {
        "Type": "TNM",
        "L1_Label": "T (Kasvain)", "L2_Label": "N (Imusolmukkeet)", "L3_Label": "M (Etäpesäkkeet)",
        "L1": ["Tis: In situ", "T1: Submukoosa", "T2: Muscularis propria", "T3: Subseroosa / perikolinen rasva", "T4a: Viseraalinen peritoneum", "T4b: Invaasio muihin elimiin"],
        "L2": ["N0: Ei imusolmukkeita", "N1a: 1 alueellinen", "N1b: 2-3 alueellista", "N1c: Kasvainkertymiä (tumor deposits)", "N2a: 4-6 alueellista", "N2b: ≥7 alueellista"],
        "L3": ["M0: Ei etäpesäkkeitä", "M1a: Yksi elin (esim. maksa)", "M1b: Useita elimiä", "M1c: Vatsakalvon levinneisyys (peritoneaalinen)"]
    },
    "Melanooma": {
        "Type": "TNM",
        "L1_Label": "T (Breslow & Ulseraatio)", "L2_Label": "N (Imusolmukkeet)", "L3_Label": "M (Etäpesäkkeet)",
        "L1": [
            "Tis: Melanoma in situ", 
            "T1a: <0.8 mm ilman ulseraatiota", "T1b: <0.8 mm ulseraatiolla TAI 0.8-1.0 mm (± ulseraatio)", 
            "T2a: >1.0-2.0 mm ilman ulseraatiota", "T2b: >1.0-2.0 mm ulseraatiolla", 
            "T3a: >2.0-4.0 mm ilman ulseraatiota", "T3b: >2.0-4.0 mm ulseraatiolla", 
            "T4a: >4.0 mm ilman ulseraatiota", "T4b: >4.0 mm ulseraatiolla"
        ],
        "L2": [
            "N0: Ei imusolmukkeita", 
            "N1a: 1 mikroskooppinen", "N1b: 1 makroskooppinen", "N1c: In-transit/satelliitti ilman solmukkeita", 
            "N2a: 2-3 mikroskooppista", "N2b: 2-3 makroskooppista", "N2c: 1 solmuke + in-transit/satelliitti", 
            "N3a: ≥4 mikroskooppista", "N3b: ≥4 makroskooppista", "N3c: ≥2 solmuketta + in-transit/satelliitti"
        ],
        "L3": [
            "M0: Ei etäpesäkkeitä", 
            "M1a: Iho, pehmytkudos, ei-alueellinen imusolmuke", 
            "M1b: Keuhko", 
            "M1c: Muu sisäelin (ei KES)", 
            "M1d: Keskushermosto (KES)"
        ]
    }
}

class Tietokanta:
    """Handles loading and accessing protocol data."""
    data: Dict[str, Any] = {}

    @classmethod
    def lataa(cls) -> None:
        """Loads data from med_data.json, creating it if necessary."""
        base_dir = Path(__file__).parent.resolve()
        filepath = base_dir / "med_data.json"

        if not filepath.exists():
            print(f"Varoitus: Tietokantaa ei löydy: {filepath}")
            cls.data = {}
            return

        try:
            cls.data = json.loads(filepath.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Virhe ladattaessa tietokantaa ({filepath}): {e}")
            cls.data = {}
            
    @classmethod
    def tallenna(cls) -> None:
        """Saves the current state of cls.data back to med_data.json."""
        base_dir = Path(__file__).parent.resolve()
        filepath = base_dir / "med_data.json"
        
        try:
            filepath.write_text(json.dumps(cls.data, indent=4, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"Virhe tallennettaessa tietokantaa ({filepath}): {e}")
