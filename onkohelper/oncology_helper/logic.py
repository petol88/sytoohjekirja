import math
from typing import Union, List, Optional
from enum import Enum

class Sukupuoli(Enum):
    MIES = "Mies"
    NAINEN = "Nainen"

class ReseptoriTila(Enum):
    POSITIIVINEN = "Positiivinen"
    NEGATIIVINEN = "Negatiivinen"

class Ki67Tila(Enum):
    MATALA = "Matala (<20%)"
    KORKEA = "Korkea (>=20%)"

class Hoitolinja(Enum):
    EI_VALITTU = "-"
    NEOADJUVANTTI = "Neoadjuvantti"
    ADJUVANTTI = "Adjuvantti"

class IsupLuokka(Enum):
    ISUP_1 = "ISUP 1 (Gleason 6)"
    ISUP_2 = "ISUP 2 (Gleason 3+4=7)"
    ISUP_3 = "ISUP 3 (Gleason 4+3=7)"
    ISUP_4 = "ISUP 4 (Gleason 8)"
    ISUP_5 = "ISUP 5 (Gleason 9-10)"

class PsaTaso(Enum):
    ALLE_10 = "PSA < 10"
    VALILLA_10_20 = "PSA 10-20"
    YLI_20 = "PSA > 20"

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
        return float(str(v).replace(",", ".").strip())
    except (ValueError, TypeError, AttributeError): 
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

