import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import sys

import compilateur
import config


class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, s):
        if not s:
            return
        try:
            self.widget.configure(state="normal")
            self.widget.insert("end", s)
            self.widget.see("end")
            self.widget.configure(state="disabled")
        except Exception:
            pass

    def flush(self):
        pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analyse Eurotunnel")
        self.geometry("640x560")
        self.filepath = None

        self._build_ui()

        sys.stdout = TextRedirector(self.log_text)
        sys.stderr = TextRedirector(self.log_text)

    def _build_ui(self):
        lbl = ttk.Label(self, text="Sélectionnez un fichier CSV à analyser :")
        lbl.pack(pady=8)

        self.file_entry = ttk.Entry(self, width=64)
        self.file_entry.pack(pady=4)

        browse = ttk.Button(self, text="Parcourir", command=self.select_file)
        browse.pack(pady=4)

        ttk.Label(self, text="Choisissez une variable :").pack(pady=(8, 0))
        self.variable_var = tk.StringVar(value="Nivellement Droit")
        self.variable_menu = ttk.Combobox(
            self, textvariable=self.variable_var, state="readonly"
        )
        self.variable_menu["values"] = (
            "Nivellement Droit",
            "Nivellement Gauche",
            "Gauche",
            "Dressage Droit",
            "Dressage Gauche",
        )
        self.variable_menu.pack(pady=6)

        date_frame = ttk.Frame(self)
        date_frame.pack(pady=6)
        ttk.Label(date_frame, text="Date début").pack(side="left")
        self.start_date_var = tk.StringVar(value="2024-01-01")
        ttk.Entry(date_frame, textvariable=self.start_date_var,
                  width=12).pack(side="left", padx=6)
        ttk.Label(date_frame, text="Date fin").pack(side="left")
        self.end_date_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.end_date_var,
                  width=12).pack(side="left", padx=6)

        self.pk_min_limit = 9000
        self.pk_max_limit = 61000
        pk_frame = ttk.Frame(self)
        pk_frame.pack(pady=6)
        ttk.Label(pk_frame, text="PK min").pack(side="left")
        self.entry_min_pk = ttk.Entry(pk_frame, width=8)
        self.entry_min_pk.insert(0, str(self.pk_min_limit))
        self.entry_min_pk.pack(side="left", padx=6)
        ttk.Label(pk_frame, text="PK max").pack(side="left")
        self.entry_max_pk = ttk.Entry(pk_frame, width=8)
        self.entry_max_pk.insert(0, str(self.pk_max_limit))
        self.entry_max_pk.pack(side="left", padx=6)

        btn_reset = ttk.Button(self, text="Réinitialiser PK",
                               command=self.reset_pk)
        btn_reset.pack(pady=6)

        actions = ttk.Frame(self)
        actions.pack(pady=8)

        heatmap_col = ttk.Frame(actions)
        heatmap_col.pack(side="left", padx=10)
        ttk.Button(heatmap_col, text="Afficher la heatmap",
                   command=self.run_pipeline).pack()

        courbes_col = ttk.Frame(actions)
        courbes_col.pack(side="left", padx=10)
        self.seuils_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(courbes_col, text="Afficher les seuils",
                        variable=self.seuils_var).pack(pady=(0, 4))
        ttk.Button(courbes_col, text="Afficher les courbes",
                   command=self.run_courbes).pack()

        self.log_text = tk.Text(self, height=10, wrap="word", state="disabled")
        self.log_text.pack(fill="both", padx=8, pady=(6, 12))

    def select_file(self):
        path = filedialog.askopenfilename(
            title="Sélectionner un fichier CSV",
            filetypes=[("CSV", "*.csv")],
        )
        if path:
            self.filepath = path
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, path)

    def reset_pk(self):
        self.entry_min_pk.delete(0, "end")
        self.entry_min_pk.insert(0, str(self.pk_min_limit))
        self.entry_max_pk.delete(0, "end")
        self.entry_max_pk.insert(0, str(self.pk_max_limit))

    def _get_pk_range(self):
        try:
            min_pk = int(float(self.entry_min_pk.get()))
        except Exception:
            min_pk = self.pk_min_limit
        try:
            max_pk = int(float(self.entry_max_pk.get()))
        except Exception:
            max_pk = self.pk_max_limit
        # clamp
        min_pk = max(self.pk_min_limit, min_pk)
        max_pk = min(self.pk_max_limit, max_pk)
        return min_pk, max_pk

    def _load_and_prepare_df(self, path):
        df = pd.read_csv(path)
        vars_cfg = config.obtenir_variables()
        nom_pk = vars_cfg["nom_pk"]
        nom_date = vars_cfg["nom_date"]

        if nom_date in df.columns:
            df[nom_date] = pd.to_datetime(df[nom_date], errors="coerce")
        df[nom_pk] = pd.to_numeric(df[nom_pk], errors="coerce")

        min_pk, max_pk = self._get_pk_range()
        df = df[(df[nom_pk] >= min_pk) & (df[nom_pk] <= max_pk)].copy()
        return df, nom_pk, nom_date

    def run_pipeline(self):
        if not self.filepath:
            messagebox.showwarning(
                "Attention", "Veuillez sélectionner un fichier CSV."
            )
            return
        try:
            df, nom_pk, nom_date = self._load_and_prepare_df(self.filepath)
            if df.empty:
                messagebox.showerror(
                    "Erreur", "Aucune donnée pour la plage de PK sélectionnée."
                )
                return

            vars_cfg = config.obtenir_variables()
            parametre_courant = self.variable_var.get()
            if parametre_courant not in vars_cfg:
                messagebox.showerror(
                    "Erreur",
                    f"Paramètre inconnu: {parametre_courant}.",
                )
                return

            compilateur.compiler_affichage_heatmap(
                data=df,
                parametre_courant=parametre_courant
            )
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))

    def run_courbes(self):
        if not self.filepath:
            messagebox.showwarning(
                "Attention", "Veuillez sélectionner un fichier CSV."
            )
            return
        try:
            df, nom_pk, nom_date = self._load_and_prepare_df(self.filepath)
            if df.empty:
                messagebox.showerror(
                    "Erreur", "Aucune donnée pour la plage de PK sélectionnée."
                )
                return

            start_date = self.start_date_var.get().strip() or None
            end_date = self.end_date_var.get().strip() or None
            if start_date:
                df = df[df[nom_date] >= pd.to_datetime(start_date,
                                                       errors="coerce")]
            if end_date:
                df = df[df[nom_date] <= pd.to_datetime(end_date,
                                                       errors="coerce")]

            if df.empty:
                messagebox.showerror(
                    "Erreur", "Aucune donnée dans l’intervalle de dates."
                )
                return

            parametre_courant = self.variable_var.get()
            compilateur.compiler_affichage_courbes(
                data=df,
                parametre_courant=parametre_courant,
                afficher_seuils=self.seuils_var.get(),
            )
        except Exception as exc:
            messagebox.showerror("Erreur", str(exc))


if __name__ == "__main__":
    App().mainloop()
