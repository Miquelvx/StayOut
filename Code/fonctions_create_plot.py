import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from Code.constants import TEAM_COLORS
from Code.fonctions_get_data import get_circuit_corners

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


def create_lap_chart(_session):
    fig = go.Figure()

    sorted_drivers = _session.results.sort_values(by='ClassifiedPosition')['Abbreviation'].tolist()

    for abb in sorted_drivers:
        driver_res = _session.results[_session.results['Abbreviation'] == abb].iloc[0]
        
        team_name = driver_res['TeamName']
        grid_pos = driver_res['GridPosition']
        final_pos = int(driver_res['Position'])
        
        driver_laps = _session.laps.pick_driver(abb)

        x_values = [0]
        y_values = [grid_pos]

        # Si le pilote a fait des tours, on les ajoute à la suite
        if not driver_laps.empty:
            x_values.extend(driver_laps['LapNumber'].tolist())
            y_values.extend(driver_laps['Position'].tolist())
        
        color = TEAM_COLORS.get(team_name, '#808080')
        
        # Ajouter la ligne au graphique
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name=f"P{final_pos} - {abb} ({team_name})",
            line=dict(color=color, width=2),
            marker=dict(size=4),
            legendrank=final_pos,
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
            traceorder="normal",
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

def create_comparison_telemetry(telemetry_data):
    fig = go.Figure()

    color_usage_count = {}

    for abb, data in telemetry_data.items():
        telemetry = data['telemetry']
        team_color = TEAM_COLORS.get(data['team'], '#808080')
        
        color_usage_count[team_color] = color_usage_count.get(team_color, 0) + 1
        line_style = 'solid'
        if color_usage_count[team_color] == 2:
            line_style = 'dash'
        elif color_usage_count[team_color] > 2:
            line_style = 'dot'
        
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'],
            y=telemetry['Speed'],
            mode='lines',
            name=f"{abb} ({data['lap_time']})",
            line=dict(
                color=team_color, 
                width=2, 
                dash=line_style  # Application du style dynamique
            ),
            hovertemplate=f"<b>{abb}</b><br>Vitesse: %{{y}} km/h<br>Distance: %{{x}}m<extra></extra>"
        ))

    fig.update_layout(
        title="<b>Comparaison de Vitesse : Meilleur Tour</b>",
        xaxis_title="Distance (m)",
        yaxis_title="Vitesse (km/h)",
        template="plotly_dark",
        height=500,
        hovermode="x unified",
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(
                size=12,         
                color="white"    
            )
        ),
        showlegend=True
    )

    return fig

def create_pedal_comparison(telemetry_data):
    # On crée 2 lignes : une pour l'accélérateur, une pour le frein
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.1,
        subplot_titles=("Accélérateur (%)", "Frein (On/Off)"),
        row_heights=[0.5, 0.5]
    )

    color_usage_count = {}

    for abb, data in telemetry_data.items():
        telemetry = data['telemetry']
        team_color = TEAM_COLORS.get(data['team'], '#808080')
        
        # Gestion du style de ligne pour les coéquipiers
        color_usage_count[team_color] = color_usage_count.get(team_color, 0) + 1
        line_style = 'dash' if color_usage_count[team_color] == 2 else 'solid'
        
        # --- 1. THROTTLE (Ligne 1) ---
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'], 
            y=telemetry['Throttle'],
            name=f"{abb}", 
            line=dict(color=team_color, width=2, dash=line_style),
            legendgroup=abb,
            hovertemplate="<b>" + abb + "</b><br>Accel: %{y}%<extra></extra>"
        ), row=1, col=1)

        # --- 2. BRAKE (Ligne 2) ---
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'], 
            y=telemetry['Brake'],
            name=f"{abb} (Frein)", 
            line=dict(color=team_color, width=2, dash=line_style),
            legendgroup=abb,
            showlegend=False, # On ne l'affiche qu'une fois dans la légende
            hovertemplate="<b>" + abb + "</b><br>Frein: %{y}<extra></extra>"
        ), row=2, col=1)

    # --- Configuration Visuelle ---
    fig.update_layout(
        height=700,
        template="plotly_dark",
        title_text="<b>Analyse du Pilotage : Pédalier</b>",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        showlegend=True
    )

    # Paramètres des axes
    fig.update_yaxes(title_text="Throttle %", range=[-5, 105], row=1, col=1)
    fig.update_yaxes(title_text="Brake", range=[-0.1, 1.1], dtick=1, row=2, col=1)
    fig.update_xaxes(title_text="Distance (m)", row=2, col=1)

    return fig

def create_gear_comparison(telemetry_data):
    fig = go.Figure()
    
    color_usage_count = {}

    for abb, data in telemetry_data.items():
        telemetry = data['telemetry']
        team_color = TEAM_COLORS.get(data['team'], '#808080')
        
        # Gestion du style de ligne (Plein vs Tirets)
        color_usage_count[team_color] = color_usage_count.get(team_color, 0) + 1
        line_style = 'dash' if color_usage_count[team_color] == 2 else 'solid'
        
        # On utilise line_shape='hv' pour un tracé en escalier (Gear Shift)
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'], 
            y=telemetry['nGear'],
            mode='lines',
            name=f"Rapports - {abb}",
            line=dict(
                color=team_color, 
                width=3, 
                dash=line_style,
                shape='hv' # Important : dessine des marches d'escalier
            ),
            hovertemplate=f"<b>{abb}</b><br>Rapport: %{{y}}<br>Distance: %{{x}}m<extra></extra>"
        ))

    fig.update_layout(
        title="<b>Comparaison des Rapports de Boîte (Gear)</b>",
        xaxis_title="Distance (m)",
        yaxis_title="Rapport Engagé",
        yaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=1,
            range=[0.5, 8.5] # La boîte F1 va de 1 à 8
        ),
        template="plotly_dark",
        height=450,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        showlegend=True
    )

    return fig

def add_corners_to_fig(fig, corners):
    if corners is None:
        return fig
    else:
        for _, corner in corners.iterrows():
            fig.add_vline(
                x=corner['Distance'],
                line_width=1,
                line_dash="dot",
                line_color="rgba(255, 255, 255, 0.3)",
                annotation_text=f"V{int(corner['Number'])}", # "V" pour Virage
                annotation_position="bottom",
                annotation_font_size=10,
                annotation_font_color="grey",
            )
        return fig