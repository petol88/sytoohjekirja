import tkinter as tk
from tkinter import ttk, messagebox
from oncology_helper.data import Tietokanta
from oncology_helper.calculators import safe_float, laske_bsa, laske_cockcroft_gault, pyorista_tabletit, Sukupuoli, laske_yksiloity_annos

class LaskuriView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.rows = []
        self._skip_update = False
        self.current_bsa = 0.0
        self.current_gfr = 0.0
        
        # Header
        h = ttk.Frame(self)
        h.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(h, text="< Takaisin", command=lambda: controller.show_frame("MainMenu")).pack(side=tk.LEFT)
        ttk.Label(h, text="Sytostaattilaskuri", font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=20)

        # Paned
        paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Top (Inputs)
        top = ttk.Frame(paned)
        paned.add(top, weight=3)
        
        cv = tk.Canvas(top)
        sb = ttk.Scrollbar(top, command=cv.yview)
        scroll = ttk.Frame(cv)
        scroll.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0), window=scroll, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        
        self.build_inputs(scroll)
        
        # Bottom (Output)
        bot = ttk.Frame(paned)
        paned.add(bot, weight=1)
        self.txt = tk.Text(bot, height=10, font=("Consolas", 10))
        self.txt.pack(side="left", fill="both", expand=True)
        sb2 = ttk.Scrollbar(bot, orient="vertical", command=self.txt.yview)
        sb2.pack(side="right", fill="y")
        self.txt['yscrollcommand'] = sb2.set
        
        # Button bar
        btn_bar = ttk.Frame(self)
        btn_bar.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Button(btn_bar, text="Kopioi leikepöydälle", command=self.kopioi).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_bar, text="Tyhjennä", command=self.tyhjenna).pack(side=tk.LEFT, padx=5)

    def validate_float(self, event):
        entry = event.widget
        try:
            val = float(entry.get().replace(",", "."))
            entry.config(foreground="black")
        except ValueError:
            if entry.get().strip() == "":
                entry.config(foreground="black")
            else:
                entry.config(foreground="red")

    def build_inputs(self, p):
        f1 = ttk.LabelFrame(p, text="Potilas", padding=10)
        f1.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Label(f1, text="Pituus (cm):").grid(row=0, column=0)
        self.e_len = ttk.Entry(f1, width=8)
        self.e_len.grid(row=0, column=1, padx=5)
        self.e_len.bind("<KeyRelease>", self.validate_float)
        
        ttk.Label(f1, text="Paino (kg):").grid(row=0, column=2)
        self.e_wei = ttk.Entry(f1, width=8)
        self.e_wei.grid(row=0, column=3, padx=5)
        self.e_wei.bind("<KeyRelease>", self.validate_float)
        
        ttk.Label(f1, text="Ikä:").grid(row=1, column=0)
        self.e_age = ttk.Entry(f1, width=8)
        self.e_age.grid(row=1, column=1, padx=5)
        self.e_age.bind("<KeyRelease>", self.validate_float)
        
        ttk.Label(f1, text="Krea:").grid(row=2, column=0)
        self.e_krea = ttk.Entry(f1, width=8)
        self.e_krea.grid(row=2, column=1, padx=5)
        self.e_krea.bind("<KeyRelease>", self.validate_float)
        
        self.v_sex = tk.StringVar(value="Mies")
        ttk.OptionMenu(f1, self.v_sex, "Mies", "Mies", "Nainen").grid(row=1, column=3, padx=5)
        
        self.l_bsa = ttk.Label(f1, text="BSA: -", font=("Arial", 9, "bold"))
        self.l_bsa.grid(row=0, column=4, padx=15)
        self.l_gfr = ttk.Label(f1, text="GFR: -", font=("Arial", 9, "bold"))
        self.l_gfr.grid(row=2, column=4, padx=15)
        
        self.v_cap_bsa = tk.BooleanVar(value=False)
        cb_cap = ttk.Checkbutton(f1, text="Max 2.2 m²", variable=self.v_cap_bsa, command=self.laske)
        cb_cap.grid(row=0, column=5, padx=5)

        f_prot = ttk.Frame(p)
        f_prot.grid(row=1, column=0, sticky="ew", pady=(10, 2), padx=5)
        
        ttk.Label(f_prot, text="Protokolla:").grid(row=0, column=0, sticky="w")
        self.c_prot = ttk.Combobox(f_prot, values=list(Tietokanta.data.keys()), state="readonly", width=40)
        self.c_prot.grid(row=1, column=0, sticky="w", padx=(0, 20))
        self.c_prot.bind("<<ComboboxSelected>>", self.update_meds)
        
        ttk.Label(f_prot, text="Rajaa syöpätyypillä:").grid(row=0, column=1, sticky="w")
        
        syopatyypit = set()
        for d in Tietokanta.data.values():
            for st in d.get("syöpätyypit", []):
                syopatyypit.add(st)
        type_values = ["Kaikki"] + sorted(list(syopatyypit))
        
        self.c_type = ttk.Combobox(f_prot, values=type_values, state="readonly", width=25)
        self.c_type.grid(row=1, column=1, sticky="w")
        self.c_type.set("Kaikki")
        self.c_type.bind("<<ComboboxSelected>>", self.filter_protocols)
        
        ttk.Label(f_prot, text="Annoksen suhteutus:").grid(row=0, column=2, sticky="w", padx=10)
        self.v_suhde = tk.StringVar(value="100 %")
        self.c_suhde = ttk.Combobox(f_prot, textvariable=self.v_suhde, 
                                    values=["100 %", "80 %", "75 %", "50 %", "25 %"], 
                                    state="readonly", width=15)
        self.c_suhde.grid(row=1, column=2, sticky="w", padx=10)

        f2 = ttk.Frame(p)
        f2.grid(row=2, column=0, sticky="ew", pady=10)
        
        self.e_labs = ttk.Entry(f2, width=50)
        self.e_labs.grid(row=1, column=1, padx=5)
        
        ttk.Button(f2, text="LASKE", command=self.laske).grid(row=0, column=2, rowspan=2, padx=10)
        
        self.f_meds = ttk.LabelFrame(p, text="Lääkkeet", padding=5)
        self.f_meds.grid(row=3, column=0, sticky="nsew", pady=5)

    def filter_protocols(self, event=None):
        selected_type = self.c_type.get()
        if selected_type == "Kaikki" or not selected_type:
            filtered = list(Tietokanta.data.keys())
        else:
            filtered = [k for k, v in Tietokanta.data.items() if selected_type in v.get("syöpätyypit", [])]
        
        self.c_prot['values'] = filtered
        if self.c_prot.get() not in filtered:
            self.c_prot.set('')
            self.update_meds()

    def update_meds(self, e=None):
        for w in self.f_meds.winfo_children(): w.destroy()
        self.rows.clear()
        sel = self.c_prot.get()
        if not sel: return
        
        d = Tietokanta.data[sel]
        self.e_labs.delete(0, tk.END)
        self.e_labs.insert(0, d.get('kontrollit', ''))
        
        cols = ["Lääke", "Annos", "Yks.", "Vahvuus", "Tulos", "Määräys"]
        for i, c in enumerate(cols): 
            ttk.Label(self.f_meds, text=c, font=("Arial", 8, "bold")).grid(row=0, column=i)
        
        for i, m in enumerate(d['lääkkeet']):
            r = i+1
            ttk.Label(self.f_meds, text=m['nimi']).grid(row=r, column=0, sticky="w")
            
            v_a = tk.StringVar(value=str(m['annos']))
            ttk.Entry(self.f_meds, textvariable=v_a, width=6).grid(row=r, column=1)
            
            v_u = tk.StringVar(value=m.get('yksikkö', 'mg/m2'))
            ttk.Combobox(self.f_meds, textvariable=v_u, values=["mg/m2", "mg/kg", "AUC", "mg"], width=8).grid(row=r, column=2)
            
            v_t = tk.StringVar()
            if "tablettikoot" in m:
                cb = ttk.Combobox(self.f_meds, textvariable=v_t, values=m["tablettikoot"], width=8)
                cb.current(0)
                cb.grid(row=r, column=3)
            else: 
                v_t.set(None)
            
            l_res = ttk.Label(self.f_meds, text="-")
            l_res.grid(row=r, column=4)
            
            v_fin = tk.StringVar()
            e_fin = ttk.Entry(self.f_meds, textvariable=v_fin, width=8, font=("Arial",9,"bold"))
            e_fin.grid(row=r, column=5)
            
            # Update report when value changes (calculated or manual)
            v_fin.trace_add("write", lambda *args: self.paivita_raportti())
            
            self.rows.append({"n":m['nimi'], "va":v_a, "vu":v_u, "vt":v_t, "lr":l_res, "v_fin":v_fin, "ef":e_fin, "d":m})

    def laske(self):
        p = safe_float(self.e_len.get())
        w = safe_float(self.e_wei.get())
        
        if p > 220.0:
            p = 220.0
            self.e_len.delete(0, tk.END)
            self.e_len.insert(0, "220")
            
        if w > 150.0:
            w = 150.0
            self.e_wei.delete(0, tk.END)
            self.e_wei.insert(0, "150")

        cap = 2.2 if self.v_cap_bsa.get() else None
        bsa = laske_bsa(p, w, cap)
        self.current_bsa = bsa
        self.l_bsa.config(text=f"BSA: {bsa:.2f}")
        
        gfr = laske_cockcroft_gault(safe_float(self.e_age.get()), w, safe_float(self.e_krea.get()), Sukupuoli(self.v_sex.get()))
        self.current_gfr = gfr
        self.l_gfr.config(text=f"GFR: {gfr:.0f}")
        
        suhde_str = self.v_suhde.get().replace("%", "").strip()
        try:
            suhde = float(suhde_str) / 100.0
        except ValueError:
            suhde = 1.0

        self._skip_update = True
        try:
            for r in self.rows:
                a = safe_float(r['va'].get())
                u = r['vu'].get()

                mg = laske_yksiloity_annos(a, u, bsa, w, gfr)
                mg = mg * suhde
                
                # Tarkistetaan mahdollinen maksimiannos (esim. Vinkristiini max 2.0 mg)
                max_mg = r['d'].get('max_mg')
                if max_mg is not None and mg > max_mg:
                    mg = max_mg

                r['lr'].config(text=f"{mg:.0f}")
                fin = int(round(mg))

                ts = r['vt'].get()
                if ts and ts != "None":
                    try:
                        # Extract strength from string like "40 mg"
                        strength = float(ts.split()[0])
                        fin = pyorista_tabletit(mg, strength)
                    except:
                        pass

                # This triggers the trace, so paivita_raportti is called automatically
                r['v_fin'].set(str(fin))
        finally:
            self._skip_update = False
            
        # Explicit update after the loop
        self.paivita_raportti()

    def paivita_raportti(self):
        if self._skip_update:
            return
        sel = self.c_prot.get()
        out = [f"PROTOKOLLA: {sel}"]
        
        if sel in Tietokanta.data:
            d = Tietokanta.data[sel]
            if "sykli" in d:
                out.append(f"Sykli: {d['sykli']}")
                
        if self.v_suhde.get() != "100 %":
            out.append(f"Annoksen suhteutus: {self.v_suhde.get()}")
        
        out.append(f"Labrat: {self.e_labs.get()}")
        out.append("-" * 40)
        
        if self.current_gfr > 0 and self.current_gfr < 60:
            out.append(f"⚠️ HUOMIO: GFR on alentunut ({self.current_gfr:.0f} ml/min).")
            out.append(f"  Harkitse annospudotusta munuaisteitse erittyville lääkkeille!\n")
            
        if self.v_cap_bsa.get() and self.current_bsa == 2.2:
            out.append(f"HUOM: BSA on rajoitettu maksimiarvoon 2.2 m².\n")
        
        for r in self.rows:
            # Read from StringVar to capture manual edits
            fin_str = r['v_fin'].get()
            fin = safe_float(fin_str)
            
            paivat = r['d'].get('päivät')
            paivat_str = ""
            if paivat:
                formatted_paivat = ", ".join(map(str, paivat))
                if isinstance(paivat[0], int) or str(paivat[0]).isdigit():
                    paivat_str = f" [pv {formatted_paivat}]"
                else:
                    paivat_str = f" [{formatted_paivat}]"
                    
            yksikko_raw = r['vu'].get()
            lisamaare = ""
            if " " in yksikko_raw:
                lisamaare = " " + yksikko_raw.split(" ", 1)[1]
                
            reitti = r['d'].get('reitti', '')
            reitti_str = f" {reitti}" if reitti else ""
            
            out.append(f"• {r['n']}{reitti_str} {fin_str} mg{lisamaare}{paivat_str}")
            
            ts = r['vt'].get()
            if ts and ts != "None" and fin > 0:
                try: 
                    strength = float(ts.split()[0])
                    out.append(f"    -> {fin/strength:.1f} kpl ({ts})")
                except: 
                    pass

        if sel:
            d = Tietokanta.data[sel]
            out.append("-" * 40)
            out.append(f"TUKIHOIDOT:\n{d.get('esilääkitys', '-')}")
            
        self.txt.delete("1.0", tk.END)
        self.txt.insert(tk.END, "\n".join(out))

    def kopioi(self):
        self.clipboard_clear()
        self.clipboard_append(self.txt.get("1.0", tk.END))
        messagebox.showinfo("OK", "Kopioitu.")

    def tyhjenna(self):
        for e in [self.e_len, self.e_wei, self.e_age, self.e_krea, self.e_labs]:
            e.delete(0, tk.END)
            e.config(foreground="black")
        self.v_sex.set("Mies")
        self.c_type.set("Kaikki")
        self.filter_protocols()
        self.v_cap_bsa.set(False)
        self.v_suhde.set("100 %")
        self.c_prot.set("")
        self.l_bsa.config(text="BSA: -")
        self.l_gfr.config(text="GFR: -")
        self.txt.delete("1.0", tk.END)
        for w in self.f_meds.winfo_children():
            w.destroy()
        self.rows.clear()
