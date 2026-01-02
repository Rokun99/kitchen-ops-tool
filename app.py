import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Kitchen Intelligence Suite | Analytics & AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LUXURY ENTERPRISE STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #1E293B; }
    .main { background-color: #F8FAFC; }
    
    /* Stat Cards */
    .metric-card {
        background: white;
        padding: 20px;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        text-align: left;
    }
    .metric-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #64748B; font-weight: 600; }
    .metric-value { font-size: 20px; font-weight: 700; color: #0F172A; }
    
    /* UI Elements */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #E2E8F0; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: transparent; border: none; font-size: 12px; font-weight: 500; }
    .stTabs [aria-selected="true"] { color: #2563EB !important; border-bottom: 2px solid #2563EB !important; }
    
    .ai-box { background: #F0F9FF; border-left: 4px solid #0EA5E9; padding: 20px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# --- AI HANDLER ---
class KitchenAI:
    def __init__(self):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except:
            self.model = None

    def audit_processes(self, df):
        if not self.model: return "API Key nicht gefunden."
        
        context = df[['Dienst', 'Aufgabe', 'Typ', 'Minuten']].to_string()
        prompt = f"""
        Analysiere folgende Küchendaten: {context}
        Prüfe auf Ineffizienzen (z.B. zu viel Logistik während der Produktion).
        Erkläre fachlich fundiert, warum bestimmte SOLL-Optimierungen nötig sind.
        Beziehe dich auf Personalbindung während der Servicezeit (11:30-12:30).
        Halte dich kurz, klinisch-präzise und professionell.
        """
        response = self.model.generate_content(prompt)
        return response.text

# --- DATA ENGINE ---
class KitchenDataManager:
    @staticmethod
    def get_full_data():
        data = [
            {"Dienst": "D1", "Start": "08:00", "Ende": "12:20", "Aufgabe": "Suppen & Diätvorbereitung", "Typ": "Produktion", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "18:09", "Aufgabe": "Nachessen & Abenddienst", "Typ": "Produktion", "Team": "Cucina"},
            {"Dienst": "E1", "Start": "07:00", "Ende": "13:00", "Aufgabe": "Beilagen & Service", "Typ": "Produktion", "Team": "Cucina"},
            {"Dienst": "E1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "Abendservice & MEP", "Typ": "Logistik", "Team": "Cucina"},
            {"Dienst": "G2", "Start": "09:30", "Ende": "13:30", "Aufgabe": "Wahlkost & Kaltküche", "Typ": "Produktion", "Team": "Cucina"},
            {"Dienst": "G2", "Start": "14:15", "Ende": "18:30", "Aufgabe": "MEP Folgetag & Reinigung", "Typ": "Logistik", "Team": "Cucina"},
            {"Dienst": "H1", "Start": "05:30", "Ende": "12:30", "Aufgabe": "Frühstück & Band Mittag", "Typ": "Service", "Team": "Restaurazione"},
            {"Dienst": "H1", "Start": "13:30", "Ende": "14:40", "Aufgabe": "Menüsalat & Abschluss", "Typ": "Logistik", "Team": "Restaurazione"},
            {"Dienst": "H2", "Start": "09:15", "Ende": "13:30", "Aufgabe": "Desserts & Patienten-Zvieri", "Typ": "Service", "Team": "Restaurazione"},
            {"Dienst": "H2", "Start": "14:15", "Ende": "18:09", "Aufgabe": "MEP Folgetag & Band Abend", "Typ": "Service", "Team": "Restaurazione"},
            {"Dienst": "H3", "Start": "09:15", "Ende": "13:30", "Aufgabe": "Salate & Wähen Produktion", "Typ": "Produktion", "Team": "Cucina"},
            {"Dienst": "H3", "Start": "14:15", "Ende": "18:09", "Aufgabe": "MEP & Reinigung Posten", "Typ": "Logistik", "Team": "Cucina"},
            {"Dienst": "R1", "Start": "06:30", "Ende": "14:00", "Aufgabe": "Warenannahme & Service Mittag", "Typ": "Service", "Team": "Restaurazione"},
            {"Dienst": "R1", "Start": "14:30", "Ende": "15:24", "Aufgabe": "Reinigung & MEP Folgetag", "Typ": "Logistik", "Team": "Restaurazione"},
            {"Dienst": "R2", "Start": "06:30", "Ende": "14:00", "Aufgabe": "Salate & Band Mittag", "Typ": "Service", "Team": "Restaurazione"},
            {"Dienst": "R2", "Start": "14:30", "Ende": "15:24", "Aufgabe": "Etiketten & Abschluss", "Typ": "Logistik", "Team": "Restaurazione"},
            {"Dienst": "S1", "Start": "07:00", "Ende": "13:00", "Aufgabe": "Fleisch & Saucen Produktion", "Typ": "Produktion", "Team": "Cucina"},
            {"Dienst": "S1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "Produktionspläne & Abschluss", "Typ": "Verwaltung", "Team": "Cucina"},
        ]
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'].str.replace('.', ':'))
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'].str.replace('.', ':'))
        df['Minuten'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- MAIN APP ---
def main():
    dm = KitchenDataManager()
    ai = KitchenAI()
    df_raw = dm.get_full_data()

    # Header
    st.markdown("<h1 style='font-size: 28px; font-weight: 700; margin-bottom: 0px;'>KITCHEN INTELLIGENCE SUITE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 14px; margin-bottom: 30px;'>Analytics & Generative Transformation</p>", unsafe_allow_html=True)

    # --- KPI SCORECARD (9 KPIs) ---
    st.markdown("<h2 style='font-size: 12px; color: #64748B; text-transform: uppercase; letter-spacing: 1px;'>Operations Scorecard</h2>", unsafe_allow_html=True)
    
    kpis = st.columns(3)
    # Row 1
    total_min = df_raw['Minuten'].sum()
    prod_min = df_raw[df_raw['Typ'] == 'Produktion']['Minuten'].sum()
    serv_min = df_raw[df_raw['Typ'] == 'Service']['Minuten'].sum()
    
    # Row 2
    log_min = df_raw[df_raw['Typ'] == 'Logistik']['Minuten'].sum()
    admin_min = df_raw[df_raw['Typ'] == 'Verwaltung']['Minuten'].sum()
    productivity = (prod_min / total_min) * 100
    
    # Row 3 (Crunch Time Logic)
    crunch_start = datetime(2026, 1, 1, 11, 30)
    crunch_end = datetime(2026, 1, 1, 12, 30)
    crunch_staff = len(df_raw[(df_raw['Start_DT'] <= crunch_start) & (df_raw['End_DT'] >= crunch_end)])
    peak_staff = 0
    for h in range(5, 20):
        for m in [0, 15, 30, 45]:
            t = datetime(2026, 1, 1, h, m)
            count = len(df_raw[(df_raw['Start_DT'] <= t) & (df_raw['End_DT'] > t)])
            if count > peak_staff: peak_staff = count

    # Render KPIs
    kpi_list = [
        ("Gesamtkapazität", f"{int(total_min/60)}h"),
        ("Produktion (h)", f"{int(prod_min/60)}h"),
        ("Service (h)", f"{int(serv_min/60)}h"),
        ("Logistik/Reinigung", f"{int(log_min/60)}h"),
        ("Administration", f"{int(admin_min/60)}h"),
        ("Produktivitäts-Rate", f"{productivity:.1f}%"),
        ("Crunch-Time Besetzung", f"{crunch_staff} MA"),
        ("Max. Personalstärke", f"{peak_staff} MA"),
        ("Team Balance (C/R)", f"{len(df_raw[df_raw['Team']=='Cucina']['Dienst'].unique())}/{len(df_raw[df_raw['Team']=='Restaurazione']['Dienst'].unique())}")
    ]

    for i, (label, value) in enumerate(kpi_list):
        with kpis[i % 3]:
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 15px;">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    # --- PROCESS FILTER (Dienst-Ebene) ---
    st.markdown("<br>", unsafe_allow_html=True)
    selected_dienste = st.multiselect(
        "Dienste selektieren/isolieren", 
        options=sorted(df_raw['Dienst'].unique()), 
        default=sorted(df_raw['Dienst'].unique())
    )
    df = df_raw[df_raw['Dienst'].isin(selected_dienste)]

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["🕒 Operative Timeline", "📊 Präzisions-Belastungskurve", "🚀 KI-Transformation & Audit"])

    with tab1:
        # Farblich optimierte Palette (Modern Subtle)
        color_discrete_map = {
            "Produktion": "#6366F1", # Indigo
            "Service": "#10B981",    # Emerald
            "Logistik": "#F59E0B",   # Amber
            "Verwaltung": "#94A3B8"  # Slate
        }
        
        fig = px.timeline(
            df, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ",
            hover_name="Aufgabe",
            color_discrete_map=color_discrete_map,
            category_orders={"Dienst": ["H1", "R1", "R2", "S1", "E1", "D1", "H2", "H3", "G2"]}
        )
        fig.update_layout(
            xaxis_title="", yaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=500, margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1, title=None)
        )
        fig.update_yaxes(gridcolor='#F1F5F9')
        fig.update_xaxes(gridcolor='#F1F5F9', dtick="3600000", tickformat="%H:%M")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with tab2:
        # Hochpräzise Kurve (15-Minuten Intervalle)
        curve_data = []
        for h in range(5, 20):
            for m in [0, 15, 30, 45]:
                t = datetime(2026, 1, 1, h, m)
                active = len(df[(df['Start_DT'] <= t) & (df['End_DT'] > t)])
                curve_data.append({"Zeit": f"{h:02d}:{m:02d}", "Personal": active})
        
        df_curve = pd.DataFrame(curve_data)
        fig_curve = px.line(df_curve, x="Zeit", y="Personal", line_shape="spline")
        fig_curve.update_traces(line_color='#0F172A', line_width=2, fill='tozeroy', fillcolor='rgba(15, 23, 42, 0.05)')
        fig_curve.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis_title="", yaxis_title="MA Aktiv",
            height=400, margin=dict(l=0, r=0, t=20, b=0)
        )
        fig_curve.update_xaxes(gridcolor='#F1F5F9', nticks=20)
        fig_curve.update_yaxes(gridcolor='#F1F5F9')
        st.plotly_chart(fig_curve, use_container_width=True, config={'displayModeBar': False})
        st.info("Präzisions-Ansicht: Diese Kurve zeigt die exakte Personalbindung in 15-Minuten-Slots. Beachten Sie die massiven Peaks während der Bandverteilung.")

    with tab3:
        col_l, col_r = st.columns([1, 1])
        
        with col_l:
            st.markdown("### Strategisches SOLL-Modell")
            st.markdown("""
            <div style='background: white; padding: 25px; border: 1px solid #E2E8F0; border-radius: 4px;'>
                <p style='font-size: 13px; line-height: 1.8;'>
                <b>1. Prozess-Trennung:</b> Verlagerung von 'Logistik' aus den Hochleistungs-Vormittagen der Posten R1/R2.<br>
                <b>2. Shared Service:</b> H3 und G2 Nachmittags-Slots zusammenführen.<br>
                <b>3. Diätetik Fokus:</b> D1 von administrativer Last befreien durch digitale Checklisten.<br>
                <b>4. Peak-Smoothing:</b> Entzerrung der MEP-Zeiten zwischen 09:00 und 10:30.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_r:
            st.markdown("### KI-Audit & Begründung (Gemini 1.5 Pro)")
            if st.button("Prozess-Analyse durch KI anfordern"):
                with st.spinner("Gemini analysiert IST-Strukturen..."):
                    audit_result = ai.audit_processes(df)
                    st.markdown(f"<div class='ai-box'>{audit_result}</div>", unsafe_allow_html=True)
            else:
                st.caption("Klicken Sie auf den Button, um eine KI-basierte Begründung für die Optimierungspotenziale zu erhalten.")

if __name__ == "__main__":
    main()
