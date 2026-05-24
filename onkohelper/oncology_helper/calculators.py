import math
from typing import Union, Optional
from enum import Enum
from dataclasses import dataclass

class Sukupuoli(Enum):
    MIES = "Mies"
    NAINEN = "Nainen"

class EcogLuokka(Enum):
    ECOG_0 = 0
    ECOG_1 = 1
    ECOG_2 = 2
    ECOG_3 = 3
    ECOG_4 = 4
    ECOG_5 = 5

def hae_ecog_kuvaus(luokka: EcogLuokka) -> str:
    """Palauttaa ECOG-suorituskykyluokan virallisen kuvauksen."""
    kuvaukset = {
        EcogLuokka.ECOG_0: "Täysin aktiivinen, kykenee jatkamaan kaikkia sairautta edeltäneitä toimintoja rajoituksetta.",
        EcogLuokka.ECOG_1: "Rajoittunut raskaassa fyysisessä rasituksessa, mutta pystyy kävelemään ja tekemään kevyttä tai istumatyötä (esim. kevyt kotityö, toimistotyö).",
        EcogLuokka.ECOG_2: "Pystyy kävelemään ja huolehtimaan itsestään, mutta ei kykene tekemään työtä. Oloillaan jalkeilla yli 50 % valveillaoloajasta.",
        EcogLuokka.ECOG_3: "Kykenee vain osittain huolehtimaan itsestään. Sidottu vuoteeseen tai tuoliin yli 50 % valveillaoloajasta.",
        EcogLuokka.ECOG_4: "Täysin autettava. Ei kykene huolehtimaan itsestään lainkaan. Täysin sidottu vuoteeseen tai tuoliin.",
        EcogLuokka.ECOG_5: "Kuollut."
    }
    return kuvaukset.get(luokka, "Tuntematon luokka.")

def safe_float(v: Union[str, float, int]) -> float:
    """Safely converts a value to float. Returns 0.0 if conversion fails."""
    try: 
        if isinstance(v, (float, int)):
            return float(v)
        return float(str(v).replace(",", ".").strip())
    except (ValueError, TypeError, AttributeError): 
        return 0.0

@dataclass
class Potilas:
    pituus_cm: float
    paino_kg: float
    ika: float
    krea: float
    sukupuoli: Sukupuoli
    
    def bsa(self, max_bsa: Optional[float] = None) -> float:
        return laske_bsa(self.pituus_cm, self.paino_kg, max_bsa)
        
    def gfr(self) -> float:
        return laske_cockcroft_gault(self.ika, self.paino_kg, self.krea, self.sukupuoli)

def laske_bsa(height_cm: float, weight_kg: float, max_bsa: Optional[float] = None) -> float:
    """Calculates Body Surface Area (BSA) using the Mosteller formula."""
    if height_cm <= 0 or weight_kg <= 0: 
        return 0.0
    bsa = math.sqrt((height_cm * weight_kg) / 3600)
    if max_bsa is not None and bsa > max_bsa:
        return max_bsa
    return bsa

def laske_cockcroft_gault(age: float, weight_kg: float, creatinine: float, sex: Sukupuoli) -> float:
    """Calculates Glomerular Filtration Rate (GFR) using the Cockcroft-Gault formula."""
    if creatinine <= 0: 
        return 0.0
    
    # Constant 0.814 is for creatinine in micromol/L.
    gfr = ((140 - age) * weight_kg) / (0.814 * creatinine)
    
    if sex == Sukupuoli.NAINEN: 
        gfr *= 0.85
        
    return gfr

def laske_calvert(auc: float, gfr: float, max_gfr: float = 125.0) -> float:
    """Calculates Carboplatin dose using the Calvert formula."""
    if auc <= 0 or gfr <= 0:
        return 0.0
    
    capped_gfr = min(gfr, max_gfr)
    return auc * (capped_gfr + 25.0)

def pyorista_tabletit(mg: float, strength: float) -> int:
    """Rounds the dosage to the nearest full tablet strength."""
    if strength <= 0: 
        return int(mg)
    return int(round(mg / strength) * strength)

def laske_yksiloity_annos(perusannos: float, yksikko: str, bsa: float, paino: float, gfr: float) -> float:
    """
    Calculates the patient-specific dose based on the given medical unit.
    
    Args:
        perusannos: The base dose from the protocol (e.g., 75 for Docetaxel).
        yksikko: The unit string ('mg/m2', 'mg/kg', 'AUC', 'mg').
        bsa: Patient's Body Surface Area.
        paino: Patient's weight in kg.
        gfr: Patient's Glomerular Filtration Rate.
        
    Returns:
        float: The calculated personalized dose in mg.
    """
    if "mg/m2" in yksikko:
        return perusannos * bsa
    elif "mg/kg" in yksikko:
        return perusannos * paino
    elif "AUC" in yksikko:
        capped_gfr = min(gfr, 125.0)
        return laske_calvert(perusannos, capped_gfr)
    
    # Fixed dose (e.g., 'mg' or 'mg (kiinteä)')
    return perusannos

def laske_ipi_pisteet(ika_yli_60: bool, ldh_koholla: bool, ecog_vahintaan_2: bool, stage_3_4: bool, ekstranodaali_yli_1: bool) -> int:
    pisteet = 0
    if ika_yli_60: pisteet += 1
    if ldh_koholla: pisteet += 1
    if ecog_vahintaan_2: pisteet += 1
    if stage_3_4: pisteet += 1
    if ekstranodaali_yli_1: pisteet += 1
    return pisteet

