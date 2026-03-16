import streamlit as st
import fastf1
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

import plotly.graph_objects as go

from Code.fonctions_get_data import get_calendar,get_race_session, calculate_race_metrics
from Code.fonctions_create_plot import create_lap_chart

from Code.constants import TEAM_COLORS

# ----------------------------
# CONFIG
# ----------------------------

st.set_page_config(page_title="StayOut - Telemetry", layout="wide")

def get_drivers_telemetry(_session, selected_drivers):
    telemetry_dict = {}
    
    for abb in selected_drivers:
        # On récupère le meilleur tour du pilote
        laps_driver = _session.laps.pick_driver(abb)
        fastest_lap = laps_driver.pick_fastest()
        
        # On extrait la télémétrie et on ajoute la distance (crucial pour l'alignement)
        telemetry = fastest_lap.get_telemetry().add_distance()
        
        # On stocke aussi le temps pour l'afficher dans la légende
        lap_time = fastest_lap['LapTime']
        # Formatage propre du temps (MM:SS.ms)
        str_lap_time = str(lap_time)[10:19] 
        
        telemetry_dict[abb] = {
            'telemetry': telemetry,
            'lap_time': str_lap_time,
            'team': fastest_lap['Team']
        }
        
    return telemetry_dict

def plot_comparison_telemetry(telemetry_data):
    fig = go.Figure()

    for abb, data in telemetry_data.items():
        telemetry = data['telemetry']
        color = TEAM_COLORS.get(data['team'], '#808080')
        
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'],
            y=telemetry['Speed'],
            mode='lines',
            name=f"{abb} ({data['lap_time']})",
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{abb}</b><br>Vitesse: %{{y}} km/h<br>Distance: %{{x}}m<extra></extra>"
        ))

    fig.update_layout(
        title="<b>Comparaison de Vitesse : Meilleur Tour</b>",
        xaxis_title="Distance (m)",
        yaxis_title="Vitesse (km/h)",
        template="plotly_dark",
        height=500,
        hovermode="x unified", # Permet de voir la vitesse de tous les pilotes au même point précis
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

sess = fastf1.get_session(2026, 2, 'Q')
sess.load(telemetry=True, weather=False, messages=False)

st.write("---")
st.subheader("🏎️ Comparaison de Télémétrie")

# On récupère la liste des pilotes ayant fait au moins un tour chrono
available_drivers = sess.laps['Driver'].unique().tolist()

selected_drivers = st.multiselect(
    "Choisir les pilotes à comparer (max 3 recommandé pour la lisibilité)",
    options=available_drivers,
    default=available_drivers[:2] # Par défaut on prend les deux premiers
)

if selected_drivers:
    try:
        # Récupération des données
        telemetry_data = get_drivers_telemetry(sess, selected_drivers)
        
        # Affichage du graph de vitesse
        fig_speed = plot_comparison_telemetry(telemetry_data)
        st.plotly_chart(fig_speed, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erreur lors du chargement de la télémétrie : {e}")
else:
    st.info("Veuillez sélectionner au moins un pilote.")