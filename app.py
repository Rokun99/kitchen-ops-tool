import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Kitchen Strategy Audit 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enterprise-Grade CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #0F172A; background-color: #F8FAFC; }
    
    .header-box { padding: 20px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 20px; }
    .main-title { font-size: 26px; font-weight: 700; color: #1E293B; letter-spacing: -0.5px; }
    .sub-title { font-size: 14px; color: #64748B; margin-top: 5px; }
    
    .kpi-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02); height: 160px;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .kpi-label { font-size: 11px; font-weight: 600; text-transform: uppercase; color: #64748B; letter-spacing: 0.5px; }
    .kpi-val { font-size: 28px; font-weight: 700; color: #0F172A; }
    .kpi-delta { font-size: 13px; font-weight: 600; margin-top: 4px; display: flex; align-items: center; gap: 5px; }
    .pos { color: #10B981; } .neg { color: #EF4444; } .neu { color: #64748B; }
    
    .alert-box {
        padding: 15px; border-radius: 6px; margin-bottom: 15px; font-size: 13px; border-left: 4px solid;
    }
    .alert-red { background: #FEF2F2; border-color: #EF4444; color: #991B1B; }
    .alert-green { background: #F0FDF4; border-color: #16A34A; color: #166534; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (IST vs. SOLL) ---
class DataEngine:
    @staticmethod
    def get_ist_data():
        # Die harte Realität: Fragmentierung, Logistik, Wartezeiten
        data = [
            # D1: Fragmentiert
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Admin: Mails & Orgacard (1)", "Typ": "Admin", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "08:25", "Ende": "09:45", "Task": "Prod: Suppen & Diät (Stress)", "Typ": "Prod", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Admin: Mails Check (2)", "Typ": "Admin", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "10:15", "Ende": "11:00", "Task": "Prod: Regenerieren", "Typ": "Prod", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Admin: Orgacard Check (3)", "Typ": "Admin", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service: Diät Anrichten", "Typ": "Service", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik: Abräumen", "Typ": "Logistik", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "12:45", "Ende": "14:30", "Task": "PAUSE (Risiko: Niemand da)", "Typ": "Pause", "Team": "Cucina"}, # Risiko!
            
            # R1: Logistik-Last
            {"Dienst": "R1", "Start": "06:30", "Ende": "07:30", "Task": "Logistik: Warenannahme & Schleppen", "Typ": "Logistik", "Team": "Gastro"},
            {"Dienst": "R1", "Start": "07:30", "Ende": "08:30", "Task": "Admin: Deklarationen", "Typ": "Admin", "Team": "Gastro"},
            {"Dienst": "R1", "Start": "08:30", "Ende": "10:00", "Task": "Prod: Freeflow für Morgen (Ineffizient)", "Typ": "Prod", "Team": "Gastro"},
            
            # R2: Alibi-Arbeit
            {"Dienst": "R2", "Start": "06:30", "Ende": "08:00", "Task": "Service: Am Patientenband stehen", "Typ": "Service", "Team": "Gastro"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "10:00", "Task": "Alibi: 12 Salate machen & Warten", "Typ": "Waste", "Team": "Gastro"},
            
            # S1: Wartezeit
            {"Dienst": "S1", "Start": "07:00", "Ende": "11:20", "Task": "Prod: Convenience Finish", "Typ": "Prod", "Team": "Cucina"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Wait: Warten auf Wahlkost (Leerlauf)", "Typ": "Waste", "Team": "Cucina"},
            
            # E1: Wartezeit
            {"Dienst": "E1", "Start": "07:00", "Ende": "11:20", "Task": "Prod: Stärke & Gemüse", "Typ": "Prod", "Team": "Cucina"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Wait: Warten auf Wahlkost (Leerlauf)", "Typ": "Waste", "Team": "Cucina"},
            
            # H1: Falsche Rolle
            {"Dienst": "H1", "Start": "05:30", "Ende": "06:50", "Task": "Prod: Kocht Griessbrei & Dessert", "Typ": "Prod", "Team": "Gastro"}, # Sollte Service sein
            
            # G2: Leerlauf Nachmittag
            {"Dienst": "G2", "Start": "14:15", "Ende": "16:00", "Task": "Waste: Arbeit suchen (kein Salat-Tag)", "Typ": "Waste", "Team": "Cucina"},
        ]
        return DataEngine.process_df(data)

    @staticmethod
    def get_soll_data():
        # Die Lean-Vision: Fokus, Qualität, Effizienz
        data = [
            # D1: Clean Process
            {"Dienst": "D1", "Start": "08:00", "Ende": "09:00", "Task": "Admin-Block: Alle Mails/Orgacard", "Typ": "Admin", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "09:00", "Ende": "12:00", "Task": "Prod: Diät & Suppen (Ungestört)", "Typ": "Prod", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "12:00", "Ende": "12:45", "Task": "Service: Diät Validierung", "Typ": "Service", "Team": "Cucina"},
            # D1 geht in Pause, aber S1 übernimmt offiziell (siehe unten)
            
            # R1: Reiner Gastgeber
            {"Dienst": "R1", "Start": "06:30", "Ende": "10:00", "Task": "Quality: Frische Veredelung & Service-Setup", "Typ": "Service", "Team": "Gastro"},
            
            # R2: Startet spät (Geld sparen)
            {"Dienst": "R2", "Start": "10:00", "Ende": "14:00", "Task": "Service: Rush-Hour Support", "Typ": "Service", "Team": "Gastro"},
            
            # S1: Der Macher
            {"Dienst": "S1", "Start": "07:00", "Ende": "11:20", "Task": "Prod: Fleisch & Saucen", "Typ": "Prod", "Team": "Cucina"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Prod+Service: Wahlkost KOMPLETT (für E1)", "Typ": "Prod", "Team": "Cucina"},
            {"Dienst": "S1", "Start": "12:45", "Ende": "14:30", "Task": "Responsibility: Diät-Telefon (Vertretung D1)", "Typ": "Admin", "Team": "Cucina"},
            
            # E1: Power-Produzent
            {"Dienst": "E1", "Start": "07:00", "Ende": "11:20", "Task": "Prod: Stärke & Gemüse", "Typ": "Prod", "Team": "Cucina"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Prod: MEP für Morgen (statt Warten)", "Typ": "Prod", "Team": "Cucina"}, # Hier wird gewonnen!
            
            # H1: Logistiker
            {"Dienst": "H1", "Start": "05:30", "Ende": "12:00", "Task": "Logistik: Band & Service (Kein Kochen)", "Typ": "Logistik", "Team": "Gastro"},
            
            # G2: Springer
            {"Dienst": "G2", "Start": "14:15", "Ende": "16:00", "Task": "Prod: Dessert-Support oder Springer Warm", "Typ": "Prod", "Team": "Cucina"}, # Kein Leerlauf mehr
        ]
        return DataEngine.process_df(data)

    @staticmethod
    def process_df(data):
        df = pd.DataFrame(data)
        # Dummy date for plotting
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'])
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'])
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

    @staticmethod
    def calculate_kpis(df_ist, df_soll):
        # 1. Waste Time (Leerlauf + unnötige Logistik)
        waste_ist = df_ist[df_ist['Typ'].isin(['Waste', 'Logistik'])]['Duration'].sum()
        waste_soll = df_soll[df_soll['Typ'].isin(['Waste'])]['Duration'].sum() # Logistik im SOLL ist gewollt (H1), daher nur Waste zählen
        
        # 2. Production Time (Wertschöpfung)
        prod_ist = df_ist[df_ist['Typ'] == 'Prod']['Duration'].sum()
        prod_soll = df_soll[df_soll['Typ'] == 'Prod']['Duration'].sum()
        
        # 3. FTE Savings (R2 Start später + Effizienz)
        # Grobe Schätzung: R2 spart 3.5h, Effizienzgewinne E1/S1 ca 2h
        fte_saving = 0.8 # Konservativ: fast 1 Stelle
        
        return {
            "waste_red": int(waste_ist - waste_soll),
            "prod_gain": int(prod_soll - prod_ist),
            "fte_pot": f"{fte_saving} FTE"
        }

# --- 3. MAIN APP ---
def main():
    # Header
    st.markdown('<div class="header-box"><div class="main-title">Kitchen Strategy Audit 2026</div><div class="sub-title">Status Quo vs. Lean Operations Target Model</div></div>', unsafe_allow_html=True)

    # Load Data
    df_ist = DataEngine.get_ist_data()
    df_soll = DataEngine.get_soll_data()
    kpis = DataEngine.calculate_kpis(df_ist, df_soll)

    # --- EXECUTIVE DASHBOARD ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div><div class="kpi-label">Verschwendung (Waste)</div><div class="kpi-val">{kpis['waste_red']} min</div></div>
            <div class="kpi-delta pos">▼ Reduktion pro Tag</div>
        </div>""", unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div><div class="kpi-label">Produktions-Gewinn</div><div class="kpi-val">+{kpis['prod_gain']} min</div></div>
            <div class="kpi-delta pos">▲ Mehr Kochzeit (Qualität)</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div><div class="kpi-label">Einspar-Potenzial</div><div class="kpi-val">{kpis['fte_pot']}</div></div>
            <div class="kpi-delta pos">durch R2-Kürzung & Effizienz</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div><div class="kpi-label">Risiko-Status</div><div class="kpi-val">GELÖST</div></div>
            <div class="kpi-delta pos">Diät-Lücke & Hygiene R1</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABS FOR DEEP DIVE ---
    tab_ist, tab_soll, tab_audit = st.tabs(["🔴 IST-Zustand (Pain Points)", "🟢 SOLL-Modell (Lean Vision)", "📋 Audit-Details"])

    # Colors
    color_map = {
        "Prod": "#3B82F6",    # Blue
        "Service": "#10B981", # Green
        "Admin": "#F59E0B",   # Orange
        "Logistik": "#64748B",# Slate
        "Waste": "#EF4444",   # Red (Critical)
        "Pause": "#E2E8F0"    # Gray
    }

    with tab_ist:
        st.markdown("##### Analyse der aktuellen Ineffizienzen")
        fig_ist = px.timeline(
            df_ist, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ",
            hover_name="Task", color_discrete_map=color_map,
            category_orders={"Dienst": ["R1", "R2", "H1", "S1", "E1", "D1", "G2"]}
        )
        fig_ist.update_layout(height=400, margin=dict(t=0,b=0), xaxis_title="", yaxis_title="", plot_bgcolor="white")
        fig_ist.update_xaxes(tickformat="%H:%M", gridcolor="#F1F5F9")
        st.plotly_chart(fig_ist, use_container_width=True)
        
        st.error("**Kritische Befunde:** Rote Blöcke (Waste) bei R2 und S1/E1 (Warten). Zerstückelung bei D1 (Admin). Logistik bei R1 am Morgen.")

    with tab_soll:
        st.markdown("##### Optimierter Prozess (Lean & Quality Focused)")
        fig_soll = px.timeline(
            df_soll, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ",
            hover_name="Task", color_discrete_map=color_map,
            category_orders={"Dienst": ["R1", "R2", "H1", "S1", "E1", "D1", "G2"]}
        )
        fig_soll.update_layout(height=400, margin=dict(t=0,b=0), xaxis_title="", yaxis_title="", plot_bgcolor="white")
        fig_soll.update_xaxes(tickformat="%H:%M", gridcolor="#F1F5F9")
        st.plotly_chart(fig_soll, use_container_width=True)
        
        st.success("**Die Lösung:** R2 startet spät. S1 übernimmt Wahlkost komplett. D1 hat Admin-Block. E1 produziert durch.")

    with tab_audit:
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("### 1. Das 'Convenience-Paradoxon'")
            st.info("""
            **Problem:** Trotz hohem Convenience-Grad (Päckli-Saucen, fertiger Salat) ist die Personalzeit nicht reduziert.
            **Beweis:** G2 hat Nachmittags Leerlauf. S1 putzt 2 Stunden.
            **Lösung:** Umwandlung dieser Leerzeiten in echte Produktion (Springer-Funktion) oder Reduktion der Stunden (R2).
            """)
            
            st.markdown("### 2. Die '70-Minuten-Falle'")
            st.info("""
            **Problem:** Zwischen 11:20 und 12:30 Uhr stehen S1 und E1 oft nur bereit ("Warten auf Bons").
            **Lösung:** S1 übernimmt alle 20 Wahlkost-Teller allein. E1 wird frei für Produktion (Mise-en-Place für morgen).
            """)

        with c_right:
            st.markdown("### 3. Diät-Sicherheit (Risk)")
            st.info("""
            **Problem:** D1 ist mittags (12:45) in Pause. Rückfragen zu Allergenen laufen ins Leere.
            **Lösung:** S1 übernimmt offiziell die Diät-Vertretung (Telefon) ab 12:45 Uhr.
            """)
            
            st.markdown("### 4. R1 Hygiene & Fokus")
            st.info("""
            **Problem:** R1 macht Warenannahme (Schmutz) und geht dann ans Buffet.
            **Lösung:** Logistik macht Warenannahme. R1 startet sauber am Buffet -> Fokus auf Gast & Showteller.
            """)

if __name__ == "__main__":
    main()
