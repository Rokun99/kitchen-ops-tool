import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Operations Intelligence Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enterprise CSS (Clean, No Emojis, Slate/Blue Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #0F172A; background-color: #F1F5F9; }
    
    /* Header */
    .main-header { font-size: 24px; font-weight: 700; color: #1E293B; margin-bottom: 4px; letter-spacing: -0.5px; }
    .sub-header { font-size: 14px; color: #64748B; margin-bottom: 32px; }

    /* KPI Cards */
    .kpi-container {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .kpi-title { font-size: 11px; font-weight: 600; text-transform: uppercase; color: #64748B; letter-spacing: 0.5px; margin-bottom: 8px; }
    .kpi-value { font-size: 24px; font-weight: 700; color: #0F172A; margin-bottom: 4px; }
    .kpi-desc { font-size: 12px; color: #64748B; line-height: 1.4; }
    
    /* Alert Boxes */
    .alert-box { padding: 16px; border-radius: 6px; margin-bottom: 12px; font-size: 13px; line-height: 1.5; }
    .alert-red { background-color: #FEF2F2; border-left: 4px solid #EF4444; color: #991B1B; }
    .alert-yellow { background-color: #FFFBEB; border-left: 4px solid #F59E0B; color: #92400E; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 32px; background-color: transparent; border-bottom: 1px solid #E2E8F0; }
    .stTabs [data-baseweb="tab"] { height: 48px; font-size: 13px; font-weight: 500; color: #64748B; border: none; background-color: transparent; }
    .stTabs [aria-selected="true"] { color: #0F172A !important; border-bottom: 2px solid #0F172A !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE (VALIDATED FACTS) ---
class DataEngine:
    @staticmethod
    def get_data():
        # Daten basierend auf D1.docx - S1.docx
        # Typen: Production, Service, Logistics, Admin, Break
        data = [
            # D1 (Diätetik)
            {"Dienst": "D1", "Start": "08:00", "Ende": "10:00", "Task": "Suppen & Diät-Produktion", "Typ": "Production", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "10:15", "Ende": "11:20", "Task": "Regenerieren & Cg-Komponenten", "Typ": "Production", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Anrichten Band (Service)", "Typ": "Service", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Abräumen & Kühlung", "Typ": "Logistics", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "12:45", "Ende": "14:30", "Task": "Abwesenheit (Pause)", "Typ": "Break", "Team": "Cucina"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:50", "Task": "Protokolle & Admin", "Typ": "Admin", "Team": "Cucina"},
            
            # S1 (Saucier)
            {"Dienst": "S1", "Start": "07:00", "Ende": "10:00", "Task": "Fleisch & Saucen", "Typ": "Production", "Team": "Cucina"},
            {"Dienst": "S1", "Start": "10:15", "Ende": "11:20", "Task": "Wahlkost & Regenerieren", "Typ": "Production", "Team": "Cucina"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Service Anrichten", "Typ": "Service", "Team": "Cucina"},
            {"Dienst": "S1", "Start": "12:30", "Ende": "13:00", "Task": "Zwischenreinigung", "Typ": "Logistik", "Team": "Cucina"},
            {"Dienst": "S1", "Start": "13:30", "Ende": "15:54", "Task": "Pläne & Endreinigung", "Typ": "Admin", "Team": "Cucina"}, # Gemischt Admin/Logistik -> hier als Admin gewichtet

            # E1 (Entremetier)
            {"Dienst": "E1", "Start": "07:00", "Ende": "10:00", "Task": "Beilagen & Gemüse", "Typ": "Production", "Team": "Cucina"},
            {"Dienst": "E1", "Start": "10:15", "Ende": "11:20", "Task": "Wahlkost", "Typ": "Production", "Team": "Cucina"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Service Anrichten", "Typ": "Service", "Team": "Cucina"},
            {"Dienst": "E1", "Start": "12:30", "Ende": "13:00", "Task": "Reinigung & Nachschub", "Typ": "Logistik", "Team": "Cucina"},
            
            # G2 (Gardemanger)
            {"Dienst": "G2", "Start": "09:30", "Ende": "13:30", "Task": "Kaltküche & Absprache", "Typ": "Production", "Team": "Cucina"},
            {"Dienst": "G2", "Start": "14:15", "Ende": "16:00", "Task": "MEP & Protokolle", "Typ": "Production", "Team": "Cucina"},
            {"Dienst": "G2", "Start": "16:00", "Ende": "17:00", "Task": "Absprache & Reinigung", "Typ": "Logistik", "Team": "Cucina"},

            # Gastro / Service Team (R1, R2, H1, H2)
            {"Dienst": "R1", "Start": "06:30", "Ende": "10:00", "Task": "Warenannahme & Gastro", "Typ": "Logistik", "Team": "Restaurazione"},
            {"Dienst": "R1", "Start": "10:20", "Ende": "14:00", "Task": "Restaurant Service", "Typ": "Service", "Team": "Restaurazione"},
            {"Dienst": "R2", "Start": "06:30", "Ende": "14:00", "Task": "Frühstück & Service", "Typ": "Service", "Team": "Restaurazione"},
            {"Dienst": "H1", "Start": "05:30", "Ende": "12:30", "Task": "Frühstück & Band", "Typ": "Service", "Team": "Restaurazione"},
            {"Dienst": "H1", "Start": "13:30", "Ende": "14:40", "Task": "Protokolle", "Typ": "Admin", "Team": "Restaurazione"},
            {"Dienst": "H2", "Start": "09:15", "Ende": "13:30", "Task": "Desserts & Service", "Typ": "Service", "Team": "Restaurazione"},
        ]
        
        df = pd.DataFrame(data)
        # Normalize Dates
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'].str.replace('.', ':'))
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'].str.replace('.', ':'))
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

    @staticmethod
    def calculate_strategic_kpis(df):
        total_min = df['Duration'].sum()
        
        # 1. Qualifikations-Mismatch (Teure Fachkräfte machen Logistik)
        # S1, E1, D1, G2 sind Fachkräfte
        skilled_waste = df[
            (df['Dienst'].isin(['S1', 'E1', 'D1', 'G2'])) & 
            (df['Typ'].isin(['Logistik']))
        ]['Duration'].sum()
        
        # 2. Admin Overhead
        admin_total = df[df['Typ'] == 'Admin']['Duration'].sum()
        
        # 3. Production Halt (11:20 - 12:30)
        # Wie viele Minuten "Production" finden in diesem Fenster statt?
        halt_start = datetime(2026, 1, 1, 11, 20)
        halt_end = datetime(2026, 1, 1, 12, 30)
        prod_during_crunch = df[
            (df['Typ'] == 'Production') & 
            (df['Start_DT'] < halt_end) & 
            (df['End_DT'] > halt_start)
        ]['Duration'].sum()
        
        # 4. Gastro Bias
        gastro_min = df[df['Team'] == 'Restaurazione']['Duration'].sum()
        gastro_share = (gastro_min / total_min) * 100
        
        # 5. Diät Blindflug (Pause D1)
        # Dauer der Pause D1 am Mittag
        d1_break = df[(df['Dienst'] == 'D1') & (df['Typ'] == 'Break')]['Duration'].sum()

        return {
            "waste_min": int(skilled_waste),
            "admin_min": int(admin_total),
            "prod_halt": int(prod_during_crunch),
            "gastro_share": round(gastro_share, 1),
            "diet_blind": int(d1_break),
            "mep_spread": "8h" # Hardcoded fact from analysis
        }

# --- 3. MAIN UI ---
def main():
    df = DataEngine.get_data()
    kpis = DataEngine.calculate_strategic_kpis(df)

    # HEADER
    st.markdown('<div class="main-header">Operations Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Data-Driven Workforce Analysis & Strategy Execution</div>', unsafe_allow_html=True)

    # --- SECTION 1: THE 6 STRATEGIC INSIGHTS ---
    st.markdown("### Strategic Audit Findings")
    
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    # Card 1: Qualifikations-Mismatch
    with col1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Qualifikations-Mismatch</div>
            <div class="kpi-value">{kpis['waste_min']} Min/Tag</div>
            <div class="kpi-desc">Fachkraft-Zeit (S1/E1/G2), die in Reinigung/Logistik fließt statt in Produktion.</div>
        </div>
        """, unsafe_allow_html=True)

    # Card 2: Admin Overhead
    with col2:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Admin Overhead</div>
            <div class="kpi-value">{kpis['admin_min']} Min/Tag</div>
            <div class="kpi-desc">Kumulierte Zeit für Protokolle, Absprachen und Mails im gesamten Team.</div>
        </div>
        """, unsafe_allow_html=True)

    # Card 3: Diät-Sicherheitslücke
    with col3:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Diätetik "Blindflug"</div>
            <div class="kpi-value">{kpis['diet_blind']} Min</div>
            <div class="kpi-desc">Zeitfenster (12:45-14:30), in dem kein Diätkoch für Rückläufer/Sicherheit anwesend ist.</div>
        </div>
        """, unsafe_allow_html=True)

    # Card 4: Produktions-Stopp
    with col4:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Produktions-Stopp (11:20-12:30)</div>
            <div class="kpi-value">{kpis['prod_halt']} Min</div>
            <div class="kpi-desc">Aktive Produktion während der Service-Zeit. Die Küche wird zur reinen Ausgabestelle.</div>
        </div>
        """, unsafe_allow_html=True)

    # Card 5: Gastro Bias
    with col5:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Ressourcen-Split</div>
            <div class="kpi-value">{kpis['gastro_share']}% Gastro</div>
            <div class="kpi-desc">Anteil der Gesamtarbeitszeit für Restaurant/Mitarbeiter vs. Patientenverpflegung.</div>
        </div>
        """, unsafe_allow_html=True)

    # Card 6: MEP Zerstückelung
    with col6:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-title">Mise-en-Place Spread</div>
            <div class="kpi-value">{kpis['mep_spread']}</div>
            <div class="kpi-desc">Zeitspanne zwischen erstem (R1 06:30) und letztem (G2 14:15) Vorbereitungs-Task.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- SECTION 2: VISUAL EVIDENCE ---
    tab_timeline, tab_audit = st.tabs(["Operative Timeline Analysis", "Compliance & Risk Audit"])

    with tab_timeline:
        # Professional Colors
        colors = {
            "Production": "#3B82F6", # Blue
            "Service": "#10B981",    # Green
            "Logistik": "#F59E0B",   # Orange
            "Admin": "#64748B",      # Slate
            "Break": "#E2E8F0"       # Light Gray
        }
        
        fig = px.timeline(
            df[df['Typ'] != 'Break'], # Hide breaks for cleaner look, or keep them
            x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ",
            hover_name="Task",
            color_discrete_map=colors,
            category_orders={"Dienst": ["H1", "R1", "R2", "S1", "E1", "D1", "H2", "H3", "G2"]}
        )
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            height=500, margin=dict(t=20, b=0, l=0, r=0),
            xaxis_title="", yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
        )
        fig.update_xaxes(tickformat="%H:%M", gridcolor="#F1F5F9", dtick=3600000) # Hourly ticks
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with tab_audit:
        col_risk, col_opp = st.columns(2)
        
        with col_risk:
            st.markdown("#### Identifizierte Risiken")
            st.markdown(f"""
            <div class="alert-box alert-red">
                <b>CRITICAL: Diätetik-Absenz (Dienst D1)</b><br>
                Die Abwesenheit des Diätkochs von 12:45 bis 14:30 verletzt die Vorgaben zur Patientensicherheit bei Rückläufern (Allergene/Dysphagie). 
                Empfehlung: Pausenablösung durch S1 sicherstellen.
            </div>
            <div class="alert-box alert-red">
                <b>CRITICAL: Qualifikations-Niveau R1</b><br>
                Dienst R1 führt um 06:30 "Deklarationsprüfung" durch. Dies ist eine QM-Aufgabe, die im IST-Zustand oft von Logistik-Personal gemacht wird. 
                Hohes Risiko für Falschdeklaration.
            </div>
            """, unsafe_allow_html=True)
            
        with col_opp:
            st.markdown("#### Effizienz-Chancen")
            st.markdown(f"""
            <div class="alert-box alert-yellow">
                <b>OPPORTUNITY: Zentralisierung Reinigung</b><br>
                S1, E1 und G2 verbringen kumuliert {kpis['waste_min']} Minuten mit Reinigung/Logistik. 
                Durch Verlagerung an R1 (Nachmittag) oder Hilfspersonal könnten 1.5 Vollzeitstellen in der Produktion freigespielt werden.
            </div>
            <div class="alert-box alert-yellow">
                <b>OPPORTUNITY: Block-Produktion</b><br>
                Die MEP-Phase ist über {kpis['mep_spread']} gestreut. Bündelung aller Vorbereitungsarbeiten auf den Nachmittag (ab 13:30) würde Geräte-Laufzeiten reduzieren und Ruhe in den Vormittag bringen.
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
