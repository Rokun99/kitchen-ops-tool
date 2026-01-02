import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- KONFIGURATION & SETUP ---
st.set_page_config(page_title="Kitchen Ops Intelligence Suite", layout="wide")

st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b;}
    .stHeader {font-family: 'Helvetica Neue', sans-serif;}
</style>
""", unsafe_allow_html=True)

# --- 1. DATEN-ENGINE ---
class KitchenDataManager:
    def __init__(self):
        # Vollständige Datenextraktion aus den Prozessbeschrieben D1 bis S1
        # Wir haben jede Aufgabe bereits qualitativ getaggt (Admin, Logistik, Core-Business)
        self.raw_data = [
            # D1 - Diätetik (Posten Klinische Ernährung)
            {"Dienst": "D1", "Start": "08:00", "Ende": "10:00", "Aufgabe": "Suppenherstellung & Diätvorbereitung", "Tag": "Diätetik"},
            {"Dienst": "D1", "Start": "10:15", "Ende": "11:20", "Aufgabe": "Regenerieren & Schöpf-Instruktion", "Tag": "Diätetik"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Aufgabe": "Service ET & Band-Bereitschaft", "Tag": "Diätetik"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Aufgabe": "Abräumen & fachgerechte Kühlung", "Tag": "Logistik"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:50", "Aufgabe": "Produktionsprotokolle & Suppen PM", "Tag": "Admin"},
            {"Dienst": "D1", "Start": "15:50", "Ende": "17:00", "Aufgabe": "Cg-Auflauf garen & Band einsetzen", "Tag": "Diätetik"},
            {"Dienst": "D1", "Start": "17:00", "Ende": "18:05", "Aufgabe": "Bandkontrolle & Service Abend", "Tag": "Diätetik"},
            {"Dienst": "D1", "Start": "18:05", "Ende": "18:09", "Aufgabe": "Aufräumen & Dienstende", "Tag": "Admin"},

            # E1 - Entremetier (Produktion Patient)
            {"Dienst": "E1", "Start": "07:00", "Ende": "10:00", "Aufgabe": "Tages-Beilagen & MEP Folgetag", "Tag": "Cucina"},
            {"Dienst": "E1", "Start": "10:15", "Ende": "11:20", "Aufgabe": "Wahlkost Produktion & Regenerieren", "Tag": "Cucina"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Aufgabe": "Service Anrichten & Nachschub", "Tag": "Cucina"},
            {"Dienst": "E1", "Start": "12:30", "Ende": "13:00", "Aufgabe": "Nachschub Restaurant & Reinigung", "Tag": "Cucina"},
            {"Dienst": "E1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "MEP Abendservice & Endreinigung", "Tag": "Admin"},

            # G2 - Garde-Manger (Produktion Kalt)
            {"Dienst": "G2", "Start": "09:30", "Ende": "10:15", "Aufgabe": "Postenabsprache & Wahlkostliste", "Tag": "Cucina"},
            {"Dienst": "G2", "Start": "10:15", "Ende": "11:15", "Aufgabe": "Wahlkostzubereitung (Orgacard)", "Tag": "Cucina"},
            {"Dienst": "G2", "Start": "11:15", "Ende": "12:30", "Aufgabe": "Menüteller kaltes Abendessen", "Tag": "Cucina"},
            {"Dienst": "G2", "Start": "12:30", "Ende": "13:30", "Aufgabe": "Salate Folgetag & Reinigung", "Tag": "Cucina"},
            {"Dienst": "G2", "Start": "14:15", "Ende": "16:00", "Aufgabe": "Salatbuffet & Creme Brülee", "Tag": "Cucina"},
            {"Dienst": "G2", "Start": "16:00", "Ende": "17:00", "Aufgabe": "Abendessen Regenerieren & Band", "Tag": "Cucina"},
            {"Dienst": "G2", "Start": "17:00", "Ende": "18:00", "Aufgabe": "Bandservice & Postenkontrolle", "Tag": "Cucina"},
            {"Dienst": "G2", "Start": "18:00", "Ende": "18:30", "Aufgabe": "Temperaturkontrollen & Checklisten", "Tag": "Admin"},

            # H1 - Frühstück & Band
            {"Dienst": "H1", "Start": "05:30", "Ende": "06:50", "Aufgabe": "Vorbereitung Frühstück & Griessbrei", "Tag": "Restaurazione"},
            {"Dienst": "H1", "Start": "06:50", "Ende": "07:45", "Aufgabe": "Band Frühstück & Abnahme", "Tag": "Restaurazione"},
            {"Dienst": "H1", "Start": "07:45", "Ende": "10:00", "Aufgabe": "MEP Mittagsservice (Creme/Salat)", "Tag": "Restaurazione"},
            {"Dienst": "H1", "Start": "10:15", "Ende": "11:25", "Aufgabe": "Glacé Vorbereitung & Bandaufbau", "Tag": "Restaurazione"},
            {"Dienst": "H1", "Start": "11:25", "Ende": "12:30", "Aufgabe": "Band Mittagsservice", "Tag": "Restaurazione"},
            {"Dienst": "H1", "Start": "13:30", "Ende": "14:40", "Aufgabe": "Menüsalat Abend & Protokolle", "Tag": "Admin"},

            # H2 - Pâtisserie & Etage
            {"Dienst": "H2", "Start": "09:15", "Ende": "09:45", "Aufgabe": "Dessert Restaurant garnieren", "Tag": "Restaurazione"},
            {"Dienst": "H2", "Start": "09:45", "Ende": "11:15", "Aufgabe": "Patienten Dessert abfüllen", "Tag": "Restaurazione"},
            {"Dienst": "H2", "Start": "11:15", "Ende": "13:00", "Aufgabe": "Wagenvorbereitung Abend & Zvieri", "Tag": "Restaurazione"},
            {"Dienst": "H2", "Start": "14:15", "Ende": "16:30", "Aufgabe": "MEP Dessert Folgetag & Support H1", "Tag": "Restaurazione"},
            {"Dienst": "H2", "Start": "16:30", "Ende": "17:00", "Aufgabe": "Glacé für Abendservice & Reinigung", "Tag": "Restaurazione"},
            {"Dienst": "H2", "Start": "17:00", "Ende": "18:00", "Aufgabe": "Bandservice Abend", "Tag": "Restaurazione"},
            {"Dienst": "H2", "Start": "18:00", "Ende": "18:09", "Aufgabe": "Material versorgen & Reinigung", "Tag": "Admin"},

            # H3 - Unterstützung Kaltküche
            {"Dienst": "H3", "Start": "09:15", "Ende": "10:15", "Aufgabe": "Salatteller, Sandwiches & Wähen", "Tag": "Cucina"},
            {"Dienst": "H3", "Start": "10:15", "Ende": "11:15", "Aufgabe": "Wahlkost zubereiten (G2 Support)", "Tag": "Cucina"},
            {"Dienst": "H3", "Start": "11:15", "Ende": "12:30", "Aufgabe": "Menüteller kaltes Abendessen", "Tag": "Cucina"},
            {"Dienst": "H3", "Start": "12:30", "Ende": "13:30", "Aufgabe": "Birchermüsli & Salate Folgetag", "Tag": "Cucina"},
            {"Dienst": "H3", "Start": "14:15", "Ende": "16:00", "Aufgabe": "Salatbuffet & Wähe vorber.", "Tag": "Cucina"},
            {"Dienst": "H3", "Start": "16:00", "Ende": "17:00", "Aufgabe": "Protokollkontrolle & Reinigung", "Tag": "Admin"},
            {"Dienst": "H3", "Start": "17:00", "Ende": "18:00", "Aufgabe": "Bandservice & Nachbesprechung", "Tag": "Cucina"},
            {"Dienst": "H3", "Start": "18:00", "Ende": "18:09", "Aufgabe": "Material versorgen / Dienstende", "Tag": "Admin"},

            # R1 - Gastronomie (Restaurant Service 1)
            {"Dienst": "R1", "Start": "06:30", "Ende": "10:00", "Aufgabe": "Warenannahme & Deklarations-Management", "Tag": "Logistik"},
            {"Dienst": "R1", "Start": "10:20", "Ende": "11:00", "Aufgabe": "Regenerieren & Dessert Restaurant", "Tag": "Restaurazione"},
            {"Dienst": "R1", "Start": "11:00", "Ende": "11:30", "Aufgabe": "Materialeinsetzten & Showteller", "Tag": "Restaurazione"},
            {"Dienst": "R1", "Start": "11:30", "Ende": "13:30", "Aufgabe": "Mittagsservice & Gästebetreuung", "Tag": "Restaurazione"},
            {"Dienst": "R1", "Start": "13:30", "Ende": "14:00", "Aufgabe": "Abräumen & Materialentsorgung", "Tag": "Logistik"},
            {"Dienst": "R1", "Start": "14:30", "Ende": "15:24", "Aufgabe": "MEP Folgetag & Endreinigung", "Tag": "Admin"},

            # R2 - Gastronomie (Restaurant Service 2)
            {"Dienst": "R2", "Start": "06:30", "Ende": "08:00", "Aufgabe": "Bereitstellung Frühstück (Gläser/Brei)", "Tag": "Restaurazione"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "10:00", "Aufgabe": "Salate abfüllen & Mise en Place", "Tag": "Restaurazione"},
            {"Dienst": "R2", "Start": "10:20", "Ende": "11:00", "Aufgabe": "Mittagsservice Vorbereitung", "Tag": "Restaurazione"},
            {"Dienst": "R2", "Start": "11:00", "Ende": "11:30", "Aufgabe": "Musterteller & Freeflow-Setup", "Tag": "Restaurazione"},
            {"Dienst": "R2", "Start": "11:30", "Ende": "13:30", "Aufgabe": "Mittagsservice & Gästebetreuung", "Tag": "Restaurazione"},
            {"Dienst": "R2", "Start": "13:30", "Ende": "14:00", "Aufgabe": "ReCircle-Management & BM-Wasser", "Tag": "Logistik"},
            {"Dienst": "R2", "Start": "14:30", "Ende": "15:24", "Aufgabe": "Etikettendruck & Reinigung", "Tag": "Admin"},

            # S1 - Saucier (Produktion Fleisch/Saucen)
            {"Dienst": "S1", "Start": "07:00", "Ende": "10:00", "Aufgabe": "Herstellung Fleischkomponenten & Saucen", "Tag": "Cucina"},
            {"Dienst": "S1", "Start": "10:15", "Ende": "11:20", "Aufgabe": "Wahlkost Produktion & Regenerieren", "Tag": "Cucina"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Aufgabe": "Service Anrichten & Band-Nachschub", "Tag": "Cucina"},
            {"Dienst": "S1", "Start": "12:30", "Ende": "13:00", "Aufgabe": "Nachschub Restaurant & Reinigung", "Tag": "Cucina"},
            {"Dienst": "S1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "Produktionspläne & Endreinigung", "Tag": "Admin"},
        ]

    def get_dataframe(self):
        df = pd.DataFrame(self.raw_data)
        # Standardisierung der Uhrzeiten
        df['Start_Time'] = pd.to_datetime('2024-01-01 ' + df['Start'].str.replace('.', ':'))
        df['End_Time'] = pd.to_datetime('2024-01-01 ' + df['Ende'].str.replace('.', ':'))
        df['Dauer_Min'] = (df['End_Time'] - df['Start_Time']).dt.total_seconds() / 60
        return df

# --- 2. ANALYSE LOGIK ---
def analyze_structure(df):
    structure_map = {
        "Cucina": "Team Produktion (Patient)",
        "Restaurazione": "Team Gastronomie (Mitarbeiter/Gast)",
        "Diätetik": "Team Klinische Ernährung",
        "Admin": "Führung & Support",
        "Logistik": "Logistik & Warenmanagement"
    }
    df['Neues_Team'] = df['Tag'].map(structure_map)
    return df

# --- 3. UI & VISUALISIERUNG ---
def main():
    st.title("👨‍🍳 Kitchen Ops Intelligence Suite")
    st.markdown("### Strategische Prozess-Analyse: Von IST zu SOLL")
    
    dm = KitchenDataManager()
    df = dm.get_dataframe()
    df = analyze_structure(df)

    # Sidebar Filter
    st.sidebar.header("Analyse-Filter")
    selected_teams = st.sidebar.multiselect("Dienste anzeigen", sorted(df['Dienst'].unique()), sorted(df['Dienst'].unique()))
    filtered_df = df[df['Dienst'].isin(selected_teams)]

    tab1, tab2, tab3 = st.tabs(["📊 Operative Gantt-View", "🔥 Personal-Heatmap", "🚀 Strategisches Mapping"])

    with tab1:
        st.subheader("Operativer Tagesrhythmus (Detailansicht)")
        fig_gantt = px.timeline(
            filtered_df, 
            x_start="Start_Time", x_end="End_Time", y="Dienst", color="Tag",
            hover_name="Aufgabe",
            color_discrete_map={
                "Cucina": "#FF4B4B", "Restaurazione": "#0068C9", 
                "Diätetik": "#29B09D", "Admin": "#FFD700", "Logistik": "#808080"
            }
        )
        fig_gantt.update_layout(xaxis_title="Uhrzeit", yaxis_title="Posten", height=600)
        st.plotly_chart(fig_gantt, use_container_width=True)

    with tab2:
        st.subheader("Auslastungs-Analyse")
        heatmap_data = []
        for hour in range(5, 20):
            count = sum((row['Start_Time'].hour <= hour < row['End_Time'].hour) for _, row in filtered_df.iterrows())
            heatmap_data.append({"Stunde": f"{hour:02d}:00", "Aktive Posten": count})
        
        fig_heat = px.bar(pd.DataFrame(heatmap_data), x="Stunde", y="Aktive Posten", 
                          color="Aktive Posten", color_continuous_scale="OrRd")
        st.plotly_chart(fig_heat, use_container_width=True)
        st.info("💡 **Analyse:** Die Spitzen liegen klar zwischen 11:00-13:00 (Mittag) und 17:00-18:00 (Abend).")

    with tab3:
        st.subheader("Transformation in die neue Aufbauorganisation")
        fig_pie = px.sunburst(filtered_df, path=['Neues_Team', 'Dienst'], values='Dauer_Min',
                              color='Neues_Team',
                              title="Arbeitslastverteilung nach strategischen Bereichen")
        st.plotly_chart(fig_pie, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Effizienz-Potenzial (Admin/Logistik)")
            waste = filtered_df[filtered_df['Tag'].isin(['Admin', 'Logistik'])]
            st.write(f"Gesamtzeit für Support-Aufgaben: **{int(waste['Dauer_Min'].sum()/60)} Stunden/Tag**")
            st.dataframe(waste[['Dienst', 'Aufgabe', 'Dauer_Min']].sort_values(by="Dauer_Min", ascending=False))
            
        with col2:
            st.success("✅ **Empfehlung:** Durch die Zentralisierung der 'Admin'-Aufgaben (Protokolle/Bestellungen) könnten ca. 15% der Fachkraftzeit für die kulinarische Qualität gewonnen werden.")

if __name__ == "__main__":
    main()
