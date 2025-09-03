import pandas as pd
import os


def importer_donnees(nom_fichier):
    chemin = os.path.join(os.path.dirname(__file__), '..', 'data', nom_fichier)
    return pd.read_csv(chemin)


def filtrer_par_dates(data, date_debut=None, date_fin=None,
                      nom_date="MEASURE_DATE"):
    selection = pd.Series([True] * len(data))
    if date_debut:
        selection &= data[nom_date] >= date_debut
    if date_fin:
        selection &= data[nom_date] <= date_fin
    return data[selection]
