import math
from typing import Union, Optional
from enum import Enum

class Sukupuoli(Enum):
    MIES = "Mies"
    NAINEN = "Nainen"

def safe_float(v: Union[str, float, int]) -> float:
    """Safely converts a value to float. Returns 0.0 if conversion fails."""
    try: 
        if isinstance(v, (float, int)):
            return float(v)
        return float(str(v).replace(",", ".").strip())
    except (ValueError, TypeError, AttributeError): 
        return 0.0

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