import math
from typing import Union, List, Optional

def safe_float(v: Union[str, float, int]) -> float:
    """
    Safely converts a value to float. Returns 0.0 if conversion fails.
    
    Args:
        v: The value to convert.
        
    Returns:
        float: The converted float value or 0.0.
    """
    try: 
        if isinstance(v, (float, int)):
            return float(v)
        return float(v.replace(",", ".").strip())
    except: 
        return 0.0

def laske_bsa(height_cm: float, weight_kg: float) -> float:
    """
    Calculates Body Surface Area (BSA) using the Mosteller formula.
    
    Args:
        height_cm: Height in centimeters.
        weight_kg: Weight in kilograms.
        
    Returns:
        float: BSA in m2. Returns 0 if inputs are invalid.
    """
    if height_cm <= 0 or weight_kg <= 0: 
        return 0.0
    return math.sqrt((height_cm * weight_kg) / 3600)

def laske_cockcroft_gault(age: float, weight_kg: float, creatinine: float, sex: str) -> float:
    """
    Calculates Glomerular Filtration Rate (GFR) using the Cockcroft-Gault formula.
    
    Args:
        age: Age in years.
        weight_kg: Weight in kilograms.
        creatinine: Serum creatinine in micromol/L.
        sex: 'Mies' or 'Nainen'.
        
    Returns:
        float: GFR in mL/min. Returns 0 if creatinine is invalid.
    """
    if creatinine <= 0: 
        return 0.0
    
    # Formula uses creatinine in micromol/L (standard in Finland/Europe usually)
    # The constant 0.814 is for creatinine in micromol/L. 
    # Standard formula: ((140-age) * weight) / (72 * Cr_mg_dL)
    # To convert micromol/L to mg/dL: divide by 88.4
    # 72 * (Cr_umol / 88.4) approx 0.814 * Cr_umol
    
    gfr = ((140 - age) * weight_kg) / (0.814 * creatinine)
    
    if sex == "Nainen": 
        gfr *= 0.85
        
    return gfr

def pyorista_tabletit(mg: float, strength: float) -> int:
    """
    Rounds the dosage to the nearest full tablet strength.
    
    Args:
        mg: The target dosage in mg.
        strength: The tablet strength in mg.
        
    Returns:
        int: The rounded dosage in mg.
    """
    if strength <= 0: 
        return int(mg)
    return int(round(mg / strength) * strength)

def laske_stage_rintasyopa(t: str, n: str, m: str) -> str:
    """
    Calculates the anatomical stage group for Breast Cancer based on TNM.
    
    Args:
        t: T-stage string (e.g., "T1c").
        n: N-stage string (e.g., "N0").
        m: M-stage string (e.g., "M0").
        
    Returns:
        str: The stage group (e.g., "Stage IIA").
    """
    # Check for Metastasis first
    if "M1" in m: return "Stage IV"
    
    # Advanced N and T
    if "N3" in n: return "Stage IIIC"
    if "T4" in t: return "Stage IIIB"
    
    # Parse T number (simplified)
    t_n = 0
    if "T1" in t or "T0" in t: t_n = 1
    elif "T2" in t: t_n = 2
    elif "T3" in t: t_n = 3
    
    # Stage Logic
    if "N2" in n:
        if t_n <= 3: return "Stage IIIA"
        
    if "T3" in t:
        if "N1" in n or "N2" in n: return "Stage IIIA"
        # T3 N0 M0 is Stage IIB
        if "N0" in n: return "Stage IIB"
        
    if "T2" in t and "N1" in n: return "Stage IIB"
    if "T3" in t and "N0" in n: return "Stage IIB"
    
    # Check N1mi first because "N1" is a substring of "N1mi"
    if ("T0" in t or "T1" in t) and "N1mi" in n: return "Stage IB"

    if ("T0" in t or "T1" in t) and "N1" in n: return "Stage IIA"
    if "T2" in t and "N0" in n: return "Stage IIA"
    
    if "T1" in t and "N0" in n: return "Stage IA"
    
    if "Tis" in t and "N0" in n: return "Stage 0"
    
    return "Ei määritettävissä"

def suosittele_hoito_rintasyopa(stage: str, t: str, n: str, m: str) -> str:
    """
    Returns a treatment recommendation (Adjuvant/Neoadjuvant) based on Breast Cancer stage.
    
    Args:
        stage: The calculated stage string (e.g., "Stage IIA").
        t: T-stage.
        n: N-stage.
        m: M-stage.
        
    Returns:
        str: Recommendation text.
    """
    if "Stage IV" in stage or "M1" in m:
        return "Palliatiivinen hoito (levinnyt tauti)."
        
    # Neoadjuvant logic: Locally advanced (Stage III) or large tumor (T3/T4) or extensive nodes (N2/N3)
    # Also considers Stage IIB (T3N0) as potential neoadjuvant candidate.
    is_locally_advanced = False
    
    if "Stage III" in stage: is_locally_advanced = True
    if "T3" in t or "T4" in t: is_locally_advanced = True
    if "N2" in n or "N3" in n: is_locally_advanced = True
    
    if is_locally_advanced:
        return "Suositellaan neoadjuvanttihoitoa (levinneisyys tai kookas kasvain)."
        
    # Early stage
    return "Suositellaan ensisijaisesti leikkausta ja adjuvanttihoitoa."

