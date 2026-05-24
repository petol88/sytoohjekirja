import tkinter as tk
from tkinter import ttk

from oncology_helper.calculators import EcogLuokka, hae_ecog_kuvaus, laske_ipi_pisteet, hae_ipi_riskiryhma, laske_cns_ipi_pisteet, hae_cns_ipi_riskiryhma, laske_mipi_pisteet, hae_mipi_riskiryhma, laske_flipi_pisteet, hae_flipi_riskiryhma, tarkista_gelf_kriteerit, hae_gelf_suositus, laske_cps_eg_pisteet, hae_cps_eg_ennuste, safe_float

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
        
        laskurit = ["ECOG-suorituskyky", "IPI (International Prognostic Index)", "CNS-IPI (CNS International Prognostic Index)", "MIPI (Mantle Cell Lymphoma International Prognostic Index)", "FLIPI (Follicular Lymphoma International Prognostic Index)", "GELF-kriteerit (Follikulaarisen lymfooman hoidon aloitus)", "CPS+EG (Rintasyövän neoadjuvanttihoidon jälkeinen ennuste)"]
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
        elif valittu == "FLIPI (Follicular Lymphoma International Prognostic Index)":
            self.build_flipi_view()
        elif valittu == "GELF-kriteerit (Follikulaarisen lymfooman hoidon aloitus)":
            self.build_gelf_view()
        elif valittu == "CPS+EG (Rintasyövän neoadjuvanttihoidon jälkeinen ennuste)":
            self.build_cps_eg_view()
            
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
        
        self.mipi_ika_var = tk.IntVar(value=0)
        self.mipi_ecog_var = tk.IntVar(value=0)
        self.mipi_ldh_var = tk.IntVar(value=0)
        self.mipi_wbc_var = tk.IntVar(value=0)
        
        col1_frame = ttk.Frame(input_frame)
        col1_frame.grid(row=0, column=0, sticky="nw", padx=(0, 40))
        col2_frame = ttk.Frame(input_frame)
        col2_frame.grid(row=0, column=1, sticky="nw")
        
        ttk.Label(col1_frame, text="Ikä (vuotta):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5,2))
        ttk.Radiobutton(col1_frame, text="< 50 (0 p)", variable=self.mipi_ika_var, value=0, command=self.laske_mipi).pack(anchor="w")
        ttk.Radiobutton(col1_frame, text="50 - 59 (1 p)", variable=self.mipi_ika_var, value=1, command=self.laske_mipi).pack(anchor="w")
        ttk.Radiobutton(col1_frame, text="60 - 69 (2 p)", variable=self.mipi_ika_var, value=2, command=self.laske_mipi).pack(anchor="w")
        ttk.Radiobutton(col1_frame, text="≥ 70 (3 p)", variable=self.mipi_ika_var, value=3, command=self.laske_mipi).pack(anchor="w")
        
        ttk.Label(col1_frame, text="ECOG-suorituskyky:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15,2))
        ttk.Radiobutton(col1_frame, text="0 - 1 (0 p)", variable=self.mipi_ecog_var, value=0, command=self.laske_mipi).pack(anchor="w")
        ttk.Radiobutton(col1_frame, text="≥ 2 (1 p)", variable=self.mipi_ecog_var, value=1, command=self.laske_mipi).pack(anchor="w")
        
        ttk.Label(col2_frame, text="LDH / viitealueen yläraja:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5,2))
        ttk.Radiobutton(col2_frame, text="< 0.67 (0 p)", variable=self.mipi_ldh_var, value=0, command=self.laske_mipi).pack(anchor="w")
        ttk.Radiobutton(col2_frame, text="0.67 - 0.99 (1 p)", variable=self.mipi_ldh_var, value=1, command=self.laske_mipi).pack(anchor="w")
        ttk.Radiobutton(col2_frame, text="1.00 - 1.49 (2 p)", variable=self.mipi_ldh_var, value=2, command=self.laske_mipi).pack(anchor="w")
        ttk.Radiobutton(col2_frame, text="≥ 1.50 (3 p)", variable=self.mipi_ldh_var, value=3, command=self.laske_mipi).pack(anchor="w")
        
        ttk.Label(col2_frame, text="Leukosyytit (WBC, E9/l):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15,2))
        ttk.Radiobutton(col2_frame, text="< 6.7 (0 p)", variable=self.mipi_wbc_var, value=0, command=self.laske_mipi).pack(anchor="w")
        ttk.Radiobutton(col2_frame, text="6.7 - 9.9 (1 p)", variable=self.mipi_wbc_var, value=1, command=self.laske_mipi).pack(anchor="w")
        ttk.Radiobutton(col2_frame, text="10.0 - 14.9 (2 p)", variable=self.mipi_wbc_var, value=2, command=self.laske_mipi).pack(anchor="w")
        ttk.Radiobutton(col2_frame, text="≥ 15.0 (3 p)", variable=self.mipi_wbc_var, value=3, command=self.laske_mipi).pack(anchor="w")
        
        self.mipi_result_frame = ttk.Frame(self.content_frame)
        self.mipi_result_frame.pack(anchor="w", fill="x", pady=20)
        self.mipi_result_label = ttk.Label(self.mipi_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.mipi_result_label.pack(anchor="w")
        self.mipi_risk_label = ttk.Label(self.mipi_result_frame, text="", font=("Segoe UI", 11))
        self.mipi_risk_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_mipi()

    def laske_mipi(self):
        pisteet = laske_mipi_pisteet(self.mipi_ika_var.get(), self.mipi_ecog_var.get(), self.mipi_ldh_var.get(), self.mipi_wbc_var.get())
        riskiryhma = hae_mipi_riskiryhma(pisteet)
        
        self.mipi_result_label.config(text=f"Tulos: sMIPI-pisteet: {pisteet}")
        self.mipi_risk_label.config(text=f"Riskiryhmä: {riskiryhma}")

    def build_flipi_view(self):
        ttk.Label(self.content_frame, text="FLIPI (Follicular Lymphoma International Prognostic Index)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi follikulaarisen lymfooman ennustetta.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        self.flipi_ika_var = tk.BooleanVar(value=False)
        self.flipi_stage_var = tk.BooleanVar(value=False)
        self.flipi_hb_var = tk.BooleanVar(value=False)
        self.flipi_nodaali_var = tk.BooleanVar(value=False)
        self.flipi_ldh_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(input_frame, text="Ikä > 60 vuotta", variable=self.flipi_ika_var, command=self.laske_flipi).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Ann Arbor Stage III tai IV", variable=self.flipi_stage_var, command=self.laske_flipi).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Hemoglobiini < 120 g/l", variable=self.flipi_hb_var, command=self.laske_flipi).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Yli 4 nodaalista aluetta", variable=self.flipi_nodaali_var, command=self.laske_flipi).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="LDH koholla (> viitealueen yläraja)", variable=self.flipi_ldh_var, command=self.laske_flipi).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
        
        self.flipi_result_frame = ttk.Frame(self.content_frame)
        self.flipi_result_frame.pack(anchor="w", fill="x", pady=20)
        self.flipi_result_label = ttk.Label(self.flipi_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.flipi_result_label.pack(anchor="w")
        self.flipi_risk_label = ttk.Label(self.flipi_result_frame, text="", font=("Segoe UI", 11))
        self.flipi_risk_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_flipi()

    def laske_flipi(self):
        pisteet = laske_flipi_pisteet(self.flipi_ika_var.get(), self.flipi_stage_var.get(), self.flipi_hb_var.get(), self.flipi_nodaali_var.get(), self.flipi_ldh_var.get())
        riskiryhma = hae_flipi_riskiryhma(pisteet)
        
        self.flipi_result_label.config(text=f"Tulos: FLIPI-pisteet: {pisteet} / 5")
        self.flipi_risk_label.config(text=f"Riskiryhmä: {riskiryhma}")

    def build_gelf_view(self):
        ttk.Label(self.content_frame, text="GELF-kriteerit (Follikulaarinen lymfooma)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi aktiivihoidon indikaatiota follikulaarisessa lymfoomassa (indikaatio jos vähintään 1 täyttyy).", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        self.gelf_bulkki_var = tk.BooleanVar(value=False)
        self.gelf_perna_var = tk.BooleanVar(value=False)
        self.gelf_kompressio_var = tk.BooleanVar(value=False)
        self.gelf_ldh_var = tk.BooleanVar(value=False)
        self.gelf_leukemia_var = tk.BooleanVar(value=False)
        self.gelf_syto_var = tk.BooleanVar(value=False)
        self.gelf_b_oireet_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(input_frame, text="Bulkki > 7 cm tai ≥3 imusolmukealuetta > 3 cm", variable=self.gelf_bulkki_var, command=self.laske_gelf).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Oireinen splenomegalia", variable=self.gelf_perna_var, command=self.laske_gelf).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Elinkompressio, pleura- tai peritoneaalieffuusio", variable=self.gelf_kompressio_var, command=self.laske_gelf).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Kohonnut LDH tai β2-mikroglobuliini", variable=self.gelf_ldh_var, command=self.laske_gelf).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Leukeeminen tauti (lymfosyytit > 5.0 E9/l)", variable=self.gelf_leukemia_var, command=self.laske_gelf).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Sytopeniat (Neut < 1.0 tai Tromb < 100)", variable=self.gelf_syto_var, command=self.laske_gelf).grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="B-oireet", variable=self.gelf_b_oireet_var, command=self.laske_gelf).grid(row=6, column=0, columnspan=2, sticky="w", pady=5)
        
        self.gelf_result_frame = ttk.Frame(self.content_frame)
        self.gelf_result_frame.pack(anchor="w", fill="x", pady=20)
        self.gelf_result_label = ttk.Label(self.gelf_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.gelf_result_label.pack(anchor="w")
        self.gelf_risk_label = ttk.Label(self.gelf_result_frame, text="", font=("Segoe UI", 11))
        self.gelf_risk_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_gelf()

    def laske_gelf(self):
        pisteet = tarkista_gelf_kriteerit(self.gelf_bulkki_var.get(), self.gelf_perna_var.get(), self.gelf_kompressio_var.get(), self.gelf_ldh_var.get(), self.gelf_leukemia_var.get(), self.gelf_syto_var.get(), self.gelf_b_oireet_var.get())
        suositus = hae_gelf_suositus(pisteet)
        
        self.gelf_result_label.config(text=f"Tulos: {pisteet} GELF-kriteeriä täyttyy.")
        self.gelf_risk_label.config(text=f"Suositus: {suositus}")

    def build_cps_eg_view(self):
        ttk.Label(self.content_frame, text="CPS+EG (Rintasyövän neoadjuvanttihoidon jälkeinen ennuste)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi rintasyövän ennustetta neoadjuvanttihoidon ja leikkauksen jälkeen.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        main_row = ttk.Frame(self.content_frame)
        main_row.pack(anchor="w", fill="x")
        
        input_frame = ttk.Frame(main_row)
        input_frame.pack(side="left", anchor="n", fill="y", expand=True)
        
        info_frame = ttk.Frame(main_row)
        info_frame.pack(side="left", anchor="n", padx=(40, 0))
        
        self.cpseg_cstage_var = tk.IntVar(value=0)
        self.cpseg_pstage_var = tk.IntVar(value=0)
        self.cpseg_er_var = tk.BooleanVar(value=False)
        self.cpseg_grade_var = tk.BooleanVar(value=False)
        
        ttk.Label(input_frame, text="Kliininen levinneisyys (cTNM) ennen hoitoa:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5,2))
        ttk.Radiobutton(input_frame, text="Stage I - IIA (0 p)", variable=self.cpseg_cstage_var, value=0, command=self.laske_cps_eg).pack(anchor="w")
        ttk.Radiobutton(input_frame, text="Stage IIB - IIIA (1 p)", variable=self.cpseg_cstage_var, value=1, command=self.laske_cps_eg).pack(anchor="w")
        ttk.Radiobutton(input_frame, text="Stage IIIB - IIIC (2 p)", variable=self.cpseg_cstage_var, value=2, command=self.laske_cps_eg).pack(anchor="w")
        
        ttk.Label(input_frame, text="Patologinen levinneisyys (ypTNM) leikkauksen jälkeen:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15,2))
        ttk.Radiobutton(input_frame, text="Stage 0 tai I (0 p)", variable=self.cpseg_pstage_var, value=0, command=self.laske_cps_eg).pack(anchor="w")
        ttk.Radiobutton(input_frame, text="Stage IIA - IIB (1 p)", variable=self.cpseg_pstage_var, value=1, command=self.laske_cps_eg).pack(anchor="w")
        ttk.Radiobutton(input_frame, text="Stage IIIA - IIIC (2 p)", variable=self.cpseg_pstage_var, value=2, command=self.laske_cps_eg).pack(anchor="w")
        
        ttk.Label(input_frame, text="Muut tekijät:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15,2))
        ttk.Checkbutton(input_frame, text="Estrogeenireseptori (ER) negatiivinen (1 p)", variable=self.cpseg_er_var, command=self.laske_cps_eg).pack(anchor="w", pady=2)
        ttk.Checkbutton(input_frame, text="Gradus 3 (1 p)", variable=self.cpseg_grade_var, command=self.laske_cps_eg).pack(anchor="w", pady=2)
        
        info_lf = ttk.LabelFrame(info_frame, text="Rintasyövän Stage-muistisääntö", padding=10)
        info_lf.pack(anchor="n", fill="both")
        stage_text = (
            "Stage I: T1 N0\n"
            "Stage IIA: T0-T1 N1 tai T2 N0\n"
            "Stage IIB: T2 N1 tai T3 N0\n"
            "Stage IIIA: T0-T2 N2 tai T3 N1-N2\n"
            "Stage IIIB: T4, mikä tahansa N\n"
            "Stage IIIC: Mikä tahansa T, N3\n\n"
            "(T1 ≤2cm, T2 2-5cm, T3 >5cm, T4 iho/rintakehä)\n"
            "(N1: 1-3 kainalo, N2: 4-9 kainalo/sis.rinta, N3: ≥10 kainalo/soliskuoppa)"
        )
        ttk.Label(info_lf, text=stage_text, justify="left", font=("Segoe UI", 10)).pack()
        
        self.cpseg_result_frame = ttk.Frame(self.content_frame)
        self.cpseg_result_frame.pack(anchor="w", fill="x", pady=20)
        self.cpseg_result_label = ttk.Label(self.cpseg_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.cpseg_result_label.pack(anchor="w")
        self.cpseg_risk_label = ttk.Label(self.cpseg_result_frame, text="", font=("Segoe UI", 11))
        self.cpseg_risk_label.pack(anchor="w", pady=(5, 0))
        self.cpseg_warning_label = ttk.Label(self.cpseg_result_frame, text="", font=("Segoe UI", 11), foreground="red")
        self.cpseg_warning_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_cps_eg()

    def laske_cps_eg(self):
        pisteet = laske_cps_eg_pisteet(self.cpseg_cstage_var.get(), self.cpseg_pstage_var.get(), self.cpseg_er_var.get(), self.cpseg_grade_var.get())
        ennuste = hae_cps_eg_ennuste(pisteet)
        
        self.cpseg_result_label.config(text=f"Tulos: CPS+EG -pisteet: {pisteet} / 6")
        self.cpseg_risk_label.config(text=f"Ennuste: {ennuste}")
        
        if pisteet >= 3:
            self.cpseg_warning_label.config(text="Huom: Jos invasiivistä jäännöstautia, niin muista olaparibi-liitännäishoidon\nmahdollisuus ituradan BRCA-mutaation omaavilla vuoden ajaksi.")
        else:
            self.cpseg_warning_label.config(text="")
