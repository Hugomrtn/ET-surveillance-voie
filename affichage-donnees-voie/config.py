def obtenir_variables():
    variables = {"nom_pk": "PK_NET_6_COEURS_ARRONDIS",
                 "nom_date": "MEASURE_DATE",
                 "Nivellement Droit": "RIGHT_LEVEL_VALUE",
                 "Nivellement Gauche": "LEFT_LEVEL_VALUE",
                 "Gauche": "TWIST_VALUE",
                 "Dressage Droit": "RIGHT_ALIGNMENT_VALUE",
                 "Dressage Gauche": "LEFT_ALIGNMENT_VALUE"
                 }
    return variables


def obtenir_seuils(parametre):
    seuils = {"RIGHT_LEVEL_VALUE": [4, 7, 10],
              "LEFT_LEVEL_VALUE": [4, 7, 10],
              "Devers": [4, 5, 9],
              "TWIST_VALUE": [3, 6, 9],
              }
    return seuils[parametre]
