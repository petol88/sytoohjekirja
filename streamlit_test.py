from streamlit_app import *

print("Load data tests:")
print("Data loaded:", "Docetaxel" in Tietokanta.data)
print("Syopatyyppi opts:", SYOPATYYPPI_OPTS)
print("Syopa to protokollat Kaikki:", SYOPA_TO_PROTOKOLLAT.get("Kaikki", []))
