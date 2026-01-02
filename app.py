import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Kitchen Intelligence | Deep Audit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enterprise CSS (Clean, No Emojis, Slate/Blue Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #0F172A; background-color: #F8FAFC; }
    
    .main-header { font-size: 26px; font-weight: 700; color: #1E293B; letter-spacing: -0.5px; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 20px;}
    .cluster-header { font-size: 14px; font-weight: 600; color: #3B82F6; text-transform: uppercase; letter-spacing: 1px; margin-top: 20px; margin-bottom: 10px; }
    
    /* KPI Cards Compact */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 15px;
        height: 120px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .kpi-title { font-size: 10px; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 5px; }
    .kpi-value { font-size: 22px; font-weight: 700; color: #0F172A; }
    .kpi-sub { font-size: 11px; color: #64748B; margin-top: 5px; }
    .trend-bad { color: #EF4444; font-weight: 600; }
    .trend-good { color: #10B981; font-weight: 600; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; border-bottom: 1px solid #E2E8F0; }
    .stTabs [data-baseweb="tab"] { font-size: 13px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (GRANULAR DATA) ---
class DataEngine:
    @staticmethod
    def get_ist_data_granular():
        # High-Resolution Data based on Audit
        data = [
            # --- D1 (Fragmented Admin) ---
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Admin: Mails & Orgacard (Start)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:25", "Ende": "08:30", "Task": "Hygiene: Wechsel Küche", "Typ": "Waste"},
            {"Dienst": "D1", "Start": "08:30", "Ende": "09:15", "Task": "Prod: Suppen Großmenge", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:15", "Ende": "09:45", "Task": "Prod: Diät-Ableitungen (Stress)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Admin: Mail-Check 2", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "10:15", "Ende": "11:00", "Task": "Prod: Regenerieren", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Admin: Letzte Änderungen", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service: Bandleitung Diät", "Typ": "Service"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik: Rückstellproben/Abräumen", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "12:45", "Ende": "14:30", "Task": "PAUSE (Risiko: Keine Vertretung)", "Typ": "Pause"}, # RISK!
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:00", "Task": "Admin: Protokolle", "Typ": "Admin"},
            
            # --- R1 (Dirty Start) ---
            {"Dienst": "R1", "Start": "06:30", "Ende": "07:15", "Task": "Logistik: Warenannahme Rampe", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:15", "Ende": "07:30", "Task": "Logistik: Verräumen", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:30", "Ende": "07:45", "Task": "Hygiene: Umziehen/Waschen", "Typ": "Waste"},
            {"Dienst": "R1", "Start": "07:45", "Ende": "08:30", "Task": "Admin: Deklarationen", "Typ": "Admin"},
            {"Dienst": "R1", "Start": "08:30", "Ende": "10:00", "Task": "Prod: Freeflow für Morgen (Zu früh)", "Typ": "Prod"},
            
            # --- R2 (Alibi) ---
            {"Dienst": "R2", "Start": "06:30", "Ende": "08:00", "Task": "Service: Bestücken Patientenband (Falsche Rolle)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "10:00", "Task": "Prod: 12 Salate (Alibi-Tätigkeit)", "Typ": "Waste"},
            {"Dienst": "R2", "Start": "10:20", "Ende": "11:30", "Task": "Service: Setup & Fotos", "Typ": "Service"},
            
            # --- S1 (Convenience Gap) ---
            {"Dienst": "S1", "Start": "07:00", "Ende": "08:00", "Task": "Prod: Saucen Finish (Päckli)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "08:00", "Ende": "10:00", "Task": "Prod: Support E1 (Unterfordert)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "10:15", "Ende": "11:20", "Task": "Logistik: Wagen bereitstellen", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "WAIT: Warten auf Wahlkost (Idle)", "Typ": "Waste"},
            {"Dienst": "S1", "Start": "12:30", "Ende": "13:00", "Task": "Logistik: Reinigung", "Typ": "Logistik"},
            
            # --- E1 (The Waiter) ---
            {"Dienst": "E1", "Start": "07:00", "Ende": "11:20", "Task": "Prod: Stärke & Gemüse", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "WAIT: Warten auf Bons (Idle)", "Typ": "Waste"},
            
            # --- H1 (Wrong Role) ---
            {"Dienst": "H1", "Start": "05:30", "Ende": "06:50", "Task": "Prod: Kocht Griessbrei (Risiko)", "Typ": "Prod"},
            
            # --- G2 (Part Time Prod) ---
            {"Dienst": "G2", "Start": "14:15", "Ende": "16:00", "Task": "Waste: Arbeit suchen (kein Mi/So)", "Typ": "Waste"},
        ]
        return DataEngine.process_df(data)

    @staticmethod
    def get_soll_data_optimized():
        # The LEAN Model
        data = [
            # D1: Focused
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:45", "Task": "Admin-Block (Fix)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:45", "Ende": "12:00", "Task": "Prod: Diät & Suppen (Flow)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "12:00", "Ende": "12:45", "Task": "Service: Diät Validierung", "Typ": "Service"},
            
            # S1: The Cover
            {"Dienst": "S1", "Start": "07:00", "Ende": "11:20", "Task": "Prod: Fleisch & Saucen", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Prod: Wahlkost KOMPLETT (Allein)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "12:45", "Ende": "14:30", "Task": "Admin: Diät-Telefon (Vertretung D1)", "Typ": "Admin"},
            
            # R1: Host
            {"Dienst": "R1", "Start": "06:30", "Ende": "10:00", "Task": "Quality: Veredelung & Host", "Typ": "Service"},
            
            # R2: Cost Saver
            {"Dienst": "R2", "Start": "10:00", "Ende": "14:00", "Task": "Service: Rush Hour Only", "Typ": "Service"},
            
            # E1: Power Producer
            {"Dienst": "E1", "Start": "07:00", "Ende": "11:20", "Task": "Prod: Stärke & Gemüse", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Prod: MEP für Morgen (statt Warten)", "Typ": "Prod"},
            
            # H3: Assembly
            {"Dienst": "H3", "Start": "12:00", "Ende": "12:30", "Task": "Prod: Bircher für H1", "Typ": "Prod"},
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
    def calculate_12_kpis(df_ist, df_soll):
        total_min_ist = df_ist['Duration'].sum()
        
        # --- Cluster A: Financial Inefficiency ---
        # 1. Skill Leakage (Fachkräfte machen Waste/Logistik)
        skilled = ['S1', 'E1', 'D1', 'G2']
        leakage_min = df_ist[(df_ist['Dienst'].isin(skilled)) & (df_ist['Typ'].isin(['Logistik', 'Waste']))]['Duration'].sum()
        leakage_pct = (leakage_min / df_ist[df_ist['Dienst'].isin(skilled)]['Duration'].sum()) * 100
        
        # 2. Parkinson Gap (Total Waste)
        parkinson_min = df_ist[df_ist['Typ'] == 'Waste']['Duration'].sum()
        
        # 3. R2 Utilization (Wertschöpfung R2)
        r2_total = df_ist[df_ist['Dienst'] == 'R2']['Duration'].sum()
        r2_value = df_ist[(df_ist['Dienst'] == 'R2') & (df_ist['Typ'] == 'Service')]['Duration'].sum()
        r2_util = (r2_value / r2_total) * 100 if r2_total > 0 else 0
        
        # --- Cluster B: Operational Excellence ---
        # 4. Production Void (11:20-12:30)
        # Check Prod in crunch time
        crunch_start = datetime(2026, 1, 1, 11, 20)
        crunch_end = datetime(2026, 1, 1, 12, 30)
        void_ist = df_ist[(df_ist['Typ'] == 'Prod') & (df_ist['Start_DT'] < crunch_end) & (df_ist['End_DT'] > crunch_start)]['Duration'].sum()
        
        # 5. Service Idle Time (E1/S1 Warten)
        idle_time = df_ist[(df_ist['Dienst'].isin(['E1', 'S1'])) & (df_ist['Task'].str.contains('WAIT'))]['Duration'].sum()
        
        # 6. MEP Spread (Hardcoded Analysis Fact)
        mep_spread = "8h" 

        # --- Cluster C: Quality & Risk ---
        # 7. Risk Exposure (D1 Pause)
        risk_min = 105 # 12:45 to 14:30
        
        # 8. Admin Fragmentation (D1 Admin Blocks)
        admin_frags = len(df_ist[(df_ist['Dienst'] == 'D1') & (df_ist['Typ'] == 'Admin')])
        
        # 9. Thermal Latency (Hardcoded Analysis Fact)
        latency = "3.5h" # Suppe 8:00 -> 11:30

        # --- Cluster D: Strategy ---
        # 10. Patient vs Gastro Split (Time)
        gastro_team = ['R1', 'R2', 'H1', 'H2']
        gastro_share = (df_ist[df_ist['Dienst'].isin(gastro_team)]['Duration'].sum() / total_min_ist) * 100
        
        # 11. Logistics Burden
        log_burden = df_ist[df_ist['Typ'] == 'Logistik']['Duration'].sum()
        
        # 12. Recovery Potential (FTE)
        # R2 Einsparung (3.5h) + Waste Reduction (~4h)
        fte_recovery = 0.9 

        return {
            "leakage": f"{leakage_pct:.0f}%",
            "parkinson": f"{int(parkinson_min)} min",
            "r2_util": f"{r2_util:.0f}%",
            "prod_void": f"{int(void_ist)} min",
            "idle": f"{int(idle_time)} min",
            "mep": mep_spread,
            "risk": f"{risk_min} min",
            "frags": f"{admin_frags}x",
            "latency": latency,
            "split": f"{100-gastro_share:.0f}/{gastro_share:.0f}",
            "logistics": f"{int(log_burden)} min",
            "recovery": f"{fte_recovery} FTE"
        }

# --- 3. MAIN UI ---
def main():
    st.markdown('<div class="main-header">KITCHEN INTELLIGENCE: DEEP AUDIT 2026</div>', unsafe_allow_html=True)

    df_ist = DataEngine.get_ist_data_granular()
    df_soll = DataEngine.get_soll_data_optimized()
    kpis = DataEngine.calculate_12_kpis(df_ist, df_soll)

    # --- THE 12 KPIS IN CLUSTERS ---
    
    # CLUSTER A: FINANZEN
    st.markdown('<div class="cluster-header">A. Finanzielle Ineffizienz</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">1. Skill Leakage</div><div class="kpi-value">{kpis['leakage']}</div><div class="kpi-sub trend-bad">Fachkraft-Zeit verschwendet</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">2. Parkinson Gap</div><div class="kpi-value">{kpis['parkinson']}</div><div class="kpi-sub trend-bad">Bez. Leerlauf / Tag</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">3. R2 Utilization</div><div class="kpi-value">{kpis['r2_util']}</div><div class="kpi-sub trend-bad">Echte Produktivität</div></div>""", unsafe_allow_html=True)

    # CLUSTER B: OPERATIONS
    st.markdown('<div class="cluster-header">B. Operative Exzellenz</div>', unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">4. Production Void</div><div class="kpi-value">{kpis['prod_void']}</div><div class="kpi-sub trend-bad">Produktion @ 11:30</div></div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">5. Service Idle Time</div><div class="kpi-value">{kpis['idle']}</div><div class="kpi-sub trend-bad">Wartezeit am Pass</div></div>""", unsafe_allow_html=True)
    with c6:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">6. MEP Spread</div><div class="kpi-value">{kpis['mep']}</div><div class="kpi-sub">Zerstückelung (Std)</div></div>""", unsafe_allow_html=True)

    # CLUSTER C: RISK & QUALITY
    st.markdown('<div class="cluster-header">C. Risiko & Qualität</div>', unsafe_allow_html=True)
    c7, c8, c9 = st.columns(3)
    with c7:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">7. Risk Exposure</div><div class="kpi-value">{kpis['risk']}</div><div class="kpi-sub trend-bad">Diät-Blindflug (Min)</div></div>""", unsafe_allow_html=True)
    with c8:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">8. Admin Fragments</div><div class="kpi-value">{kpis['frags']}</div><div class="kpi-sub trend-bad">Unterbrechungen D1</div></div>""", unsafe_allow_html=True)
    with c9:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">9. Thermal Latency</div><div class="kpi-value">{kpis['latency']}</div><div class="kpi-sub">Prod. zu Verzehr</div></div>""", unsafe_allow_html=True)

    # CLUSTER D: STRATEGY
    st.markdown('<div class="cluster-header">D. Strategische Ausrichtung</div>', unsafe_allow_html=True)
    c10, c11, c12 = st.columns(3)
    with c10:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">10. Pat/Gastro Split</div><div class="kpi-value">{kpis['split']}</div><div class="kpi-sub">Fokus Patient vs Gast</div></div>""", unsafe_allow_html=True)
    with c11:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">11. Logistics Burden</div><div class="kpi-value">{kpis['logistics']}</div><div class="kpi-sub">Minuten Transport/Tag</div></div>""", unsafe_allow_html=True)
    with c12:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-title">12. Recovery Pot.</div><div class="kpi-value">{kpis['recovery']}</div><div class="kpi-sub trend-good">FTE Einsparung</div></div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- TIMELINES ---
    tab1, tab2 = st.tabs(["🔴 IST-ZUSTAND (DETAIL-ANALYSE)", "🟢 SOLL-MODELL (LEAN TARGET)"])

    color_map = {
        "Prod": "#3B82F6", "Service": "#10B981", "Admin": "#F59E0B", 
        "Logistik": "#64748B", "Waste": "#EF4444", "Pause": "#CBD5E1", "Coord": "#8B5CF6"
    }

    with tab1:
        st.markdown("**Befund:** Extreme Zerstückelung (D1), Wartezeiten (Grau/Rot) bei S1/E1/R2. Logistik (Grau) dominiert den Start.")
        fig = px.timeline(df_ist[df_ist['Typ'] != 'Pause'], x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ",
                          hover_name="Task", color_discrete_map=color_map, height=450)
        fig.update_yaxes(categoryorder="array", categoryarray=["R1", "R2", "H1", "S1", "E1", "D1", "G2"])
        fig.update_xaxes(tickformat="%H:%M")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("**Lösung:** R2 startet spät. D1/E1 haben lange blaue Blöcke (Produktionsfluss). Admin ist gebündelt.")
        fig2 = px.timeline(df_soll, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ",
                          hover_name="Task", color_discrete_map=color_map, height=450)
        fig2.update_yaxes(categoryorder="array", categoryarray=["R1", "R2", "H1", "S1", "E1", "D1", "G2"])
        fig2.update_xaxes(tickformat="%H:%M")
        st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    main()
