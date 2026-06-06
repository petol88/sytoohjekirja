import tkinter as tk
from tkinter import ttk
from oncology_helper.toxicity import HAITTAVAIKUTUKSET, ANNOSTASOT

class ToxicityView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        h = ttk.Frame(self)
        h.pack(fill="x", pady=10)
        ttk.Button(h, text="< Takaisin valikkoon", command=lambda: self.controller.show_frame("MainMenu")).pack(side="left", padx=10)
        ttk.Label(h, text="HAITTAVAIKUTUSTEN HALLINTA", font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)
        
        # Main content
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Selectors
        sel_frame = ttk.Frame(main_frame)
        sel_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(sel_frame, text="Valitse lääkeaine:").pack(side="left")
        self.laake_var = tk.StringVar()
        self.laake_cb = ttk.Combobox(sel_frame, textvariable=self.laake_var, state="readonly", values=sorted(list(HAITTAVAIKUTUKSET.keys())), width=25)
        self.laake_cb.pack(side="left", padx=(5, 20))
        self.laake_cb.bind("<<ComboboxSelected>>", self.on_laake_select)
        
        ttk.Label(sel_frame, text="Valitse haitta:").pack(side="left")
        self.haitta_var = tk.StringVar()
        self.haitta_cb = ttk.Combobox(sel_frame, textvariable=self.haitta_var, state="readonly", width=45)
        self.haitta_cb.pack(side="left", padx=5)
        self.haitta_cb.bind("<<ComboboxSelected>>", self.on_haitta_select)
        
        # Output
        self.text_widget = tk.Text(main_frame, font=("Segoe UI", 11), wrap="word", padx=10, pady=10)
        self.text_widget.pack(fill="both", expand=True)
        
    def on_laake_select(self, event=None):
        laake = self.laake_var.get()
        if laake:
            haitat = sorted(list(HAITTAVAIKUTUKSET[laake].keys()))
            self.haitta_cb.config(values=haitat)
            self.haitta_var.set("")
            self.text_widget.delete("1.0", tk.END)
            
            if laake in ANNOSTASOT:
                self.text_widget.insert(tk.END, self._format_annostasot(laake))
            
    def on_haitta_select(self, event=None):
        laake = self.laake_var.get()
        haitta = self.haitta_var.get()
        self.text_widget.delete("1.0", tk.END)
        
        if laake:
            out = ""
            if laake in ANNOSTASOT:
                out += self._format_annostasot(laake)
                
            if haitta:
                ohjeet = HAITTAVAIKUTUKSET[laake][haitta]
                out += f"TOIMENPIDEOHJEET:\n{laake} – {haitta}\n"
                out += "=" * 60 + "\n\n"
                
                for gradus, ohje in ohjeet.items():
                    out += f"[{gradus}]\n{ohje}\n\n"
                    
            self.text_widget.insert(tk.END, out)
            
    def _format_annostasot(self, laake):
        tasot = ANNOSTASOT.get(laake, {})
        if not tasot: return ""
        out = f"ANNOSTASOT ({laake}):\n"
        out += "=" * 60 + "\n"
        for k, v in tasot.items():
            out += f"• {k}: {v}\n"
        out += "\n"
        return out