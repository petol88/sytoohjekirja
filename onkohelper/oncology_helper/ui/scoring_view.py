import tkinter as tk
from tkinter import ttk

from oncology_helper.calculators import EcogLuokka, hae_ecog_kuvaus, laske_ipi_pisteet, hae_ipi_riskiryhma, laske_cns_ipi_pisteet, hae_cns_ipi_riskiryhma, laske_mipi_pisteet, hae_mipi_riskiryhma, safe_float

class PisteytyksetView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        h = ttk.Frame(self)
        h.pack(fill="x", pady=10)
        ttk.Button(h, text="< Takaisin valikkoon", command=lambda: self.controller.show_frame("MainMenu")).pack(side="left", padx=10)
        ttk.Label(h, text="LÄÄKETIETEELLISET PISTEYTYKSET", font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)
        
        # Main layout
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side: Select calculator
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side="left", fill="y", padx=(0, 20))
        left_frame.pack_propagate(False) # Prevent shrinking
        
        ttk.Label(left_frame, text="Valitse laskuri:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # We will use a Listbox for selection
        self.laskuri_listbox = tk.Listbox(left_frame, font=("Segoe UI", 11), height=20, selectmode=tk.SINGLE)
        self.laskuri_listbox.pack(fill="both", expand=True)
        
        laskurit = ["ECOG-suorituskyky", "IPI (International Prognostic Index)", "CNS-IPI (CNS International Prognostic Index)", "MIPI (Mantle Cell Lymphoma International Prognostic Index)"]
        for item in laskurit:
            self.laskuri_listbox.insert(tk.END, item)
            
        self.laskuri_listbox.bind('<<ListboxSelect>>', self.on_laskuri_select)
        
        # Right side: Calculator Content
        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side="left", fill="both", expand=True)
        
        # Container to hold the dynamic content
        self.content_frame = ttk.Frame(self.right_frame)
        self.content_frame.pack(fill="both", expand=True)
        
        # Select first item by default
        self.laskuri_listbox.selection_set(0)
        self.on_laskuri_select(None)
        
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def on_laskuri_select(self, event):
        selection = self.laskuri_listbox.curselection()
        if not selection:
            return
            
        valittu = self.laskuri_listbox.get(selection[0])
        self.clear_content()
        
        if valittu == "ECOG-suorituskyky":
            self.build_ecog_view()
        elif valittu == "IPI (International Prognostic Index)":
            self.build_ipi_view()
        elif valittu == "CNS-IPI (CNS International Prognostic Index)":
            self.build_cns_ipi_view()
        elif valittu == "MIPI (Mantle Cell Lymphoma International Prognostic Index)":
            self.build_mipi_view()
            
    def build_ecog_view(self):
        ttk.Label(self.content_frame, text="ECOG (Eastern Cooperative Oncology Group)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi potilaan toimintakykyä ja päivittäisistä toiminnoista suoriutumista.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        # Variable to hold the selected radio button value
        self.ecog_var = tk.IntVar(value=-1) # -1 means no selection
        
        # Frame for radio buttons
        radio_frame = ttk.Frame(self.content_frame)
        radio_frame.pack(anchor="w", fill="x")
        
        # Result frame
        self.result_frame = ttk.Frame(self.content_frame)
        self.result_frame.pack(anchor="w", fill="x", pady=20)
        self.result_label = ttk.Label(self.result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.result_label.pack(anchor="w")
        self.warning_label = ttk.Label(self.result_frame, text="", font=("Segoe UI", 11), foreground="red")
        self.warning_label.pack(anchor="w", pady=(5, 0))
        
        def on_ecog_change():
            arvo = self.ecog_var.get()
            self.result_label.config(text=f"Tulos: Potilaan suorituskyky on ECOG {arvo}.")
            if arvo >= 3:
                self.warning_label.config(text="Huom: ECOG 3 tai huonompi on usein vasta-aihe raskaalle solunsalpaajahoidolle.")
            else:
                self.warning_label.config(text="")

        for luokka in EcogLuokka:
            kuvaus = hae_ecog_kuvaus(luokka)
            arvo = luokka.value
            teksti = f"ECOG {arvo}: {kuvaus}"
            
            # Using tk.Radiobutton for better text wrapping support compared to ttk.Radiobutton
            rb = tk.Radiobutton(
                radio_frame, 
                text=teksti, 
                variable=self.ecog_var, 
                value=arvo,
                command=on_ecog_change,
                font=("Segoe UI", 11),
                wraplength=600, # Wrap text if it's too long
                justify="left"
            )
            rb.pack(anchor="w", pady=5)

    def build_ipi_view(self):
        ttk.Label(self.content_frame, text="IPI (International Prognostic Index)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi diffuusin suurisoluisen B-solulymfooman (DLBCL) ennustetta.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        self.ipi_ika_var = tk.BooleanVar(value=False)
        self.ipi_ldh_var = tk.BooleanVar(value=False)
        self.ipi_ecog_var = tk.BooleanVar(value=False)
        self.ipi_stage_var = tk.BooleanVar(value=False)
        self.ipi_en_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(input_frame, text="Ikä > 60 vuotta", variable=self.ipi_ika_var, command=self.laske_ipi).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="LDH koholla (> viitealueen yläraja)", variable=self.ipi_ldh_var, command=self.laske_ipi).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="ECOG-suorituskyky ≥ 2", variable=self.ipi_ecog_var, command=self.laske_ipi).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Ann Arbor Stage III tai IV", variable=self.ipi_stage_var, command=self.laske_ipi).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Yli 1 ekstranodaalinen pesäke", variable=self.ipi_en_var, command=self.laske_ipi).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
        
        self.ipi_result_frame = ttk.Frame(self.content_frame)
        self.ipi_result_frame.pack(anchor="w", fill="x", pady=20)
        self.ipi_result_label = ttk.Label(self.ipi_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.ipi_result_label.pack(anchor="w")
        self.ipi_risk_label = ttk.Label(self.ipi_result_frame, text="", font=("Segoe UI", 11))
        self.ipi_risk_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_ipi()

    def laske_ipi(self):
        pisteet = laske_ipi_pisteet(self.ipi_ika_var.get(), self.ipi_ldh_var.get(), self.ipi_ecog_var.get(), self.ipi_stage_var.get(), self.ipi_en_var.get())
        riskiryhma = hae_ipi_riskiryhma(pisteet)
        
        self.ipi_result_label.config(text=f"Tulos: IPI-pisteet: {pisteet} / 5")
        self.ipi_risk_label.config(text=f"Riskiryhmä: {riskiryhma}")

    def build_cns_ipi_view(self):
        ttk.Label(self.content_frame, text="CNS-IPI (CNS International Prognostic Index)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi keskushermostorelapssin riskiä diffuusissa suurisoluisessa B-solulymfoomassa (DLBCL).", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        self.cns_ika_var = tk.BooleanVar(value=False)
        self.cns_ldh_var = tk.BooleanVar(value=False)
        self.cns_ecog_var = tk.BooleanVar(value=False)
        self.cns_stage_var = tk.BooleanVar(value=False)
        self.cns_en_var = tk.BooleanVar(value=False)
        self.cns_kidney_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(input_frame, text="Ikä > 60 vuotta", variable=self.cns_ika_var, command=self.laske_cns_ipi).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="LDH koholla (> viitealueen yläraja)", variable=self.cns_ldh_var, command=self.laske_cns_ipi).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="ECOG-suorituskyky ≥ 2", variable=self.cns_ecog_var, command=self.laske_cns_ipi).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Ann Arbor Stage III tai IV", variable=self.cns_stage_var, command=self.laske_cns_ipi).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Yli 1 ekstranodaalinen pesäke", variable=self.cns_en_var, command=self.laske_cns_ipi).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Munuaisten ja/tai lisämunuaisten affisio", variable=self.cns_kidney_var, command=self.laske_cns_ipi).grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
        
        self.cns_result_frame = ttk.Frame(self.content_frame)
        self.cns_result_frame.pack(anchor="w", fill="x", pady=20)
        self.cns_result_label = ttk.Label(self.cns_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.cns_result_label.pack(anchor="w")
        self.cns_risk_label = ttk.Label(self.cns_result_frame, text="", font=("Segoe UI", 11))
        self.cns_risk_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_cns_ipi()

    def laske_cns_ipi(self):
        pisteet = laske_cns_ipi_pisteet(self.cns_ika_var.get(), self.cns_ldh_var.get(), self.cns_ecog_var.get(), self.cns_stage_var.get(), self.cns_en_var.get(), self.cns_kidney_var.get())
        riskiryhma = hae_cns_ipi_riskiryhma(pisteet)
        
        self.cns_result_label.config(text=f"Tulos: CNS-IPI-pisteet: {pisteet} / 6")
        self.cns_risk_label.config(text=f"Riskiryhmä: {riskiryhma}")

    def build_mipi_view(self):
        ttk.Label(self.content_frame, text="MIPI (Mantle Cell Lymphoma International Prognostic Index)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi manttelisolulymfooman ennustetta (yksinkertaistettu sMIPI).", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        self.mipi_ika_var = tk.StringVar(value="60")
        self.mipi_ecog_var = tk.StringVar(value="0")
        self.mipi_ldh_var = tk.StringVar(value="1.0")
        self.mipi_wbc_var = tk.StringVar(value="5.0")
        
        # Päivitetään tulokset automaattisesti
        self.mipi_ika_var.trace_add("write", lambda *args: self.laske_mipi())
        self.mipi_ecog_var.trace_add("write", lambda *args: self.laske_mipi())
        self.mipi_ldh_var.trace_add("write", lambda *args: self.laske_mipi())
        self.mipi_wbc_var.trace_add("write", lambda *args: self.laske_mipi())
        
        ttk.Label(input_frame, text="Ikä (vuotta):").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.mipi_ika_var, width=10).grid(row=0, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Label(input_frame, text="ECOG-suorituskyky:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Combobox(input_frame, textvariable=self.mipi_ecog_var, values=[str(i) for i in range(5)], width=8, state="readonly").grid(row=1, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Label(input_frame, text="LDH / viitealueen yläraja (suhdeluku esim. 1.5):").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.mipi_ldh_var, width=10).grid(row=2, column=1, sticky="w", pady=5, padx=5)
        
        ttk.Label(input_frame, text="Leukosyytit (WBC, E9/l):").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(input_frame, textvariable=self.mipi_wbc_var, width=10).grid(row=3, column=1, sticky="w", pady=5, padx=5)
        
        self.mipi_result_frame = ttk.Frame(self.content_frame)
        self.mipi_result_frame.pack(anchor="w", fill="x", pady=20)
        self.mipi_result_label = ttk.Label(self.mipi_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.mipi_result_label.pack(anchor="w")
        self.mipi_risk_label = ttk.Label(self.mipi_result_frame, text="", font=("Segoe UI", 11))
        self.mipi_risk_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_mipi()

    def laske_mipi(self):
        try: ika = int(self.mipi_ika_var.get())
        except ValueError: ika = 0
            
        try: ecog = int(self.mipi_ecog_var.get())
        except ValueError: ecog = 0
            
        ldh = safe_float(self.mipi_ldh_var.get())
        wbc = safe_float(self.mipi_wbc_var.get())
            
        pisteet = laske_mipi_pisteet(ika, ecog, ldh, wbc)
        riskiryhma = hae_mipi_riskiryhma(pisteet)
        
        self.mipi_result_label.config(text=f"Tulos: sMIPI-pisteet: {pisteet}")
        self.mipi_risk_label.config(text=f"Riskiryhmä: {riskiryhma}")
