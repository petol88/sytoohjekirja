import time
from onkohelper.oncology_helper.data import Tietokanta

Tietokanta.lataa()
data = Tietokanta.data

# Original way
start = time.perf_counter()
for _ in range(1000):
    indikaatiot = set()
    for prot_data in data.values():
        tyypit = prot_data.get('syöpätyypit', [])
        if tyypit:
            for t in tyypit:
                indikaatiot.add(t)
        else:
            indikaatiot.add("Ei määritelty")

    syopatyyppi_opts = ["Kaikki"] + sorted(list(indikaatiot))

    # filter for all, ei määritelty, and one specific
    protokollat_kaikki = list(data.keys())
    protokollat_ei_maar = [
        nimi for nimi, d in data.items()
        if not d.get('syöpätyypit')
    ]
    protokollat_spec = [
        nimi for nimi, d in data.items()
        if "Rintasyöpä" in d.get('syöpätyypit', [])
    ]
end = time.perf_counter()
print(f"Original inline filtering: {(end - start) / 1000 * 1000:.4f} ms per iteration")

# Setup for Optimized way
def pre_calculate(data):
    indikaatiot = set()
    pmap = {"Kaikki": list(data.keys()), "Ei määritelty": []}

    for nimi, d in data.items():
        tyypit = d.get('syöpätyypit', [])
        if not tyypit:
            indikaatiot.add("Ei määritelty")
            pmap["Ei määritelty"].append(nimi)
        else:
            for t in tyypit:
                indikaatiot.add(t)
                if t not in pmap:
                    pmap[t] = []
                pmap[t].append(nimi)

    opts = ("Kaikki",) + tuple(sorted(list(indikaatiot)))
    # convert pmap lists to tuples for even faster use
    for k in pmap:
        pmap[k] = tuple(sorted(pmap[k]))

    return opts, pmap

syopatyyppi_opts, pmap = pre_calculate(data)

# Optimized way (during render)
start = time.perf_counter()
for _ in range(1000):
    # Instead of calculating, we just lookup
    opts = syopatyyppi_opts
    protokollat_kaikki = pmap["Kaikki"]
    protokollat_ei_maar = pmap.get("Ei määritelty", ())
    protokollat_spec = pmap.get("Rintasyöpä", ())

end = time.perf_counter()
print(f"Optimized lookup filtering: {(end - start) / 1000 * 1000:.4f} ms per iteration")
