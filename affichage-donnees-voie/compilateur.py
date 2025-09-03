import config
import affichage_2d


def compiler_affichage_courbes(data, parametre_courant,
                               afficher_seuils=False):
    variables = config.obtenir_variables()
    nom_pk = variables["nom_pk"]
    nom_date = variables["nom_date"]
    parametre = variables[parametre_courant]
    seuils = config.obtenir_seuils(parametre) if afficher_seuils else []

    affichage_2d.afficher_courbes_2d(data, parametre, nom_pk, nom_date, seuils)


def compiler_affichage_heatmap(data, parametre_courant):
    variables = config.obtenir_variables()
    nom_pk = variables["nom_pk"]
    nom_date = variables["nom_date"]
    parametre = variables[parametre_courant]

    fig, data_pivot = affichage_2d.afficher_heatmap(data, nom_pk, parametre,
                                                    nom_date)
    fig.show()
