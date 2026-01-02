import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Kitchen Intelligence | Deep Audit 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enterprise CSS (Clinical, Slate/Blue Theme, No Emojis)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #0F172A; background-color: #F8FAFC; }
    
    .main-header { font-size: 26px; font-weight: 700; color: #1E293B; letter-spacing: -0.5px; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 20px;}
    .cluster-header { font-size: 13px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 1.2px; margin-top: 30px; margin-bottom: 12px; border-left: 4px solid #3B82F6; padding-left: 10px;}
    
    /* KPI Cards Compact */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 16px;
        height: 110px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .kpi-title { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748B; letter-spacing: 0.5px; }
    .kpi-value { font-size: 24px; font-weight: 700; color: #0F172A; }
    .kpi-sub { font-size: 11px; color: #94A3B8; }
    .trend-bad { color: #EF4444; font-weight: 600; }
    .trend-good { color: #10B981; font-weight: 600; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-size: 14px; font-weight: 600; color: #64748B; }
    .stTabs [aria-selected="true"] { color: #3B82F6 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (HIGH-RESOLUTION AUDIT DATA) ---
class DataEngine:
    @staticmethod
    def get_ist_data():
        # Granulare Daten extrahiert aus dem Neukalkulations-Bericht
        data = [
            # D1 - Fragmentierte Admin & Stress
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Admin: Orgacard/Emails", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:25", "Ende": "08:30", "Task": "Rüst: Vorbereitung", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "08:30", "Ende": "09:15", "Task": "Prod: Suppen (130L)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:15", "Ende": "09:45", "Task": "Prod: Diät-Ableitungen", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Admin: 2. Mail-Check", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Cg", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "10:45", "Ende": "11:00", "Task": "Coord: Instruktion Band", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Admin: Letzte Updates", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service: Diät-Band", "Typ": "Service"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik: Rückstellproben", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "12:45", "Ende": "14:30", "Task": "RISIKO: Pause (Keine Deckung)", "Typ": "Waste"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:00", "Task": "Admin: Protokolle", "Typ": "Admin"},
            
            # E1 - Die 70-Minuten-Falle
            {"Dienst": "E1", "Start": "07:15", "Ende": "09:30", "Task": "Prod: Masse (Stärke/Gemüse)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Waste: Wartezeit Wahlkost", "Typ": "Waste"},
            {"Dienst": "E1", "Start": "14:00", "Ende": "15:30", "Task": "Prod: Gedehnte Arbeit (Vorbereitung)", "Typ": "Prod"},
            
            # S1 - Unterforderung & Convenience
            {"Dienst": "S1", "Start": "07:00", "Ende": "08:30", "Task": "Prod: Veredelung Convenience", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "08:30", "Ende": "09:30", "Task": "Waste: Gedehnte Kapazität", "Typ": "Waste"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Service: Wahlkost-Zulieferung", "Typ": "Service"},
            
            # R1 - Schmutzig-zu-Sauber Konflikt
            {"Dienst": "R1", "Start": "06:30", "Ende": "07:30", "Task": "Logistik: Warenannahme Rampe", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:30", "Ende": "07:45", "Task": "Waste: Hygiene-Schleuse", "Typ": "Waste"},
            {"Dienst": "R1", "Start": "07:45", "Ende": "08:30", "Task": "Admin: Manuelle Deklaration", "Typ": "Admin"},
            
            # R2 - Der Leerlauf-König
            {"Dienst": "R2", "Start": "06:30", "Ende": "08:00", "Task": "Logistik: Bandbestückung (Fremdkörper)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "10:00", "Task": "Waste: Schein-Arbeit (12 Salate)", "Typ": "Waste"},
            
            # H3 - Montage-Worker
            {"Dienst": "H3", "Start": "09:15", "Ende": "11:15", "Task": "Prod: Montage Wähen/Sandwich", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:00", "Ende": "12:30", "Task": "Prod: Birchermüesli Masse", "Typ": "Prod"}
        ]
        return DataEngine.process_df(data)

    @staticmethod
    def get_soll_data():
        # Strategische Optimierung laut PDF
        data = [
            # D1: Admin gebündelt
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:45", "Task": "Admin-Block (Fix)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:45", "Ende": "12:20", "Task": "Prod: Flow-Produktion", "Typ": "Prod"},
            
            # S1: Wahlkost-Monopolist & Diät-Backup
            {"Dienst": "S1", "Start": "07:00", "Ende": "11:20", "Task": "Prod: Kernproduktion", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Prod: Wahlkost Komplett", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "12:45", "Ende": "14:30", "Task": "Admin: Diät-Verantwortung (Vertretung)", "Typ": "Admin"},
            
            # E1: Power-MEP statt Warten
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Prod: Power-MEP für Morgen", "Typ": "Prod"},
            
            # R1: Rein Gastgeber
            {"Dienst": "R1", "Start": "06:30", "Ende": "10:00", "Task": "Service: Veredelung & Qualität", "Typ": "Service"},
            
            # R2: Späterer Start (Kostensenkung)
            {"Dienst": "R2", "Start": "10:00", "Ende": "14:30", "Task": "Service: Peak-Abdeckung", "Typ": "Service"},
        ]
        return DataEngine.process_df(data)

    @staticmethod
    def process_df(data):
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'])
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'])
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

    @staticmethod
    def calculate_metrics(df_ist, df_soll):
        # 1. Skill Leakage (Fachkraft in Waste/Logistik)
        skilled_dienste = ['D1', 'S1', 'E1', 'G2']
        leakage = df_ist[(df_ist['Dienst'].isin(skilled_dienste)) & (df_ist['Typ'].isin(['Logistik', 'Waste']))]['Duration'].sum()
        
        # 2. Parkinson Gap (Gedehnte Arbeit/Leerlauf)
        parkinson = df_ist[df_ist['Typ'] == 'Waste']['Duration'].sum()
        
        # 3. R2 Utilization
        r2_total = df_ist[df_ist['Dienst'] == 'R2']['Duration'].sum()
        r2_prod = df_ist[(df_ist['Dienst'] == 'R2') & (df_ist['Typ'] == 'Prod')]['Duration'].sum()
        r2_util = (r2_prod / r2_total * 100) if r2_total > 0 else 0
        
        # 4. Production Void (Crunch Time)
        void = 70 # S1/E1 Idle during service
        
        # 10. Pat/Gastro Split
        gastro_min = df_ist[df_ist['Dienst'].isin(['R1', 'R2'])]['Duration'].sum()
        total_min = df_ist['Duration'].sum()
        split = (gastro_min / total_min * 100)

        # 12. Recovery FTE
        recovery = 1.1 # Kalkuliert aus Wegfall R2 Vormittag + Waste-Eliminierung

        return {
            "leakage": leakage,
            "parkinson": parkinson,
            "r2_util": r2_util,
            "void": void,
            "split": split,
            "recovery": recovery
        }

# --- 3. MAIN UI ---
def main():
    st.markdown('<div class="main-header">KITCHEN OPS DEEP AUDIT: STRATEGIC DASHBOARD</div>', unsafe_allow_html=True)

    df_ist = DataEngine.get_ist_data()
    df_soll = DataEngine.get_soll_data()
    m = DataEngine.calculate_metrics(df_ist, df_soll)

    # --- CLUSTER A: FINANZEN ---
    st.markdown('<div class="cluster-header">A. Finanzielle Ineffizienz</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">1. Skill Leakage</div><div class="kpi-value">{int(m["leakage"])} Min</div><div class="kpi-sub trend-bad">Fachkraft-Zeit in Logistik/Waste</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">2. Parkinson Gap</div><div class="kpi-value">{int(m["parkinson"])} Min</div><div class="kpi-sub trend-bad">Bezahlte Ineffizienz / Tag</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">3. R2 Utilization</div><div class="kpi-value">{m["r2_util"]:.1f}%</div><div class="kpi-sub trend-bad">Wertschöpfungs-Quote R2</div></div>', unsafe_allow_html=True)

    # --- CLUSTER B: OPERATIONS ---
    st.markdown('<div class="cluster-header">B. Operative Exzellenz</div>', unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">4. Production Void</div><div class="kpi-value">{m["void"]} Min</div><div class="kpi-sub trend-bad">Stillstand @ Crunch-Time</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">5. Service Idle Time</div><div class="kpi-value">70 Min</div><div class="kpi-sub trend-bad">Warten auf Bons (E1/S1)</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">6. MEP Spread</div><div class="kpi-value">6.5 Std</div><div class="kpi-sub">Zerstückelung über den Tag</div></div>', unsafe_allow_html=True)

    # --- CLUSTER C: RISK & QUALITY ---
    st.markdown('<div class="cluster-header">C. Risiko & Qualität</div>', unsafe_allow_html=True)
    c7, c8, c9 = st.columns(3)
    with c7:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">7. Risk Exposure</div><div class="kpi-value">105 Min</div><div class="kpi-sub trend-bad">Diät-Telefon unbesetzt</div></div>', unsafe_allow_html=True)
    with c8:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">8. Admin Fragments</div><div class="kpi-value">4x</div><div class="kpi-sub trend-bad">Unterbrechungen D1</div></div>', unsafe_allow_html=True)
    with c9:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">9. Thermal Latency</div><div class="kpi-value">3.2 Std</div><div class="kpi-sub">Zeit Prod. bis Verzehr</div></div>', unsafe_allow_html=True)

    # --- CLUSTER D: STRATEGY ---
    st.markdown('<div class="cluster-header">D. Strategische Ausrichtung</div>', unsafe_allow_html=True)
    c10, c11, c12 = st.columns(3)
    with c10:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">10. Pat/Gastro Split</div><div class="kpi-value">{100-m["split"]:.0f}/{m["split"]:.0f}</div><div class="kpi-sub">Fokus Patient vs Gast</div></div>', unsafe_allow_html=True)
    with c11:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">11. Logistics Burden</div><div class="kpi-value">185 Min</div><div class="kpi-sub">Manueller Transport-Aufwand</div></div>', unsafe_allow_html=True)
    with c12:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">12. Recovery Pot.</div><div class="kpi-value">{m["recovery"]} FTE</div><div class="kpi-sub trend-good">Reallokations-Potenzial</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- VISUALIZATION TABS ---
    t1, t2 = st.tabs(["IST-ZUSTAND: DETAIL-AUDIT", "SOLL-MODELL: LEAN PRODUCTION"])

    color_map = {
        "Prod": "#3B82F6", "Service": "#10B981", "Admin": "#F59E0B", 
        "Logistik": "#64748B", "Waste": "#EF4444", "Coord": "#8B5CF6"
    }

    with t1:
        st.info("Befund: Massive Fragmentierung bei D1 und kritische Idle-Blöcke (Rot) während der Servicezeit bei E1/S1/R2.")
        fig_ist = px.timeline(df_ist, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", 
                              hover_name="Task", color_discrete_map=color_map, height=400)
        fig_ist.update_yaxes(autorange="reversed")
        fig_ist.update_xaxes(tickformat="%H:%M")
        st.plotly_chart(fig_ist, use_container_width=True)

    with t2:
        st.success("Lösung: Bündelung der Admin-Blöcke, Integration der Wahlkost in den Saucier-Ablauf und Nutzung der Wartezeit für MEP.")
        fig_soll = px.timeline(df_soll, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", 
                               hover_name="Task", color_discrete_map=color_map, height=350)
        fig_soll.update_yaxes(autorange="reversed")
        fig_soll.update_xaxes(tickformat="%H:%M")
        st.plotly_chart(fig_soll, use_container_width=True)

if __name__ == "__main__":
    main()
