import streamlit as st
import fastf1
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os

import plotly.graph_objects as go

from Code.fonctions_get_data import calculate_race_metrics
from Code.fonctions_create_plot import create_lap_chart

# ----------------------------
# CONFIG
# ----------------------------

st.set_page_config(page_title="StayOut - Race Analysis", layout="wide")

# ----------------------------
# CONFIG FASTF1 CACHE
# ----------------------------


# ----------------------------
# MAIN RACE ANALYSIS PAGE
# ----------------------------

def main():

    st.title("Race analysis")
    session = fastf1.get_session(2026, 1, 'R')
    session.load(telemetry=True, weather=False, messages=False)

    fig = create_lap_chart(session)

    st.plotly_chart(fig, use_container_width=True)

    # --- Affichage Streamlit ---
    total_ov, dnfs, top_ov = calculate_race_metrics(session)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Dépassements", total_ov)
    col2.metric("Abandons (DNF)", dnfs)
    col3.metric("Roi du dépassement", top_ov['Driver'], f"{top_ov['Overtakes']} fois")


if __name__ == "__main__":
    main()