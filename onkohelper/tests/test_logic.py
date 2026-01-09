import unittest
from oncology_helper.logic import laske_bsa, laske_cockcroft_gault, pyorista_tabletit, laske_stage_rintasyopa, suosittele_hoito_rintasyopa, maarita_hoitosuunnitelma_rintasyopa

class TestLogic(unittest.TestCase):
    
    def test_laske_bsa(self):
        # Normal case: 180cm, 80kg -> sqrt(14400/3600) = sqrt(4) = 2.0
        self.assertAlmostEqual(laske_bsa(180, 80), 2.0)
        # Edge cases
        self.assertEqual(laske_bsa(0, 80), 0.0)
        self.assertEqual(laske_bsa(180, 0), 0.0)
        
    def test_laske_cockcroft_gault(self):
        # Man: 50y, 80kg, 100 umol/L
        # Formula: (140-50)*80 / (0.814*100) = 7200 / 81.4 = 88.45...
        gfr_man = laske_cockcroft_gault(50, 80, 100, "Mies")
        self.assertAlmostEqual(gfr_man, 88.45, delta=0.1)
        
        # Woman: 50y, 80kg, 100 umol/L
        # Formula: 88.45... * 0.85 = 75.18...
        gfr_woman = laske_cockcroft_gault(50, 80, 100, "Nainen")
        self.assertAlmostEqual(gfr_woman, 75.18, delta=0.1)
        
        # Invalid krea
        self.assertEqual(laske_cockcroft_gault(50, 80, 0, "Mies"), 0.0)

    def test_pyorista_tabletit(self):
        # Exact
        self.assertEqual(pyorista_tabletit(100, 100), 100)
        # Round up
        self.assertEqual(pyorista_tabletit(90, 50), 100)
        # Round down
        self.assertEqual(pyorista_tabletit(70, 50), 50)
        # Zero strength
        self.assertEqual(pyorista_tabletit(55.5, 0), 55)

    def test_laske_stage_rintasyopa(self):
        # Stage IV
        self.assertEqual(laske_stage_rintasyopa("T1", "N0", "M1"), "Stage IV")
        # Stage 0
        self.assertEqual(laske_stage_rintasyopa("Tis", "N0", "M0"), "Stage 0")
        # Stage IA (T1 N0)
        self.assertEqual(laske_stage_rintasyopa("T1c", "N0", "M0"), "Stage IA")
        # Stage IIB (T3 N0)
        self.assertEqual(laske_stage_rintasyopa("T3", "N0", "M0"), "Stage IIB")
        # Stage IIA (T2 N0)
        self.assertEqual(laske_stage_rintasyopa("T2", "N0", "M0"), "Stage IIA")
        # Stage IIA (T1 N1)
        self.assertEqual(laske_stage_rintasyopa("T1", "N1", "M0"), "Stage IIA")
        # Stage IB (T1 N1mi) - verify correct order of checking N1mi vs N1
        self.assertEqual(laske_stage_rintasyopa("T1c", "N1mi", "M0"), "Stage IB")
        # Unknown
        self.assertEqual(laske_stage_rintasyopa("Tx", "N0", "M0"), "Ei määritettävissä")

    def test_suosittele_hoito_rintasyopa(self):
        # Palliatiivinen
        self.assertIn("Palliatiivinen", suosittele_hoito_rintasyopa("Stage IV", "T1", "N0", "M1"))
        
        # Neoadjuvantti (Stage III or large)
        self.assertIn("neoadjuvantti", suosittele_hoito_rintasyopa("Stage IIIA", "T3", "N1", "M0").lower())
        self.assertIn("neoadjuvantti", suosittele_hoito_rintasyopa("Stage IIB", "T3", "N0", "M0").lower())
        self.assertIn("neoadjuvantti", suosittele_hoito_rintasyopa("Stage IIIA", "T1", "N2", "M0").lower())
        
        # Adjuvantti (Early)
        self.assertIn("adjuvantti", suosittele_hoito_rintasyopa("Stage I", "T1", "N0", "M0").lower())
        self.assertIn("adjuvantti", suosittele_hoito_rintasyopa("Stage IIA", "T2", "N0", "M0").lower())

    def test_maarita_hoitosuunnitelma_rintasyopa(self):
        # TNBC Neoadjuvant (auto)
        res = maarita_hoitosuunnitelma_rintasyopa("Stage IIB", "T2", "N1", "M0", "Negatiivinen", "Negatiivinen", "Korkea")
        self.assertIn("Kolmoisnegatiivinen", res)
        self.assertIn("Hoitolinja: Neoadjuvantti", res)
        self.assertIn("Paklitakseli", res)
        
        # HER2+ Adjuvant (auto, T1N0)
        res = maarita_hoitosuunnitelma_rintasyopa("Stage I", "T1c", "N0", "M0", "Positiivinen", "Positiivinen", "Korkea")
        self.assertIn("HER2-positiivinen", res)
        self.assertIn("Hoitolinja: Adjuvantti", res)
        self.assertIn("Trastutsumabi", res)
        
        # Manual override: TNBC Stage II (Optimal: Neoadjuvant) -> Selected: Adjuvant
        res = maarita_hoitosuunnitelma_rintasyopa("Stage IIB", "T2", "N1", "M0", 
                                                  "Negatiivinen", "Negatiivinen", "Korkea", 
                                                  valittu_hoitolinja="Adjuvantti")
        self.assertIn("Hoitolinja: Adjuvantti", res)
        self.assertIn("Huom: Optimaalinen suositus olisi Neoadjuvantti", res)
        # Should NOT suggest Pembrolizumab (neoadjuvant only usually) or Neoadjuvant regimen
        self.assertIn("Dosetakseli-Syklofosfamidi", res) 
        
        # Luminal A Adjuvant (T1N0)
        res = maarita_hoitosuunnitelma_rintasyopa("Stage I", "T1b", "N0", "M0", "Positiivinen", "Negatiivinen", "Matala")
        self.assertIn("Luminal A", res)
        self.assertIn("hormonihoito", res.lower())

if __name__ == '__main__':
    unittest.main()
