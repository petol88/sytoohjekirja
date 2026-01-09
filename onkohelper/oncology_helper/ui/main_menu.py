import tkinter as tk
from tkinter import ttk

class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        c = ttk.Frame(self)
        c.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(c, text="Onkologian Työpöytä", font=("Segoe UI", 24, "bold")).pack(pady=40)
        
        ttk.Button(c, text="LÄÄKELASKURI", 
                   command=lambda: controller.show_frame("LaskuriView"), 
                   width=30).pack(pady=10)
