import unittest
from oncology_helper.calculators import laske_bsa, laske_cockcroft_gault, pyorista_tabletit, Sukupuoli
from oncology_helper.staging import laske_stage_rintasyopa, maarita_hoitosuunnitelma_rintasyopa, ReseptoriTila, Ki67Tila, Hoitolinja

class TestLogic(unittest.TestCase):
    
    def test_laske_bsa(self):
        self.assertAlmostEqual(laske_bsa(180, 80), 2.0)
        self.assertEqual(laske_bsa(0, 80), 0.0)
        self.assertEqual(laske_bsa(180, 0), 0.0)
        
    def test_laske_cockcroft_gault(self):
        gfr_man = laske_cockcroft_gault(50, 80, 100, Sukupuoli.MIES)
        self.assertAlmostEqual(gfr_man, 88.45, delta=0.1)
        
        gfr_woman = laske_cockcroft_gault(50, 80, 100, Sukupuoli.NAINEN)
        self.assertAlmostEqual(gfr_woman, 75.18, delta=0.1)
        
        self.assertEqual(laske_cockcroft_gault(50, 80, 0, Sukupuoli.MIES), 0.0)

    def test_pyorista_tabletit(self):
        self.assertEqual(pyorista_tabletit(100, 100), 100)
        self.assertEqual(pyorista_tabletit(90, 50), 100)
        self.assertEqual(pyorista_tabletit(70, 50), 50)
        self.assertEqual(pyorista_tabletit(55.5, 0), 55)

    def test_laske_stage_rintasyopa(self):
        self.assertEqual(laske_stage_rintasyopa("T1", "N0", "M1"), "Stage IV")
        self.assertEqual(laske_stage_rintasyopa("Tis", "N0", "M0"), "Stage 0")
        self.assertEqual(laske_stage_rintasyopa("T1c", "N0", "M0"), "Stage IA")
        self.assertEqual(laske_stage_rintasyopa("T3", "N0", "M0"), "Stage IIB")
        self.assertEqual(laske_stage_rintasyopa("T2", "N0", "M0"), "Stage IIA")
        self.assertEqual(laske_stage_rintasyopa("T1", "N1", "M0"), "Stage IIA")
        self.assertEqual(laske_stage_rintasyopa("T1c", "N1mi", "M0"), "Stage IB")
        self.assertEqual(laske_stage_rintasyopa("Tx", "N0", "M0"), "Ei määritettävissä")

    def test_maarita_hoitosuunnitelma_rintasyopa(self):
        res = maarita_hoitosuunnitelma_rintasyopa("Stage IIB", "T2", "N1", "M0", ReseptoriTila.NEGATIIVINEN, ReseptoriTila.NEGATIIVINEN, Ki67Tila.KORKEA)
        self.assertIn("Kolmoisnegatiivinen", res)
        self.assertIn("Hoitolinja: Neoadjuvantti", res)
        self.assertIn("Paklitakseli", res)
        
        res = maarita_hoitosuunnitelma_rintasyopa("Stage I", "T1c", "N0", "M0", ReseptoriTila.POSITIIVINEN, ReseptoriTila.POSITIIVINEN, Ki67Tila.KORKEA)
        self.assertIn("HER2-positiivinen", res)
        self.assertIn("Hoitolinja: Adjuvantti", res)
        self.assertIn("Trastutsumabi", res)
        
        res = maarita_hoitosuunnitelma_rintasyopa("Stage IIB", "T2", "N1", "M0", 
                                                  ReseptoriTila.NEGATIIVINEN, ReseptoriTila.NEGATIIVINEN, Ki67Tila.KORKEA,
                                                  valittu_hoitolinja=Hoitolinja.ADJUVANTTI)
        self.assertIn("Hoitolinja: Adjuvantti", res)
        self.assertIn("Huom: Optimaalinen suositus olisi Neoadjuvantti", res)
        self.assertIn("Dosetakseli-Syklofosfamidi", res) 
        
        res = maarita_hoitosuunnitelma_rintasyopa("Stage I", "T1b", "N0", "M0", ReseptoriTila.POSITIIVINEN, ReseptoriTila.NEGATIIVINEN, Ki67Tila.MATALA)
        self.assertIn("Luminal A", res)
        self.assertIn("hormonihoito", res.lower())

if __name__ == '__main__':
    unittest.main()
