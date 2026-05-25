import timeit
from onkohelper.oncology_helper.calculators import hae_ecog_kuvaus, EcogLuokka

def bench():
    for luokka in EcogLuokka:
        hae_ecog_kuvaus(luokka)

if __name__ == '__main__':
    baseline_time = timeit.timeit("bench()", globals=globals(), number=100000)
    print(f"Baseline: {baseline_time:.4f} seconds")
