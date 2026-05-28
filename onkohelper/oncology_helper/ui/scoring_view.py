import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False

from oncology_helper.calculators import EcogLuokka, hae_ecog_kuvaus, laske_ipi_pisteet, hae_ipi_riskiryhma, laske_cns_ipi_pisteet, hae_cns_ipi_riskiryhma, laske_mipi_pisteet, hae_mipi_riskiryhma, laske_flipi_pisteet, hae_flipi_riskiryhma, tarkista_gelf_kriteerit, hae_gelf_suositus, laske_cps_eg_pisteet, hae_cps_eg_ennuste, laske_ips_pisteet, hae_ips_ennuste, tarkista_hl_paikallinen_riskitekijat, hae_hl_paikallinen_riskiryhma, laske_child_pugh_pisteet, hae_child_pugh_luokka, laske_psadt, hae_psadt_tulkinta, laske_mascc_pisteet, hae_mascc_suositus, laske_qtc, hae_qtc_suositus, laske_antrasykliini_kertyma, laske_bsa, safe_float

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
        
        laskurit = ["ECOG-suorituskyky", "Kertyvä annos (Antrasykliinit)", "QTc-ajan korjauslaskuri (Bazett & Fridericia)", "MASCC-pisteytys (Kuumeinen neutropenia)", "IPI (International Prognostic Index)", "CNS-IPI (CNS International Prognostic Index)", "MIPI (Mantle Cell Lymphoma International Prognostic Index)", "FLIPI (Follicular Lymphoma International Prognostic Index)", "IPS (International Prognostic Score - Hodgkin lymfooma)", "Hodgkin lymfooma - Paikallisen taudin (Stage I-II) riskitekijät", "GELF-kriteerit (Follikulaarisen lymfooman hoidon aloitus)", "CPS+EG (Rintasyövän neoadjuvanttihoidon jälkeinen ennuste)", "Child-Pugh -luokitus (Maksan vajaatoiminta)", "PSA:n kahdentumisaika (PSADT)"]
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
        elif valittu == "Kertyvä annos (Antrasykliinit)":
            self.build_kumulatiivinen_view()
        elif valittu == "QTc-ajan korjauslaskuri (Bazett & Fridericia)":
            self.build_qtc_view()
        elif valittu == "MASCC-pisteytys (Kuumeinen neutropenia)":
            self.build_mascc_view()
        elif valittu == "IPI (International Prognostic Index)":
            self.build_ipi_view()
        elif valittu == "CNS-IPI (CNS International Prognostic Index)":
            self.build_cns_ipi_view()
        elif valittu == "MIPI (Mantle Cell Lymphoma International Prognostic Index)":
            self.build_mipi_view()
        elif valittu == "FLIPI (Follicular Lymphoma International Prognostic Index)":
            self.build_flipi_view()
        elif valittu == "IPS (International Prognostic Score - Hodgkin lymfooma)":
            self.build_ips_view()
        elif valittu == "Hodgkin lymfooma - Paikallisen taudin (Stage I-II) riskitekijät":
            self.build_hl_paikallinen_view()
        elif valittu == "GELF-kriteerit (Follikulaarisen lymfooman hoidon aloitus)":
            self.build_gelf_view()
        elif valittu == "CPS+EG (Rintasyövän neoadjuvanttihoidon jälkeinen ennuste)":
            self.build_cps_eg_view()
        elif valittu == "Child-Pugh -luokitus (Maksan vajaatoiminta)":
            self.build_child_pugh_view()
        elif valittu == "PSA:n kahdentumisaika (PSADT)":
            self.build_psadt_view()
            
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
            
    def build_kumulatiivinen_view(self):
        ttk.Label(self.content_frame, text="Kertyvän annoksen seuranta (Antrasykliinit)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Laskee antrasykliinien kumulatiivisen annoksen doksorubisiini-ekvivalentteina.\nDoksorubisiinin suositeltu elinikäinen maksimiannos on sydäntoksisuuden vuoksi 450–500 mg/m².", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        self.syotto_mode = tk.StringVar(value="mg/m2")
        
        mode_frame = ttk.Frame(self.content_frame)
        mode_frame.pack(anchor="w", fill="x", pady=(0, 10))
        ttk.Label(mode_frame, text="Syötettävien annosten yksikkö:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="mg/m²", variable=self.syotto_mode, value="mg/m2", command=self.toggle_kertyva_mode).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Absoluuttinen (mg)", variable=self.syotto_mode, value="mg", command=self.toggle_kertyva_mode).pack(side="left", padx=5)
        
        self.patient_frame = ttk.LabelFrame(self.content_frame, text="Potilaan tiedot (BSA:n laskentaa varten)", padding=10)
        
        ttk.Label(self.patient_frame, text="Pituus (cm):").grid(row=0, column=0, sticky="w", pady=5)
        self.kertyva_pituus = self.controller.shared_pituus
        ttk.Entry(self.patient_frame, textvariable=self.kertyva_pituus, width=10).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        ttk.Label(self.patient_frame, text="Paino (kg):").grid(row=0, column=2, sticky="w", pady=5, padx=(10,0))
        self.kertyva_paino = self.controller.shared_paino
        ttk.Entry(self.patient_frame, textvariable=self.kertyva_paino, width=10).grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
        self.input_frame = ttk.Frame(self.content_frame)
        self.input_frame.pack(anchor="w", fill="x")
        
        self.lbl_ohje = ttk.Label(self.input_frame, text="Syötä potilaan aiemmin saamat kokonaisannokset (mg/m²):", font=("Segoe UI", 10, "bold"))
        self.lbl_ohje.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        self.lbl_doxo = ttk.Label(self.input_frame, text="Doksorubisiini (mg/m²):")
        self.lbl_doxo.grid(row=1, column=0, sticky="w", pady=5)
        self.doxo_var = tk.StringVar(value="0")
        ttk.Entry(self.input_frame, textvariable=self.doxo_var, width=15).grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        self.lbl_epi = ttk.Label(self.input_frame, text="Epirubisiini (mg/m²):")
        self.lbl_epi.grid(row=2, column=0, sticky="w", pady=5)
        self.epi_var = tk.StringVar(value="0")
        ttk.Entry(self.input_frame, textvariable=self.epi_var, width=15).grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        self.lbl_ida = ttk.Label(self.input_frame, text="Idarubisiini (mg/m²):")
        self.lbl_ida.grid(row=3, column=0, sticky="w", pady=5)
        self.ida_var = tk.StringVar(value="0")
        ttk.Entry(self.input_frame, textvariable=self.ida_var, width=15).grid(row=3, column=1, sticky="w", padx=10, pady=5)
        
        self.lbl_mito = ttk.Label(self.input_frame, text="Mitoksantroni (mg/m²):")
        self.lbl_mito.grid(row=4, column=0, sticky="w", pady=5)
        self.mito_var = tk.StringVar(value="0")
        ttk.Entry(self.input_frame, textvariable=self.mito_var, width=15).grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        ttk.Button(self.content_frame, text="Laske kumulatiivinen annos", command=self.laske_kertyva_action).pack(anchor="w", pady=20)
        
        self.kertyva_result_frame = ttk.Frame(self.content_frame)
        self.kertyva_result_frame.pack(anchor="w", fill="x")
        self.kertyva_result_label = ttk.Label(self.kertyva_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.kertyva_result_label.pack(anchor="w")
        self.kertyva_risk_label = ttk.Label(self.kertyva_result_frame, text="", font=("Segoe UI", 11), wraplength=700)
        self.kertyva_risk_label.pack(anchor="w", pady=(5, 0))
        self.kertyva_warning_label = ttk.Label(self.kertyva_result_frame, text="", font=("Segoe UI", 11, "bold"), foreground="red", wraplength=700)
        self.kertyva_warning_label.pack(anchor="w", pady=(5, 0))
        
    def toggle_kertyva_mode(self):
        if self.syotto_mode.get() == "mg":
            self.patient_frame.pack(before=self.input_frame, anchor="w", fill="x", pady=(0, 10))
            self.lbl_ohje.config(text="Syötä potilaan aiemmin saamat absoluuttiset kokonaisannokset (mg):")
            self.lbl_doxo.config(text="Doksorubisiini (mg):")
            self.lbl_epi.config(text="Epirubisiini (mg):")
            self.lbl_ida.config(text="Idarubisiini (mg):")
            self.lbl_mito.config(text="Mitoksantroni (mg):")
        else:
            self.patient_frame.pack_forget()
            self.lbl_ohje.config(text="Syötä potilaan aiemmin saamat kokonaisannokset (mg/m²):")
            self.lbl_doxo.config(text="Doksorubisiini (mg/m²):")
            self.lbl_epi.config(text="Epirubisiini (mg/m²):")
            self.lbl_ida.config(text="Idarubisiini (mg/m²):")
            self.lbl_mito.config(text="Mitoksantroni (mg/m²):")
        
    def laske_kertyva_action(self):
        doxo = safe_float(self.doxo_var.get())
        epi = safe_float(self.epi_var.get())
        ida = safe_float(self.ida_var.get())
        mito = safe_float(self.mito_var.get())
        
        bsa_text = ""
        if self.syotto_mode.get() == "mg":
            h = safe_float(self.kertyva_pituus.get())
            w = safe_float(self.kertyva_paino.get())
            bsa = laske_bsa(h, w)
            if bsa <= 0:
                self.kertyva_result_label.config(text="Tarkista pituus ja paino!")
                self.kertyva_risk_label.config(text="")
                self.kertyva_warning_label.config(text="")
                return
            doxo = doxo / bsa
            epi = epi / bsa
            ida = ida / bsa
            mito = mito / bsa
            bsa_text = f" (BSA: {bsa:.2f} m²)"

        equiv, remaining, suositus = laske_antrasykliini_kertyma(doxo, epi, ida, mito)
        self.kertyva_result_label.config(text=f"Tulos{bsa_text}: Doksorubisiini-ekvivalentti kertyvä annos on {equiv:.0f} mg/m²")
        
        rem_str = ""
        if remaining > 0:
            rem_str = "\n\nJäljellä oleva annos maksimirajaan (450 mg/m²) eri lääkkeinä:\n"
            if self.syotto_mode.get() == "mg":
                rem_str += f"• Doksorubisiini: {remaining:.0f} mg/m² (n. {remaining * bsa:.0f} mg)\n"
                rem_str += f"• Epirubisiini: {remaining / 0.5:.0f} mg/m² (n. {(remaining / 0.5) * bsa:.0f} mg)\n"
                rem_str += f"• Idarubisiini: {remaining / 3.0:.0f} mg/m² (n. {(remaining / 3.0) * bsa:.0f} mg)\n"
                rem_str += f"• Mitoksantroni: {remaining / 3.0:.0f} mg/m² (n. {(remaining / 3.0) * bsa:.0f} mg)"
            else:
                rem_str += f"• Doksorubisiini: {remaining:.0f} mg/m²\n"
                rem_str += f"• Epirubisiini: {remaining / 0.5:.0f} mg/m²\n"
                rem_str += f"• Idarubisiini: {remaining / 3.0:.0f} mg/m²\n"
                rem_str += f"• Mitoksantroni: {remaining / 3.0:.0f} mg/m²"
                
        if equiv >= 450:
            self.kertyva_risk_label.config(text="")
            self.kertyva_warning_label.config(text=f"⚠️ {suositus}")
        elif equiv >= 300:
            self.kertyva_risk_label.config(text=f"Tulkinta: {suositus}{rem_str}")
            self.kertyva_warning_label.config(text="Huom: Annoskertymä on suuri, huomioi sydäntoksisuuden riski.")
        else:
            self.kertyva_risk_label.config(text=f"Tulkinta: {suositus}{rem_str}")
            self.kertyva_warning_label.config(text="")
            
    def build_qtc_view(self):
        ttk.Label(self.content_frame, text="QTc-ajan korjauslaskuri", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Laskee sykekorjatun QT-ajan (QTc) Bazettin ja Friderician kaavoilla.\nSyöpähoidoissa (esim. TK-estäjät) suositellaan usein Friderician kaavaa.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        ttk.Label(input_frame, text="Sähkökardiogrammin QT-aika (ms):", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.qt_var = tk.StringVar(value="400")
        ttk.Entry(input_frame, textvariable=self.qt_var, width=15).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        ttk.Label(input_frame, text="Syke (bpm):", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.hr_var = tk.StringVar(value="60")
        ttk.Entry(input_frame, textvariable=self.hr_var, width=15).grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        ttk.Button(self.content_frame, text="Laske QTc", command=self.laske_qtc_action).pack(anchor="w", pady=20)
        
        self.qtc_result_frame = ttk.Frame(self.content_frame)
        self.qtc_result_frame.pack(anchor="w", fill="x")
        self.qtc_result_label = ttk.Label(self.qtc_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.qtc_result_label.pack(anchor="w")
        self.qtc_risk_label = ttk.Label(self.qtc_result_frame, text="", font=("Segoe UI", 11))
        self.qtc_risk_label.pack(anchor="w", pady=(5, 0))
        self.qtc_warning_label = ttk.Label(self.qtc_result_frame, text="", font=("Segoe UI", 11, "bold"), foreground="red")
        self.qtc_warning_label.pack(anchor="w", pady=(5, 0))
        
    def laske_qtc_action(self):
        qt = safe_float(self.qt_var.get())
        hr = safe_float(self.hr_var.get())
        
        qtc_b, qtc_f = laske_qtc(qt, hr)
        
        if qtc_b == 0.0:
            self.qtc_result_label.config(text="Tarkista syötteet (QT ja syke on oltava > 0).")
            self.qtc_risk_label.config(text="")
            self.qtc_warning_label.config(text="")
            return
            
        self.qtc_result_label.config(text=f"Bazett (QTcB): {qtc_b:.0f} ms  |  Fridericia (QTcF): {qtc_f:.0f} ms")
        self.qtc_risk_label.config(text=f"Tulkinta (Fridericia): {hae_qtc_suositus(qtc_f)}")
        
        if qtc_f > 500: self.qtc_warning_label.config(text="⚠️ VAKAVA QTc-PIDENTYMÄ YLI 500 ms!")
        elif qtc_f > 480: self.qtc_warning_label.config(text="⚠️ QTc-Aika > 480 ms!")
        else: self.qtc_warning_label.config(text="")

    def build_mascc_view(self):
        ttk.Label(self.content_frame, text="MASCC (Multinational Association for Supportive Care in Cancer)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi komplikaatioriskiä potilaalla, jolla on kuumeinen neutropenia.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        ttk.Label(input_frame, text="Oireiden vaikeusaste (valitse yksi):", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(5,2))
        self.mascc_oire_var = tk.IntVar(value=5)
        ttk.Radiobutton(input_frame, text="Lievät tai ei oireita (5 p)", variable=self.mascc_oire_var, value=5, command=self.laske_mascc).grid(row=1, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(input_frame, text="Kohtalaiset oireet (3 p)", variable=self.mascc_oire_var, value=3, command=self.laske_mascc).grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(input_frame, text="Vaikeat oireet (0 p)", variable=self.mascc_oire_var, value=0, command=self.laske_mascc).grid(row=3, column=0, columnspan=2, sticky="w")
        
        ttk.Label(input_frame, text="Muut kriteerit:", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, columnspan=2, sticky="w", pady=(15,2))
        
        self.mascc_hypo_var = tk.BooleanVar(value=False)
        self.mascc_copd_var = tk.BooleanVar(value=False)
        self.mascc_tumor_var = tk.BooleanVar(value=False)
        self.mascc_dehydr_var = tk.BooleanVar(value=False)
        self.mascc_outpat_var = tk.BooleanVar(value=False)
        self.mascc_age_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(input_frame, text="Ei hypotensiota (RR systolinen > 90 mmHg) (5 p)", variable=self.mascc_hypo_var, command=self.laske_mascc).grid(row=5, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(input_frame, text="Ei aktiivista COPD:tä (keuhkoahtaumatautia) (4 p)", variable=self.mascc_copd_var, command=self.laske_mascc).grid(row=6, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(input_frame, text="Solidi tuumori TAI hematologinen syöpä ilman aiempaa sieni-infektiota (4 p)", variable=self.mascc_tumor_var, command=self.laske_mascc).grid(row=7, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(input_frame, text="Ei suonensisäisen nestehoidon tarvetta kuivumisen vuoksi (3 p)", variable=self.mascc_dehydr_var, command=self.laske_mascc).grid(row=8, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(input_frame, text="Potilas on ollut avohoidossa kuumeen alkaessa (3 p)", variable=self.mascc_outpat_var, command=self.laske_mascc).grid(row=9, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(input_frame, text="Ikä alle 60 vuotta (2 p)", variable=self.mascc_age_var, command=self.laske_mascc).grid(row=10, column=0, columnspan=2, sticky="w", pady=2)
        
        self.mascc_result_frame = ttk.Frame(self.content_frame)
        self.mascc_result_frame.pack(anchor="w", fill="x", pady=20)
        self.mascc_result_label = ttk.Label(self.mascc_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.mascc_result_label.pack(anchor="w")
        self.mascc_risk_label = ttk.Label(self.mascc_result_frame, text="", font=("Segoe UI", 11))
        self.mascc_risk_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_mascc()

    def laske_mascc(self):
        pisteet = laske_mascc_pisteet(self.mascc_oire_var.get(), self.mascc_hypo_var.get(), self.mascc_copd_var.get(), self.mascc_tumor_var.get(), self.mascc_dehydr_var.get(), self.mascc_outpat_var.get(), self.mascc_age_var.get())
        suositus = hae_mascc_suositus(pisteet)
        
        self.mascc_result_label.config(text=f"Tulos: MASCC-pisteet: {pisteet} / 26")
        self.mascc_risk_label.config(text=f"Suositus: {suositus}")

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

    def build_ips_view(self):
        ttk.Label(self.content_frame, text="IPS (International Prognostic Score)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi levinneen (Stage IIB-IV) Hodgkinin lymfooman ennustetta.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        self.ips_alb_var = tk.BooleanVar(value=False)
        self.ips_hb_var = tk.BooleanVar(value=False)
        self.ips_mies_var = tk.BooleanVar(value=False)
        self.ips_ika_var = tk.BooleanVar(value=False)
        self.ips_stage_var = tk.BooleanVar(value=False)
        self.ips_wbc_var = tk.BooleanVar(value=False)
        self.ips_lymf_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(input_frame, text="Albumiini < 40 g/l", variable=self.ips_alb_var, command=self.laske_ips).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Hemoglobiini < 105 g/l", variable=self.ips_hb_var, command=self.laske_ips).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Mies-sukupuoli", variable=self.ips_mies_var, command=self.laske_ips).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Ikä ≥ 45 vuotta", variable=self.ips_ika_var, command=self.laske_ips).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Stage IV -tauti", variable=self.ips_stage_var, command=self.laske_ips).grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Leukosyytit (WBC) ≥ 15.0 E9/l", variable=self.ips_wbc_var, command=self.laske_ips).grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Lymfosyytit < 0.6 E9/l (tai < 8% WBC)", variable=self.ips_lymf_var, command=self.laske_ips).grid(row=6, column=0, columnspan=2, sticky="w", pady=5)
        
        self.ips_result_frame = ttk.Frame(self.content_frame)
        self.ips_result_frame.pack(anchor="w", fill="x", pady=20)
        self.ips_result_label = ttk.Label(self.ips_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.ips_result_label.pack(anchor="w")
        self.ips_risk_label = ttk.Label(self.ips_result_frame, text="", font=("Segoe UI", 11))
        self.ips_risk_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_ips()

    def laske_ips(self):
        pisteet = laske_ips_pisteet(self.ips_alb_var.get(), self.ips_hb_var.get(), self.ips_mies_var.get(), self.ips_ika_var.get(), self.ips_stage_var.get(), self.ips_wbc_var.get(), self.ips_lymf_var.get())
        ennuste = hae_ips_ennuste(pisteet)
        
        self.ips_result_label.config(text=f"Tulos: IPS-pisteet: {pisteet} / 7")
        self.ips_risk_label.config(text=f"Ennuste: {ennuste}")

    def build_hl_paikallinen_view(self):
        ttk.Label(self.content_frame, text="Hodgkin lymfooma - Paikallisen taudin riskitekijät", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi paikallisen (Stage I-II) Hodgkinin lymfooman riskiryhmää (EORTC/GHSG -kriteerit).", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        self.hl_med_var = tk.BooleanVar(value=False)
        self.hl_eks_var = tk.BooleanVar(value=False)
        self.hl_alue_var = tk.BooleanVar(value=False)
        self.hl_la_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(input_frame, text="Iso mediastinumin tuumori (> 1/3 rintakehän leveydestä)", variable=self.hl_med_var, command=self.laske_hl_paikallinen).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="Tautia imusolmukkeen ulkopuolisessa elimessä (E-leesio)", variable=self.hl_eks_var, command=self.laske_hl_paikallinen).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="≥ 3 affisoitunutta imusolmukealuetta", variable=self.hl_alue_var, command=self.laske_hl_paikallinen).grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(input_frame, text="La > 50 mm/t (Stage IA, IIA) TAI La > 30 mm/t (Stage IB, IIB)", variable=self.hl_la_var, command=self.laske_hl_paikallinen).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        self.hl_result_frame = ttk.Frame(self.content_frame)
        self.hl_result_frame.pack(anchor="w", fill="x", pady=20)
        self.hl_result_label = ttk.Label(self.hl_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.hl_result_label.pack(anchor="w")
        self.hl_risk_label = ttk.Label(self.hl_result_frame, text="", font=("Segoe UI", 11))
        self.hl_risk_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_hl_paikallinen()

    def laske_hl_paikallinen(self):
        pisteet = tarkista_hl_paikallinen_riskitekijat(self.hl_med_var.get(), self.hl_eks_var.get(), self.hl_alue_var.get(), self.hl_la_var.get())
        ryhma = hae_hl_paikallinen_riskiryhma(pisteet)
        
        self.hl_result_label.config(text=f"Tulos: {pisteet} riskitekijä(ä) täyttyy.")
        self.hl_risk_label.config(text=f"Riskiryhmä: {ryhma}")

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
            
    def build_child_pugh_view(self):
        ttk.Label(self.content_frame, text="Child-Pugh -luokitus", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi kroonisen maksasairauden / kirroosin vakavuutta ja ennustetta.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        self.cp_bili_var = tk.IntVar(value=1)
        self.cp_alb_var = tk.IntVar(value=1)
        self.cp_inr_var = tk.IntVar(value=1)
        self.cp_ascites_var = tk.IntVar(value=1)
        self.cp_enk_var = tk.IntVar(value=1)
        
        col1_frame = ttk.Frame(input_frame)
        col1_frame.grid(row=0, column=0, sticky="nw", padx=(0, 40))
        col2_frame = ttk.Frame(input_frame)
        col2_frame.grid(row=0, column=1, sticky="nw")
        
        ttk.Label(col1_frame, text="Bilirubiini (µmol/l):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5,2))
        ttk.Radiobutton(col1_frame, text="< 34 (1 p)", variable=self.cp_bili_var, value=1, command=self.laske_cp).pack(anchor="w")
        ttk.Radiobutton(col1_frame, text="34 - 50 (2 p)", variable=self.cp_bili_var, value=2, command=self.laske_cp).pack(anchor="w")
        ttk.Radiobutton(col1_frame, text="> 50 (3 p)", variable=self.cp_bili_var, value=3, command=self.laske_cp).pack(anchor="w")
        
        ttk.Label(col1_frame, text="Albumiini (g/l):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15,2))
        ttk.Radiobutton(col1_frame, text="> 35 (1 p)", variable=self.cp_alb_var, value=1, command=self.laske_cp).pack(anchor="w")
        ttk.Radiobutton(col1_frame, text="28 - 35 (2 p)", variable=self.cp_alb_var, value=2, command=self.laske_cp).pack(anchor="w")
        ttk.Radiobutton(col1_frame, text="< 28 (3 p)", variable=self.cp_alb_var, value=3, command=self.laske_cp).pack(anchor="w")
        
        ttk.Label(col1_frame, text="INR:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15,2))
        ttk.Radiobutton(col1_frame, text="< 1.7 (1 p)", variable=self.cp_inr_var, value=1, command=self.laske_cp).pack(anchor="w")
        ttk.Radiobutton(col1_frame, text="1.7 - 2.2 (2 p)", variable=self.cp_inr_var, value=2, command=self.laske_cp).pack(anchor="w")
        ttk.Radiobutton(col1_frame, text="> 2.2 (3 p)", variable=self.cp_inr_var, value=3, command=self.laske_cp).pack(anchor="w")
        
        ttk.Label(col2_frame, text="Askites:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5,2))
        ttk.Radiobutton(col2_frame, text="Ei (1 p)", variable=self.cp_ascites_var, value=1, command=self.laske_cp).pack(anchor="w")
        ttk.Radiobutton(col2_frame, text="Lievä / lääkityksellä hallinnassa (2 p)", variable=self.cp_ascites_var, value=2, command=self.laske_cp).pack(anchor="w")
        ttk.Radiobutton(col2_frame, text="Keskivaikea tai vaikea / huonosti reagoiva (3 p)", variable=self.cp_ascites_var, value=3, command=self.laske_cp).pack(anchor="w")
        
        ttk.Label(col2_frame, text="Enkefalopatia:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15,2))
        ttk.Radiobutton(col2_frame, text="Ei (1 p)", variable=self.cp_enk_var, value=1, command=self.laske_cp).pack(anchor="w")
        ttk.Radiobutton(col2_frame, text="Aste I-II (Lievä / lääkityksellä hallinnassa) (2 p)", variable=self.cp_enk_var, value=2, command=self.laske_cp).pack(anchor="w")
        ttk.Radiobutton(col2_frame, text="Aste III-IV (Vaikea / kooma) (3 p)", variable=self.cp_enk_var, value=3, command=self.laske_cp).pack(anchor="w")
        
        self.cp_result_frame = ttk.Frame(self.content_frame)
        self.cp_result_frame.pack(anchor="w", fill="x", pady=20)
        self.cp_result_label = ttk.Label(self.cp_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.cp_result_label.pack(anchor="w")
        self.cp_risk_label = ttk.Label(self.cp_result_frame, text="", font=("Segoe UI", 11))
        self.cp_risk_label.pack(anchor="w", pady=(5, 0))
        
        self.laske_cp()

    def laske_cp(self):
        pisteet = laske_child_pugh_pisteet(self.cp_bili_var.get(), self.cp_alb_var.get(), self.cp_inr_var.get(), self.cp_ascites_var.get(), self.cp_enk_var.get())
        luokka = hae_child_pugh_luokka(pisteet)
        
        self.cp_result_label.config(text=f"Tulos: Child-Pugh -pisteet: {pisteet} / 15")
        self.cp_risk_label.config(text=f"Luokitus: {luokka}")

    def build_psadt_view(self):
        ttk.Label(self.content_frame, text="PSA:n kahdentumisaika (PSADT)", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(self.content_frame, text="Arvioi eturauhassyövän etenemistä mittaamalla aikaa, jossa PSA-arvo kaksinkertaistuu.", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))
        
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(anchor="w", fill="x")
        
        col1_frame = ttk.Frame(input_frame)
        col1_frame.grid(row=0, column=0, sticky="nw", padx=(0, 40))
        col2_frame = ttk.Frame(input_frame)
        col2_frame.grid(row=0, column=1, sticky="nw")
        
        ttk.Label(col1_frame, text="1. mittaus", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5,5))
        ttk.Label(col1_frame, text="Päivämäärä (pp.kk.vvvv):").pack(anchor="w")
        self.psadt_pvm1_var = tk.StringVar(value=(datetime.now() - timedelta(days=90)).strftime("%d.%m.%Y"))
        if HAS_TKCALENDAR:
            DateEntry(col1_frame, textvariable=self.psadt_pvm1_var, date_pattern="dd.mm.yyyy", width=13, background='darkblue', foreground='white', borderwidth=2).pack(anchor="w", pady=(0, 10))
        else:
            ttk.Entry(col1_frame, textvariable=self.psadt_pvm1_var, width=15).pack(anchor="w", pady=(0, 10))
            
        ttk.Label(col1_frame, text="PSA-arvo 1:").pack(anchor="w")
        self.psadt_psa1_var = tk.StringVar(value="5.0")
        ttk.Entry(col1_frame, textvariable=self.psadt_psa1_var, width=15).pack(anchor="w")
        
        ttk.Label(col2_frame, text="2. mittaus", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5,5))
        ttk.Label(col2_frame, text="Päivämäärä (pp.kk.vvvv):").pack(anchor="w")
        self.psadt_pvm2_var = tk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        if HAS_TKCALENDAR:
            DateEntry(col2_frame, textvariable=self.psadt_pvm2_var, date_pattern="dd.mm.yyyy", width=13, background='darkblue', foreground='white', borderwidth=2).pack(anchor="w", pady=(0, 10))
        else:
            ttk.Entry(col2_frame, textvariable=self.psadt_pvm2_var, width=15).pack(anchor="w", pady=(0, 10))
            
        ttk.Label(col2_frame, text="PSA-arvo 2:").pack(anchor="w")
        self.psadt_psa2_var = tk.StringVar(value="10.0")
        ttk.Entry(col2_frame, textvariable=self.psadt_psa2_var, width=15).pack(anchor="w")
        
        ttk.Button(self.content_frame, text="Laske PSADT", command=self.laske_psadt_action).pack(anchor="w", pady=20)
        
        self.psadt_result_frame = ttk.Frame(self.content_frame)
        self.psadt_result_frame.pack(anchor="w", fill="x")
        self.psadt_result_label = ttk.Label(self.psadt_result_frame, text="", font=("Segoe UI", 12, "bold"))
        self.psadt_result_label.pack(anchor="w")
        self.psadt_risk_label = ttk.Label(self.psadt_result_frame, text="", font=("Segoe UI", 11))
        self.psadt_risk_label.pack(anchor="w", pady=(5, 0))
        
    def laske_psadt_action(self):
        try:
            pvm1 = datetime.strptime(self.psadt_pvm1_var.get(), "%d.%m.%Y").date()
            pvm2 = datetime.strptime(self.psadt_pvm2_var.get(), "%d.%m.%Y").date()
            psa1 = float(self.psadt_psa1_var.get().replace(",", "."))
            psa2 = float(self.psadt_psa2_var.get().replace(",", "."))
            
            if pvm2 <= pvm1:
                self.psadt_result_label.config(text="Virhe: Jälkimmäisen päivämäärän on oltava ensimmäisen jälkeen.")
                self.psadt_risk_label.config(text="")
                return
            if psa2 <= psa1:
                self.psadt_result_label.config(text="Virhe: Jälkimmäisen PSA-arvon on oltava suurempi.")
                self.psadt_risk_label.config(text="")
                return
                
            psadt = laske_psadt(pvm1, psa1, pvm2, psa2)
            tulkinta = hae_psadt_tulkinta(psadt)
            
            self.psadt_result_label.config(text=f"Tulos: PSADT = {psadt:.1f} kuukautta")
            self.psadt_risk_label.config(text=f"Tulkinta: {tulkinta}")
        except ValueError:
            self.psadt_result_label.config(text="Virhe: Tarkista päivämäärät (pp.kk.vvvv) ja PSA-arvot.")
            self.psadt_risk_label.config(text="")
