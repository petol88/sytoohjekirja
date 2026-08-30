import pytest
from oncology_helper.calculators import (
    laske_bsa, 
    laske_calvert, 
    laske_cockcroft_gault, 
    laske_yksiloity_annos,
    Sukupuoli,
    hae_flipi_riskiryhma
)

def test_laske_bsa():
    # Tunnettu potilas: 175 cm, 70 kg -> BSA n. 1.84
    bsa = laske_bsa(175, 70)
    assert round(bsa, 2) == 1.84

    # Testaa maksimikatto
    bsa_capped = laske_bsa(200, 150, max_bsa=2.2)
    assert bsa_capped == 2.2

    # Nolla-arvot ja virheelliset syötteet
    assert laske_bsa(0, 70) == 0.0
    assert laske_bsa(175, 0) == 0.0

def test_laske_calvert():
    # AUC 5, GFR 100 -> Annos = 5 * (100 + 25) = 625
    annos = laske_calvert(5, 100)
    assert annos == 625.0

    # Testaa GFR:n maksimikatto (oletus 125)
    # Vaikka potilaan GFR olisi 150, laskennassa käytetään arvoa 125: 5 * (125 + 25) = 750
    annos_capped = laske_calvert(5, 150)
    assert annos_capped == 750.0

def test_laske_cockcroft_gault():
    # Mies, 50v, 80kg, krea 100 umol/L -> n. 88.45
    gfr_mies = laske_cockcroft_gault(50, 80, 100, Sukupuoli.MIES)
    assert round(gfr_mies, 2) == 88.45

    # Nainen, 50v, 80kg, krea 100 umol/L -> n. 75.18 (kertoimella 0.85)
    gfr_nainen = laske_cockcroft_gault(50, 80, 100, Sukupuoli.NAINEN)
    assert round(gfr_nainen, 2) == 75.18

    # Edge cases
    # Nolla-ikä (ei välttämättä realistinen potilaalla, mutta laskenta sallii)
    gfr_0_vuotias = laske_cockcroft_gault(0, 80, 100, Sukupuoli.MIES)
    assert round(gfr_0_vuotias, 2) == 137.59

    # Nollapaino
    gfr_nolla_paino = laske_cockcroft_gault(50, 0, 100, Sukupuoli.MIES)
    assert gfr_nolla_paino == 0.0

def test_laske_yksiloity_annos():
    # Varmistetaan, että yksikön mukainen reititys toimii oikein
    assert laske_yksiloity_annos(100, "mg/m2", bsa=2.0, paino=80, gfr=100) == 200.0
    assert laske_yksiloity_annos(5, "mg/kg", bsa=2.0, paino=80, gfr=100) == 400.0
    assert laske_yksiloity_annos(5, "AUC", bsa=2.0, paino=80, gfr=100) == 625.0
    # Kiinteä annos
    assert laske_yksiloity_annos(50, "mg (kiinteä)", bsa=2.0, paino=80, gfr=100) == 50.0

def test_hae_flipi_riskiryhma():
    # Matala riski (0-1 p)
    assert hae_flipi_riskiryhma(0) == "Matala riski (0-1 p) - 5-vuoden elossaoloennuste n. 91 % (10-vuoden n. 71 %)"
    assert hae_flipi_riskiryhma(1) == "Matala riski (0-1 p) - 5-vuoden elossaoloennuste n. 91 % (10-vuoden n. 71 %)"
    assert hae_flipi_riskiryhma(-1) == "Matala riski (0-1 p) - 5-vuoden elossaoloennuste n. 91 % (10-vuoden n. 71 %)"

    # Kohtalainen riski (2 p)
    assert hae_flipi_riskiryhma(2) == "Kohtalainen riski (2 p) - 5-vuoden elossaoloennuste n. 78 % (10-vuoden n. 51 %)"

    # Korkea riski (3-5 p)
    assert hae_flipi_riskiryhma(3) == "Korkea riski (3-5 p) - 5-vuoden elossaoloennuste n. 53 % (10-vuoden n. 36 %)"
    assert hae_flipi_riskiryhma(4) == "Korkea riski (3-5 p) - 5-vuoden elossaoloennuste n. 53 % (10-vuoden n. 36 %)"
    assert hae_flipi_riskiryhma(5) == "Korkea riski (3-5 p) - 5-vuoden elossaoloennuste n. 53 % (10-vuoden n. 36 %)"
    assert hae_flipi_riskiryhma(10) == "Korkea riski (3-5 p) - 5-vuoden elossaoloennuste n. 53 % (10-vuoden n. 36 %)"