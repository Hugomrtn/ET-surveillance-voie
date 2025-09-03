import os
import threading
import queue
import contextlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from compilateur import Compilateur


class QueueWriter:
    def __init__(self, q):
        self.q = q

    def write(self, s: str):
        if s:
            self.q.put(s)

    def flush(self):
        pass


class PlaceholderEntry(tk.Entry):
    def __init__(self, master, placeholder="facultatif", width=None):
        super().__init__(master, width=width)
        self.placeholder = placeholder
        self.placeholder_color = "#C2C2C2"
        self.default_fg = self.cget("fg")
        self._has_placeholder = False

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder_if_empty)

        self._add_placeholder_if_empty()

    def _clear_placeholder(self, event=None):
        if self._has_placeholder:
            self.delete(0, "end")
            self.config(fg=self.default_fg)
            self._has_placeholder = False

    def _add_placeholder_if_empty(self, event=None):
        if not super().get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
            self._has_placeholder = True

    def get_value(self) -> str:
        return "" if self._has_placeholder else super().get()

    def set_value(self, value: str):
        self._clear_placeholder()
        self.delete(0, "end")
        if value:
            self.insert(0, value)
            self.config(fg=self.default_fg)
            self._has_placeholder = False
        else:
            self._add_placeholder_if_empty()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TRAITEMENT EXPORT GEOMETRY")
        self.geometry("760x560")

        self.q = queue.Queue()
        self.writer = QueueWriter(self.q)

        self._build_ui()
        self.after(100, self._poll_log_queue)

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True)

        # Fichier (obligatoire)
        ttk.Label(frm, text="Fichier CSV (obligatoire):").grid(
            row=0, column=0, sticky="w", **pad)
        self.file_entry = PlaceholderEntry(
            frm, width=70, placeholder="chemin du CSV (obligatoire)")
        self.file_entry.grid(row=0, column=1, **pad)
        ttk.Button(frm, text="Parcourir…", command=self._browse).grid(
            row=0, column=2, **pad)

        # Dossier de sortie (facultatif)
        ttk.Label(frm, text="Dossier de sortie:").grid(
            row=1, column=0, sticky="w", **pad)
        self.out_dir_entry = PlaceholderEntry(
            frm, width=70, placeholder="par défaut: dossier courant")
        self.out_dir_entry.grid(row=1, column=1, **pad)
        ttk.Button(frm, text="Choisir…", command=self._browse_dir).grid(
            row=1, column=2, **pad)

        # Tunnel
        ttk.Label(frm, text="Tunnel:").grid(row=2, column=0, sticky="w", **pad)
        self.tunnel_var = tk.StringVar(value="Les deux")
        ttk.Combobox(
            frm,
            textvariable=self.tunnel_var,
            values=["NORD", "SUD", "Les deux"],
            state="readonly",
            width=15,
        ).grid(row=2, column=1, sticky="w", **pad)

        # Nom sauvegarde
        ttk.Label(frm, text="Nom de sauvegarde (sans .csv):").grid(
            row=3, column=0, sticky="w", **pad)
        self.nom_entry = PlaceholderEntry(frm, width=30,
                                          placeholder="facultatif")
        self.nom_entry.grid(row=3, column=1, sticky="w", **pad)

        # PK
        ttk.Label(frm, text="Début PK:").grid(row=4, column=0,
                                              sticky="w", **pad)
        self.debut_pk_entry = PlaceholderEntry(frm, width=18,
                                               placeholder="facultatif")
        self.debut_pk_entry.grid(row=4, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Fin PK:").grid(row=4, column=2, sticky="w", **pad)
        self.fin_pk_entry = PlaceholderEntry(frm, width=18,
                                             placeholder="facultatif")
        self.fin_pk_entry.grid(row=4, column=3, sticky="w", **pad)

        # Dates
        ttk.Label(frm, text="Début date (YYYY-MM-DD):").grid(
            row=5, column=0, sticky="w", **pad)
        self.debut_date_entry = PlaceholderEntry(frm, width=18,
                                                 placeholder="facultatif")
        self.debut_date_entry.grid(row=5, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Fin date (YYYY-MM-DD):").grid(
            row=5, column=2, sticky="w", **pad)
        self.fin_date_entry = PlaceholderEntry(frm, width=18,
                                               placeholder="facultatif")
        self.fin_date_entry.grid(row=5, column=3, sticky="w", **pad)

        ttk.Label(frm, text="Dates choisies (séparées par ,):").grid(
            row=6, column=0, sticky="w", **pad)
        self.dates_choisies_entry = PlaceholderEntry(frm, width=40,
                                                     placeholder="facultatif")
        self.dates_choisies_entry.grid(row=6, column=1, columnspan=3,
                                       sticky="w", **pad)

        # Décalage
        self.decalage_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, text="Appliquer le décalage",
                        variable=self.decalage_var).grid(
                            row=7, column=0, sticky="w", **pad)

        # Boutons
        btns = ttk.Frame(frm)
        btns.grid(row=8, column=0, columnspan=4, sticky="w", **pad)
        self.run_btn = ttk.Button(btns, text="Lancer le traitement",
                                  command=self._run)
        self.run_btn.pack(side="left", padx=4)
        ttk.Button(btns, text="Quitter", command=self.destroy).pack(
            side="left", padx=4)

        # Logs
        ttk.Label(frm, text="Logs:").grid(row=9, column=0, sticky="w", **pad)
        self.log = ScrolledText(frm, height=14, wrap="word")
        self.log.grid(row=10, column=0, columnspan=4, sticky="nsew", padx=8,
                      pady=(0, 8))
        frm.rowconfigure(10, weight=1)
        frm.columnconfigure(1, weight=1)

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Choisir le fichier CSV",
            filetypes=[("CSV", "*.csv"), ("Tous les fichiers", "*.*")],
        )
        if path:
            self.file_entry.set_value(path)

    def _browse_dir(self):
        path = filedialog.askdirectory(title="Choisir le dossier de sortie")
        if path:
            self.out_dir_entry.set_value(path)

    def _append_log(self, text: str):
        self.log.insert("end", text)
        self.log.see("end")

    def _poll_log_queue(self):
        try:
            while True:
                msg = self.q.get_nowait()
                self._append_log(msg)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._poll_log_queue)

    def _run(self):
        fichier = self.file_entry.get_value().strip()
        if not fichier:
            messagebox.showerror("Erreur",
                                 "Veuillez sélectionner un fichier CSV.")
            return

        compilateur = Compilateur()

        # Tunnel
        tunnel_sel = self.tunnel_var.get()
        tunnel = None if tunnel_sel == "Les deux" else tunnel_sel

        # Nom de sauvegarde
        nom_sauvegarde = self.nom_entry.get_value().strip() or None

        # PK
        def parse_int_or_none(v):
            v = v.strip()
            if not v:
                return None
            try:
                return int(v)
            except ValueError:
                raise ValueError(f"Valeur PK invalide: {v}")

        try:
            debut_pk = parse_int_or_none(self.debut_pk_entry.get_value())
            fin_pk = parse_int_or_none(self.fin_pk_entry.get_value())
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        # Dates
        def normalize_str_or_none(v):
            v = v.strip()
            return v if v else None

        debut_date = normalize_str_or_none(self.debut_date_entry.get_value())
        fin_date = normalize_str_or_none(self.fin_date_entry.get_value())

        dates_choisies_str = self.dates_choisies_entry.get_value().strip()
        dates_choisies = None
        if dates_choisies_str:
            dates_choisies = \
                [d.strip() for d in dates_choisies_str.split(",") if d.strip()]

        decalage_bool = bool(self.decalage_var.get())

        # Lancer dans un thread
        self.run_btn.config(state="disabled")
        self.log.delete("1.0", "end")
        self._append_log("Démarrage du traitement…\n")

        output_dir = self.out_dir_entry.get_value().strip() or None

        def worker():
            old_cwd = os.getcwd()
            try:
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                with (contextlib.redirect_stdout(self.writer),
                      contextlib.redirect_stderr(self.writer)):
                    if output_dir:
                        os.chdir(output_dir)
                    compilateur.traitement_donnees_fichier_complet(
                        fichier=fichier,
                        nom_sauvegarde=nom_sauvegarde,
                        debut_pk=debut_pk,
                        fin_pk=fin_pk,
                        debut_date=debut_date,
                        fin_date=fin_date,
                        dates_choisies=dates_choisies,
                        tunnel=tunnel,
                        decalage_bool=decalage_bool,
                    )
                self.q.put("\n[OK] Traitement terminé.\n")
            except Exception as e:
                import traceback
                self.q.put(f"\n[ERREUR] {e}\n")
                self.q.put(traceback.format_exc())
            finally:
                try:
                    os.chdir(old_cwd)
                except Exception:
                    pass
                self.after(0, lambda: self.run_btn.config(state="normal"))

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
