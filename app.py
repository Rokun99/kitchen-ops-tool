import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & ENTERPRISE STYLING ---
st.set_page_config(
    page_title="Kitchen Intelligence | Deep Audit 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clinical Slate/Blue Theme (No Emojis)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #0F172A; background-color: #F8FAFC; }
    
    .main-header { font-size: 24px; font-weight: 700; color: #1E293B; letter-spacing: -0.5px; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 20px;}
    .cluster-header { font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 1.2px; margin-top: 30px; margin-bottom: 12px; border-left: 4px solid #3B82F6; padding-left: 10px;}
    
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
    .kpi-value { font-size: 22px; font-weight: 700; color: #0F172A; }
    .kpi-sub { font-size: 11px; color: #94A3B8; }
    .trend-bad { color: #EF4444; font-weight: 600; }
    .trend-good { color: #10B981; font-weight: 600; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-size: 13px; font-weight: 600; color: #64748B; }
    .stTabs [aria-selected="true"] { color: #3B82F6 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (HIGH-RESOLUTION AUDIT DATA) ---
class DataEngine:
    @staticmethod
    def get_granular_data():
        # Detaillierte Datenbasis aus der PDF-Neukalkulation
        ist_data = [
            # D1 - Diätkoch (Die Admin-Zerstückelung)
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Administration (Mails/Pläne)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:25", "Ende": "08:30", "Task": "Rüstzeit (Posten einrichten)", "Typ": "Rüst"},
            {"Dienst": "D1", "Start": "08:30", "Ende": "09:15", "Task": "Produktion Suppen (Großmenge)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:15", "Ende": "09:45", "Task": "Produktion Ernährungstherapie", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Administration (Check 2)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "10:15", "Ende": "10:45", "Task": "Regenerieren (Cg-Komponenten)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "10:45", "Ende": "11:00", "Task": "Instruktion (Band-Mitarbeiter)", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Administration (Letzte Updates)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service am Band (Diät-Taktung)", "Typ": "Service"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik (Abräumen/Reste)", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:00", "Task": "Administration (Protokolle)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "15:00", "Ende": "16:30", "Typ": "Prod", "Task": "MEP & Vorproduktion"},
            {"Dienst": "D1", "Start": "17:00", "Ende": "18:00", "Typ": "Service", "Task": "Bandabendessen"},

            # E1 - Entremetier (Das Wahlkost-Dilemma)
            {"Dienst": "E1", "Start": "07:15", "Ende": "08:30", "Task": "Prod Stärke (Großmenge)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "08:30", "Ende": "09:30", "Task": "Prod Gemüse (Großmenge)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "10:15", "Ende": "10:45", "Task": "Prod Wahlkost (à la minute)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Wartezeit/Leerlauf (Wahlkost-Abruf)", "Typ": "Waste"},
            {"Dienst": "E1", "Start": "14:00", "Ende": "15:00", "Task": "MEP Folgetag (Gemüse rüsten)", "Typ": "Prod"},

            # S1 - Saucier (Convenience & Joker)
            {"Dienst": "S1", "Start": "07:00", "Ende": "08:30", "Task": "Regenerieren Saucen/Fleisch", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "08:30", "Ende": "09:30", "Task": "Support E1 (Gemüse)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Leerlauf (Warten auf Bons)", "Typ": "Waste"},

            # R1 - Gastronomie (Schmutzig-Sauber-Konflikt)
            {"Dienst": "R1", "Start": "06:30", "Ende": "07:30", "Task": "Warenannahme (Rampe/Schmutzig)", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:30", "Ende": "07:45", "Task": "Hygiene-Schleuse (Umziehen)", "Typ": "Waste"},
            {"Dienst": "R1", "Start": "07:45", "Ende": "08:30", "Task": "Administration (Deklarationen)", "Typ": "Admin"},

            # R2 - Gastronomie (Der Leerlauf-König)
            {"Dienst": "R2", "Start": "06:30", "Ende": "08:00", "Task": "Bestückung Patientenband", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "10:00", "Task": "Schein-Arbeit (Salat-Finish)", "Typ": "Waste"}
        ]
        
        # Generierung SOLL (LEAN)
        soll_data = [
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:45", "Task": "Zentraler Admin-Block", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:45", "Ende": "12:00", "Task": "Fokussierte Diät-Produktion", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Integration Wahlkost komplett", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Power-MEP für Folgetag", "Typ": "Prod"},
            {"Dienst": "R1", "Start": "06:30", "Ende": "10:00", "Task": "Veredelung & Gastgeberschaft", "Typ": "Service"},
            {"Dienst": "R2", "Start": "10:00", "Ende": "14:30", "Task": "Flex-Service (Späterer Start)", "Typ": "Service"}
        ]
        
        return DataEngine.process(ist_data), DataEngine.process(soll_data)

    @staticmethod
    def process(data):
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'])
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'])
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- 3. BUSINESS LOGIC & KPI CALCULATION ---
def get_kpis(df_ist, df_soll):
    # 1. Talent-Fehlallokation (Skill Leakage)
    skilled = ['D1', 'S1', 'E1']
    leakage = df_ist[(df_ist['Dienst'].isin(skilled)) & (df_ist['Typ'].isin(['Logistik', 'Waste']))]['Duration'].sum()
    
    # 2. Parkinson-Verschwendung (Unproduktive Zeit)
    total_waste = df_ist[df_ist['Typ'] == 'Waste']['Duration'].sum()
    
    # 4. Kernzeit-Vakuum (Crunch Time Prod)
    crunch_prod = df_ist[(df_ist['Typ'] == 'Prod') & (df_ist['Start'] >= '11:20') & (df_ist['Start'] <= '12:30')]['Duration'].sum()

    # 12. Reallokations-Potenzial (FTE Recovery)
    # Kalkuliert: R2 Einsparung (3.5h) + Waste-Minimierung
    fte_recovery = 1.1 

    return {
        "leakage": f"{int(leakage)} Min",
        "parkinson": f"{int(total_waste)} Min",
        "r2_eff": "33%",
        "crunch_prod": f"{int(crunch_prod)} Min",
        "idle_service": "70 Min",
        "mep_spread": "6.5 Std",
        "risk_exposure": "105 Min",
        "admin_rate": "4.2x / Tag",
        "thermal_gap": "3.5 Std",
        "time_split": "68/32",
        "log_burden": "190 Min",
        "fte_recovery": f"{fte_recovery} FTE"
    }

# --- 4. MAIN UI ---
def main():
    st.markdown('<div class="main-header">KITCHEN INTELLIGENCE: DEEP AUDIT DASHBOARD</div>', unsafe_allow_html=True)

    df_ist, df_soll = DataEngine.get_granular_data()
    kpis = get_kpis(df_ist, df_soll)

    # --- THE 12 KPIS (REFINED NAMES) ---
    
    st.markdown('<div class="cluster-header">A. Finanzielle Ineffizienz & Fehlallokation</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-title">1. Talent-Fehlallokation</div><div class="kpi-value">{kpis["leakage"]}</div><div class="kpi-sub trend-bad">Fachkraft-Zeit in Logistik/Waste</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-title">2. Parkinson-Verschwendung</div><div class="kpi-value">{kpis["parkinson"]}</div><div class="kpi-sub trend-bad">Bezahlter Leerlauf pro Tag</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-title">3. Kapazitäts-Nutzungsgrad</div><div class="kpi-value">{kpis["r2_eff"]}</div><div class="kpi-sub trend-bad">Effektive Auslastung R2 (Gastro)</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="cluster-header">B. Operative Performance & Flow</div>', unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    c4.markdown(f'<div class="kpi-card"><div class="kpi-title">4. Kernzeit-Vakuum</div><div class="kpi-value">{kpis["crunch_prod"]}</div><div class="kpi-sub trend-bad">Wertschöpfung @ Band-Service</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="kpi-card"><div class="kpi-title">5. Bereitschafts-Leerlauf</div><div class="kpi-value">{kpis["idle_service"]}</div><div class="kpi-sub trend-bad">Wartezeit am Wahlkost-Band</div></div>', unsafe_allow_html=True)
    c6.markdown(f'<div class="kpi-card"><div class="kpi-title">6. Produktions-Fragmentierung</div><div class="kpi-value">{kpis["mep_spread"]}</div><div class="kpi-sub">Zerstückelung MEP-Vorbereitung</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="cluster-header">C. Risiko, Governance & Qualität</div>', unsafe_allow_html=True)
    c7, c8, c9 = st.columns(3)
    c7.markdown(f'<div class="kpi-card"><div class="kpi-title">7. Haftungs-Risiko (Blindflug)</div><div class="kpi-value">{kpis["risk_exposure"]}</div><div class="kpi-sub trend-bad">Pause Diätkoch ohne Backup</div></div>', unsafe_allow_html=True)
    c8.markdown(f'<div class="kpi-card"><div class="kpi-title">8. Interruptions-Rate</div><div class="kpi-value">{kpis["admin_rate"]}</div><div class="kpi-sub trend-bad">Admin-Splitting (Context Switch)</div></div>', unsafe_allow_html=True)
    c9.markdown(f'<div class="kpi-card"><div class="kpi-title">9. Frische-Latenz (Thermal Gap)</div><div class="kpi-value">{kpis["thermal_gap"]}</div><div class="kpi-sub">Zeit Prod. bis Verzehr</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="cluster-header">D. Strategische Ausrichtung</div>', unsafe_allow_html=True)
    c10, c11, c12 = st.columns(3)
    c10.markdown(f'<div class="kpi-card"><div class="kpi-title">10. Patienten- vs. Gast-Fokus</div><div class="kpi-value">{kpis["time_split"]}</div><div class="kpi-sub">Zeit-Verhältnis (Pat/Gastro)</div></div>', unsafe_allow_html=True)
    c11.markdown(f'<div class="kpi-card"><div class="kpi-title">11. Logistik-Ballast</div><div class="kpi-value">{kpis["log_burden"]}</div><div class="kpi-sub">Minuten Transport/Reinigung</div></div>', unsafe_allow_html=True)
    c12.markdown(f'<div class="kpi-card"><div class="kpi-title">12. Reallokations-Potenzial</div><div class="kpi-value">{kpis["fte_recovery"]}</div><div class="kpi-sub trend-good">FTE Optimierungs-Chance</div></div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- 5. DETAILED BELASTUNGSKURVE ---
    st.markdown('<div class="cluster-header">E. Detaillierte Belastungskurve (Personalstärke)</div>', unsafe_allow_html=True)
    
    # 15-Minute Grid Calculation
    load_data = []
    for h in range(5, 20):
        for m in [0, 15, 30, 45]:
            t = datetime(2026, 1, 1, h, m)
            active = len(df_ist[(df_ist['Start_DT'] <= t) & (df_ist['End_DT'] > t)])
            load_data.append({"Zeit": f"{h:02d}:{m:02d}", "Personal": active})
    
    fig_load = px.area(pd.DataFrame(load_data), x="Zeit", y="Personal", line_shape="spline")
    fig_load.update_traces(line_color="#3B82F6", fillcolor="rgba(59, 130, 246, 0.1)")
    fig_load.update_layout(plot_bgcolor="white", height=300, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="MA Aktiv")
    st.plotly_chart(fig_load, use_container_width=True)

    # --- 6. TRIPLE TIMELINES ---
    st.markdown('<div class="cluster-header">F. Zeit-Struktur & Verschwendung (Lean Check)</div>', unsafe_allow_html=True)
    
    tab_ist, tab_waste, tab_soll = st.tabs(["1. IST-ZUSTAND (DETAIL)", "2. VERSCHWENDUNGS-ANALYSE", "3. SOLL-MODELL (LEAN)"])

    color_map = {
        "Prod": "#3B82F6", "Service": "#10B981", "Admin": "#F59E0B", 
        "Logistik": "#64748B", "Waste": "#EF4444", "Rüst": "#94A3B8", "Coord": "#8B5CF6"
    }

    with tab_ist:
        st.info("Befund: Starke Fragmentierung der Admin-Blöcke (Gelb) und ungenutzte Kapazitäten bei R2/S1.")
        fig1 = px.timeline(df_ist, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", 
                           hover_name="Task", color_discrete_map=color_map, height=450)
        fig1.update_yaxes(autorange="reversed")
        fig1.update_xaxes(tickformat="%H:%M")
        st.plotly_chart(fig1, use_container_width=True)

    with tab_waste:
        st.error("Identifizierte Verschwendung: Die roten Blöcke markieren die '70-Minuten-Falle' und die 'Schein-Arbeit'. Hier werden Kosten ohne Gegenwert generiert.")
        df_waste = df_ist[df_ist['Typ'] == 'Waste']
        fig2 = px.timeline(df_waste, x_start="Start_DT", x_end="End_DT", y="Dienst", color_discrete_sequence=["#EF4444"], height=300)
        fig2.update_yaxes(autorange="reversed")
        fig2.update_xaxes(tickformat="%H:%M")
        st.plotly_chart(fig2, use_container_width=True)

    with tab_soll:
        st.success("Zielbild: Integrierte Wahlkost, gebündelte Administration und Power-Produktion in den Leerlaufzeiten.")
        fig3 = px.timeline(df_soll, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", 
                           hover_name="Task", color_discrete_map=color_map, height=400)
        fig3.update_yaxes(autorange="reversed")
        fig3.update_xaxes(tickformat="%H:%M")
        st.plotly_chart(fig3, use_container_width=True)

if __name__ == "__main__":
    main()
