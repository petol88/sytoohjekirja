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

class IpiRiskiluokka(Enum):
    MATALA = "Matala riski (0-1 pistettä)"
    MATALA_KOHTALAINEN = "Matala-kohtalainen riski (2 pistettä)"
    KORKEA_KOHTALAINEN = "Korkea-kohtalainen riski (3 pistettä)"
    KORKEA = "Korkea riski (4-5 pistettä)"

def laske_ipi_pisteet(ika_yli_60: bool, levinneisyys_3_tai_4: bool, 
                      ekstranodaalipesakkeet_yli_1: bool, ecog_yli_1: bool, 
                      ldh_koholla: bool) -> int:
    """Laskee IPI (International Prognostic Index) -pisteet (0-5)."""
    pisteet = 0
    if ika_yli_60: pisteet += 1
    if levinneisyys_3_tai_4: pisteet += 1
    if ekstranodaalipesakkeet_yli_1: pisteet += 1
    if ecog_yli_1: pisteet += 1
    if ldh_koholla: pisteet += 1
    return pisteet

def maarita_ipi_riskiluokka(pisteet: int) -> IpiRiskiluokka:
    """Määrittää IPI-riskiluokan pisteiden perusteella."""
    if pisteet <= 1:
        return IpiRiskiluokka.MATALA
    elif pisteet == 2:
        return IpiRiskiluokka.MATALA_KOHTALAINEN
    elif pisteet == 3:
        return IpiRiskiluokka.KORKEA_KOHTALAINEN
    else:
        return IpiRiskiluokka.KORKEA

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