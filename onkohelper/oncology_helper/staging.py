from typing import Optional
from enum import Enum

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

def pura_luokka(arvo: str) -> str:
    """
    Erottaa pelkän T/N/M-luokan käyttöliittymän selitetekstistä.
    Esimerkiksi 'T4a: Rintakehän seinämä' -> 'T4a'
    """
    return arvo.split(":")[0].strip() if ":" in arvo else arvo.strip()

def laske_stage_rintasyopa(t: str, n: str, m: str) -> str:
    t_puhdas = pura_luokka(t)
    n_puhdas = pura_luokka(n)
    m_puhdas = pura_luokka(m)

    if m_puhdas == "M1": return "Stage IV"
    
    if n_puhdas.startswith("N3"): return "Stage IIIC"
    if t_puhdas.startswith("T4"): return "Stage IIIB"
    
    t_n = 0
    if t_puhdas in ["T0", "T1", "T1mi", "T1a", "T1b", "T1c"]: t_n = 1
    elif t_puhdas == "T2": t_n = 2
    elif t_puhdas == "T3": t_n = 3
    
    if n_puhdas.startswith("N2") and t_n <= 3: return "Stage IIIA"
        
    if t_puhdas == "T3" and n_puhdas in ["N1", "N1mi", "N2a", "N2b"]: return "Stage IIIA"
    if t_puhdas == "T3" and n_puhdas == "N0": return "Stage IIB"
        
    if t_puhdas == "T2" and n_puhdas.startswith("N1"): return "Stage IIB"
    
    if t_puhdas in ["T0", "T1", "T1mi", "T1a", "T1b", "T1c"]:
        if n_puhdas == "N1mi": return "Stage IB"
        if n_puhdas.startswith("N1"): return "Stage IIA"
    
    if t_puhdas == "T2" and n_puhdas == "N0": return "Stage IIA"
    if t_puhdas.startswith("T1") and n_puhdas == "N0": return "Stage IA"
    if t_puhdas == "Tis" and n_puhdas == "N0": return "Stage 0"
    
    return "Ei määritettävissä"

def maarita_hoitosuunnitelma_rintasyopa(stage: str, t: str, n: str, m: str, 
                                        er: ReseptoriTila, her2: ReseptoriTila, ki67: Ki67Tila, 
                                        valittu_hoitolinja: Optional[Hoitolinja] = None) -> str:
    if "Stage IV" in stage or "M1" in m:
        return "Levinnyt rintasyöpä: Hoito on palliatiivista. Hoidon valinta perustuu potilaan vointiin ja biologiseen alatyyppiin (ER/HER2)."

    subtype = ""
    if her2 == ReseptoriTila.POSITIIVINEN:
        subtype = "HER2-positiivinen"
        if er == ReseptoriTila.POSITIIVINEN: subtype += " (Luminal B -like)"
        else: subtype += " (Non-Luminal)"
    elif er == ReseptoriTila.POSITIIVINEN:
        if ki67 == Ki67Tila.KORKEA: subtype = "Luminal B -like (HER2-)"
        else: subtype = "Luminal A -like"
    else:
        subtype = "Kolmoisnegatiivinen (TNBC)"
        
    res = f"Biologinen alatyyppi: {subtype}\n"
    
    is_optimal_neoadjuvant = False
    if "Stage III" in stage or ("T3" in t or "T4" in t) or ("N2" in n or "N3" in n):
        is_optimal_neoadjuvant = True
        
    if (subtype == "Kolmoisnegatiivinen (TNBC)" or "HER2-positiivinen" in subtype) and ("T2" in t or "N1" in n):
        is_optimal_neoadjuvant = True

    optimal_setting = "Neoadjuvantti" if is_optimal_neoadjuvant else "Adjuvantti"
    
    setting = optimal_setting
    if valittu_hoitolinja and valittu_hoitolinja in [Hoitolinja.NEOADJUVANTTI, Hoitolinja.ADJUVANTTI]:
        setting = valittu_hoitolinja.value

    res += f"Hoitolinja: {setting}"
    if setting != optimal_setting:
        res += f" (Huom: Optimaalinen suositus olisi {optimal_setting})"
    res += "\n\n"
    
    res += "Lääkehoitosuositus:\n"
    
    if "HER2-positiivinen" in subtype:
        chemo = "Dosetakseli-Syklofosfamidi (D-C) tai T-FEC"
        anti_her2 = "Trastutsumabi"
        if setting == "Neoadjuvantti": 
            chemo = "Dosetakseli-Karboplatiini"
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
            
        res += "• Huom: Harkitse geneettistä neuvontaa (BRCA) ja korkean riskin taudissa adjuvantti-Olaparibia (OlympiA).\n"
            
    elif "Luminal A" in subtype:
        if "N0" in n:
            res += "• Ensisijaisesti hormonihoito (Tamoksifeeni tai AI).\n"
            res += "• Solunsalpaajahoitoa ei rutiinisti suositella, ellei korkea riski (esim. genomitesti).\n"
        else:
            res += "• Hormonihoito (Tamoksifeeni tai AI).\n"
            res += "• Solunsalpaajahoito (esim. D-C x 6 tai EC-Doc) harkinnan mukaan (imusolmukepositiivinen).\n"
            if "N2" in n or "N3" in n or ("N1" in n and ("T3" in t or "T4" in t)):
                res += "• Harkitse abemasisiklibiä adjuvanttina hormonihoidon tukena (MonarchE -kriteerit).\n"
            
    elif "Luminal B" in subtype:
        res += "• Solunsalpaaja: Dosetakseli-Syklofosfamidi (D-C) x 6 tai EC -> Dosetakseli\n"
        res += "• Hormonihoito: Tamoksifeeni tai aromataasinestäjä.\n"
        if "N0" in n or "N1" in n:
            res += "• Solunsalpaajahoidon todellinen hyöty voidaan usein tarkentaa geeniprofiloinnilla (esim. Prosigna / Oncotype).\n"
        if "N2" in n or "N3" in n or ("N1" in n and (ki67 == Ki67Tila.KORKEA or "T3" in t or "T4" in t)):
            res += "• Harkitse abemasisiklibiä adjuvanttina hormonihoidon tukena (MonarchE -kriteerit).\n"

    return res

