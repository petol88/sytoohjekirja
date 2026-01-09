import sys
import os
import tkinter as tk
from tkinter import ttk

# Add parent directory to path if running directly to allow absolute imports
# This must be done BEFORE importing from the package
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oncology_helper.data import Tietokanta
from oncology_helper.ui.main_menu import MainMenu
from oncology_helper.ui.calculator_view import LaskuriView
# from oncology_helper.ui.staging_view import LevinneisyysView

# High DPI support for Windows
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Onkologian Työpöytä v2.3")
        self.geometry("1050x900")
        
        # Load Data
        Tietokanta.lataa()
        
        # Container
        c = ttk.Frame(self)
        c.pack(fill="both", expand=True)
        c.grid_rowconfigure(0, weight=1)
        c.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (MainMenu, LaskuriView):
            self.frames[F.__name__] = F(c, self)
            self.frames[F.__name__].grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("MainMenu")

    def show_frame(self, n):
        self.frames[n].tkraise()

if __name__ == "__main__":
    MainApp().mainloop()
