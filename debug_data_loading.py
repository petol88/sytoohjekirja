import os
import sys
import json

# Mimic the path setup in streamlit_app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.join(current_dir, 'onkohelper')
if package_dir not in sys.path:
    sys.path.append(package_dir)

from oncology_helper.data import Tietokanta

print("Loading data...")
Tietokanta.lataa()
print(f"Data keys: {list(Tietokanta.data.keys())}")
print(f"Data count: {len(Tietokanta.data)}")
