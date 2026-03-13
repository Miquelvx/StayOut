import streamlit as st
import fastf1
import pandas as pd

from Code.constants import TEAM_COLORS

@st.cache_data(show_spinner="Récupération du calendrier F1...")
def get_calendar(year):
    calendar = fastf1.get_event_schedule(year)
    
    df_calendar = calendar.copy()

    colonnes = [
        'RoundNumber','Country','Location','EventDate','EventName',
        'Session1','Session1DateUtc','Session2','Session2DateUtc',
        'Session3','Session3DateUtc','Session4','Session4DateUtc',
        'Session5','Session5DateUtc'
    ]
    
    df_calendar = df_calendar[colonnes]

    sessions_cols = ['Session1DateUtc', 'Session2DateUtc', 'Session3DateUtc','Session4DateUtc', 'Session5DateUtc']
    
    df_calendar['EventDate'] = pd.to_datetime(df_calendar['EventDate'])
    
    for col in sessions_cols:
        df_calendar[col] = pd.to_datetime(df_calendar[col]) + pd.Timedelta(hours=1)

    return df_calendar

@st.cache_data()
def get_current_standings(actual_date):
    drivers_df = pd.DataFrame()
    constructors_df = pd.DataFrame()
    drivers_data = {}
    constructors_data = {}

    df_calendar = get_calendar(actual_date.year)
    
    try:
        completed_events = df_calendar[df_calendar['Session5DateUtc'] < actual_date]

        for _, event in completed_events.iterrows():
            try:
                # Chargement des résultats de la course
                session = fastf1.get_session(actual_date.year, event['RoundNumber'], 'R')
                session.load(telemetry=False, weather=False, messages=False)
                
                if hasattr(session, 'results'):
                    for _, row in session.results.iterrows():
                        abb = row['Abbreviation']
                        team = row['TeamName']
                        pts = row['Points']
                        
                        # Pilotes
                        if abb not in drivers_data:
                            drivers_data[abb] = {'Pilote': row['FullName'], 'Ecurie': team, 'Points': 0.0, 'Victoires': 0}
                        drivers_data[abb]['Points'] += pts
                        if row['Position'] == 1.0:
                            drivers_data[abb]['Victoires'] += 1
                            
                        # Constructeurs
                        if team not in constructors_data:
                            constructors_data[team] = {'Ecurie': team, 'Points': 0.0, 'Victoires': 0}
                        constructors_data[team]['Points'] += pts
                        if row['Position'] == 1.0:
                            constructors_data[team]['Victoires'] += 1
                
                # Gestion des points Sprint
                if event['EventFormat'] == 'sprint':
                    s_sess = fastf1.get_session(actual_date.year, event['RoundNumber'], 'S')
                    s_sess.load(telemetry=False, weather=False, messages=False)
                    if hasattr(s_sess, 'results'):
                        for _, row in s_sess.results.iterrows():
                            abb = row['Abbreviation']
                            team = row['TeamName']
                            pts = row['Points']
                            
                            if abb in drivers_data: drivers_data[abb]['Points'] += pts
                            if team in constructors_data: constructors_data[team]['Points'] += pts
                            
            except Exception:
                continue

        # Création des DataFrames finaux
        if drivers_data:
            drivers_df = pd.DataFrame(drivers_data.values())
            drivers_df = drivers_df.sort_values(by=['Points', 'Victoires'], ascending=False).reset_index(drop=True)
            drivers_df['Pos'] = drivers_df.index + 1
            drivers_df = drivers_df[['Pos', 'Pilote', 'Ecurie', 'Points', 'Victoires']]
            
        if constructors_data:
            constructors_df = pd.DataFrame(constructors_data.values())
            constructors_df = constructors_df.sort_values(by=['Points', 'Victoires'], ascending=False).reset_index(drop=True)
            constructors_df['Pos'] = constructors_df.index + 1
            constructors_df = constructors_df[['Pos', 'Ecurie', 'Points', 'Victoires']]
        
    except Exception as e:
        st.error(f"Erreur lors de la récupération des classements : {e}")
        
    return drivers_df, constructors_df

@st.cache_data()
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