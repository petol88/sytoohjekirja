import re

with open('streamlit_app.py', 'r') as f:
    content = f.read()

# Fix the fallback tuple typo
old_ui = """        # 2. Haetaan valmiiksi lajitellut protokollat valitun syöpätyypin perusteella
        protokollat_opts = PROTOKOLLAT_MAP.get(valittu_syopatyyppi, (""))"""

new_ui = """        # 2. Haetaan valmiiksi lajitellut protokollat valitun syöpätyypin perusteella
        protokollat_opts = PROTOKOLLAT_MAP.get(valittu_syopatyyppi, ("",))"""

content = content.replace(old_ui, new_ui)

# Fix the potential NameError
old_exception = """try:
    # Always update Tietokanta.data with cached/loaded data and get pre-calculated UI options
    _data, SYOPATYYPPI_OPTS, PROTOKOLLAT_MAP = load_data()
    Tietokanta.data = _data
except Exception as e:
    st.error(f"Virhe ladattaessa tietokantaa: {e}")"""

new_exception = """SYOPATYYPPI_OPTS = ("Kaikki",)
PROTOKOLLAT_MAP = {}

try:
    # Always update Tietokanta.data with cached/loaded data and get pre-calculated UI options
    _data, SYOPATYYPPI_OPTS, PROTOKOLLAT_MAP = load_data()
    Tietokanta.data = _data
except Exception as e:
    st.error(f"Virhe ladattaessa tietokantaa: {e}")"""

content = content.replace(old_exception, new_exception)

with open('streamlit_app.py', 'w') as f:
    f.write(content)