def laske_stage_suolistosyopa(t: str, n: str, m: str) -> str:
    t_puhdas = pura_luokka(t)
    n_puhdas = pura_luokka(n)
    m_puhdas = pura_luokka(m)

    if m_puhdas.startswith("M1"):
        if m_puhdas == "M1a": return "Stage IVA"
        if m_puhdas == "M1b": return "Stage IVB"
        if m_puhdas == "M1c": return "Stage IVC"
        return "Stage IV"
        
    if n_puhdas.startswith("N1") or n_puhdas.startswith("N2"):
        if t_puhdas == "T4b": return "Stage IIIC"
        if n_puhdas == "N2b": return "Stage IIIC"
        if n_puhdas == "N2a":
            if t_puhdas in ["T4a", "T3"]: return "Stage IIIC" if t_puhdas == "T4a" else "Stage IIIB"
            return "Stage IIIB"
        if n_puhdas.startswith("N1"):
            if t_puhdas in ["T1", "T2"]: return "Stage IIIA"
            if t_puhdas in ["T3", "T4a"]: return "Stage IIIB"
        return "Stage III"

    if n_puhdas == "N0":
        if t_puhdas == "Tis": return "Stage 0"
        if t_puhdas in ["T1", "T2"]: return "Stage I"
        if t_puhdas == "T3": return "Stage IIA"
        if t_puhdas == "T4a": return "Stage IIB"
        if t_puhdas == "T4b": return "Stage IIC"

    return "Ei määritettävissä"