def hae_ipi_riskiryhma(pisteet: int) -> str:
    ryhmat = {
        0: "Matala riski (5-vuoden elossaoloennuste n. 90 %)", 
        1: "Matala riski (5-vuoden elossaoloennuste n. 90 %)", 
        2: "Matala-kohtalainen riski (5-vuoden elossaoloennuste n. 77 %)", 
        3: "Korkea-kohtalainen riski (5-vuoden elossaoloennuste n. 67 %)", 
        4: "Korkea riski (5-vuoden elossaoloennuste n. 55 %)", 
        5: "Korkea riski (5-vuoden elossaoloennuste n. 55 %)"
    }
    return ryhmat.get(pisteet, "Tuntematon riski")

def laske_cns_ipi_pisteet(ika_yli_60: bool, ldh_koholla: bool, ecog_vahintaan_2: bool, stage_3_4: bool, ekstranodaali_yli_1: bool, munuainen_lisamunuainen: bool) -> int:
    pisteet = 0
    if ika_yli_60: pisteet += 1
    if ldh_koholla: pisteet += 1
    if ecog_vahintaan_2: pisteet += 1
    if stage_3_4: pisteet += 1
    if ekstranodaali_yli_1: pisteet += 1
    if munuainen_lisamunuainen: pisteet += 1
    return pisteet

def hae_cns_ipi_riskiryhma(pisteet: int) -> str:
    if pisteet <= 1: return "Matala riski (2 vuoden CNS-relapsin todennäköisyys n. 0,6 %)"
    elif pisteet <= 3: return "Kohtalainen riski (2 vuoden CNS-relapsin todennäköisyys n. 3,4 %)"
    else: return "Korkea riski (2 vuoden CNS-relapsin todennäköisyys n. 10,2 %)"

def laske_mipi_pisteet(ika_pisteet: int, ecog_pisteet: int, ldh_pisteet: int, wbc_pisteet: int) -> int:
    return ika_pisteet + ecog_pisteet + ldh_pisteet + wbc_pisteet

def hae_mipi_riskiryhma(pisteet: int) -> str:
    if pisteet <= 3: return "Matala riski (0-3 p) - 5-vuoden elossaoloennuste n. 83 %"
    elif pisteet <= 5: return "Kohtalainen riski (4-5 p) - Mediaani elossaoloaika n. 51 kk"
    else: return "Korkea riski (≥6 p) - Mediaani elossaoloaika n. 29 kk"

def laske_flipi_pisteet(ika_yli_60: bool, stage_3_4: bool, hb_alle_120: bool, nodaali_yli_4: bool, ldh_koholla: bool) -> int:
    pisteet = 0
    if ika_yli_60: pisteet += 1
    if stage_3_4: pisteet += 1
    if hb_alle_120: pisteet += 1
    if nodaali_yli_4: pisteet += 1
    if ldh_koholla: pisteet += 1
    return pisteet

def hae_flipi_riskiryhma(pisteet: int) -> str:
    if pisteet <= 1: return "Matala riski (0-1 p) - 5-vuoden elossaoloennuste n. 91 % (10-vuoden n. 71 %)"
    elif pisteet == 2: return "Kohtalainen riski (2 p) - 5-vuoden elossaoloennuste n. 78 % (10-vuoden n. 51 %)"
    else: return "Korkea riski (3-5 p) - 5-vuoden elossaoloennuste n. 53 % (10-vuoden n. 36 %)"

def tarkista_gelf_kriteerit(bulkki: bool, perna: bool, kompressio: bool, ldh_b2m: bool, leukemia: bool, sytopeniat: bool, b_oireet: bool) -> int:
    # Palautetaan täyttyvien kriteerien määrä
    return sum([bulkki, perna, kompressio, ldh_b2m, leukemia, sytopeniat, b_oireet])

def hae_gelf_suositus(pisteet: int) -> str:
    if pisteet > 0:
        return "Aktiivihoidon indikaatio täyttyy (≥1 GELF-kriteeri)."
    return "Ei vahvaa aktiivihoidon indikaatiota (Watch & Wait -seuranta mahdollinen)."

def laske_cps_eg_pisteet(c_stage_pisteet: int, p_stage_pisteet: int, er_negatiivinen: bool, grade_3: bool) -> int:
    pisteet = c_stage_pisteet + p_stage_pisteet
    if er_negatiivinen: pisteet += 1
    if grade_3: pisteet += 1
    return pisteet

def hae_cps_eg_ennuste(pisteet: int) -> str:
    ennusteet = {
        0: "0 p - 5-vuoden tautispesifinen elossaoloennuste (DSS) n. 100 %",
        1: "1 p - 5-vuoden tautispesifinen elossaoloennuste (DSS) n. 98 %",
        2: "2 p - 5-vuoden tautispesifinen elossaoloennuste (DSS) n. 94 %",
        3: "3 p - 5-vuoden tautispesifinen elossaoloennuste (DSS) n. 84 %",
        4: "4 p - 5-vuoden tautispesifinen elossaoloennuste (DSS) n. 71 %",
        5: "5-6 p - 5-vuoden tautispesifinen elossaoloennuste (DSS) n. 42 %",
        6: "5-6 p - 5-vuoden tautispesifinen elossaoloennuste (DSS) n. 42 %"
    }
    return ennusteet.get(pisteet, "Tuntematon ennuste")