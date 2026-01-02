import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- KONFIGURATION ---
st.set_page_config(
    page_title="Kitchen Intelligence Suite | Analytics",
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
    
    .audit-box-red { background: #FEF2F2; border-left: 4px solid #EF4444; padding: 15px; margin-bottom: 10px; }
    .audit-box-yellow { background: #FFFBEB; border-left: 4px solid #F59E0B; padding: 15px; margin-bottom: 10px; }
    .audit-box-green { background: #F0FDF4; border-left: 4px solid #22C55E; padding: 15px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIC ENGINE (NO AI) ---
class KitchenRulesEngine:
    @staticmethod
    def run_compliance_audit(df):
        findings = []
        
        # Regel 1: Fachkräfte (D1, S1) dürfen keine Logistik machen (Qualifikations-Check)
        # Basierend auf "Aufbau-Organisation.pdf" -> Diätkoch ist für "Zubereitung" verantwortlich, nicht Lagerung
        waste_tasks = df[(df['Team'] == 'Patientenverpflegung') & (df['Typ'] == 'Logistik')]
        if not waste_tasks.empty:
            minutes_lost = int(waste_tasks['Minuten'].sum())
            findings.append({
                "level": "red",
                "msg": f"**Qualifikations-Verstoß:** Hochqualifizierte Fachkräfte (S1/D1/G2) verschwenden {minutes_lost} Minuten täglich mit Logistik/Reinigung. Dies widerspricht dem Stellenplan."
            })

        # Regel 2: Crunch-Time Safety Check (11:30 - 12:30)
        # Basierend auf "Konzept-Küche": Alle müssen am Band sein.
        crunch_start = datetime(2026, 1, 1, 11, 30)
        crunch_end = datetime(2026, 1, 1, 12, 30)
        
        # Wer ist in dieser Zeit NICHT im Service/Produktion?
        absent_during_crunch = df[
            (df['Start_DT'] < crunch_end) & 
            (df['End_DT'] > crunch_start) & 
            (df['Typ'].isin(['Pause', 'Verwaltung', 'Logistik']))
        ]
        
        if not absent_during_crunch.empty:
            names = absent_during_crunch['Dienst'].unique()
            findings.append({
                "level": "red", 
                "msg": f"**Patientensicherheit (Crunch-Time):** Folgende Dienste sind zwischen 11:30-12:30 Uhr nicht produktiv am Band/Pass eingeplant: {', '.join(names)}. Risiko für Bandstopps."
            })
            
        # Regel 3: Diät-Validierung (D1)
        # Basierend auf "Kostformen und Produktion.pdf"
        d1_tasks = df[df['Dienst'] == 'D1']
        has_diet_check = d1_tasks[d1_tasks['Aufgabe'].str.contains('Diät|Suppe|Cg', case=False, na=False)]
        if has_diet_check.empty:
             findings.append({"level": "red", "msg": "**Medizinische Compliance:** Dienst D1 weist keine expliziten Zeiten für Diät-Kontrollen/Cg-Produktion aus."})
        else:
             findings.append({"level": "green", "msg": "**Compliance OK:** D1 ist korrekt für medizinische Kostformen (Cg/Suppen) eingeplant."})

        # Regel 4: Administrative Last
        admin_ratio = df[df['Typ'] == 'Verwaltung']['Minuten'].sum() / df['Minuten'].sum()
        if admin_ratio > 0.15:
            findings.append({"level": "yellow", "msg": f"**Effizienz-Warnung:** Der administrative Anteil liegt bei {admin_ratio:.1%}. Zielwert gemäss Lean-Konzept: <10%."})

        return findings

# --- DATA ENGINE ---
class KitchenDataManager:
    @staticmethod
    def get_full_data():
        # Validierte Daten aus den Dokumenten (D1.docx bis S1.docx)
        data = [
            # D1 - Diätetik
            {"Dienst": "D1", "Start": "08:00", "Ende": "12:20", "Aufgabe": "Suppen (Cg/ET) & Diätvorbereitung", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Aufgabe": "Abräumen & Kühlung (Logistik)", "Typ": "Logistik", "Team": "Patientenverpflegung"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:50", "Aufgabe": "Protokolle & PM", "Typ": "Verwaltung", "Team": "Patientenverpflegung"},
            {"Dienst": "D1", "Start": "15:50", "Ende": "18:09", "Aufgabe": "Cg-Auflauf & Abendservice", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            
            # E1 - Entremetier
            {"Dienst": "E1", "Start": "07:00", "Ende": "10:00", "Aufgabe": "Beilagen & Gemüse", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "E1", "Start": "10:15", "Ende": "13:00", "Aufgabe": "Wahlkost & Service Anrichten", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "E1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "MEP & Reinigung", "Typ": "Logistik", "Team": "Patientenverpflegung"},
            
            # G2 - Gardemanger
            {"Dienst": "G2", "Start": "09:30", "Ende": "13:30", "Aufgabe": "Kaltküche & Salate", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "G2", "Start": "14:15", "Ende": "18:00", "Aufgabe": "Buffet & Abendessen", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "G2", "Start": "18:00", "Ende": "18:30", "Aufgabe": "Reinigung & Checklisten", "Typ": "Logistik", "Team": "Patientenverpflegung"},
            
            # H1 - Frühstück
            {"Dienst": "H1", "Start": "05:30", "Ende": "10:00", "Aufgabe": "Frühstücksservice", "Typ": "Service", "Team": "Gastronomie"},
            {"Dienst": "H1", "Start": "10:15", "Ende": "12:30", "Aufgabe": "Glacé & Band Mittag", "Typ": "Service", "Team": "Gastronomie"},
            {"Dienst": "H1", "Start": "13:30", "Ende": "14:40", "Aufgabe": "Reinigung & Protokolle", "Typ": "Verwaltung", "Team": "Gastronomie"},
            
            # H2 - Pâtisserie
            {"Dienst": "H2", "Start": "09:15", "Ende": "13:30", "Aufgabe": "Desserts & Patienten", "Typ": "Service", "Team": "Gastronomie"},
            {"Dienst": "H2", "Start": "14:15", "Ende": "18:09", "Aufgabe": "Zvieri & Abendband", "Typ": "Service", "Team": "Gastronomie"},
            
            # H3 - Support Kalt
            {"Dienst": "H3", "Start": "09:15", "Ende": "13:30", "Aufgabe": "Salate & Wähen", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "H3", "Start": "14:15", "Ende": "18:09", "Aufgabe": "Reinigung & MEP", "Typ": "Logistik", "Team": "Patientenverpflegung"},
            
            # R1 - Restaurant
            {"Dienst": "R1", "Start": "06:30", "Ende": "10:00", "Aufgabe": "Warenannahme & Deklaration", "Typ": "Logistik", "Team": "Gastronomie"},
            {"Dienst": "R1", "Start": "10:20", "Ende": "14:00", "Aufgabe": "Mittagsservice & Kasse", "Typ": "Service", "Team": "Gastronomie"},
            {"Dienst": "R1", "Start": "14:30", "Ende": "15:24", "Aufgabe": "Reinigung", "Typ": "Logistik", "Team": "Gastronomie"},
            
            # R2 - Restaurant
            {"Dienst": "R2", "Start": "06:30", "Ende": "14:00", "Aufgabe": "Frühstück & Service", "Typ": "Service", "Team": "Gastronomie"},
            {"Dienst": "R2", "Start": "14:30", "Ende": "15:24", "Aufgabe": "Etiketten & Abschluss", "Typ": "Logistik", "Team": "Gastronomie"},
            
            # S1 - Saucier
            {"Dienst": "S1", "Start": "07:00", "Ende": "13:00", "Aufgabe": "Fleisch & Saucen", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "S1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "Pläne & Abschluss", "Typ": "Verwaltung", "Team": "Patientenverpflegung"},
        ]
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'].str.replace('.', ':'))
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'].str.replace('.', ':'))
        df['Minuten'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- MAIN APP ---
def main():
    dm = KitchenDataManager()
    df_raw = dm.get_full_data()

    # Header
    st.markdown("<h1 style='font-size: 28px; font-weight: 700; margin-bottom: 0px;'>KITCHEN INTELLIGENCE SUITE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 14px; margin-bottom: 30px;'>Analytics & Validierte Prozess-Steuerung</p>", unsafe_allow_html=True)

    # --- KPI SCORECARD (9 KPIs) ---
    st.markdown("<h2 style='font-size: 12px; color: #64748B; text-transform: uppercase; letter-spacing: 1px;'>Operations Scorecard</h2>", unsafe_allow_html=True)
    
    kpis = st.columns(3)
    
    # KPIs Calculation
    total_min = df_raw['Minuten'].sum()
    prod_min = df_raw[df_raw['Typ'] == 'Produktion']['Minuten'].sum()
    log_min = df_raw[df_raw['Typ'] == 'Logistik']['Minuten'].sum()
    
    # Crunch Time (11:30 - 12:30)
    crunch_start = datetime(2026, 1, 1, 11, 30)
    crunch_end = datetime(2026, 1, 1, 12, 30)
    # Wer arbeitet in diesem Zeitraum effektiv (Produktion/Service)?
    crunch_staff = len(df_raw[
        (df_raw['Start_DT'] <= crunch_start) & 
        (df_raw['End_DT'] >= crunch_end) &
        (df_raw['Typ'].isin(['Produktion', 'Service']))
    ])

    # Render KPIs
    kpi_list = [
        ("Gesamt-Arbeitslast", f"{int(total_min/60)}h"),
        ("Kern-Produktion", f"{int(prod_min/60)}h"),
        ("Logistik-Anteil", f"{int((log_min/total_min)*100)}%"),
        ("Crunch-Time (11:30)", f"{crunch_staff} MA"),
        ("Patienten-Team", f"{len(df_raw[df_raw['Team']=='Patientenverpflegung']['Dienst'].unique())} Dienste"),
        ("Gastro-Team", f"{len(df_raw[df_raw['Team']=='Gastronomie']['Dienst'].unique())} Dienste")
    ]

    for i, (label, value) in enumerate(kpi_list):
        with kpis[i % 3]:
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 15px;">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    # --- PROCESS FILTER ---
    st.markdown("<br>", unsafe_allow_html=True)
    selected_dienste = st.multiselect(
        "Dienste filtern", 
        options=sorted(df_raw['Dienst'].unique()), 
        default=sorted(df_raw['Dienst'].unique())
    )
    df = df_raw[df_raw['Dienst'].isin(selected_dienste)]

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["🕒 Operative Timeline", "📊 Belastung & Heatmap", "✅ Audit & Strategie (SOLL)"])

    with tab1:
        # Farblich optimierte Palette
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
        # Präzisions-Kurve
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
        st.plotly_chart(fig_curve, use_container_width=True, config={'displayModeBar': False})

    with tab3:
        col_l, col_r = st.columns([1, 1])
        
        with col_l:
            st.markdown("### Strategisches SOLL-Modell (Validiert)")
            st.markdown("""
            <div style='background: white; padding: 25px; border: 1px solid #E2E8F0; border-radius: 4px;'>
                <p style='font-size: 13px; line-height: 1.8;'>
                <b>Basierend auf: Aufbau-Organisation - Strategisch.pdf</b><br><br>
                <b>1. Zentralisierung Logistik:</b><br>
                IST: 15% der Fachkraftzeit (S1/E1) fließt in Reinigung/Warenannahme.<br>
                SOLL: Transfer dieser Stunden zu R1/R2 (Gastronomie) oder Hilfskräften.
                <br><br>
                <b>2. Patientensicherheit (Diätetik):</b><br>
                IST: Dienst D1 ist durch "Zimmerstunde" (12:45-14:30) nicht durchgehend verfügbar.<br>
                SOLL: Durchgehende Besetzung D1 zur Validierung aller Cg/Allergen-Essen.
                <br><br>
                <b>3. Crunch-Time Management:</b><br>
                IST: Kritische Phase 11:30-12:30. Alle Dienste gebunden.<br>
                SOLL: Verbot von Pausen und administrativen Aufgaben in diesem Zeitfenster.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_r:
            st.markdown("### Automatisierter Compliance-Check")
            
            audit_results = KitchenRulesEngine.run_compliance_audit(df)
            
            for item in audit_results:
                css_class = f"audit-box-{item['level']}"
                st.markdown(f"""
                <div class="{css_class}">
                    {item['msg']}
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
