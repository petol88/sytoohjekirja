import timeit
import json

data = {}
try:
    with open("onkohelper/oncology_helper/med_data.json", "r") as f:
        data = json.load(f)
except Exception:
    pass

def old_way():
    indikaatiot = set()
    for prot_data in data.values():
        tyypit = prot_data.get('syöpätyypit', [])
        if tyypit:
            for t in tyypit:
                indikaatiot.add(t)
        else:
            indikaatiot.add("Ei määritelty")

    valittu_syopatyyppi = "Rintasyöpä" # Just an example

    if valittu_syopatyyppi == "Kaikki":
        protokollat = list(data.keys())
    elif valittu_syopatyyppi == "Ei määritelty":
        protokollat = [
            nimi for nimi, data_item in data.items()
            if not data_item.get('syöpätyypit')
        ]
    else:
        protokollat = [
            nimi for nimi, data_item in data.items()
            if valittu_syopatyyppi in data_item.get('syöpätyypit', [])
        ]
    return sorted(list(indikaatiot)), sorted(protokollat)

def precalculate():
    syopatyyppi_opts = set()
    protokolla_map = {"Kaikki": []}
    for nimi, d in data.items():
        protokolla_map["Kaikki"].append(nimi)
        tyypit = d.get('syöpätyypit', [])
        if not tyypit:
            syopatyyppi_opts.add("Ei määritelty")
            if "Ei määritelty" not in protokolla_map:
                protokolla_map["Ei määritelty"] = []
            protokolla_map["Ei määritelty"].append(nimi)
        else:
            for t in tyypit:
                syopatyyppi_opts.add(t)
                if t not in protokolla_map:
                    protokolla_map[t] = []
                protokolla_map[t].append(nimi)

    # Sort them all
    syopatyyppi_opts = tuple(["Kaikki"] + sorted(list(syopatyyppi_opts)))
    for k in protokolla_map:
        protokolla_map[k] = tuple(sorted(protokolla_map[k]))

    return syopatyyppi_opts, protokolla_map

opts, pmap = precalculate()

def new_way():
    valittu_syopatyyppi = "Rintasyöpä"
    return opts, pmap[valittu_syopatyyppi]

print("Old way:", timeit.timeit(old_way, number=1000))
print("New way:", timeit.timeit(new_way, number=1000))