def maarita_hoitosuunnitelma_suolistosyopa(stage: str, t: str, n: str, m: str) -> str:
    if "Stage IV" in stage or "M1" in m:
        return (
            "Levinnyt suolistosyöpä:\n"
            "• Palliatiivinen solunsalpaajahoito (esim. FOLFOX, FOLFIRI, CAPOX) yhdistettynä biologiseen "
            "hoitoon (esim. bevasitsumabi tai panitumumabi/setuksimabi RAS-villityypin taudissa).\n"
            "• Etäpesäkkeiden (esim. maksa/keuhko) kirurginen poisto moniammatillisen harkinnan mukaan."
        )
    
    res = "Lääkehoitosuositus (Adjuvantti):\n"
    if "Stage III" in stage:
        res += "• Adjuvanttisolunsalpaajahoito on indisoitu.\n"
        if "T4" in t or "N2" in n:
            res += "• Korkean riskin Stage III: CAPOX 3-6 kk tai FOLFOX 6 kk ensisijaisena.\n"
        else:
            res += "• Matalan riskin Stage III (T1-3 N1): CAPOX 3 kk (tai FOLFOX 3-6 kk).\n"
        res += "• Yli 70-vuotiailla tai haurailla potilailla voidaan harkita solunsalpaajamonoterapiaa (Kapesitabiini 6 kk).\n"
    elif "Stage II" in stage:
        res += "• Matalan riskin tauti (T3N0M0, ei riskitekijöitä): Usein pelkkä seuranta.\n"
        res += "• Korkean riskin tauti (esim. T4, perforaatio, ileus, <12 tutkittua imusolmuketta): Harkitaan adjuvanttihoitoa (Kapesitabiini 6 kk tai CAPOX 3-6 kk / FOLFOX 6 kk).\n"
    elif "Stage I" in stage or "Stage 0" in stage:
        res += "• Ei adjuvanttisolunsalpaajahoidon indikaatiota. Pelkkä kirurginen poisto ja seuranta.\n"
    else:
        res += "• Suositusta ei voida antaa automaattisesti näillä arvoilla.\n"
        
    return res

def laske_riskiryhma_eturauhassyopa(t: str, n: str, m: str, isup: IsupLuokka, psa: PsaTaso) -> str:
    if "M1" in m: return "Metastasoitunut (Levinnyt)"
    if "N1" in n: return "Paikallisesti levinnyt (Imusolmukepositiivinen)"
    
    # Optimoitu: käytetään suoria 'or' ehtoja genraattorin sijaan välttämään allokaatio-overhead (n. 10x nopeampi)
    t_high = "T2c" in t or "T3" in t or "T4" in t
    isup_high = isup in [IsupLuokka.ISUP_4, IsupLuokka.ISUP_5]
    psa_high = psa == PsaTaso.YLI_20
    
    t_int = "T2b" in t
    isup_int = isup in [IsupLuokka.ISUP_2, IsupLuokka.ISUP_3]
    psa_int = psa == PsaTaso.VALILLA_10_20
    
    if t_high or isup_high or psa_high:
        return "Korkea riski"
    if t_int or isup_int or psa_int:
        return "Kohtalainen riski"
        
    return "Matala riski"

def maarita_hoitosuunnitelma_eturauhassyopa(riski: str, t: str, n: str, m: str) -> str:
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
    t_puhdas = pura_luokka(t)
    n_puhdas = pura_luokka(n)
    m_puhdas = pura_luokka(m)

    if m_puhdas.startswith("M1"): return "Stage IV"
    if n_puhdas.startswith("N1") or n_puhdas.startswith("N2") or n_puhdas.startswith("N3"): return "Stage III"
    if n_puhdas == "N0":
        if t_puhdas == "Tis": return "Stage 0"
        if t_puhdas == "T1a": return "Stage IA"
        if t_puhdas in ["T1b", "T2a"]: return "Stage IB"
        if t_puhdas in ["T2b", "T3a"]: return "Stage IIA"
        if t_puhdas in ["T3b", "T4a"]: return "Stage IIB"
        if t_puhdas == "T4b": return "Stage IIC"
    return "Ei määritettävissä"

