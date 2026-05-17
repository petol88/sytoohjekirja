import time
import json
import random
from onkohelper.oncology_helper.data import Tietokanta

Tietokanta.lataa()

# Benchmark current inline filtering
def current_filtering(data, valittu_syopatyyppi):
    indikaatiot = set()
    for prot_data in data.values():
        tyypit = prot_data.get('syöpätyypit', [])
        if tyypit:
            for t in tyypit:
                indikaatiot.add(t)
        else:
            indikaatiot.add("Ei määritelty")

    if valittu_syopatyyppi == "Kaikki":
        protokollat = list(data.keys())
    elif valittu_syopatyyppi == "Ei määritelty":
        protokollat = [
            nimi for nimi, data in data.items()
            if not data.get('syöpätyypit')
        ]
    else:
        protokollat = [
            nimi for nimi, data in data.items()
            if valittu_syopatyyppi in data.get('syöpätyypit', [])
        ]
    return protokollat

# Benchmark cached filtering
def pre_calculate(data):
    indikaatiot = set()
    protokolla_map = {"Kaikki": list(data.keys()), "Ei määritelty": []}

    for nimi, prot_data in data.items():
        tyypit = prot_data.get('syöpätyypit', [])
        if tyypit:
            for t in tyypit:
                indikaatiot.add(t)
                if t not in protokolla_map:
                    protokolla_map[t] = []
                protokolla_map[t].append(nimi)
        else:
            indikaatiot.add("Ei määritelty")
            protokolla_map["Ei määritelty"].append(nimi)

    syopatyyppi_opts = ["Kaikki"] + sorted(list(indikaatiot))
    return syopatyyppi_opts, protokolla_map

def optimized_filtering(protokolla_map, valittu_syopatyyppi):
    return protokolla_map.get(valittu_syopatyyppi, [])

# Run benchmark
iterations = 1000
syopatyyppi_opts, protokolla_map = pre_calculate(Tietokanta.data)
valittu = "Rintasyöpä"

start = time.perf_counter()
for _ in range(iterations):
    current_filtering(Tietokanta.data, valittu)
current_time = (time.perf_counter() - start) / iterations * 1000

start = time.perf_counter()
for _ in range(iterations):
    optimized_filtering(protokolla_map, valittu)
opt_time = (time.perf_counter() - start) / iterations * 1000

print(f"Current inline: {current_time:.4f} ms")
print(f"Optimized lookup: {opt_time:.4f} ms")
