import pytest
from oncology_helper.data import Tietokanta

def test_abraxane_karboplatiini_protocol_exists():
    """
    Verifies that the "Abraxane-Karboplatiini (7vrk)" protocol exists
    and contains the correct data as specified in the request.
    """
    Tietokanta.lataa()
    data = Tietokanta.data
    protocol_name = "Abraxane-Karboplatiini (7vrk)"

    assert protocol_name in data, f"{protocol_name} not found in med_data.json"

    protocol = data[protocol_name]

    assert protocol["sykli"] == "7 vuorokautta"
    assert protocol["kontrollit"] == "PVK, Krea, Alat."
    assert protocol["esilääkitys"] == "Ondansetroni 8mg. Deksametasoni 8mg+tarvittaessa 4mg pv 2 ja 3 PO."

    drugs = protocol["lääkkeet"]
    assert len(drugs) == 2

    # Check first drug: Abraxane
    abraxane = next((d for d in drugs if d["nimi"] == "Abraxane (IV)"), None)
    assert abraxane is not None
    assert abraxane["annos"] == 125
    assert abraxane["yksikkö"] == "mg/m2"
    assert abraxane["päivät"] == "D1"

    # Check second drug: Karboplatiini
    karboplatiini = next((d for d in drugs if d["nimi"] == "Karboplatiini (IV)"), None)
    assert karboplatiini is not None
    assert karboplatiini["annos"] == 1.5
    assert karboplatiini["yksikkö"] == "AUC"
    assert karboplatiini["päivät"] == "D1"

def test_gemsitabiini_abraxane_protocol_exists():
    """
    Verifies that the "Gemsitabiini-Abraxane (21vrk)" protocol exists
    and contains the correct data as specified in the request.
    """
    Tietokanta.lataa()
    data = Tietokanta.data
    protocol_name = "Gemsitabiini-Abraxane (21vrk)"

    assert protocol_name in data, f"{protocol_name} not found in med_data.json"

    protocol = data[protocol_name]

    assert protocol["sykli"] == "21 vuorokautta"
    assert protocol["kontrollit"] == "PVK, Krea, Alat."
    assert protocol["esilääkitys"] == "Ondansetroni 8mg. Deksametasoni 8mg+tarvittaessa 4mg pv 2 ja 3 PO."

    drugs = protocol["lääkkeet"]
    assert len(drugs) == 2

    # Check first drug: Abraxane
    abraxane = next((d for d in drugs if d["nimi"] == "Abraxane (IV)"), None)
    assert abraxane is not None
    assert abraxane["annos"] == 125
    assert abraxane["yksikkö"] == "mg/m2"
    assert abraxane["päivät"] == "D1,D8,D15"

    # Check second drug: Gemsitabiini
    gemsitabiini = next((d for d in drugs if d["nimi"] == "Gemsitabiini (IV)"), None)
    assert gemsitabiini is not None
    assert gemsitabiini["annos"] == 1000
    assert gemsitabiini["yksikkö"] == "mg/m2"
    assert gemsitabiini["päivät"] == "D1, D8, D15"