def maarita_hoitosuunnitelma_melanooma(stage: str, t: str, n: str, m: str) -> str:
    if "Stage IV" in stage or "M1" in m:
        return (
            "Levinnyt melanooma (Stage IV):\n"
            "• BRAF-mutaatiostatus tulee määrittää.\n"
            "• Immunoterapia (esim. Pembrolitsumabi, Nivolumab tai Ipilimumabi + Nivolumab).\n"
            "• BRAF-positiivisilla potilailla kohdennettu hoito (esim. Dabrafenibi + Trametinibi) on vaihtoehto."
        )
    res = "Lääkehoitosuositus (Adjuvantti):\n"
    if "Stage III" in stage:
        res += "• Adjuvanttilääkehoito on vahvasti indisoitu imusolmukepositiivisessa taudissa.\n"
        res += "• Immunoterapia: Pembrolitsumabi tai Nivolumab 1 vuoden ajan.\n"
        res += "• BRAF-mutaatiopositiivisilla vaihtoehtona kohdennettu hoito (esim. Dabrafenibi + Trametinibi 1 v).\n"
    elif "Stage IIB" in stage or "Stage IIC" in stage:
        res += "• Korkean riskin paikallinen tauti (syvä invaasio / ulseraatio).\n"
        res += "• Harkittavissa adjuvantti-immunoterapia (Nivolumab tai Pembrolitsumabi 1 vuoden ajan).\n"
    elif "Stage 0" in stage or "Stage I" in stage or "Stage IIA" in stage:
        res += "• Ei adjuvanttilääkehoidon indikaatiota. Radikaali kirurginen poisto ja seuranta.\n"
    else:
        res += "• Suositusta ei voida antaa automaattisesti näillä arvoilla.\n"
    return res

def laske_stage_keuhkosyopa(t: str, n: str, m: str) -> str:
    if "M1" in m:
        if "M1c" in m: return "Stage IVB"
        return "Stage IVA"
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
        if "T2" in t: return "Stage IB"
        if "T1c" in t: return "Stage IA3"
        if "T1b" in t: return "Stage IA2"
        if "T1a" in t: return "Stage IA1"
        if "T1" in t: return "Stage IA"
    return "Ei määritettävissä"

def maarita_hoitosuunnitelma_keuhkosyopa(stage: str, t: str, n: str, m: str) -> str:
    if "Stage IV" in stage or "M1" in m:
        return (
            "Levinnyt keuhkosyöpä (Stage IV):\n"
            "• Mutaatiotestaus on kriittinen (EGFR, ALK, ROS1, BRAF, KRAS jne.) sekä PD-L1 -ilmentymä.\n"
            "• Kohdennettu hoito, jos löytyy ajajamutaatio (esim. Osimertinibi tai Alektinibi).\n"
            "• Muuten immunoterapia (esim. Pembrolitsumabi) joko yksin (jos PD-L1 korkea) tai yhdistettynä solunsalpaajahoitoon."
        )
    res = "Lääkehoitosuositus (Paikallinen tai paikallisesti levinnyt tauti):\n"
    if "Stage III" in stage:
        res += "• Stage IIIA (operabeli): Neoadjuvantti immunokemoterapia -> leikkaus (-> adjuvanttihoito harkinnan mukaan).\n"
        res += "• Stage IIIB-IIIC (inoperabeli): Radikaali kemosädehoito, jonka jälkeen ylläpito-immunoterapia (Durvalumabi 1 vuoden ajan).\n"
    elif "Stage II" in stage:
        res += "• Operabelissa taudissa harkitaan vahvasti neoadjuvantti immunokemoterapiaa (esim. solunsalpaaja + Nivolumabi) tai perioperatiivista hoitoa ennen kirurgiaa.\n"
        res += "• Radikaali kirurginen poisto (mikäli ei ensisijaisesti leikattu tai edennyt).\n"
        res += "• Jos ensisijaisesti leikattu ilman esihoitoa, adjuvanttisolunsalpaajahoito on indisoitu.\n"
        res += "• Solunsalpaajan jälkeen harkitaan adjuvantti-immunoterapiaa (Atezolitsumabi) tai täsmähoitoa (Osimertinibi) PD-L1/EGFR-statuksen mukaan.\n"
    elif "Stage IA" in stage or "Stage IB" in stage:
        res += "• Radikaali kirurginen poisto (lobektomia).\n"
        res += "• Adjuvanttihoitoa harkitaan varoen riskitekijöiden (esim. tuumorin koko >4cm tai huono erilaistumisaste) perusteella.\n"
    else:
        res += "• Suositusta ei voida antaa automaattisesti näillä arvoilla.\n"
    return res

def laske_stage_munuaissyopa(t: str, n: str, m: str) -> str:
    t_puhdas = pura_luokka(t)
    n_puhdas = pura_luokka(n)
    m_puhdas = pura_luokka(m)

    if m_puhdas == "M1": return "Stage IV"
    if t_puhdas == "T4": return "Stage IV"
    if n_puhdas == "N1": return "Stage III"
    if t_puhdas.startswith("T3"): return "Stage III"
    if t_puhdas.startswith("T2"): return "Stage II"
    if t_puhdas.startswith("T1"): return "Stage I"
    return "Ei määritettävissä"

