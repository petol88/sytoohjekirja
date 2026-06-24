import runpy
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
runpy.run_path("onkohelper/streamlit_app.py")
