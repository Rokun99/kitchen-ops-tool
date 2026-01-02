import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime, timedelta

# --- 1. SETTINGS & ENTERPRISE STYLING ---
st.set_page_config(
    page_title="Kitchen Ops Intelligence | Deep Audit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #0F172A; background-color: #F8FAFC; }
    .main-header { font-size: 26px; font-weight: 700; color: #1E293B; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 20px;}
    .cluster-header { font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 30px; margin-bottom: 12px; border-left: 3px solid #3B82F6; padding-left: 10px;}
    .kpi-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 2px; padding: 16px; height: 110px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03); display: flex; flex-direction: column; justify-content: space-between; }
    .kpi-title { font-size: 9px; font-weight: 700; text-transform: uppercase; color: #64748B; }
    .kpi-value { font-size: 22px; font-weight: 700; color: #0F172A; }
    .kpi-sub { font-size: 10px; color: #94A3B8; }
    .trend-bad { color: #EF4444; font-weight: 600; }
    .trend-good { color: #10B981; font-weight: 600; }
    .ai-box { background: #F0F9FF; border-left: 4px solid #0EA5E9; padding: 20px; border-radius: 2px; font-size: 13px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# --- 2. AI AUDIT HANDLER ---
class KitchenAI:
    def __init__(self):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except:
            self.model = None

    def audit_report(self, data):
        if not self.model: return "KI-Modul nicht aktiv. Bitte API-Key prüfen."
        prompt = f"Analysiere diesen IST-Dienstplan auf Verschwendung (Muda). Beziehe dich auf die '70-Minuten-Falle' und die 'Admin-Zerstückelung'. Erkläre kurz das Recovery-Potenzial in FTE. Daten: {data}"
        try:
            return self.model.generate_content(prompt).text
        except:
            return "Analyse temporär nicht verfügbar."

# --- 3. DATA ENGINE (GRANULAR MAPPING) ---
class DataEngine:
    @staticmethod
    def get_audit_data():
        # Granularer IST-Zustand gemäss PDF Audit
        ist = [
            # D1 - Diätkoch
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Admin: E-Mails/Mutationen", "Typ": "Admin", "Load": 0.8},
            {"Dienst": "D1", "Start": "08:25", "Ende": "08:30", "Task": "Hygiene: Rüsten/Wechsel", "Typ": "Logistik", "Load": 0.5},
            {"Dienst": "D1", "Start": "08:30", "Ende": "09:15", "Task": "Prod: Suppen (130L)", "Typ": "Prod", "Load": 0.9},
            {"Dienst": "D1", "Start": "09:15", "Ende": "09:45", "Task": "Prod: Ernährungstherapie ET", "Typ": "Prod", "Load": 1.0},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Admin: 2. Mail-Check", "Typ": "Admin", "Load": 0.6},
            {"Dienst": "D1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Cg", "Typ": "Prod", "Load": 0.6},
            {"Dienst": "D1", "Start": "10:45", "Ende": "11:00", "Task": "Coord: Instruktion Band", "Typ": "Coord", "Load": 0.6},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Admin: Letzte Orgacard", "Typ": "Admin", "Load": 0.9},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service: Diäten am Band", "Typ": "Service", "Load": 1.0},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik: Rückstellproben", "Typ": "Logistik", "Load": 0.5},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:00", "Task": "Admin: Protokolle", "Typ": "Admin", "Load": 0.4},
            # E1 - Entremetier
            {"Dienst": "E1", "Start": "07:15", "Ende": "09:30", "Task": "Prod: Stärke/Gemüse (Masse)", "Typ": "Prod", "Load": 0.9},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Waste: Wartezeit Wahlkost", "Typ": "Waste", "Load": 0.2},
            {"Dienst": "E1", "Start": "13:30", "Ende": "15:00", "Task": "Prod: Gedehnte MEP", "Typ": "Waste", "Load": 0.3},
            # S1 - Saucier
            {"Dienst": "S1", "Start": "07:00", "Ende": "08:30", "Task": "Prod: Convenience Saucen", "Typ": "Prod", "Load": 0.6},
            {"Dienst": "S1", "Start": "08:30", "Ende": "09:30", "Task": "Coord: Support E1 (Puffer)", "Typ": "Coord", "Load": 0.5},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Waste: Warten auf Bons", "Typ": "Waste", "Load": 0.2},
            # R1 - Gastro
            {"Dienst": "R1", "Start": "06:30", "Ende": "07:30", "Task": "Logistik: Warenannahme", "Typ": "Logistik", "Load": 0.9},
            {"Dienst": "R1", "Start": "07:45", "Ende": "08:30", "Task": "Admin: Deklarationen", "Typ": "Admin", "Load": 0.4},
            # R2 - Leerlauf-König
            {"Dienst": "R2", "Start": "06:30", "Ende": "08:00", "Task": "Logistik: Bandbestückung", "Typ": "Logistik", "Load": 0.5},
            {"Dienst": "R2", "Start": "08:00", "Ende": "10:00", "Task": "Waste: Schein-Arbeit (Salat)", "Typ": "Waste", "Load": 0.3},
            # H3 - Montage
            {"Dienst": "H3", "Start": "09:15", "Ende": "11:15", "Task": "Prod: Montage Sandwich/Wähe", "Typ": "Prod", "Load": 0.7},
            {"Dienst": "H3", "Start": "12:00", "Ende": "12:30", "Task": "Prod: Bircher-Masse", "Typ": "Prod", "Load": 0.6}
        ]
        
        # LEAN-Modell (Soll)
        soll = [
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:45", "Task": "Fokussierter Admin-Block", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:45", "Ende": "12:20", "Task": "Flow-Produktion & Suppen", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Wahlkost-Monopolist (Full)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Power-MEP Folgetag", "Typ": "Prod"},
            {"Dienst": "R2", "Start": "10:00", "Ende": "14:30", "Task": "Late-Entry / Service-Only", "Typ": "Service"}
        ]
        
        return DataEngine.process(ist), DataEngine.process(soll)

    @staticmethod
    def process(data):
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'])
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'])
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- 4. SCORECARD LOGIC ---
def render_kpis(df_ist):
    st.markdown('<div class="cluster-header">Strategische Performance-Indikatoren (Scorecard)</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    # Financials
    total_min = df_ist['Duration'].sum()
    waste_min = df_ist[df_ist['Typ'] == 'Waste']['Duration'].sum()
    leakage = (df_ist[(df_ist['Dienst'].isin(['D1','S1','E1'])) & (df_ist['Typ'].isin(['Logistik','Waste']))]['Duration'].sum() / total_min) * 100
    
    c1.markdown(f'<div class="kpi-card"><div class="kpi-title">1. Skill-Leakage Rate</div><div class="kpi-value">{leakage:.1f}%</div><div class="kpi-sub trend-bad">Fachkraftzeit in Logistik/Waste</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-title">2. Parkinson-Gap</div><div class="kpi-value">{int(waste_min)} Min</div><div class="kpi-sub trend-bad">Gedehnte Arbeit / Tag</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-title">3. Utilisation-Grad R2</div><div class="kpi-value">33%</div><div class="kpi-sub trend-bad">Effektive Last Vormittag</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card"><div class="kpi-title">4. Recovery-Potenzial</div><div class="kpi-value">1.15 FTE</div><div class="kpi-sub trend-good">Freisetzbare Kapazität</div></div>', unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    c5.markdown(f'<div class="kpi-card"><div class="kpi-title">5. Kernzeit-Vakuum</div><div class="kpi-value">115 Min</div><div class="kpi-sub trend-bad">Leerlauf am Band (11:20-12:30)</div></div>', unsafe_allow_html=True)
    c6.markdown(f'<div class="kpi-card"><div class="kpi-title">6. Readiness-Loss</div><div class="kpi-value">70 Min</div><div class="kpi-sub">S1/E1 Warten auf Bons</div></div>', unsafe_allow_html=True)
    c7.markdown(f'<div class="kpi-card"><div class="kpi-title">7. Context-Switch Rate</div><div class="kpi-value">4.2x</div><div class="kpi-sub">Admin-Wechsel D1 pro Schicht</div></div>', unsafe_allow_html=True)
    c8.markdown(f'<div class="kpi-card"><div class="kpi-title">8. Logistics Burden</div><div class="kpi-value">190 Min</div><div class="kpi-sub">Manueller Transport-Aufwand</div></div>', unsafe_allow_html=True)

    c9, c10, c11, c12 = st.columns(4)
    c9.markdown(f'<div class="kpi-card"><div class="kpi-title">9. Liability Gap</div><div class="kpi-value">105 Min</div><div class="kpi-sub trend-bad">Unbesetzte Diätetik (Mittag)</div></div>', unsafe_allow_html=True)
    c10.markdown(f'<div class="kpi-card"><div class="kpi-title">10. Hygiene-Risk Index</div><div class="kpi-value">Hoch</div><div class="kpi-sub">Rampe-Service Wechsel R1</div></div>', unsafe_allow_html=True)
    c11.markdown(f'<div class="kpi-card"><div class="kpi-title">11. Resource Split</div><div class="kpi-value">68/32</div><div class="kpi-sub">Verhältnis Patient / Gastro</div></div>', unsafe_allow_html=True)
    c12.markdown(f'<div class="kpi-card"><div class="kpi-title">12. Thermal Latency</div><div class="kpi-value">3.5 Std</div><div class="kpi-sub">Zeit Prod. bis Verzehr</div></div>', unsafe_allow_html=True)

# --- 5. MAIN APPLICATION ---
def main():
    st.markdown('<div class="main-header">KITCHEN INTELLIGENCE SUITE: STRATEGIC AUDIT 2026</div>', unsafe_allow_html=True)
    
    df_ist, df_soll = DataEngine.get_audit_data()
    render_kpis(df_ist)

    # --- AI SECTION ---
    st.markdown('<div class="cluster-header">KI-Befund & Begründung (Gemini 1.5)</div>', unsafe_allow_html=True)
    ai = KitchenAI()
    if st.button("Prozess-Audit durch KI starten"):
        with st.spinner("KI analysiert Ineffizienzen..."):
            report = ai.audit_report(df_ist.to_dict())
            st.markdown(f'<div class="ai-box">{report}</div>', unsafe_allow_html=True)

    # --- LOAD CURVE ---
    st.markdown('<div class="cluster-header">Personal-Bindung am Band (15-Minuten Auflösung)</div>', unsafe_allow_html=True)
    load_data = []
    for h in range(5, 20):
        for m in [0, 15, 30, 45]:
            t = datetime(2026, 1, 1, h, m)
            active = len(df_ist[(df_ist['Start_DT'] <= t) & (df_ist['End_DT'] > t)])
            load_data.append({"Zeit": f"{h:02d}:{m:02d}", "Staff": active})
    
    fig_load = px.area(pd.DataFrame(load_data), x="Zeit", y="Staff", line_shape="spline")
    fig_load.update_traces(line_color="#0F172A", fillcolor="rgba(15, 23, 42, 0.05)")
    fig_load.update_layout(plot_bgcolor="white", height=250, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Personen")
    st.plotly_chart(fig_load, use_container_width=True)

    # --- TIMELINES ---
    st.markdown('<div class="cluster-header">Zeit-Struktur & Transformations-Ebenen</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["1. IST-ZUSTAND (DETAIL-AUDIT)", "2. VERSCHWENDUNGS-ISO (MUDA)", "3. SOLL-MODELL (LEAN)"])

    color_map = {"Prod": "#3B82F6", "Service": "#10B981", "Admin": "#F59E0B", "Logistik": "#64748B", "Waste": "#EF4444", "Coord": "#8B5CF6"}

    with tab1:
        fig1 = px.timeline(df_ist, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", hover_name="Task", color_discrete_map=color_map, height=450)
        fig1.update_yaxes(categoryorder="array", categoryarray=["H1","R1","R2","S1","E1","D1","H2","H3","G2"])
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        df_waste = df_ist[df_ist['Typ'] == 'Waste']
        fig2 = px.timeline(df_waste, x_start="Start_DT", x_end="End_DT", y="Dienst", color_discrete_sequence=["#EF4444"], height=300)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        fig3 = px.timeline(df_soll, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", hover_name="Task", color_discrete_map=color_map, height=350)
        st.plotly_chart(fig3, use_container_width=True)

if __name__ == "__main__":
    main()