def maarita_hoitosuunnitelma_munuaissyopa(stage: str, t: str, n: str, m: str) -> str:
    if "Stage IV" in stage or "M1" in m:
        return (
            "Levinnyt munuaissyöpä:\n"
            "• Hoitolinjaus perustuu IMDC-riskipisteytykseen (suotuisa, kohtalainen, huono).\n"
            "• Ensisijaisena hoitona immunoterapia + TKI -yhdistelmä (esim. Pembrolitsumabi + Aksitinibi tai Nivolumabi + Kabotsantinibi) tai IO+IO (Nivolumabi + Ipilimumabi).\n"
            "• Solunsalpaajahoitoja ei rutiinisti käytetä (munuaissyöpä on niille yleensä resistentti)."
        )
    res = "Lääkehoitosuositus (Paikallinen tauti):\n"
    if "Stage III" in stage or "Stage II" in stage:
        res += "• Ensisijainen hoito on radikaali nefrektomia (tai osapoisto).\n"
        res += "• Korkean uusiutumisriskin taudissa (esim. pT3 tai pN1) voidaan harkita adjuvantti-immunoterapiaa (Pembrolitsumabi 1 vuoden ajan) leikkauksen jälkeen.\n"
    elif "Stage I" in stage:
        res += "• Radikaali leikkaushoito (munuaisen osapoisto suositeltavin T1-taudissa).\n"
        res += "• Adjuvanttihoitoa ei suositella, pelkkä seuranta leikkauksen jälkeen.\n"
    else:
        res += "• Suositusta ei voida antaa automaattisesti näillä arvoilla.\n"
    return res

def laske_stage_haimasyopa(t: str, n: str, m: str) -> str:
    t_puhdas = pura_luokka(t)
    n_puhdas = pura_luokka(n)
    m_puhdas = pura_luokka(m)

    if m_puhdas == "M1": return "Stage IV"
    if t_puhdas == "T4": return "Stage III"
    if n_puhdas == "N2": return "Stage III"
    if n_puhdas == "N1": return "Stage IIB"
    if n_puhdas == "N0":
        if t_puhdas == "T3": return "Stage IIA"
        if t_puhdas == "T2": return "Stage IB"
        if t_puhdas == "T1": return "Stage IA"
        if t_puhdas == "Tis": return "Stage 0"
    return "Ei määritettävissä"

def maarita_hoitosuunnitelma_haimasyopa(stage: str, t: str, n: str, m: str) -> str:
    if "Stage IV" in stage or "M1" in m:
        return (
            "Levinnyt haimasyöpä (Stage IV):\n"
            "• Palliatiivinen lääkehoito hyväkuntoisille (ECOG 0-1) potilaille.\n"
            "• Ensisijaiset solunsalpaajavaihtoehdot: FOLFIRINOX tai Gemssitabiini + Nab-paklitakseli.\n"
            "• Hauraammilla potilailla (ECOG 2) Gemssitabiini-monoterapia."
        )
    res = "Hoitosuositus (Paikallinen tauti):\n"
    if "Stage III" in stage or "T4" in t:
        res += "• Paikallisesti levinnyt / inoperabeli tauti (SMA/keliakia-akseli affisioitu).\n"
        res += "• Usein aloitetaan induktiosolunsalpaajahoidolla (FOLFIRINOX). Jos vaste hyvä, voidaan harkita kemosädehoitoa tai uudelleenarvioida leikkausmahdollisuutta.\n"
    elif "Stage I" in stage or "Stage II" in stage:
        res += "• Operabeli (resektoitava) tauti: Radikaalileikkaus ensisijainen.\n"
        res += "• Borderline resectable -taudissa suositellaan neoadjuvanttihoitoa (esim. FOLFIRINOX) ennen leikkausta.\n"
        res += "• Radikaalileikkauksen (R0/R1) jälkeen adjuvanttisolunsalpaajahoito (mFOLFIRINOX 6 kk, tai vaihtoehtoisesti Gemssitabiini-Kapesitabiini).\n"
    else:
        res += "• Suositusta ei voida antaa automaattisesti näillä arvoilla.\n"
    return res