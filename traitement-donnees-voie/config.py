def obtenir_config():
    dates_decalage_nord = ["2024-12-13", "2024-10-02", "2024-07-10",
                           "2024-06-12", "2024-05-29", "2024-04-24"]
    dates_decalage_sud = ["2024-05-09", "2024-05-15", "2024-07-10",
                          "2024-10-30"]
    decalage = 80

    config = {
        "nom_pk": "PK_NET_6_COEURS",
        "nom_date": "MEASURE_DATE",
        "dates_decalage_nord": dates_decalage_nord,
        "dates_decalage_sud": dates_decalage_sud,
        "decalage": decalage,
    }

    return config
