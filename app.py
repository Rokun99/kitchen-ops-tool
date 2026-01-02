import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Kitchen Intelligence | Executive View",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CORPORATE STYLING (CLEAN & SEXY) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #0F172A; background-color: #F8FAFC; }
    
    /* Hide Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* KPI CARD DESIGN */
    div.css-1r6slb0 {gap: 1rem;} 
    
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 24px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease-in-out;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .kpi-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .kpi-title {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 4px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.025em;
    }

    .kpi-sub {
        font-size: 12px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .trend-up { color: #10B981; }   /* Green */
    .trend-down { color: #EF4444; } /* Red */
    .trend-neutral { color: #64748B; } /* Grey */

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 32px; 
        background-color: transparent; 
        padding-bottom: 0px;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        font-size: 14px;
        font-weight: 500;
        color: #64748B;
        border: none;
        background-color: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #0F172A !important;
        border-bottom: 2px solid #0F172A !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA ENGINE ---
class KitchenDataManager:
    @staticmethod
    def get_full_data():
        # Validierte Daten aus den Prozessbeschrieben
        data = [
            # D1 - Diätetik (Spezialfall)
            {"Dienst": "D1", "Start": "08:00", "Ende": "12:20", "Aufgabe": "Suppen (Cg/ET) & Diätvorbereitung", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Aufgabe": "Logistik & Kühlung", "Typ": "Logistik", "Team": "Patientenverpflegung"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:50", "Aufgabe": "Protokolle & PM", "Typ": "Verwaltung", "Team": "Patientenverpflegung"},
            {"Dienst": "D1", "Start": "15:50", "Ende": "18:09", "Aufgabe": "Cg-Auflauf & Abendservice", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            
            # E1 & S1 (Warme Küche)
            {"Dienst": "E1", "Start": "07:00", "Ende": "13:00", "Aufgabe": "Beilagen & Service", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "E1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "MEP & Reinigung", "Typ": "Logistik", "Team": "Patientenverpflegung"},
            {"Dienst": "S1", "Start": "07:00", "Ende": "13:00", "Aufgabe": "Fleisch & Saucen", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "S1", "Start": "13:30", "Ende": "15:54", "Aufgabe": "Pläne & Abschluss", "Typ": "Verwaltung", "Team": "Patientenverpflegung"},
            
            # G2 & H3 (Kalte Küche)
            {"Dienst": "G2", "Start": "09:30", "Ende": "13:30", "Aufgabe": "Kaltküche & Salate", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "G2", "Start": "14:15", "Ende": "18:30", "Aufgabe": "Logistik & Reinigung", "Typ": "Logistik", "Team": "Patientenverpflegung"},
            {"Dienst": "H3", "Start": "09:15", "Ende": "13:30", "Aufgabe": "Salate & Wähen", "Typ": "Produktion", "Team": "Patientenverpflegung"},
            {"Dienst": "H3", "Start": "14:15", "Ende": "18:09", "Aufgabe": "Reinigung & MEP", "Typ": "Logistik", "Team": "Patientenverpflegung"},
            
            # Gastro Team
            {"Dienst": "H1", "Start": "05:30", "Ende": "12:30", "Aufgabe": "Frühstück & Band", "Typ": "Service", "Team": "Gastronomie"},
            {"Dienst": "H1", "Start": "13:30", "Ende": "14:40", "Aufgabe": "Protokolle", "Typ": "Verwaltung", "Team": "Gastronomie"},
            {"Dienst": "H2", "Start": "09:15", "Ende": "13:30", "Aufgabe": "Desserts & Patienten", "Typ": "Service", "Team": "Gastronomie"},
            {"Dienst": "R1", "Start": "06:30", "Ende": "14:00", "Aufgabe": "Warenannahme & Service", "Typ": "Service", "Team": "Gastronomie"},
            {"Dienst": "R1", "Start": "14:30", "Ende": "15:24", "Aufgabe": "Reinigung", "Typ": "Logistik", "Team": "Gastronomie"},
            {"Dienst": "R2", "Start": "06:30", "Ende": "14:00", "Aufgabe": "Frühstück & Service", "Typ": "Service", "Team": "Gastronomie"},
        ]
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'].str.replace('.', ':'))
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'].str.replace('.', ':'))
        df['Minuten'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- METRIC CALCULATION ENGINE ---
def calculate_metrics(df):
    total_min = df['Minuten'].sum()
    
    # 1. FTE Bedarf (Basis 8.2h = 492min pro Tag produktiv)
    fte_count = total_min / 492
    
    # 2. Skill Leakage (Fachkräfte machen Logistik/Verwaltung)
    # Nur Teams S1, E1, D1, G2 (Fachkräfte)
    specialists = ['S1', 'E1', 'D1', 'G2']
    spec_waste_min = df[
        (df['Dienst'].isin(specialists)) & 
        (df['Typ'].isin(['Logistik', 'Verwaltung']))
    ]['Minuten'].sum()
    spec_total_min = df[df['Dienst'].isin(specialists)]['Minuten'].sum()
    skill_leakage_pct = (spec_waste_min / spec_total_min) * 100
    
    # 3. Crunch Time Density (12:00 Uhr)
    crunch_time = datetime(2026, 1, 1, 12, 00)
    active_staff = len(df[(df['Start_DT'] <= crunch_time) & (df['End_DT'] > crunch_time)])
    total_staff = len(df['Dienst'].unique())
    density_pct = (active_staff / total_staff) * 100
    
    # 4. Diät Safety (Ist D1 zwischen 11:30 und 12:15 da?)
    d1_service = df[
        (df['Dienst'] == 'D1') & 
        (df['Start_DT'] <= datetime(2026, 1, 1, 11, 30)) & 
        (df['End_DT'] >= datetime(2026, 1, 1, 12, 15))
    ]
    diet_safe = not d1_service.empty
    
    # 5. Lean Index (Produktion+Service vs Rest)
    value_add = df[df['Typ'].isin(['Produktion', 'Service'])]['Minuten'].sum()
    lean_index = (value_add / total_min) * 100
    
    # 6. Strategic Split
    cucina_min = df[df['Team'] == 'Patientenverpflegung']['Minuten'].sum()
    split_pct = (cucina_min / total_min) * 100

    return {
        "fte": f"{fte_count:.1f} FTE",
        "leakage": f"{skill_leakage_pct:.0f}%",
        "density": f"{density_pct:.0f}%",
        "diet_safe": "Gewährleistet" if diet_safe else "Kritisch",
        "lean": f"{lean_index:.0f}%",
        "split": f"{split_pct:.0f}% / {100-split_pct:.0f}%"
    }

# --- MAIN UI ---
def main():
    dm = KitchenDataManager()
    df = dm.get_full_data()
    m = calculate_metrics(df)

    st.markdown("## KITCHEN INTELLIGENCE SUITE")
    st.markdown("<div style='margin-bottom: 30px; color: #64748B;'>Operations Analytics & Strategic Planning</div>", unsafe_allow_html=True)

    # --- THE 6 STRATEGIC KPI CARDS ---
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    cards = [
        (c1, "FTE Bedarf (Ist)", m['fte'], "Vollzeitstellen heute", "trend-neutral"),
        (c2, "Skill Leakage", m['leakage'], "Fachkraft-Verschwendung", "trend-down"),
        (c3, "Crunch Density", m['density'], "Auslastung 12:00 Uhr", "trend-down"),
        (c4, "Diät Safety", m['diet_safe'], "Präsenz D1 Service", "trend-up" if m['diet_safe']=="Gewährleistet" else "trend-down"),
        (c5, "Lean Index", m['lean'], "Wertschöpfungs-Anteil", "trend-up"),
        (c6, "Strat. Split", m['split'], "Patient vs. Gast", "trend-neutral")
    ]

    for col, title, val, sub, trend in cards:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div>
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-value">{val}</div>
                </div>
                <div class="kpi-sub {trend}">
                    {sub}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["Operative Timeline", "Strategische Heatmap", "Prozessdaten"])

    with tab1:
        # Hier verstecken wir den Filter elegant im Expander, falls man ihn doch braucht
        with st.expander("Ansicht filtern", expanded=False):
            sel = st.multiselect("Dienste anzeigen", sorted(df['Dienst'].unique()), default=sorted(df['Dienst'].unique()))
            df_filtered = df[df['Dienst'].isin(sel)]
        
        # Timeline
        color_map = {"Produktion": "#1E293B", "Service": "#10B981", "Logistik": "#F59E0B", "Verwaltung": "#94A3B8"}
        
        fig = px.timeline(
            df_filtered, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ",
            hover_name="Aufgabe", color_discrete_map=color_map,
            category_orders={"Dienst": ["H1", "R1", "R2", "S1", "E1", "D1", "H2", "H3", "G2"]}
        )
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white", height=450, margin=dict(t=20, b=0, l=0, r=0),
            xaxis_title="", yaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title="")
        )
        fig.update_xaxes(tickformat="%H:%M", gridcolor="#F1F5F9")
        fig.update_yaxes(gridcolor="#F1F5F9")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with tab2:
        # Heatmap (Stress Intensity)
        st.markdown("##### Kognitive Last über den Tag (Heatmap)")
        
        # Data prep for heatmap
        heatmap_data = []
        time_slots = []
        for h in range(6, 19):
            for m in [0, 30]:
                time_slots.append(f"{h:02d}:{m:02d}")
        
        postens = sorted(df['Dienst'].unique())
        
        z_values = []
        for p in postens:
            row = []
            p_df = df[df['Dienst'] == p]
            for slot in time_slots:
                h, m = map(int, slot.split(':'))
                t = datetime(2026, 1, 1, h, m)
                # Check if active
                is_active = not p_df[(p_df['Start_DT'] <= t) & (p_df['End_DT'] > t)].empty
                # Value logic: Service/Crunch = 1.0, Produktion = 0.6, Logistik = 0.3, Inactive = 0
                val = 0
                if is_active:
                    task = p_df[(p_df['Start_DT'] <= t) & (p_df['End_DT'] > t)].iloc[0]
                    if task['Typ'] == 'Service': val = 1.0
                    elif task['Typ'] == 'Produktion': val = 0.6
                    elif task['Typ'] == 'Logistik': val = 0.3
                    elif task['Typ'] == 'Verwaltung': val = 0.2
                row.append(val)
            z_values.append(row)

        fig_heat = go.Figure(data=go.Heatmap(
            z=z_values, x=time_slots, y=postens,
            colorscale=[[0, 'white'], [0.3, '#F59E0B'], [0.6, '#6366F1'], [1.0, '#EF4444']],
            showscale=False
        ))
        fig_heat.update_layout(height=400, margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
        
        c1, c2, c3 = st.columns(3)
        c1.caption("🟦 Produktion (Normal)")
        c2.caption("🟧 Logistik (Niedrige Last)")
        c3.caption("🟥 Service/Crunch (Hohe Last)")

    with tab3:
        st.dataframe(df_filtered[['Dienst', 'Start', 'Ende', 'Aufgabe', 'Typ', 'Team']], use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
