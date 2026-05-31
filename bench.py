import time
import json
from onkohelper.oncology_helper.data import Tietokanta

Tietokanta.lataa()
data = Tietokanta.data

def inline_method():
    indikaatiot = set()
    for prot_data in data.values():
        tyypit = prot_data.get('syöpätyypit', [])
        if tyypit:
            for t in tyypit:
                indikaatiot.add(t)
        else:
            indikaatiot.add("Ei määritelty")

    valittu_syopatyyppi = "Kaikki" # or something else

    if valittu_syopatyyppi == "Kaikki":
        protokollat = list(data.keys())
    elif valittu_syopatyyppi == "Ei määritelty":
        protokollat = [
            nimi for nimi, d in data.items()
            if not d.get('syöpätyypit')
        ]
    else:
        protokollat = [
            nimi for nimi, d in data.items()
            if valittu_syopatyyppi in d.get('syöpätyypit', [])
        ]

def precalculated_method():
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

    syopatyyppi_opts = ("Kaikki",) + tuple(sorted(list(indikaatiot)))
    for k in protokolla_map:
        protokolla_map[k] = tuple(sorted(protokolla_map[k]))

    return syopatyyppi_opts, protokolla_map

opts, pmap = precalculated_method()

def precalculated_access():
    valittu = "Kaikki"
    protokollat = pmap[valittu]

n = 10000

t0 = time.time()
for _ in range(n):
    inline_method()
t1 = time.time()

t2 = time.time()
for _ in range(n):
    precalculated_access()
t3 = time.time()

print(f"Inline: {(t1-t0)/n*1000:.4f} ms")
print(f"Precalculated: {(t3-t2)/n*1000:.4f} ms")
