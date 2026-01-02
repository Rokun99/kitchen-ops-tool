import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Kitchen Intelligence | Ops Suite",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM BRANDING & UX STYLING ---
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    
    /* Card Design */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
        margin-bottom: 20px;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    /* Status Colors */
    .stProgress > div > div > div > div { background-color: #3b82f6; }
</style>
""", unsafe_allow_html=True)

# --- DATA ENGINE ---
class KitchenDataManager:
    def __init__(self):
        # Daten mit deutschen Kategorien: Produktion, Gastronomie, Verwaltung, Logistik, Diätetik
        self.raw_data = [
            # D1 - Diätetik
            {"Posten": "D1", "Start": "08:00", "Ende": "10:00", "Aufgabe": "Suppenküche & Diät-Vorbereitung", "Bereich": "Diätetik"},
            {"Posten": "D1", "Start": "10:15", "Ende": "11:20", "Aufgabe": "Regenerieren & Instruktion Band", "Bereich": "Diätetik"},
            {"Posten": "D1", "Start": "11:20", "Ende": "12:20", "Aufgabe": "Service ET & Band-Bereitschaft", "Bereich": "Diätetik"},
            {"Posten": "D1", "Start": "12:20", "Ende": "12:45", "Aufgabe": "Abräumen & Lager-Sicherung", "Bereich": "Logistik"},
            {"Posten": "D1", "Start": "14:30", "Ende": "15:50", "Aufgabe": "Produktionsprotokolle & PM", "Bereich": "Verwaltung"},
            {"Posten": "D1", "Start": "15:50", "Ende": "18:05", "Aufgabe": "Service Abend & Bandkontrolle", "Bereich": "Diätetik"},
            
            # E1 - Entremetier
            {"Posten": "E1", "Start": "07:00", "Ende": "10:00", "Aufgabe": "Tages-Beilagen & MEP Folgetag", "Bereich": "Produktion"},
            {"Posten": "E1", "Start": "10:15", "Ende": "12:30", "Aufgabe": "Wahlkost & Service Anrichten", "Bereich": "Produktion"},
            {"Posten": "E1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "MEP Abend & Postenreinigung", "Bereich": "Verwaltung"},

            # G2 - Garde-Manger
            {"Posten": "G2", "Start": "09:30", "Ende": "13:30", "Aufgabe": "Kalte Küche, Salate & Dessert", "Bereich": "Produktion"},
            {"Posten": "G2", "Start": "14:15", "Ende": "18:00", "Aufgabe": "Buffet, MEP & Bandservice", "Bereich": "Produktion"},
            {"Posten": "G2", "Start": "18:00", "Ende": "18:30", "Aufgabe": "Checklisten & Kontrollen", "Bereich": "Verwaltung"},

            # H1 - Frühstück
            {"Posten": "H1", "Start": "05:30", "Ende": "10:00", "Aufgabe": "Frühstücksservice & Band", "Bereich": "Gastronomie"},
            {"Posten": "H1", "Start": "10:15", "Ende": "12:30", "Aufgabe": "Glacé & Band Mittag", "Bereich": "Gastronomie"},
            {"Posten": "H1", "Start": "13:30", "Ende": "14:40", "Aufgabe": "Protokolle & MHD Prüfung", "Bereich": "Verwaltung"},

            # H2 - Pâtisserie
            {"Posten": "H2", "Start": "09:15", "Ende": "13:00", "Aufgabe": "Desserts Restaurant & Patienten", "Bereich": "Gastronomie"},
            {"Posten": "H2", "Start": "14:15", "Ende": "18:00", "Aufgabe": "Zvieri & Abendservice", "Bereich": "Gastronomie"},

            # R1 & R2 - Gastronomie
            {"Posten": "R1", "Start": "06:30", "Ende": "10:00", "Aufgabe": "Warenannahme & Deklaration", "Bereich": "Logistik"},
            {"Posten": "R1", "Start": "10:20", "Ende": "15:24", "Aufgabe": "Mittagsservice & Restaurant", "Bereich": "Gastronomie"},
            {"Posten": "R2", "Start": "06:30", "Ende": "10:00", "Aufgabe": "Frühstück MEP & Salate", "Bereich": "Gastronomie"},
            {"Posten": "R2", "Start": "10:20", "Ende": "15:24", "Aufgabe": "Mittagsservice & ReCircle", "Bereich": "Gastronomie"},

            # S1 - Saucier
            {"Posten": "S1", "Start": "07:00", "Ende": "10:00", "Aufgabe": "Fleischkomponenten & Saucen", "Bereich": "Produktion"},
            {"Posten": "S1", "Start": "10:15", "Ende": "13:00", "Aufgabe": "Wahlkost & Band-Support", "Bereich": "Produktion"},
            {"Posten": "S1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "Produktionspläne & Hygiene", "Bereich": "Verwaltung"},
        ]

    def get_df(self):
        df = pd.DataFrame(self.raw_data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'].str.replace('.', ':'))
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'].str.replace('.', ':'))
        df['Minuten'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- UI LOGIC ---
def main():
    dm = KitchenDataManager()
    df = dm.get_df()

    # --- SIDEBAR (MODERN) ---
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/restaurant-menu.png", width=80)
        st.title("Ops Filter")
        st.markdown("---")
        
        alle_bereiche = sorted(df['Bereich'].unique())
        selected_bereiche = st.multiselect("Fokus-Bereiche", alle_bereiche, default=alle_bereiche)
        
        st.markdown("---")
        st.info("Diese Suite transformiert Prozessbeschriebe in strategische Kennzahlen.")

    # --- MAIN CONTENT ---
    st.markdown('<div class="main-header">Kitchen Intelligence Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Optimierung der Küchenorganisation & Prozesslandschaft</div>', unsafe_allow_html=True)

    # Filtered Data
    mask = df['Bereich'].isin(selected_bereiche)
    f_df = df[mask]

    # --- KPI ROW ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><small>Gesamt-Arbeitszeit</small><h3>{int(f_df["Minuten"].sum()/60)}h</h3></div>', unsafe_allow_html=True)
    with col2:
        prod_h = int(f_df[f_df["Bereich"] == "Produktion"]["Minuten"].sum()/60)
        st.markdown(f'<div class="metric-card"><small>Produktions-Fokus</small><h3>{prod_h}h</h3></div>', unsafe_allow_html=True)
    with col3:
        gast_h = int(f_df[f_df["Bereich"] == "Gastronomie"]["Minuten"].sum()/60)
        st.markdown(f'<div class="metric-card"><small>Gastronomie-Fokus</small><h3>{gast_h}h</h3></div>', unsafe_allow_html=True)
    with col4:
        admin_ratio = (f_df[f_df["Bereich"] == "Verwaltung"]["Minuten"].sum() / f_df["Minuten"].sum()) * 100
        st.markdown(f'<div class="metric-card"><small>Verwaltungs-Anteil</small><h3>{admin_ratio:.1f}%</h3></div>', unsafe_allow_html=True)

    # --- TABS ---
    tab_gantt, tab_load, tab_strategy = st.tabs(["🕒 Operative Timeline", "📊 Belastungsprofil", "🚀 Strategie-Mapping"])

    with tab_gantt:
        st.subheader("Tagesablauf nach Posten")
        fig = px.timeline(
            f_df, x_start="Start_DT", x_end="End_DT", y="Posten", color="Bereich",
            hover_name="Aufgabe",
            color_discrete_map={
                "Produktion": "#EF4444", "Gastronomie": "#3B82F6", 
                "Diätetik": "#10B981", "Verwaltung": "#F59E0B", "Logistik": "#64748B"
            },
            category_orders={"Posten": sorted(f_df['Posten'].unique(), reverse=True)}
        )
        fig.update_layout(
            xaxis_title="Uhrzeit", yaxis_title="",
            plot_bgcolor="white", paper_bgcolor="white",
            height=500, margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab_load:
        st.subheader("Ressourcen-Einsatz über den Tag")
        # Generate load curve
        load_data = []
        for h in range(5, 20):
            for m in [0, 30]:
                check_time = datetime(2026, 1, 1, h, m)
                active_count = len(f_df[(f_df['Start_DT'] <= check_time) & (f_df['End_DT'] > check_time)])
                load_data.append({"Zeit": f"{h:02d}:{m:02d}", "Aktive_Posten": active_count})
        
        load_df = pd.DataFrame(load_data)
        fig_area = px.area(load_df, x="Zeit", y="Aktive_Posten", line_shape="spline",
                           color_discrete_sequence=["#3B82F6"])
        fig_area.update_layout(plot_bgcolor="white", xaxis_tickangle=-45)
        st.plotly_chart(fig_area, use_container_width=True)
        st.info("Insight: Die Grafik zeigt die personelle Dichte. Ideal zur Identifikation von 'Zimmerstunden' oder Personalengpässen beim Schöpfen.")

    with tab_strategy:
        st.subheader("Transformation: IST-Tätigkeiten zu SOLL-Struktur")
        
        # Sunburst for Strategy
        fig_sun = px.sunburst(
            f_df, path=['Bereich', 'Posten', 'Aufgabe'], values='Minuten',
            color='Bereich',
            color_discrete_map={
                "Produktion": "#EF4444", "Gastronomie": "#3B82F6", 
                "Diätetik": "#10B981", "Verwaltung": "#F59E0B", "Logistik": "#64748B"
            }
        )
        fig_sun.update_layout(height=650)
        st.plotly_chart(fig_sun, use_container_width=True)
        
        # Recommendations
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.warning("⚠️ **Potenzial: Fachfremde Aufgaben**")
            waste = f_df[f_df['Bereich'].isin(['Verwaltung', 'Logistik'])].groupby('Posten')['Minuten'].sum().reset_index()
            waste['Stunden'] = (waste['Minuten']/60).round(1)
            st.write("Folgende Posten leisten hohen Verwaltungsaufwand:")
            st.dataframe(waste[['Posten', 'Stunden']].sort_values('Stunden', ascending=False), hide_index=True)
            
        with c2:
            st.success("✅ **Strategisches Zielbild**")
            st.markdown("""
            1. **Zentralisierung Logistik:** R1/D1 entlasten durch dedizierte Warenannahme.
            2. **Digitale Verwaltung:** Reduktion der manuellen Protokollzeit bei S1/E1/H1.
            3. **Fokus Produktion:** Verschiebung von 10-15% der Zeit zurück in die Kulinarik.
            """)

if __name__ == "__main__":
    main()