def laske_cockcroft_gault(age: float, weight_kg: float, creatinine: float, sex: Sukupuoli) -> float:
    """
    Calculates Glomerular Filtration Rate (GFR) using the Cockcroft-Gault formula.
    
    Args:
        age: Age in years.
        weight_kg: Weight in kilograms.
        creatinine: Serum creatinine in micromol/L.
        sex: Sukupuoli Enum.
        
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
    
    if sex == Sukupuoli.NAINEN: 
        gfr *= 0.85
        
    return gfr

def laske_calvert(auc: float, gfr: float, max_gfr: float = 125.0) -> float:
    """
    Calculates Carboplatin dose using the Calvert formula.
    
    Args:
        auc: Target AUC.
        gfr: Glomerular Filtration Rate (mL/min).
        max_gfr: Maximum allowed GFR to prevent overdosing (default 125.0).
        
    Returns:
        float: Total Carboplatin dose in milligrams (mg).
    """
    if auc <= 0 or gfr <= 0:
        return 0.0
    
    capped_gfr = min(gfr, max_gfr)
    return auc * (capped_gfr + 25.0)

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
    if yksikko == "mg/m2":
        return perusannos * bsa
    elif yksikko == "mg/kg":
        return perusannos * paino
    elif yksikko == "AUC":
        capped_gfr = min(gfr, 125.0)
        return laske_calvert(perusannos, capped_gfr)
    
    # Fixed dose (e.g., 'mg' or 'mg (kiinteä)')
    return perusannos

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

def maarita_hoitosuunnitelma_rintasyopa(stage: str, t: str, n: str, m: str, 
                                         er: ReseptoriTila, her2: ReseptoriTila, ki67: Ki67Tila, 
                                         valittu_hoitolinja: Optional[Hoitolinja] = None) -> str:
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
    if her2 == ReseptoriTila.POSITIIVINEN:
        subtype = "HER2-positiivinen"
        if er == ReseptoriTila.POSITIIVINEN: subtype += " (Luminal B -like)"
        else: subtype += " (Non-Luminal)"
    elif er == ReseptoriTila.POSITIIVINEN:
        if ki67 == Ki67Tila.KORKEA: subtype = "Luminal B -like (HER2-)"
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
    if valittu_hoitolinja and valittu_hoitolinja in [Hoitolinja.NEOADJUVANTTI, Hoitolinja.ADJUVANTTI]:
        setting = valittu_hoitolinja.value

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
        if er == ReseptoriTila.POSITIIVINEN:
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

def laske_stage_suolistosyopa(t: str, n: str, m: str) -> str:
    """
    Calculates the anatomical stage group for Colorectal Cancer based on TNM.
    """
    if "M1" in m:
        if "M1a" in m: return "Stage IVA"
        if "M1b" in m: return "Stage IVB"
        if "M1c" in m: return "Stage IVC"
        return "Stage IV"
        
    if "N1" in n or "N2" in n:
        if "T4b" in t: return "Stage IIIC"
        if "N2b" in n: return "Stage IIIC"
        if "N2a" in n:
            if "T4a" in t or "T3" in t: return "Stage IIIC" if "T4a" in t else "Stage IIIB"
            return "Stage IIIB"
        if "N1" in n:
            if "T1" in t or "T2" in t: return "Stage IIIA"
            if "T3" in t or "T4a" in t: return "Stage IIIB"
        return "Stage III"

    if "N0" in n:
        if "Tis" in t: return "Stage 0"
        if "T1" in t or "T2" in t: return "Stage I"
        if "T3" in t: return "Stage IIA"
        if "T4a" in t: return "Stage IIB"
        if "T4b" in t: return "Stage IIC"

    return "Ei määritettävissä"

def maarita_hoitosuunnitelma_suolistosyopa(stage: str, t: str, n: str, m: str) -> str:
    """
    Determines the comprehensive treatment plan for Colorectal Cancer.
    """
    if "Stage IV" in stage or "M1" in m:
        return (
            "Levinnyt suolistosyöpä:\n"
            "• Palliatiivinen solunsalpaajahoito (esim. FOLFOX, FOLFIRI, CAPOX) yhdistettynä biologiseen "
            "hoitoon (esim. bevasitsumabi tai panitumumabi/setuksimabi RAS-villityypin taudissa).\n"
            "• Etäpesäkkeiden (esim. maksa/keuhko) kirurginen poisto moniammatillisen harkinnan mukaan."
        )
    
    res = "Lääkehoitosuositus (Adjuvantti):\n"
    if "Stage I" in stage or "Stage 0" in stage:
        res += "• Ei adjuvanttisolunsalpaajahoidon indikaatiota. Pelkkä kirurginen poisto ja seuranta.\n"
    elif "Stage II" in stage:
        res += "• Matalan riskin tauti (T3N0M0, ei riskitekijöitä): Usein pelkkä seuranta.\n"
        res += "• Korkean riskin tauti (esim. T4, perforaatio, ileus, <12 tutkittua imusolmuketta): Harkitaan adjuvanttihoitoa (Kapesitabiini 6 kk tai CAPOX 3-6 kk / FOLFOX 6 kk).\n"
    elif "Stage III" in stage:
        res += "• Adjuvanttisolunsalpaajahoito on indisoitu.\n"
        if "T4" in t or "N2" in n:
             res += "• Korkean riskin Stage III: CAPOX 3-6 kk tai FOLFOX 6 kk ensisijaisena.\n"
        else:
             res += "• Matalan riskin Stage III (T1-3 N1): CAPOX 3 kk (tai FOLFOX 3-6 kk).\n"
        res += "• Yli 70-vuotiailla tai haurailla potilailla voidaan harkita solunsalpaajamonoterapiaa (Kapesitabiini 6 kk).\n"
    else:
        res += "• Suositusta ei voida antaa automaattisesti näillä arvoilla.\n"
        
    return res

def laske_riskiryhma_eturauhassyopa(t: str, n: str, m: str, isup: IsupLuokka, psa: PsaTaso) -> str:
    """
    Calculates Prostate Cancer risk group based on EAU guidelines.
    """
    if "M1" in m: return "Metastasoitunut (Levinnyt)"
    if "N1" in n: return "Paikallisesti levinnyt (Imusolmukepositiivinen)"
    
    t_high = any(x in t for x in ["T3", "T4"])
    isup_high = isup in [IsupLuokka.ISUP_4, IsupLuokka.ISUP_5]
    psa_high = psa == PsaTaso.YLI_20
    
    t_int = any(x in t for x in ["T2b", "T2c"])
    isup_int = isup in [IsupLuokka.ISUP_2, IsupLuokka.ISUP_3]
    psa_int = psa == PsaTaso.VALILLA_10_20
    
    if t_high or isup_high or psa_high:
        return "Korkea riski"
    if t_int or isup_int or psa_int:
        return "Kohtalainen riski"
        
    return "Matala riski"

def maarita_hoitosuunnitelma_eturauhassyopa(riski: str, t: str, n: str, m: str) -> str:
    """
    Determines the comprehensive treatment plan for Prostate Cancer.
    """
    res = "Hoitosuositus:\n"
    if "Metastasoitunut" in riski:
        res += "• Androgeenideprivaatiohoito (ADT) on perushoito.\n"
        res += "• Yhdistetään uuden polven hormonilääkkeeseen (ARPI: esim. Abirateroni, Entsalutamidi tai Darolutamidi).\n"
        res += "• Suuren tautitaakan (high volume) M1-taudissa voidaan harkita ADT + Dosetakseli + ARPI -kolmoishoitoa.\n"
        res += "• Jos luustoetäpesäkkeitä, harkitaan luustolääkitystä (Denosumabi/Tsoledronihappo)."
    elif "Imusolmukepositiivinen" in riski:
        res += "• Pitkä ADT (2-3 vuotta) yhdistettynä lantion ja eturauhasen sädehoitoon.\n"
        res += "• Voidaan harkita Abirateronin yhdistämistä hoitoon STAMPEDE-kriteerein."
    elif riski == "Korkea riski":
        res += "• Radikaali sädehoito + pitkä ADT (1.5 - 3 vuotta).\n"
        res += "• Vaihtoehtoisesti radikaalileikkaus ja laaja lantion imusolmukkeiden poisto."
    elif riski == "Kohtalainen riski":
        res += "• Radikaalileikkaus TAI sädehoito.\n"
        res += "• Sädehoidon yhteydessä lyhyt ADT (4 - 6 kuukautta).\n"
        res += "• Tietyissä suotuisissa tapauksissa aktiiviseuranta on mahdollinen."
    elif riski == "Matala riski":
        res += "• Ensisijaisesti aktiiviseuranta (Active Surveillance).\n"
        res += "• Radikaalihoito vain oireiden tai potilaan vahvan toiveen perusteella."
    return res

def laske_stage_melanooma(t: str, n: str, m: str) -> str:
    """
    Calculates the anatomical stage group for Melanoma based on TNM (AJCC 8th edition).
    """
    if "M1" in m:
        return "Stage IV"
        
    if "N1" in n or "N2" in n or "N3" in n:
        return "Stage III"
        
    if "N0" in n:
        if "Tis" in t: return "Stage 0"
        if "T1a" in t: return "Stage IA"
        if "T1b" in t or "T2a" in t: return "Stage IB"
        if "T2b" in t or "T3a" in t: return "Stage IIA"
        if "T3b" in t or "T4a" in t: return "Stage IIB"
        if "T4b" in t: return "Stage IIC"

    return "Ei määritettävissä"

def maarita_hoitosuunnitelma_melanooma(stage: str, t: str, n: str, m: str) -> str:
    """
    Determines the comprehensive treatment plan for Melanoma.
    """
    if "Stage IV" in stage or "M1" in m:
        return (
            "Levinnyt melanooma (Stage IV):\n"
            "• BRAF-mutaatiostatus tulee määrittää.\n"
            "• Immunoterapia (esim. Pembrolitsumabi, Nivolumab tai Ipilimumabi + Nivolumab).\n"
            "• BRAF-positiivisilla potilailla kohdennettu hoito (esim. Dabrafenibi + Trametinibi) on vaihtoehto."
        )
    
    res = "Lääkehoitosuositus (Adjuvantti):\n"
    if "Stage 0" in stage or "Stage I" in stage or "Stage IIA" in stage:
        res += "• Ei adjuvanttilääkehoidon indikaatiota. Radikaali kirurginen poisto ja seuranta.\n"
    elif "Stage IIB" in stage or "Stage IIC" in stage:
        res += "• Korkean riskin paikallinen tauti (syvä invaasio / ulseraatio).\n"
        res += "• Harkittavissa adjuvantti-immunoterapia (esim. Pembrolitsumabi 1 vuoden ajan).\n"
    elif "Stage III" in stage:
        res += "• Adjuvanttilääkehoito on vahvasti indisoitu imusolmukepositiivisessa taudissa.\n"
        res += "• Immunoterapia: Pembrolitsumabi tai Nivolumab 1 vuoden ajan.\n"
        res += "• BRAF-mutaatiopositiivisilla vaihtoehtona kohdennettu hoito (esim. Dabrafenibi + Trametinibi 1 v).\n"
    else:
        res += "• Suositusta ei voida antaa automaattisesti näillä arvoilla.\n"
        
    return res

def laske_stage_keuhkosyopa(t: str, n: str, m: str) -> str:
    """
    Calculates the anatomical stage group for Non-Small Cell Lung Cancer (NSCLC) based on TNM (AJCC 8th ed).
    """
    if "M1" in m:
        if "M1c" in m: return "Stage IVB"
        return "Stage IVA" # M1a and M1b
        
    if "N3" in n:
        if "T3" in t or "T4" in t: return "Stage IIIC"
        return "Stage IIIB"
        
    if "N2" in n:
        if "T3" in t or "T4" in t: return "Stage IIIB"
        return "Stage IIIA"
        
    if "N1" in n:
        if "T3" in t or "T4" in t: return "Stage IIIA"
        return "Stage IIB"
        
    if "N0" in n:
        if "T4" in t: return "Stage IIIA"
        if "T3" in t: return "Stage IIB"
        if "T2b" in t: return "Stage IIA"
        if "T2a" in t: return "Stage IB"
        if "T1c" in t: return "Stage IA3"
        if "T1b" in t: return "Stage IA2"
        if "T1a" in t: return "Stage IA1"

    return "Ei määritettävissä"

def maarita_hoitosuunnitelma_keuhkosyopa(stage: str, t: str, n: str, m: str) -> str:
    """
    Determines the comprehensive treatment plan for NSCLC.
    """
    if "Stage IV" in stage or "M1" in m:
        return (
            "Levinnyt keuhkosyöpä (Stage IV):\n"
            "• Mutaatiotestaus on kriittinen (EGFR, ALK, ROS1, BRAF, KRAS jne.) sekä PD-L1 -ilmentymä.\n"
            "• Kohdennettu hoito, jos löytyy ajajamutaatio (esim. Osimertinibi tai Alektinibi).\n"
            "• Muuten immunoterapia (esim. Pembrolitsumabi) joko yksin (jos PD-L1 korkea) tai yhdistettynä solunsalpaajahoitoon."
        )
    
    res = "Lääkehoitosuositus (Paikallinen tai paikallisesti levinnyt tauti):\n"
    if "Stage IA" in stage or "Stage IB" in stage:
        res += "• Radikaali kirurginen poisto (lobektomia).\n"
        res += "• Adjuvanttihoitoa harkitaan varoen riskitekijöiden (esim. tuumorin koko >4cm tai huono erilaistumisaste) perusteella.\n"
    elif "Stage II" in stage:
        res += "• Radikaali kirurginen poisto.\n"
        res += "• Adjuvanttisolunsalpaajahoito on indisoitu (esim. Sisplatiini-Vinorelbiini 4 sykliä).\n"
        res += "• PD-L1 / EGFR -status määrittää mahdollisen adjuvantti-immunoterapian (esim. Atezolitsumabi) tai täsmähoidon (esim. Osimertinibi) tarpeen solunsalpaajan jälkeen.\n"
    elif "Stage III" in stage:
        res += "• Stage IIIA (operabeli): Neoadjuvantti immunokemoterapia -> leikkaus (-> adjuvanttihoito harkinnan mukaan).\n"
        res += "• Stage IIIB-IIIC (inoperabeli): Radikaali kemosädehoito, jonka jälkeen ylläpito-immunoterapia (Durvalumabi 1 vuoden ajan).\n"
    else:
        res += "• Suositusta ei voida antaa automaattisesti näillä arvoilla.\n"
        
    return res