def maarita_hoitosuunnitelma_rintasyopa(stage: str, t: str, n: str, m: str, 
                                         er: str, her2: str, ki67: str, 
                                         valittu_hoitolinja: Optional[str] = None) -> str:
    """
    Determines the comprehensive treatment plan for Breast Cancer.
    
    Args:
        stage: Calculated stage.
        t: T-stage.
        n: N-stage.
        m: M-stage.
        er: Estrogen Receptor status ("Positiivinen" / "Negatiivinen").
        her2: HER2 status ("Positiivinen" / "Negatiivinen").
        ki67: Ki-67 index ("Matala (<20%)" / "Korkea (>=20%)").
        valittu_hoitolinja: Manually selected line ("Neoadjuvantti" / "Adjuvantti" / "-").
        
    Returns:
        str: Detailed treatment recommendation.
    """
    if "Stage IV" in stage or "M1" in m:
        return "Levinnyt rintasyöpä: Hoito on palliatiivista. Hoidon valinta perustuu potilaan vointiin ja biologiseen alatyyppiin (ER/HER2)."

    # 1. Determine Subtype
    subtype = ""
    if her2 == "Positiivinen":
        subtype = "HER2-positiivinen"
        if er == "Positiivinen": subtype += " (Luminal B -like)"
        else: subtype += " (Non-Luminal)"
    elif er == "Positiivinen":
        if "Korkea" in ki67: subtype = "Luminal B -like (HER2-)"
        else: subtype = "Luminal A -like"
    else: # ER- HER2-
        subtype = "Kolmoisnegatiivinen (TNBC)"
        
    res = f"Biologinen alatyyppi: {subtype}\n"
    
    # 2. Determine Optimal Setting (Neoadjuvant vs Adjuvant)
    is_optimal_neoadjuvant = False
    if "Stage III" in stage or ("T3" in t or "T4" in t) or ("N2" in n or "N3" in n):
        is_optimal_neoadjuvant = True
        
    # TNBC and HER2+ often get neoadjuvant even in Stage II (T2 or N1)
    if (subtype == "Kolmoisnegatiivinen (TNBC)" or "HER2-positiivinen" in subtype) and ("T2" in t or "N1" in n):
        is_optimal_neoadjuvant = True

    optimal_setting = "Neoadjuvantti" if is_optimal_neoadjuvant else "Adjuvantti"
    
    # Determine Actual Setting based on user selection
    setting = optimal_setting
    if valittu_hoitolinja and valittu_hoitolinja in ["Neoadjuvantti", "Adjuvantti"]:
        setting = valittu_hoitolinja

    res += f"Hoitolinja: {setting}"
    if setting != optimal_setting:
        res += f" (Huom: Optimaalinen suositus olisi {optimal_setting})"
    res += "\n\n"
    
    # 3. Treatment Recommendations
    res += "Lääkehoitosuositus:\n"
    
    if "HER2-positiivinen" in subtype:
        chemo = "Dosetakseli-Syklofosfamidi (D-C) tai T-FEC"
        anti_her2 = "Trastutsumabi"
        if setting == "Neoadjuvantti": 
            chemo = "Dosetakseli-Karboplatiini" # often used with dual block
            anti_her2 += " + Pertutsumabi"
            
        res += f"• Solunsalpaaja: {chemo}\n"
        res += f"• Täsmähoito: {anti_her2}\n"
        if er == "Positiivinen":
            res += "• Hormonihoito: Tamoksifeeni tai aromataasinestäjä (solunsalpaajahoidon jälkeen)\n"
            
    elif subtype == "Kolmoisnegatiivinen (TNBC)":
        if setting == "Neoadjuvantti":
            res += "• Solunsalpaaja: Paklitakseli/Dosetakseli + Karboplatiini -> EC (Epirubisiini-Syklofosfamidi)\n"
            res += "• Immunoterapia: Pembrolitsumabi (harkinnan mukaan korkean riskin taudissa)\n"
        else:
            res += "• Solunsalpaaja: Dosetakseli-Syklofosfamidi (D-C) x 6 tai EC -> Dosetakseli\n"
            
    elif "Luminal A" in subtype:
        # Usually N0 -> endocrine only, Node positive -> considers chemo
        if "N0" in n:
            res += "• Ensisijaisesti hormonihoito (Tamoksifeeni tai AI).\n"
            res += "• Solunsalpaajahoitoa ei rutiinisti suositella, ellei korkea riski (esim. genomitesti).\n"
        else:
            res += "• Hormonihoito (Tamoksifeeni tai AI).\n"
            res += "• Solunsalpaajahoito (esim. D-C x 6 tai EC-Doc) harkinnan mukaan (imusolmukepositiivinen).\n"
            
    elif "Luminal B" in subtype:
        res += "• Solunsalpaaja: Dosetakseli-Syklofosfamidi (D-C) x 6 tai EC -> Dosetakseli\n"
        res += "• Hormonihoito: Tamoksifeeni tai aromataasinestäjä.\n"
        if "N2" in n or "N3" in n:
             res += "• Harkitse abemasisiklibiä adjuvanttina (korkea uusiutumisriski).\n"

    return res
