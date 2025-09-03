import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import numpy as np


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("L'exécution a dépassé 30 secondes.")


def afficher_courbes_2d(data, parametre='RIGHT_LEVEL_VALUE',
                        nom_pk='PK_NET_6_COEURS_ARRONDIS',
                        nom_date='MEASURE_DATE',
                        seuils=[]):
    fig = go.Figure()
    for i, (date_val, group) in enumerate(data.groupby(nom_date)):
        dash = 'solid' if i % 2 == 0 else 'dash'
        fig.add_trace(go.Scatter(
            x=group[nom_pk], y=group[parametre],
            mode='lines',
            name=str(date_val),
            line=dict(dash=dash)
        ))

    if seuils:
        seuils = seuils + [-seuil for seuil in seuils]
        max_parametre = np.nanmax(data[parametre])
        min_parametre = np.nanmin(data[parametre])

        for seuil in seuils:
            if min_parametre <= seuil and seuil <= max_parametre:
                fig.add_hline(
                    y=seuil,
                    line_dash="dot",
                    line_width=1.5,
                    line_color="red",
                )

    fig.update_layout(
        title=f'{parametre} en fonction de {nom_pk} pour chaque {nom_date}',
        xaxis_title=nom_pk,
        yaxis_title=parametre
    )
    fig.show()


def afficher_heatmap(data,
                     parametre='RIGHT_LEVEL_VALUE',
                     nom_pk='PK_NET_6_COEURS_ARRONDIS',
                     nom_date='MEASURE_DATE'):
    data = data.copy()
    data[nom_date] = pd.to_datetime(data[nom_date])

    data_pivot = data.pivot_table(index=nom_date, columns=nom_pk,
                                  values=parametre)
    data_pivot = data_pivot.sort_index()
    data_pivot = data_pivot.interpolate(axis=0)
    fig = px.imshow(
        data_pivot.values,
        labels=dict(x=nom_pk, y=nom_date, color=parametre),
        x=data_pivot.columns,
        y=[d.strftime('%Y-%m-%d') for d in data_pivot.index],
        aspect='auto',
        color_continuous_scale='jet',
        zmin=-8, zmax=8
    )
    fig.update_layout(
        title=f'{parametre} en fonction de {nom_pk} et du temps',
        xaxis_title=nom_pk,
        yaxis_title='Date'
    )
    return fig, data_pivot
