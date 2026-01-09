import tkinter as tk
from tkinter import ttk
from oncology_helper.data import TNM_DATA
from oncology_helper.logic import laske_stage_rintasyopa, suosittele_hoito_rintasyopa, maarita_hoitosuunnitelma_rintasyopa

class LevinneisyysView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        h = ttk.Frame(self)
        h.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(h, text="< Takaisin", 
                   command=lambda: controller.show_frame("MainMenu")).pack(side=tk.LEFT)
        ttk.Label(h, text="Levinneisyys & Luokitus", 
                  font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=20)
        
        c = ttk.LabelFrame(self, text="Määritys", padding=15)
        c.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tauti valinta
        sf = ttk.Frame(c)
        sf.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(sf, text="Syöpätyyppi:", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        self.v_tauti = tk.StringVar()
        self.cb_tauti = ttk.Combobox(sf, textvariable=self.v_tauti, 
                                     values=list(TNM_DATA.keys()), 
                                     state="readonly", width=30)
        self.cb_tauti.pack(side=tk.LEFT, padx=10)
        self.cb_tauti.bind("<<ComboboxSelected>>", self.update_opts)

        ttk.Label(sf, text="Hoitolinja:", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(20, 0))
        self.v_hoito = tk.StringVar()
        self.cb_hoito = ttk.Combobox(sf, textvariable=self.v_hoito, 
                                     values=["-", "Neoadjuvantti", "Adjuvantti"], 
                                     state="readonly", width=20)
        self.cb_hoito.pack(side=tk.LEFT, padx=10)
        self.cb_hoito.current(0)
        self.cb_hoito.bind("<<ComboboxSelected>>", self.calc_res)

        # Rintasyöpä spesifit valinnat (Visible only for Breast Cancer)
        self.f_rinta = ttk.LabelFrame(c, text="Rintasyövän biologiset tekijät", padding=10)
        # We pack it later dynamically

        rf = self.f_rinta
        ttk.Label(rf, text="ER Status:").grid(row=0, column=0, padx=5, sticky="e")
        self.v_er = tk.StringVar(value="Positiivinen")
        self.cb_er = ttk.Combobox(rf, textvariable=self.v_er, values=["Positiivinen", "Negatiivinen"], state="readonly", width=15)
        self.cb_er.grid(row=0, column=1, padx=5, sticky="w")
        self.cb_er.bind("<<ComboboxSelected>>", self.calc_res)

        ttk.Label(rf, text="HER2 Status:").grid(row=1, column=0, padx=5, sticky="e")
        self.v_her2 = tk.StringVar(value="Negatiivinen")
        self.cb_her2 = ttk.Combobox(rf, textvariable=self.v_her2, values=["Positiivinen", "Negatiivinen"], state="readonly", width=15)
        self.cb_her2.grid(row=1, column=1, padx=5, sticky="w")
        self.cb_her2.bind("<<ComboboxSelected>>", self.calc_res)
        
        ttk.Label(rf, text="Ki-67:").grid(row=2, column=0, padx=5, sticky="e")
        self.v_ki67 = tk.StringVar(value="Matala (<20%)")
        self.cb_ki67 = ttk.Combobox(rf, textvariable=self.v_ki67, values=["Matala (<20%)", "Korkea (>=20%)"], state="readonly", width=15)
        self.cb_ki67.grid(row=2, column=1, padx=5, sticky="w")
        self.cb_ki67.bind("<<ComboboxSelected>>", self.calc_res)

        # Grid (Dynamic labels)
        gf = ttk.Frame(c)
        gf.pack(anchor="w", pady=10, fill=tk.X)
        
        self.labels = []
        self.combos = []
        self.vars = []
        
        for i in range(3):
            lbl = ttk.Label(gf, text=f"Arvo {i+1}:", font=("Arial", 10, "bold"))
            lbl.grid(row=i, column=0, padx=5, pady=10, sticky="e")
            self.labels.append(lbl)
            
            var = tk.StringVar()
            cb = ttk.Combobox(gf, textvariable=var, state="readonly", width=80)
            cb.grid(row=i, column=1, padx=5, sticky="w")
            cb.bind("<<ComboboxSelected>>", self.calc_res)
            self.combos.append(cb)
            self.vars.append(var)
        
        ttk.Label(c, text="Lausunto:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(20, 5))
        self.txt = tk.Text(c, height=10, width=50, font=("Consolas", 11))
        self.txt.pack(fill=tk.BOTH, expand=True)

    def update_opts(self, e=None):
        t = self.v_tauti.get()
        if not t: return
        d = TNM_DATA[t]
        
        # Toggle Breast Cancer specific frame
        if t == "Rintasyöpä":
            self.f_rinta.pack(after=self.cb_hoito.master, fill=tk.X, pady=10)
        else:
            self.f_rinta.pack_forget()

        # Päivitä labelit ja listat
        self.labels[0].config(text=f"{d['L1_Label']}:")
        self.combos[0]['values'] = d['L1']
        
        self.labels[1].config(text=f"{d['L2_Label']}:")
        self.combos[1]['values'] = d['L2']
        
        self.labels[2].config(text=f"{d['L3_Label']}:")
        self.combos[2]['values'] = d['L3']
        
        for c in self.combos: c.set('')
        self.txt.delete("1.0", tk.END)

    def calc_res(self, e=None):
        tauti = self.v_tauti.get()
        v1 = self.vars[0].get()
        v2 = self.vars[1].get()
        v3 = self.vars[2].get()
        
        c1 = v1.split(":")[0] if v1 else "?"
        c2 = v2.split(":")[0] if v2 else "?"
        c3 = v3.split(":")[0] if v3 else "?"
        
        d = TNM_DATA[tauti]
        res = f"Diagnoosi: {tauti}\n"
        
        if d['Type'] == "AnnArbor":
            # Ann Arbor Logiikka
            # c1 = Stage (I, II, III, IV)
            # c2 = Oireet (A, B)
            # c3 = Extra (E, S, X)
            stage_base = c1
            symptoms = c2 if c2 in ["A", "B"] else ""
            modifiers = c3 if c3 not in ["-", "?"] else ""
            
            full_stage = f"{stage_base}{symptoms}"
            if modifiers: full_stage += f" {modifiers}"
            
            res += f"Ann Arbor levinneisyys: {full_stage}\n"
            res += "-"*40 + "\n"
            if v1: res += f"• Levinneisyys: {v1}\n"
            if v2: res += f"• Oireet: {v2}\n"
            if v3 and c3 != "-": res += f"• Lisämääre: {v3}\n"
            
        else:
            # TNM Logiikka
            res += f"Levinneisyys (cTNM): {c1}{c2}{c3}"
            if tauti == "Rintasyöpä" and "?" not in (c1, c2, c3):
                st = laske_stage_rintasyopa(c1, c2, c3)
                res += f"\nAnatominen levinneisyysryhmä: {st}"
                
                # Full treatment plan
                plan = maarita_hoitosuunnitelma_rintasyopa(
                    st, c1, c2, c3, 
                    self.v_er.get(), self.v_her2.get(), self.v_ki67.get(),
                    self.v_hoito.get()
                )
                res += f"\n\n--- HOITOSUUNNITELMA ---\n{plan}"
                
            res += "\n" + "-"*40 + "\n"
            if v1: res += f"• {d['L1_Label']}: {v1}\n"
            if v2: res += f"• {d['L2_Label']}: {v2}\n"
            if v3: res += f"• {d['L3_Label']}: {v3}\n"

        self.txt.delete("1.0", tk.END)
        self.txt.insert(tk.END, res)
