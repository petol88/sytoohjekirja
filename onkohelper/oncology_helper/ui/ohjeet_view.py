import tkinter as tk
from tkinter import ttk
from oncology_helper.guidelines import OHJEET

class OhjeetView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        h = ttk.Frame(self)
        h.pack(fill="x", pady=10)
        ttk.Button(h, text="< Takaisin valikkoon", command=lambda: self.controller.show_frame("MainMenu")).pack(side="left", padx=10)
        ttk.Label(h, text="OHJEET JA PROTOKOLLAT", font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)
        
        # Main layout
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side: Select guideline
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        left_frame.pack_propagate(False)
        
        ttk.Label(left_frame, text="Valitse ohje:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        self.listbox = tk.Listbox(left_frame, font=("Segoe UI", 11), height=20, selectmode=tk.SINGLE)
        self.listbox.pack(fill="both", expand=True)
        
        for item in OHJEET.keys():
            self.listbox.insert(tk.END, item)
            
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # Right side: Content
        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side="left", fill="both", expand=True)
        
        self.text_widget = tk.Text(self.right_frame, font=("Segoe UI", 11), wrap="word", padx=10, pady=10)
        self.text_widget.pack(fill="both", expand=True)
        
    def on_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            valittu = self.listbox.get(selection[0])
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert(tk.END, OHJEET[valittu])