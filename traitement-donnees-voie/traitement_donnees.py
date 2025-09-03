import pandas as pd
import numpy as np
import warnings


def importer_csv(fichier):
    return pd.read_csv(fichier)


def sauvegarder_csv(data, fichier):
    data.to_csv(fichier, index=False)


def nettoyer_na(data, parametre="PK_NET_6_COEURS"):
    return data.dropna(subset=[parametre])


def data_ajustement(
    data,
    dates_a_modifier,
    ecart,
    nom_pk="PK_NET_6_COEURS_ARRONDIS",
    nom_date="MEASURE_DATE",
):
    if dates_a_modifier and ecart:
        data = data.copy()
        dates_a_modifier = pd.to_datetime(dates_a_modifier, errors="coerce")
        data.loc[data[nom_date].isin(dates_a_modifier), nom_pk] += ecart
    return data


def selectionner_plage(data, debut, fin, nom_pk="PK_NET_6_COEURS_ARRONDIS"):
    if debut or fin:
        data = data.copy()
        if debut:
            data = data[(data[nom_pk] >= debut)]
        if fin:
            data = data[(data[nom_pk] <= fin)]
    return data


def selectionner_dates(data, dates_a_choisir, nom_date="MEASURE_DATE"):
    if dates_a_choisir:
        data = data.copy()
        data = data[data[nom_date].isin(dates_a_choisir)]
    return data


def arrondissement_rapide(data, valeur="PK_NET_6_COEURS"):
    data = data.copy()
    data = data.sort_values(["MEASURE_DATE", valeur])
    valeur_arrondie = valeur + "_ARRONDIS"

    data[valeur_arrondie] = np.round(data[valeur] * 4) / 4

    def resoudre_doublons_groupe(groupe):
        if len(groupe) <= 1:
            return groupe

        doublons_mask = groupe.duplicated(subset=[valeur_arrondie], keep=False)
        if not doublons_mask.any():
            return groupe

        doublons_df = groupe[doublons_mask].copy()

        for pk_val in doublons_df[valeur_arrondie].unique():
            if pd.isna(pk_val):
                continue

            indices = doublons_df[doublons_df[valeur_arrondie] == pk_val].index

            if len(indices) <= 1:
                continue

            for i, idx in enumerate(indices[1:], 1):
                for step in range(1, 10):
                    for direction in [1, -1]:
                        candidate = pk_val + direction * step * 0.25
                        candidate = round(candidate * 4) / 4

                        if candidate not in groupe[valeur_arrondie].values:
                            groupe.loc[idx, valeur_arrondie] = candidate
                            break
                    else:
                        continue
                    break
                else:
                    groupe.loc[idx, valeur_arrondie] = pk_val + i * 0.25

        return groupe

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        data = data.groupby("MEASURE_DATE", group_keys=False).apply(
            resoudre_doublons_groupe
        )
    data = data.drop_duplicates(
        subset=["MEASURE_DATE", "PK_NET_6_COEURS_ARRONDIS"], keep="first"
    )
    return data


def transformation_en_date(data, nom_date="MEASURE_DATE"):
    data = data.copy()
    data[nom_date] = pd.to_datetime(data[nom_date])
    return data


def choix_du_tunnel(data, tunnel):
    if tunnel:
        return data[data["TUNNEL"] == tunnel]
    else:
        return data


def date_minimale(data, date, nom_date="MEASURE_DATE"):
    if date:
        return data[data[nom_date] >= date]
    else:
        return data


def date_maximale(data, date, nom_date="MEASURE_DATE"):
    if date:
        return data[data[nom_date] <= date]
    else:
        return data
