import tkinter as tk
from tkinter import ttk
from oncology_helper.toxicity import IO_HAITTAVAIKUTUKSET, _IO_HAITTAVAIKUTUKSET_OIREET

class IOToxicityView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        h = ttk.Frame(self)
        h.pack(fill="x", pady=10)
        ttk.Button(h, text="< Takaisin valikkoon", command=lambda: self.controller.show_frame("MainMenu")).pack(side="left", padx=10)
        ttk.Label(h, text="IO-HAITTOJEN HOITO", font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)
        
        # Main content
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Selectors
        sel_frame = ttk.Frame(main_frame)
        sel_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(sel_frame, text="Valitse IO-haittavaikutus:").pack(side="left")
        self.haitta_var = tk.StringVar()
        self.haitta_cb = ttk.Combobox(sel_frame, textvariable=self.haitta_var, state="readonly", values=_IO_HAITTAVAIKUTUKSET_OIREET, width=45)
        self.haitta_cb.pack(side="left", padx=10)
        self.haitta_cb.bind("<<ComboboxSelected>>", self.on_haitta_select)
        
        # Output
        self.text_widget = tk.Text(main_frame, font=("Segoe UI", 11), wrap="word", padx=10, pady=10)
        self.text_widget.pack(fill="both", expand=True)
        
    def on_haitta_select(self, event=None):
        haitta = self.haitta_var.get()
        self.text_widget.delete("1.0", tk.END)
        
        if haitta:
            ohjeet = IO_HAITTAVAIKUTUKSET[haitta]
            out = f"TOIMENPIDEOHJEET: {haitta}\n"
            out += "=" * 60 + "\n\n"
            
            for gradus, ohje in ohjeet.items():
                out += f"[{gradus}]\n{ohje}\n\n"
                
            self.text_widget.insert(tk.END, out)