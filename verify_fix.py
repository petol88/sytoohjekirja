import sys
import os

# Add onkohelper to sys.path
sys.path.append(os.path.join(os.getcwd(), 'onkohelper'))

from oncology_helper.logic import safe_float, pyorista_tabletit

def test_safe_float():
    print("Testing safe_float...")
    assert safe_float(None) == 0.0
    assert safe_float("") == 0.0
    assert safe_float("abc") == 0.0
    assert safe_float("12,5") == 12.5
    assert safe_float(10) == 10.0
    print("safe_float tests passed!")

def test_tablet_logic_simulation():
    print("Testing tablet logic simulation...")

    # Simulate logic in LaskuriView.laske
    def simulate_laske(mg, ts):
        fin = int(round(mg))
        if ts and ts != "None":
            try:
                strength = float(ts.split()[0])
                fin = pyorista_tabletit(mg, strength)
            except (ValueError, IndexError):
                pass
        return fin

    assert simulate_laske(100, "40 mg") == 80 # Rounding to nearest 40
    assert simulate_laske(100, "invalid") == 100 # Should ignore and return original
    assert simulate_laske(100, "") == 100
    assert simulate_laske(100, None) == 100

    # Simulate logic in LaskuriView.paivita_raportti
    def simulate_paivita_raportti(fin, ts):
        results = []
        if ts and ts != "None" and fin > 0:
            try:
                strength = float(ts.split()[0])
                results.append(f"{fin/strength:.1f} kpl")
            except (ValueError, IndexError, ZeroDivisionError):
                pass
        return results

    assert simulate_paivita_raportti(100, "40 mg") == ["2.5 kpl"]
    assert simulate_paivita_raportti(100, "0 mg") == [] # ZeroDivisionError caught
    assert simulate_paivita_raportti(100, "invalid") == [] # ValueError/IndexError caught
    assert simulate_paivita_raportti(100, " ") == [] # IndexError caught

    print("Tablet logic simulation passed!")

if __name__ == "__main__":
    try:
        test_safe_float()
        test_tablet_logic_simulation()
        print("\nAll verifications passed!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        sys.exit(1)
