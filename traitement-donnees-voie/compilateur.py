import traitement_donnees
import config

from datetime import date


class Compilateur():
    def _traitement_tunnel(
        self,
        data,
        tunnel,
        dates_decalage,
        decalage,
        decalage_bool,
        debut_pk,
        fin_pk,
        nom_pk,
        nom_pk_arrondis,
        nom_date,
    ):
        print(f"Arrondissement des PK {tunnel}.")
        data = traitement_donnees.transformation_en_date(data, nom_date)
        data = traitement_donnees.arrondissement_rapide(data, nom_pk)

        nom_pk = nom_pk_arrondis

        if decalage_bool:
            print("Ajustement du décalage des PK.")
            signe = 1
            if tunnel == "SUD":
                signe = -1
            data = traitement_donnees.data_ajustement(
                data, dates_decalage, decalage * signe, nom_pk_arrondis
            )

        debut = data[nom_pk_arrondis].min() if not debut_pk else debut_pk
        fin = data[nom_pk_arrondis].max() if not fin_pk else fin_pk

        print(f"Sélection de la plage {debut}-{fin}.")
        data = traitement_donnees.selectionner_plage(data, debut, fin,
                                                     nom_pk_arrondis)
        return data

    def traitement_donnees_fichier_complet(
        self,
        fichier,
        nom_sauvegarde=None,
        debut_pk=None,
        fin_pk=None,
        debut_date=None,
        fin_date=None,
        dates_choisies=None,
        tunnel=None,
        decalage_bool=False,
    ):
        print("Début de la sauvegarde.")

        configuration = config.obtenir_config()
        nom_pk = configuration["nom_pk"]
        nom_pk_arrondis = nom_pk+"_ARRONDIS"
        nom_date = configuration["nom_date"]

        dates_decalage_nord = (
            configuration["dates_decalage_nord"] if decalage_bool else None
        )
        dates_decalage_sud = (
            configuration["dates_decalage_sud"] if decalage_bool else None
            )
        decalage = configuration["decalage"] if decalage_bool else None

        print("Importation du fichier.")
        data = traitement_donnees.importer_csv(fichier)

        print("Nettoyage des NA.")
        data = traitement_donnees.nettoyer_na(data)

        print("Sélection des dates.")
        data = traitement_donnees.date_minimale(data, debut_date, nom_date)
        data = traitement_donnees.date_maximale(data, fin_date, nom_date)
        data = traitement_donnees.selectionner_dates(data, dates_choisies,
                                                     nom_date)

        if tunnel:
            print("Sélection du tunnel.")
            data = traitement_donnees.choix_du_tunnel(data, tunnel)

            if tunnel == "NORD":
                dates_decalage = dates_decalage_nord
            else:
                dates_decalage = dates_decalage_sud

            data = self._traitement_tunnel(
                data,
                tunnel,
                dates_decalage,
                decalage,
                decalage_bool,
                debut_pk,
                fin_pk,
                nom_pk,
                nom_pk_arrondis,
                nom_date,
            )

            print("Sauvegarde du fichier.")
            if nom_sauvegarde:
                traitement_donnees.sauvegarder_csv(
                    data, nom_sauvegarde + ".csv")
            else:
                traitement_donnees.sauvegarder_csv(
                    data, "tunnel_" + tunnel + str(date.today()) + ".csv"
                )

        else:
            print("Séparation des tunnels")
            nord = traitement_donnees.choix_du_tunnel(data, "NORD")
            sud = traitement_donnees.choix_du_tunnel(data, "SUD")

            print("Traitement du tunnel nord.")
            nord = self._traitement_tunnel(
                nord,
                "NORD",
                dates_decalage_nord,
                decalage,
                decalage_bool,
                debut_pk,
                fin_pk,
                nom_pk,
                nom_pk_arrondis,
                nom_date,
            )

            print("Traitement du tunnel sud.")
            sud = self._traitement_tunnel(
                sud,
                "SUD",
                dates_decalage_sud,
                decalage,
                decalage_bool,
                debut_pk,
                fin_pk,
                nom_pk,
                nom_pk_arrondis,
                nom_date,
            )

            print("Sauvegarde des fichiers.")
            if nom_sauvegarde:
                traitement_donnees.sauvegarder_csv(
                    nord, nom_sauvegarde + "_NORD.csv")
                traitement_donnees.sauvegarder_csv(
                    sud, nom_sauvegarde + "_SUD.csv")
            else:
                traitement_donnees.sauvegarder_csv(
                    nord, "tunnel_" + "NORD_" + str(date.today()) + ".csv"
                )
                traitement_donnees.sauvegarder_csv(
                    sud, "tunnel_" + "SUD_" + str(date.today()) + ".csv"
                )

        print("Fin de la sauvegarde.")
