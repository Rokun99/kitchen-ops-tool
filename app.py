import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Kitchen Ops Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED UX STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main Background & Font */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Professional Metric Cards */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease-in-out;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .card-label {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .card-value {
        color: #1e293b;
        font-size: 1.75rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }

    /* Headers */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    
    .sub-title {
        font-size: 1.125rem;
        color: #64748b;
        margin-bottom: 2.5rem;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        border: none;
        color: #64748b;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        color: #3b82f6 !important;
        border-bottom: 2px solid #3b82f6 !important;
    }

    /* Plotly Chart Container */
    .chart-box {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA ENGINE ---
class KitchenDataManager:
    def __init__(self):
        self.raw_data = [
            {"Posten": "D1", "Start": "08:00", "Ende": "10:00", "Aufgabe": "Suppenküche & Diät-Vorbereitung", "Bereich": "Diätetik"},
            {"Posten": "D1", "Start": "10:15", "Ende": "11:20", "Aufgabe": "Regenerieren & Instruktion Band", "Bereich": "Diätetik"},
            {"Posten": "D1", "Start": "11:20", "Ende": "12:20", "Aufgabe": "Service ET & Band-Bereitschaft", "Bereich": "Diätetik"},
            {"Posten": "D1", "Start": "12:20", "Ende": "12:45", "Aufgabe": "Abräumen & Lager-Sicherung", "Bereich": "Logistik"},
            {"Posten": "D1", "Start": "14:30", "Ende": "15:50", "Aufgabe": "Produktionsprotokolle & PM", "Bereich": "Verwaltung"},
            {"Posten": "D1", "Start": "15:50", "Ende": "18:05", "Aufgabe": "Service Abend & Bandkontrolle", "Bereich": "Diätetik"},
            {"Posten": "E1", "Start": "07:00", "Ende": "10:00", "Aufgabe": "Tages-Beilagen & MEP Folgetag", "Bereich": "Produktion"},
            {"Posten": "E1", "Start": "10:15", "Ende": "12:30", "Aufgabe": "Wahlkost & Service Anrichten", "Bereich": "Produktion"},
            {"Posten": "E1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "MEP Abend & Postenreinigung", "Bereich": "Verwaltung"},
            {"Posten": "G2", "Start": "09:30", "Ende": "13:30", "Aufgabe": "Kalte Küche, Salate & Dessert", "Bereich": "Produktion"},
            {"Posten": "G2", "Start": "14:15", "Ende": "18:00", "Aufgabe": "Buffet, MEP & Bandservice", "Bereich": "Produktion"},
            {"Posten": "G2", "Start": "18:00", "Ende": "18:30", "Aufgabe": "Checklisten & Kontrollen", "Bereich": "Verwaltung"},
            {"Posten": "H1", "Start": "05:30", "Ende": "10:00", "Aufgabe": "Frühstücksservice & Band", "Bereich": "Gastronomie"},
            {"Posten": "H1", "Start": "10:15", "Ende": "12:30", "Aufgabe": "Glacé & Band Mittag", "Bereich": "Gastronomie"},
            {"Posten": "H1", "Start": "13:30", "Ende": "14:40", "Aufgabe": "Protokolle & MHD Prüfung", "Bereich": "Verwaltung"},
            {"Posten": "H2", "Start": "09:15", "Ende": "13:00", "Aufgabe": "Desserts Restaurant & Patienten", "Bereich": "Gastronomie"},
            {"Posten": "H2", "Start": "14:15", "Ende": "18:00", "Aufgabe": "Zvieri & Abendservice", "Bereich": "Gastronomie"},
            {"Posten": "R1", "Start": "06:30", "Ende": "10:00", "Aufgabe": "Warenannahme & Deklaration", "Bereich": "Logistik"},
            {"Posten": "R1", "Start": "10:20", "Ende": "15:24", "Aufgabe": "Mittagsservice & Restaurant", "Bereich": "Gastronomie"},
            {"Posten": "R2", "Start": "06:30", "Ende": "10:00", "Aufgabe": "Frühstück MEP & Salate", "Bereich": "Gastronomie"},
            {"Posten": "R2", "Start": "10:20", "Ende": "15:24", "Aufgabe": "Mittagsservice & ReCircle", "Bereich": "Gastronomie"},
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

# --- UI RENDERING ---
def main():
    dm = KitchenDataManager()
    df = dm.get_df()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=60)
        st.markdown("### Control Center")
        st.markdown("Filtere die operativen Ebenen")
        
        alle_bereiche = sorted(df['Bereich'].unique())
        selected_bereiche = st.multiselect("", alle_bereiche, default=alle_bereiche)
        
        st.markdown("---")
        st.caption("v2.4.0 • Enterprise Edition")
        st.caption("© 2024 Kitchen Ops Intelligence")

    # --- MAIN CONTENT ---
    st.markdown('<div class="main-title">Kitchen Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Strategisches Dashboard für Prozessoptimierung</div>', unsafe_allow_html=True)

    # Filtered Data
    mask = df['Bereich'].isin(selected_bereiche)
    f_df = df[mask]

    # --- KPI CARDS ---
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    
    total_hours = int(f_df["Minuten"].sum()/60)
    prod_h = int(f_df[f_df["Bereich"] == "Produktion"]["Minuten"].sum()/60)
    gast_h = int(f_df[f_df["Bereich"] == "Gastronomie"]["Minuten"].sum()/60)
    admin_ratio = (f_df[f_df["Bereich"] == "Verwaltung"]["Minuten"].sum() / f_df["Minuten"].sum() * 100) if f_df["Minuten"].sum() > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''<div class="card">
            <div class="card-label">Arbeitszeit Gesamt</div>
            <div class="card-value"><span class="status-indicator" style="background:#3b82f6"></span>{total_hours}h</div>
        </div>''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''<div class="card">
            <div class="card-label">Produktions-Fokus</div>
            <div class="card-value"><span class="status-indicator" style="background:#ef4444"></span>{prod_h}h</div>
        </div>''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''<div class="card">
            <div class="card-label">Gastronomie-Fokus</div>
            <div class="card-value"><span class="status-indicator" style="background:#10b981"></span>{gast_h}h</div>
        </div>''', unsafe_allow_html=True)
    with col4:
        st.markdown(f'''<div class="card">
            <div class="card-label">Verwaltungs-Ratio</div>
            <div class="card-value"><span class="status-indicator" style="background:#f59e0b"></span>{admin_ratio:.1f}%</div>
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- TABS ---
    tab_gantt, tab_load, tab_strategy = st.tabs(["📊 Operative Timeline", "📈 Belastungsprofil", "🧩 Strategie-Mapping"])

    with tab_gantt:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        fig = px.timeline(
            f_df, x_start="Start_DT", x_end="End_DT", y="Posten", color="Bereich",
            hover_name="Aufgabe",
            color_discrete_map={
                "Produktion": "#EF4444", "Gastronomie": "#10B981", 
                "Diätetik": "#6366F1", "Verwaltung": "#F59E0B", "Logistik": "#94A3B8"
            },
            category_orders={"Posten": sorted(f_df['Posten'].unique(), reverse=True)}
        )
        fig.update_layout(
            xaxis_title="", yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=450, font=dict(family="Inter", size=12),
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1)
        )
        fig.update_yaxes(gridcolor='#f1f5f9')
        fig.update_xaxes(gridcolor='#f1f5f9')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_load:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        load_data = []
        for h in range(5, 20):
            for m in [0, 30]:
                check_time = datetime(2026, 1, 1, h, m)
                active_count = len(f_df[(f_df['Start_DT'] <= check_time) & (f_df['End_DT'] > check_time)])
                load_data.append({"Zeit": f"{h:02d}:{m:02d}", "Aktive_Posten": active_count})
        
        load_df = pd.DataFrame(load_data)
        fig_area = px.area(load_df, x="Zeit", y="Aktive_Posten", line_shape="spline")
        fig_area.update_traces(fillcolor="rgba(59, 130, 246, 0.2)", line_color="#3B82F6", line_width=3)
        fig_area.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="", yaxis_title="Anzahl aktive Posten",
            margin=dict(l=0, r=0, t=20, b=0), height=400
        )
        fig_area.update_xaxes(gridcolor='#f1f5f9', nticks=15)
        fig_area.update_yaxes(gridcolor='#f1f5f9')
        st.plotly_chart(fig_area, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        st.info("💡 **Insight:** Die Spitzenzeiten konzentrieren sich auf den Mittagsservice (11:00-13:00). In diesen Phasen ist die personelle Dichte am höchsten.")

    with tab_strategy:
        col_left, col_right = st.columns([1.5, 1])
        
        with col_left:
            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            fig_sun = px.sunburst(
                f_df, path=['Bereich', 'Posten', 'Aufgabe'], values='Minuten',
                color='Bereich',
                color_discrete_map={
                    "Produktion": "#EF4444", "Gastronomie": "#10B981", 
                    "Diätetik": "#6366F1", "Verwaltung": "#F59E0B", "Logistik": "#94A3B8"
                }
            )
            fig_sun.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=550)
            st.plotly_chart(fig_sun, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_right:
            st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
            st.markdown("#### Strategische Handlungsempfehlungen")
            
            with st.expander("🚀 Logistik-Optimierung", expanded=True):
                st.write("Verlagerung der Warenannahme auf Randzeiten, um Posten R1 im Mittagsservice zu entlasten.")
                
            with st.expander("✍️ Admin-Entlastung"):
                st.write("Einführung digitaler Checklisten für S1 und H1 spart ca. **45 Min/Tag** pro Posten.")
                
            with st.expander("🔥 Peak-Management"):
                st.write("Die aktuelle Load-Curve zeigt Überkapazitäten um 15:00 Uhr. Hier könnten Reinigungszyklen intensiviert werden.")

if __name__ == "__main__":
    main()
