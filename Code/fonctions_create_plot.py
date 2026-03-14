import streamlit as st
import plotly.graph_objects as go

from Code.constants import TEAM_COLORS

@st.cache_data(show_spinner="Calcul des classements F1...")
def display_f1_standings(drivers_df, constructors_df):
    # CSS pour le style "Live Timing"
    st.markdown("""
        <style>
        .standing-row {
            display: flex;
            align-items: center;
            background-color: #15151E;
            margin-bottom: 6px;
            padding: 10px 15px;
            border-radius: 4px;
        }
        .standing-pos {
            width: 30px;
            font-weight: bold;
            font-size: 0.9em;
            color: #949498;
        }
        .team-bar {
            width: 4px;
            height: 20px;
            margin-right: 12px;
            border-radius: 2px;
        }
        .standing-name {
            flex-grow: 1;
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }
        .standing-pts {
            font-weight: bold;
            font-family: 'Arial Black', sans-serif;
            min-width: 40px;
            text-align: right;
        }
        .podium-card {
            background: linear-gradient(180deg, #1f1f2a 0%, #15151e 100%);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-bottom: 3px solid #FF1801;
            margin-bottom: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2, gap="large")

    # --- CLASSEMENT PILOTES ---
    with col_left:
        st.markdown("### 🏎️ CLASSEMENT PILOTES")
        if not drivers_df.empty:
            # Podium Top 3 (Version simplifiée sans victoires)
            p_cols = st.columns(3)
            order = [1, 0, 2] # P2, P1, P3
            for i, idx in enumerate(order):
                if idx < len(drivers_df):
                    row = drivers_df.iloc[idx]
                    color = TEAM_COLORS.get(row['Ecurie'], '#FFFFFF')
                    with p_cols[i]:
                        st.markdown(f"""
                            <div class="podium-card" style="border-top: 4px solid {color};">
                                <div style="font-size:0.7em; color:#949498; font-weight:bold;">P{row['Pos']}</div>
                                <div style="font-weight:bold; font-size:1em;">{row['Pilote'].split()[-1].upper()}</div>
                                <div style="color:#FF1801; font-weight:bold;">{int(row['Points'])}</div>
                            </div>
                        """, unsafe_allow_html=True)

            # Reste du classement (P4+)
            for _, row in drivers_df.iloc[3:].iterrows():
                color = TEAM_COLORS.get(row['Ecurie'], '#FFFFFF')
                st.markdown(f"""
                    <div class="standing-row">
                        <div class="standing-pos">{row['Pos']}</div>
                        <div class="team-bar" style="background-color: {color};"></div>
                        <div class="standing-name">{row['Pilote']}</div>
                        <div class="standing-pts">{int(row['Points'])}</div>
                    </div>
                """, unsafe_allow_html=True)

    # --- CLASSEMENT CONSTRUCTEURS ---
    with col_right:
        st.markdown("### 🏗️ CLASSEMENT ECURIES")
        if not constructors_df.empty:
            # Podium Top 3
            c_cols = st.columns(3)
            for i, idx in enumerate(order):
                if idx < len(constructors_df):
                    row = constructors_df.iloc[idx]
                    color = TEAM_COLORS.get(row['Ecurie'], '#FFFFFF')
                    with c_cols[i]:
                        name = row['Ecurie'].replace(' Racing', '').replace('F1 Team', '').upper()
                        with c_cols[i]:
                            st.markdown(f"""
                                <div class="podium-card" style="border-top: 4px solid {color};">
                                    <div style="font-size:0.7em; color:#949498; font-weight:bold;">P{row['Pos']}</div>
                                    <div style="font-weight:bold; font-size:0.8em; height:30px; display:flex; align-items:center; justify-content:center;">{name}</div>
                                    <div style="color:#FF1801; font-weight:bold;">{int(row['Points'])}</div>
                                </div>
                            """, unsafe_allow_html=True)

            # Reste du classement (P4+)
            for _, row in constructors_df.iloc[3:].iterrows():
                color = TEAM_COLORS.get(row['Ecurie'], '#FFFFFF')
                st.markdown(f"""
                    <div class="standing-row">
                        <div class="standing-pos">{row['Pos']}</div>
                        <div class="team-bar" style="background-color: {color};"></div>
                        <div class="standing-name">{row['Ecurie']}</div>
                        <div class="standing-pts">{int(row['Points'])}</div>
                    </div>
                """, unsafe_allow_html=True)


@st.cache_data()
def create_lap_chart(_session):
    fig = go.Figure()

    # Récupérer la liste des abréviations des pilotes présents dans la session
    drivers = _session.drivers
    driver_abbs = [_session.get_driver(d)['Abbreviation'] for d in drivers]

    sorted_drivers = _session.results.sort_values(by='ClassifiedPosition')['Abbreviation'].tolist()

    for abb in driver_abbs:
        # Filtrer les données pour le pilote
        driver_laps = _session.laps.pick_driver(abb)
        
        # Si le pilote n'a pas de tours (ex: DNS), on passe au suivant
        if driver_laps.empty:
            continue
            
        # Récupérer les infos du pilote
        driver_info = _session.get_driver(abb)
        team_name = driver_info['TeamName']
        color = TEAM_COLORS.get(team_name, '#808080')
        
        # Ajouter la ligne au graphique
        fig.add_trace(go.Scatter(
            x=driver_laps['LapNumber'],
            y=driver_laps['Position'],
            mode='lines+markers',
            name=f"{abb} ({team_name})",
            line=dict(color=color, width=2),
            marker=dict(size=4),
            # Rendre le survol plus propre
            hovertemplate="<b>" + abb + "</b><br>Pos: %{y}<extra></extra>"
        ))

    # Personnalisation de l'affichage
    fig.update_layout(
        title=dict(
            text=f"<b>Évolution des positions</b><br><span style='font-size:14px; color:grey'>{_session.event['EventName']} {_session.event.year}</span>",
            x=0, # Aligné à gauche
            font=dict(size=24)
        ),
        xaxis=dict(
            title="Tour",
            showgrid=True, 
            gridcolor='rgba(255, 255, 255, 0.1)', 
            zeroline=False,
            dtick=5,
            hoverformat="Tour %d",
        ),
        yaxis=dict(
            title="Position",
            autorange="reversed",
            tickmode='linear',
            tick0=1,
            dtick=1,
            gridcolor='rgba(255, 255, 255, 0.1)',
            range=[len(sorted_drivers) + 0.5, 0.5],
            zeroline=False,
            fixedrange=True # Empêche le zoom vertical bizarre
        ),
        template="plotly_dark",
        height=700,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(30, 30, 30,1)", # Fond sombre semi-transparent
            font_size=10,
            font_family="Arial",
            bordercolor="white"
            ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=12),
            bgcolor="rgba(0,0,0,0)"
        )
    )

    return fig