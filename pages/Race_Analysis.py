import streamlit as st
import fastf1
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os



session = fastf1.get_session(2023, 1, 'R')
session.load(telemetry=True, weather=False, messages=False)

import plotly.graph_objects as go
import fastf1.plotting

# Activer le support des couleurs FastF1
fastf1.plotting.setup_mpl(misc_mpl_mods=False)

# (On suppose que votre session est déjà chargée)
# session = fastf1.get_session(2023, 1, 'R')
# session.load(telemetry=True, weather=False, messages=False)

fig = go.Figure()

# Récupérer la liste des pilotes
drivers = session.drivers
# On transforme les numéros en abréviations (ex: 'VER')
driver_abbs = [session.get_driver(d)['Abbreviation'] for d in drivers]

for abb in driver_abbs:
    # Filtrer les données pour le pilote
    driver_laps = session.laps.pick_driver(abb)
    
    # Récupérer la couleur officielle du pilote
    color = fastf1.plotting.driver_color(abb)
    
    # Ajouter la ligne au graphique Plotly
    fig.add_trace(go.Scatter(
        x=driver_laps['LapNumber'],
        y=driver_laps['Position'],
        mode='lines+markers',
        name=abb,
        line=dict(color=color, width=2),
        marker=dict(size=4),
        hovertemplate=f"Pilote: {abb}<br>Tour: %{{x}}<br>Position: %{{y}}<extra></extra>"
    ))

# Personnalisation de l'affichage
fig.update_layout(
    title=f"Évolution des positions - {session.event['EventName']} {session.event.year}",
    xaxis_title="Tour",
    yaxis_title="Position",
    yaxis=dict(
        autorange="reversed",  # Inverse l'axe pour que P1 soit en haut
        tickmode='linear',
        tick0=1,
        dtick=1,
        range=[20.5, 0.5]
    ),
    template="plotly_dark", # Style sombre pour coller à l'univers F1
    height=700,
    hovermode="x unified" # Permet de voir toutes les positions en survolant un tour
)

fig.show()