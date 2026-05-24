import tkinter as tk
from tkinter import ttk

from oncology_helper.calculators import EcogLuokka, hae_ecog_kuvaus

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
        
        laskurit = ["ECOG-suorituskyky"]
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
        ttk.Label(self.content_frame, text="Ennustetekijä aggressiivisille non-Hodgkin-lymfoomille (esim. DLBCL).", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))

        checkbox_frame = ttk.Frame(self.content_frame)
        checkbox_frame.pack(anchor="w", fill="x")

        self.ipi_ika_var = tk.BooleanVar()
        self.ipi_stage_var = tk.BooleanVar()
        self.ipi_extra_var = tk.BooleanVar()
        self.ipi_ecog_var = tk.BooleanVar()
        self.ipi_ldh_var = tk.BooleanVar()

        def on_ipi_change():
            pisteet = laske_ipi_pisteet(
                self.ipi_ika_var.get(),
                self.ipi_stage_var.get(),
                self.ipi_extra_var.get(),
                self.ipi_ecog_var.get(),
                self.ipi_ldh_var.get()
            )
            riskiluokka = maarita_ipi_riskiluokka(pisteet)
            self.ipi_result_label.config(text=f"Tulos: {pisteet} / 5 pistettä")
            self.ipi_class_label.config(text=f"Riskiluokka: {riskiluokka.value}")

        checkboxes = [
            ("Ikä yli 60 vuotta", self.ipi_ika_var),
            ("Levinneisyysaste III tai IV", self.ipi_stage_var),
            ("Yli 1 ekstranodaalinen pesäke", self.ipi_extra_var),
            ("ECOG-suorituskyky ≥ 2", self.ipi_ecog_var),
            ("Seerumin LDH yli viitearvon", self.ipi_ldh_var)
        ]

        for teksti, var in checkboxes:
            cb = ttk.Checkbutton(
                checkbox_frame, 
                text=teksti, 
                variable=var, 
                command=on_ipi_change
            )
            cb.pack(anchor="w", pady=5)

        self.ipi_result_frame = ttk.Frame(self.content_frame)
        self.ipi_result_frame.pack(anchor="w", fill="x", pady=20)
        self.ipi_result_label = ttk.Label(self.ipi_result_frame, text="Tulos: 0 / 5 pistettä", font=("Segoe UI", 12, "bold"))
        self.ipi_result_label.pack(anchor="w")
        self.ipi_class_label = ttk.Label(self.ipi_result_frame, text="Riskiluokka: Matala riski (0-1 pistettä)", font=("Segoe UI", 11, "bold"), foreground="green")
        self.ipi_class_label.pack(anchor="w", pady=(5, 0))
