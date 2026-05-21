import timeit

def with_list_comp():
    indikaatiot = set()
    protocols = {f"p_{i}": {"syöpätyypit": ["Rintasyöpä", "Keuhkosyöpä"] if i % 2 == 0 else []} for i in range(110)}
    for prot_data in protocols.values():
        tyypit = prot_data.get('syöpätyypit', [])
        if tyypit:
            for t in tyypit:
                indikaatiot.add(t)
        else:
            indikaatiot.add("Ei määritelty")

    valittu_syopatyyppi = "Rintasyöpä"
    if valittu_syopatyyppi == "Kaikki":
        protokollat = list(protocols.keys())
    elif valittu_syopatyyppi == "Ei määritelty":
        protokollat = [
            nimi for nimi, data in protocols.items()
            if not data.get('syöpätyypit')
        ]
    else:
        protokollat = [
            nimi for nimi, data in protocols.items()
            if valittu_syopatyyppi in data.get('syöpätyypit', [])
        ]
    return protokollat

print("Time: ", timeit.timeit(with_list_comp, number=1000))
