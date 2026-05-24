import time
from oncology_helper.data import Tietokanta

def inline_calc():
    indikaatiot = set()
    for prot_data in Tietokanta.data.values():
        tyypit = prot_data.get('syöpätyypit', [])
        if tyypit:
            for t in tyypit:
                indikaatiot.add(t)
        else:
            indikaatiot.add("Ei määritelty")

    syopatyyppi_opts = ["Kaikki"] + sorted(list(indikaatiot))

    valittu_syopatyyppi = "Kaikki"

    if valittu_syopatyyppi == "Kaikki":
        protokollat = list(Tietokanta.data.keys())
    elif valittu_syopatyyppi == "Ei määritelty":
        protokollat = [
            nimi for nimi, data in Tietokanta.data.items()
            if not data.get('syöpätyypit')
        ]
    else:
        protokollat = [
            nimi for nimi, data in Tietokanta.data.items()
            if valittu_syopatyyppi in data.get('syöpätyypit', [])
        ]

    return syopatyyppi_opts, protokollat

Tietokanta.lataa()

# Multiply data for benchmarking
Tietokanta.data = {f"{k}_{i}": v for i in range(100) for k, v in Tietokanta.data.items()}

start = time.perf_counter()
for _ in range(1000):
    inline_calc()
end = time.perf_counter()

print(f"Inline calculation time (1000 iter): {end - start:.5f} s")

def precalc():
    syopatyyppi_set = set()
    protokolla_map = {"Kaikki": list(Tietokanta.data.keys()), "Ei määritelty": []}

    for nimi, prot_data in Tietokanta.data.items():
        tyypit = prot_data.get('syöpätyypit', [])
        if not tyypit:
            syopatyyppi_set.add("Ei määritelty")
            protokolla_map["Ei määritelty"].append(nimi)
        else:
            for t in tyypit:
                syopatyyppi_set.add(t)
                if t not in protokolla_map:
                    protokolla_map[t] = []
                protokolla_map[t].append(nimi)

    syopatyyppi_opts = ["Kaikki"] + sorted(list(syopatyyppi_set))
    for k in protokolla_map:
        protokolla_map[k].sort()

    return syopatyyppi_opts, protokolla_map

syopatyyppi_opts, protokolla_map = precalc()

start = time.perf_counter()
for _ in range(1000):
    valittu_syopatyyppi = "Kaikki"
    protokollat = protokolla_map[valittu_syopatyyppi]
end = time.perf_counter()

print(f"Lookup time (1000 iter): {end - start:.5f} s")
