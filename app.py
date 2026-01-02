import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & ENTERPRISE STYLING ---
st.set_page_config(
    page_title="Kitchen Ops Analytics | Deep Audit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Deep Slate & Academic Blue Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #0F172A; background-color: #F8FAFC; }
    
    .main-header { font-size: 24px; font-weight: 700; color: #1E293B; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 20px;}
    .cluster-header { font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 1.2px; margin-top: 30px; margin-bottom: 12px; border-left: 4px solid #3B82F6; padding-left: 10px;}
    
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 16px;
        height: 115px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .kpi-title { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.5px; }
    .kpi-value { font-size: 22px; font-weight: 700; color: #0F172A; }
    .kpi-sub { font-size: 11px; color: #94A3B8; }
    .trend-bad { color: #EF4444; font-weight: 600; }
    .trend-good { color: #10B981; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (HIGH RESOLUTION FROM DEEP AUDIT PDF) ---
class DataEngine:
    @staticmethod
    def get_audit_data():
        # Granular IST-State based on "Neukalkulation" PDFs
        ist = [
            # D1 - Diätkoch (Die Admin-Zerstückelung)
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Administration (Mutationen/Mails)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:25", "Ende": "08:30", "Task": "Rüstzeit (Posten einrichten)", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "08:30", "Ende": "09:15", "Task": "Produktion Suppen (520 Port.)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:15", "Ende": "09:45", "Task": "Produktion ET (Ernährungstherapie)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Administration (Mail-Check 2)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "10:15", "Ende": "10:45", "Task": "Regenerieren Cg-Komponenten", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "10:45", "Ende": "11:00", "Task": "Instruktion Band-MA", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Administration (Letzte Orgacard)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service am Band (Diät)", "Typ": "Service"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik (Abräumen/Rückstellproben)", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:00", "Task": "Admin (Produktionsprotokolle)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "15:00", "Ende": "15:50", "Task": "MEP Folgetag", "Typ": "Prod"},

            # E1 - Entremetier (Wahlkost-Leerlauf)
            {"Dienst": "E1", "Start": "07:15", "Ende": "09:30", "Task": "Masse-Prod (Stärke/Gemüse)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "10:15", "Ende": "10:45", "Task": "Prod Wahlkost (Kleinmengen)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "10:45", "Ende": "11:20", "Task": "Regenerieren Band", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Leerlauf (Warten auf Wahlkost-Abruf)", "Typ": "Waste"},
            {"Dienst": "E1", "Start": "13:30", "Ende": "15:00", "Task": "MEP Folgetag (Gedehnte Arbeit)", "Typ": "Waste"},

            # S1 - Saucier (Convenience Joker)
            {"Dienst": "S1", "Start": "07:00", "Ende": "08:30", "Task": "Convenience Veredelung (Päckli)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "08:30", "Ende": "09:30", "Task": "Support E1 (Leerlauf-Überbrückung)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "70-Minuten-Falle (Warten auf Bons)", "Typ": "Waste"},

            # R2 - Gastro (Leerlauf-König)
            {"Dienst": "R2", "Start": "06:30", "Ende": "08:00", "Task": "Fremdkörper am Patientenband", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "10:00", "Task": "Schein-Arbeit (12 Salate in 2h)", "Typ": "Waste"},
            {"Dienst": "R2", "Start": "10:20", "Ende": "11:30", "Task": "Service-Setup (Redundanz)", "Typ": "Waste"},
        ]

        # SOLL / LEAN Model
        soll = [
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:45", "Task": "Bündelung Administration", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:45", "Ende": "12:30", "Task": "Fokussierte Produktion", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Wahlkost-Monopolist (Full Prod)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Power-MEP (Kein Warten)", "Typ": "Prod"},
            {"Dienst": "R2", "Start": "10:00", "Ende": "14:00", "Task": "Spätstart (Kostenersparnis)", "Typ": "Service"}
        ]
        
        return DataEngine.process(ist), DataEngine.process(soll)

    @staticmethod
    def process(data):
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'])
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'])
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- 3. ANALYTICAL SCORECARD (12 KPIs) ---
def render_scorecard(df_ist):
    st.markdown('<div class="cluster-header">A. Finanzielle Effizienz & Talent-Allokation</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    # KPI 1: Talent-Fehlallokationsrate (Fachkräfte in Logistik/Waste)
    skilled = ['D1', 'S1', 'E1']
    leakage = (df_ist[(df_ist['Dienst'].isin(skilled)) & (df_ist['Typ'].isin(['Logistik', 'Waste']))]['Duration'].sum() / df_ist[df_ist['Dienst'].isin(skilled)]['Duration'].sum()) * 100
    c1.markdown(f'<div class="kpi-card"><div class="kpi-title">1. Skill-Leakage Rate</div><div class="kpi-value">{leakage:.1f}%</div><div class="kpi-sub trend-bad">Fachkraftzeit ohne Wertschöpfung</div></div>', unsafe_allow_html=True)
    
    # KPI 2: Parkinson-Verschwendung (Bezahlter Leerlauf)
    waste_min = df_ist[df_ist['Typ'] == 'Waste']['Duration'].sum()
    c2.markdown(f'<div class="kpi-card"><div class="kpi-title">2. Parkinson-Gap</div><div class="kpi-value">{int(waste_min)} Min</div><div class="kpi-sub trend-bad">Gedehnte Arbeit / Tag</div></div>', unsafe_allow_html=True)
    
    # KPI 3: Kapazitäts-Nutzungsgrad R2
    r2_util = 33.0 # Basierend auf Audit-Bericht (40 Min Arbeit in 120 Min Zeit)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-title">3. Kapazitäts-Nutzung R2</div><div class="kpi-value">{r2_util}%</div><div class="kpi-sub trend-bad">Effektive Auslastung Vormittag</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="cluster-header">B. Operative Exzellenz & Flow-Dynamik</div>', unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    
    # KPI 4: Kernzeit-Produktionsvakuum
    c4.markdown(f'<div class="kpi-card"><div class="kpi-title">4. Crunch-Time Vakuum</div><div class="kpi-value">125 Min</div><div class="kpi-sub trend-bad">Kumulierter Leerlauf @ Bandservice</div></div>', unsafe_allow_html=True)
    
    # KPI 5: Bereitschafts-Latenz
    c5.markdown(f'<div class="kpi-card"><div class="kpi-title">5. Readiness Idle Time</div><div class="kpi-value">70 Min</div><div class="kpi-sub">S1/E1 Warten auf Wahlkost-Bons</div></div>', unsafe_allow_html=True)
    
    # KPI 6: Prozess-Zerstückelung (Admin)
    c6.markdown(f'<div class="kpi-card"><div class="kpi-title">6. Context-Switch Ratio</div><div class="kpi-value">4.2x</div><div class="kpi-sub">Büro-Küche Wechsel D1 / Tag</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="cluster-header">C. Risiko-Governance & Qualitäts-Sicherung</div>', unsafe_allow_html=True)
    c7, c8, c9 = st.columns(3)
    
    # KPI 7: Haftungskritische Deckungslücke (Pause D1)
    c7.markdown(f'<div class="kpi-card"><div class="kpi-title">7. Liability Exposure</div><div class="kpi-value">105 Min</div><div class="kpi-sub trend-bad">Diätetik ohne fachliche Deckung</div></div>', unsafe_allow_html=True)
    
    # KPI 8: Hygienerisiko-Faktor (R1)
    c8.markdown(f'<div class="kpi-card"><div class="kpi-title">8. Cross-Contamination Risk</div><div class="kpi-value">Hoch</div><div class="kpi-sub">Schmutzig/Sauber Wechsel R1</div></div>', unsafe_allow_html=True)
    
    # KPI 9: Thermische Latenzzeit
    c9.markdown(f'<div class="kpi-card"><div class="kpi-title">9. Thermal Gap</div><div class="kpi-value">3.5 Std</div><div class="kpi-sub">Zeit Prod. bis Verzehr (Suppe)</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="cluster-header">D. Strategisches Zielbild & Recovery</div>', unsafe_allow_html=True)
    c10, c11, c12 = st.columns(3)
    
    # KPI 10: Patient vs. Gastro Fokus (Time Share)
    c10.markdown(f'<div class="kpi-card"><div class="kpi-title">10. Resource Allocation</div><div class="kpi-value">68/32</div><div class="kpi-sub">Zeitanteil Patient / Gast</div></div>', unsafe_allow_html=True)
    
    # KPI 11: Logistischer Ballastfaktor
    c11.markdown(f'<div class="kpi-card"><div class="kpi-title">11. Logistics Burden</div><div class="kpi-value">190 Min</div><div class="kpi-sub">Manuelle Transportprozesse / Tag</div></div>', unsafe_allow_html=True)
    
    # KPI 12: Recovery-Potenzial (FTE)
    c12.markdown(f'<div class="kpi-card"><div class="kpi-title">12. FTE Recovery Potential</div><div class="kpi-value">1.25 FTE</div><div class="kpi-sub trend-good">Reallokations-Chance</div></div>', unsafe_allow_html=True)

# --- 4. MAIN UI ---
def main():
    st.markdown('<div class="main-header">KITCHEN INTELLIGENCE SUITE: STRATEGIC DEEP AUDIT</div>', unsafe_allow_html=True)

    df_ist, df_soll = DataEngine.get_audit_data()
    render_scorecard(df_ist)

    # --- 5. BELASTUNGSKURVE (DETAIL) ---
    st.markdown('<div class="cluster-header">E. Dynamisches Belastungsprofil (15-Minuten-Auflösung)</div>', unsafe_allow_html=True)
    
    load_data = []
    for h in range(5, 20):
        for m in [0, 15, 30, 45]:
            t = datetime(2026, 1, 1, h, m)
            active = len(df_ist[(df_ist['Start_DT'] <= t) & (df_ist['End_DT'] > t)])
            load_data.append({"Zeit": f"{h:02d}:{m:02d}", "Personalstärke": active})
    
    fig_load = px.area(pd.DataFrame(load_data), x="Zeit", y="Personalstärke", line_shape="spline")
    fig_load.update_traces(line_color="#3B82F6", fillcolor="rgba(59, 130, 246, 0.1)")
    fig_load.update_layout(plot_bgcolor="white", height=300, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="MA Aktiv")
    st.plotly_chart(fig_load, use_container_width=True)

    # --- 6. TRIPLE TIMELINE (IST, WASTE, SOLL) ---
    st.markdown('<div class="cluster-header">F. Zeit-Struktur-Analyse & Transformation</div>', unsafe_allow_html=True)
    
    tab_ist, tab_waste, tab_lean = st.tabs(["1. IST-ZUSTAND (AUDIT-DETAIL)", "2. VERSCHWENDUNGS-FOKUS", "3. SOLL-MODELL (LEAN TARGET)"])

    color_map = {
        "Prod": "#3B82F6", "Service": "#10B981", "Admin": "#F59E0B", 
        "Logistik": "#64748B", "Waste": "#EF4444", "Coord": "#8B5CF6"
    }

    with tab_ist:
        st.info("Befund: Kritische Admin-Fragmentierung bei D1 und massive Idle-Blöcke (Rot) während der Bandverteilung.")
        fig1 = px.timeline(df_ist, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", 
                           hover_name="Task", color_discrete_map=color_map, height=400)
        fig1.update_yaxes(autorange="reversed")
        st.plotly_chart(fig1, use_container_width=True)

    with tab_waste:
        st.error("Identifizierte Verlustzeiten: Diese Blöcke generieren Kosten ohne Gegenwert (Warten, Alibi-Tätigkeiten, Doppelarbeit).")
        df_waste_only = df_ist[df_ist['Typ'] == 'Waste']
        fig2 = px.timeline(df_waste_only, x_start="Start_DT", x_end="End_DT", y="Dienst", color_discrete_sequence=["#EF4444"], height=300)
        st.plotly_chart(fig2, use_container_width=True)

    with tab_lean:
        st.success("Target-Modell: Gebündelte Administration, Springer-Systeme und Eliminierung von Bereitschafts-Leerläufen.")
        fig3 = px.timeline(df_soll, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", 
                           hover_name="Task", color_discrete_map=color_map, height=350)
        st.plotly_chart(fig3, use_container_width=True)

if __name__ == "__main__":
    main()
