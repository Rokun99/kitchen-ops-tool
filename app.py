import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- SETTINGS ---
st.set_page_config(
    page_title="Kitchen Intelligence Suite | Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LUXURY ENTERPRISE STYLING (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --primary: #0F172A;
        --secondary: #64748B;
        --background: #F8FAFC;
        --border: #E2E8F0;
        --accent: #3B82F6;
    }

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: var(--primary);
    }

    .main { background-color: var(--background); }

    /* Clean Metric Cards */
    .metric-container {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }

    .metric-card {
        background: white;
        padding: 24px;
        border: 1px solid var(--border);
        border-radius: 4px;
        flex: 1;
    }

    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--secondary);
        margin-bottom: 8px;
        font-weight: 600;
    }

    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--primary);
    }

    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 40px;
        border-bottom: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border: none;
        color: var(--secondary);
        font-weight: 500;
        font-size: 13px;
    }

    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary) !important;
    }

    /* Sidebar Clean */
    section[data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid var(--border);
    }

    h1, h2, h3 {
        letter-spacing: -0.02em;
        font-weight: 700;
    }

    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- DATA ENGINE ---
class KitchenDataManager:
    @staticmethod
    def get_full_data():
        # Alle Dienste D1, E1, G2, H1, H2, H3, R1, R2, S1 basierend auf den Dokumenten
        data = [
            # D1 - Diätetik
            {"Dienst": "D1", "Start": "08:00", "Ende": "12:20", "Aufgabe": "Suppen & Diätvorbereitung", "Typ": "Produktion"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "18:09", "Aufgabe": "Nachessen & Abenddienst", "Typ": "Produktion"},
            # E1 - Entremetier
            {"Dienst": "E1", "Start": "07:00", "Ende": "13:00", "Aufgabe": "Beilagen & Service", "Typ": "Produktion"},
            {"Dienst": "E1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "Abendservice & MEP", "Typ": "Logistik"},
            # G2 - Kaltküche
            {"Dienst": "G2", "Start": "09:30", "Ende": "13:30", "Aufgabe": "Wahlkost & Kaltküche", "Typ": "Produktion"},
            {"Dienst": "G2", "Start": "14:15", "Ende": "18:30", "Aufgabe": "MEP Folgetag & Reinigung", "Typ": "Logistik"},
            # H1 - Frühstück / Band
            {"Dienst": "H1", "Start": "05:30", "Ende": "12:30", "Aufgabe": "Frühstück & Band Mittag", "Typ": "Gastronomie"},
            {"Dienst": "H1", "Start": "13:30", "Ende": "14:40", "Aufgabe": "Menüsalat & Abschluss", "Typ": "Logistik"},
            # H2 - Patisserie
            {"Dienst": "H2", "Start": "09:15", "Ende": "13:30", "Aufgabe": "Desserts & Patienten-Zvieri", "Typ": "Gastronomie"},
            {"Dienst": "H2", "Start": "14:15", "Ende": "18:09", "Aufgabe": "MEP Folgetag & Band Abend", "Typ": "Gastronomie"},
            # H3 - Unterstützung (NEU integriert)
            {"Dienst": "H3", "Start": "09:15", "Ende": "13:30", "Aufgabe": "Salate & Wähen Produktion", "Typ": "Produktion"},
            {"Dienst": "H3", "Start": "14:15", "Ende": "18:09", "Aufgabe": "MEP & Reinigung Posten", "Typ": "Logistik"},
            # R1 - Service 1
            {"Dienst": "R1", "Start": "06:30", "Ende": "14:00", "Aufgabe": "Warenannahme & Service Mittag", "Typ": "Gastronomie"},
            {"Dienst": "R1", "Start": "14:30", "Ende": "15:24", "Aufgabe": "Reinigung & MEP Folgetag", "Typ": "Logistik"},
            # R2 - Service 2
            {"Dienst": "R2", "Start": "06:30", "Ende": "14:00", "Aufgabe": "Salate & Band Mittag", "Typ": "Gastronomie"},
            {"Dienst": "R2", "Start": "14:30", "Ende": "15:24", "Aufgabe": "Etiketten & Abschluss", "Typ": "Logistik"},
            # S1 - Saucier
            {"Dienst": "S1", "Start": "07:00", "Ende": "13:00", "Aufgabe": "Fleisch & Saucen Produktion", "Typ": "Produktion"},
            {"Dienst": "S1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "Produktionspläne & Abschluss", "Typ": "Verwaltung"},
        ]
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'].str.replace('.', ':'))
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'].str.replace('.', ':'))
        df['Minuten'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- UI LOGIC ---
def main():
    dm = KitchenDataManager()
    df = dm.get_full_data()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("<div style='padding-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='font-size: 16px;'>PROZESS-FILTER</h2>", unsafe_allow_html=True)
        typen = sorted(df['Typ'].unique())
        selected_typen = st.multiselect("Anzeige nach Kategorie", typen, default=typen)
        st.markdown("---")
        st.caption("Kitchen Intelligence Suite v3.0\nSecure Enterprise Environment")

    # --- HEADER ---
    st.markdown("<h1 style='font-size: 32px; margin-bottom: 5px;'>KITCHEN OPERATIONS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 14px; margin-bottom: 40px;'>Analytische Übersicht der IST-Prozesse und strategische SOLL-Transformation</p>", unsafe_allow_html=True)

    # --- METRICS ---
    f_df = df[df['Typ'].isin(selected_typen)]
    total_h = int(f_df['Minuten'].sum() / 60)
    prod_ratio = (f_df[f_df['Typ'] == 'Produktion']['Minuten'].sum() / f_df['Minuten'].sum() * 100) if f_df['Minuten'].sum() > 0 else 0
    
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card">
            <div class="metric-label">Gesamtstunden Kapazität</div>
            <div class="metric-value">{total_h}h</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Produktions-Fokus</div>
            <div class="metric-value">{prod_ratio:.1f}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Aktive Posten (Dienstplan)</div>
            <div class="metric-value">{f_df['Dienst'].nunique()}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["IST-ANALYSE (TIMELINE)", "BELASTUNGSPROFIL", "SOLL-TRANSFORMATION"])

    with tab1:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        # Gantt Chart High-End
        fig = px.timeline(
            f_df, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ",
            hover_name="Aufgabe",
            color_discrete_map={
                "Produktion": "#0F172A", 
                "Gastronomie": "#334155", 
                "Logistik": "#94A3B8",
                "Verwaltung": "#CBD5E1"
            },
            category_orders={"Dienst": ["H1", "R1", "R2", "S1", "E1", "D1", "H2", "H3", "G2"]}
        )
        fig.update_layout(
            xaxis_title="", yaxis_title="",
            plot_bgcolor="white", paper_bgcolor="white",
            height=500, margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, title=None)
        )
        fig.update_yaxes(gridcolor='#F1F5F9', fixedrange=True)
        fig.update_xaxes(gridcolor='#F1F5F9', fixedrange=True)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with tab2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        # Heatmap / Load Profil
        load_data = []
        for h in range(5, 20):
            for m in [0, 30]:
                check_time = datetime(2026, 1, 1, h, m)
                count = len(f_df[(f_df['Start_DT'] <= check_time) & (f_df['End_DT'] > check_time)])
                load_data.append({"Zeit": f"{h:02d}:{m:02d}", "Personalstärke": count})
        
        load_df = pd.DataFrame(load_data)
        fig_load = px.area(load_df, x="Zeit", y="Personalstärke")
        fig_load.update_traces(line_color='#0F172A', fillcolor='rgba(15, 23, 42, 0.1)')
        fig_load.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis_title="", yaxis_title="Aktive Personen",
            height=400, margin=dict(l=0, r=0, t=20, b=0)
        )
        fig_load.update_xaxes(gridcolor='#F1F5F9', nticks=15)
        fig_load.update_yaxes(gridcolor='#F1F5F9')
        st.plotly_chart(fig_load, use_container_width=True, config={'displayModeBar': False})

    with tab3:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        col_l, col_r = st.columns([1, 1])
        
        with col_l:
            st.markdown("<h3 style='font-size: 14px; text-transform: uppercase;'>Struktur-Analyse</h3>", unsafe_allow_html=True)
            fig_sun = px.sunburst(
                f_df, path=['Typ', 'Dienst', 'Aufgabe'], values='Minuten',
                color_discrete_sequence=["#0F172A", "#334155", "#94A3B8"]
            )
            fig_sun.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=500)
            st.plotly_chart(fig_sun, use_container_width=True)

        with col_r:
            st.markdown("<h3 style='font-size: 14px; text-transform: uppercase;'>Strategische Optimierung</h3>", unsafe_allow_html=True)
            st.markdown("""
            <div style='background: white; padding: 30px; border: 1px solid #E2E8F0; border-radius: 4px;'>
                <p style='font-weight: 600; font-size: 13px; color: #0F172A;'>SOLL-EMPFHLUNGEN:</p>
                <ul style='font-size: 13px; color: #64748B; line-height: 1.8;'>
                    <li><b>Zentralisierung der Logistik:</b> Posten R1/R2 entlasten, um Fokus auf Gästebetreuung zu erhöhen.</li>
                    <li><b>Dienst-Verschmelzung:</b> H3 und G2 am Nachmittag bündeln, um Reinigungseffizienz zu steigern.</li>
                    <li><b>Entlastung D1:</b> Verlagerung administrativer Diät-Checks in digitale Vormittags-Slots.</li>
                    <li><b>Crunch-Time:</b> Optimierung des Bandes zwischen 11:20 und 12:30 durch Springer-System.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
