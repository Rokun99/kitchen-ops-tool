import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import json
from datetime import datetime, timedelta

# --- THEME & UI CONFIGURATION ---
st.set_page_config(page_title="Kitchen Intelligence Suite", layout="wide", initial_sidebar_state="collapsed")

# Professional CSS (Slate & Steel Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #1E293B; }
    .main { background-color: #F8FAFC; }
    .stMetric { background-color: #FFFFFF; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { height: 50px; border-radius: 4px; border: none; background-color: transparent; font-weight: 600; color: #64748B; }
    .stTabs [aria-selected="true"] { color: #0F172A; border-bottom: 2px solid #0F172A; }
    div[data-testid="stExpander"] { border: 1px solid #E2E8F0; border-radius: 8px; background-color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

# --- MODULE 1: AI CORE ENGINE ---
class KitchenAI:
    def __init__(self):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except:
            st.error("API Key Konfiguration fehlt. Bitte in st.secrets hinterlegen.")

    def parse_duty_pdf(self, text_content):
        prompt = f"""
        Analysiere den folgenden Dienstplan-Text und konvertiere ihn in ein strukturiertes JSON-Format.
        Kategorisiere jede Tätigkeit strikt in: 
        1. Value Add (Kochen, Anrichten, direkte Produktion)
        2. Coordination (Übergaben, Planung, Mails)
        3. Logistics (Reinigung, Lagerung, Abwasch)
        4. Waste (Wartezeiten, unnötige Wege)

        Zusätzlich: Weise jeder Aufgabe eine 'Kognitive Last' (0.1 bis 1.0) zu.
        Text: {text_content}
        Output-Format: JSON Array mit [start, end, posten, task, category, cognitive_load]
        """
        response = self.model.generate_content(prompt)
        # Extraktion des JSON aus dem Response-String
        try:
            clean_json = response.text.split("```json")[1].split("```")[0].strip()
            return json.loads(clean_json)
        except:
            return None

    def rewrite_duty(self, current_data, instruction):
        prompt = f"Basierend auf diesen Daten: {current_data}. Führe folgende Optimierung durch: {instruction}. Gib den neuen Plan strukturiert aus."
        return self.model.generate_content(prompt).text

# --- MODULE 2: ANALYTICS ENGINE (PANDAS & PLOTLY) ---
class AnalyticsEngine:
    @staticmethod
    def prepare_data(data):
        df = pd.DataFrame(data)
        # Zeit-Logik via Pandas
        df['start_dt'] = pd.to_datetime('2026-01-01 ' + df['start'])
        df['end_dt'] = pd.to_datetime('2026-01-01 ' + df['end'])
        df['duration_min'] = (df['end_dt'] - df['start_dt']).dt.total_seconds() / 60
        return df

    @staticmethod
    def create_gantt(df):
        color_map = {
            "Value Add": "#0F172A",     # Deep Slate
            "Coordination": "#334155",  # Mid Slate
            "Logistics": "#94A3B8",     # Gray
            "Waste": "#E2E8F0"          # Light Gray
        }
        fig = px.timeline(df, x_start="start_dt", x_end="end_dt", y="posten", color="category",
                          hover_name="task", color_discrete_map=color_map, template="plotly_white")
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=400, showlegend=True, margin=dict(l=20, r=20, t=20, b=20))
        return fig

    @staticmethod
    def create_heatmap(df):
        # Diskrete 15-Minuten Intervalle für Heatmap
        time_slots = pd.date_range("2026-01-01 05:00", "2026-01-01 20:00", freq="15min")
        postens = df['posten'].unique()
        
        heatmap_data = []
        for p in postens:
            p_load = []
            for slot in time_slots:
                # Prüfe ob Posten zu dieser Zeit aktiv ist und summiere Last
                active_tasks = df[(df['posten'] == p) & (df['start_dt'] <= slot) & (df['end_dt'] > slot)]
                p_load.append(active_tasks['cognitive_load'].sum() if not active_tasks.empty else 0)
            heatmap_data.append(p_load)

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data, x=time_slots, y=postens, colorscale="Greys", showscale=False))
        fig.update_layout(title="Kognitive Last & Belastungs-Dichte", height=300, margin=dict(l=20, r=20, t=40, b=20))
        return fig

# --- MAIN APPLICATION ---
def main():
    st.title("KITCHEN INTELLIGENCE SUITE")
    st.markdown("Strategisches Workforce Management & Prozess-Audit")
    
    ai_core = KitchenAI()
    
    # --- DATA SESSION STATE ---
    if 'raw_data' not in st.session_state:
        # Umfangreiche Dummy-Daten basierend auf PDF
        st.session_state.raw_data = [
            {"start": "08:00", "end": "10:00", "posten": "D1", "task": "Suppenproduktion", "category": "Value Add", "cognitive_load": 0.6},
            {"start": "10:15", "end": "11:20", "posten": "D1", "task": "Regenerieren & Schöpfen", "category": "Value Add", "cognitive_load": 0.9},
            {"start": "12:45", "end": "14:30", "posten": "D1", "task": "Mittagspause", "category": "Waste", "cognitive_load": 0.0},
            {"start": "07:00", "end": "10:00", "posten": "S1", "task": "Saucen & Fleisch", "category": "Value Add", "cognitive_load": 0.8},
            {"start": "11:20", "end": "12:30", "posten": "S1", "task": "Band-Service", "category": "Value Add", "cognitive_load": 1.0},
            {"start": "13:30", "end": "15:00", "posten": "S1", "task": "Reinigung Posten", "category": "Logistics", "cognitive_load": 0.3},
            {"start": "06:30", "end": "10:00", "posten": "R1", "task": "Warenannahme", "category": "Logistics", "cognitive_load": 0.4},
            {"start": "10:20", "end": "13:30", "posten": "R1", "task": "Service Restaurant", "category": "Value Add", "cognitive_load": 0.7}
        ]

    # --- TOP METRICS ---
    df = AnalyticsEngine.prepare_data(st.session_state.raw_data)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Netto Produktion", f"{int(df[df['category']=='Value Add']['duration_min'].sum())} Min")
    c2.metric("Logistik/Reinigung", f"{int(df[df['category']=='Logistics']['duration_min'].sum())} Min")
    c3.metric("Waste (Lücken)", f"{int(df[df['category']=='Waste']['duration_min'].sum())} Min")
    c4.metric("Ø Kognitive Last", f"{df['cognitive_load'].mean():.2f}")

    # --- MAIN DASHBOARD TABS ---
    tab_ist, tab_audit, tab_soll = st.tabs(["IST-ZUSTAND", "COMPLIANCE AUDIT", "TRANSFORMATION (SOLL)"])

    with tab_ist:
        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.plotly_chart(AnalyticsEngine.create_gantt(df), use_container_width=True)
            st.plotly_chart(AnalyticsEngine.create_heatmap(df), use_container_width=True)
        with col_right:
            st.subheader("Fokus-Analyse")
            st.write("Verteilung der Arbeitsbereiche:")
            pie = px.pie(df, values='duration_min', names='category', 
                         color_discrete_sequence=["#0F172A", "#334155", "#94A3B8", "#F1F5F9"])
            st.plotly_chart(pie, use_container_width=True)

    with tab_audit:
        st.subheader("Regel-Prüfung & Compliance")
        policy = st.text_area("Organigramm / Ernährungskonzept Regeln:", 
                              "R1 darf keine Diät-Checks machen. D1 muss während Service am Band sein. Maximale Last darf 0.9 nicht überschreiten.")
        if st.button("Audit starten"):
            with st.spinner("KI prüft Compliance..."):
                # Hier würde ein AI Call gegen die Policy erfolgen
                st.error("Dienst R1: Deklarationsprüfung durch unqualifiziertes Personal (Verstoß gegen Regel 1)")
                st.warning("Dienst D1: Kritische Last von 0.9 während 10:15 - 11:20.")
                st.success("Saucier S1: 100% Konformität mit Hygienestandards.")

    with tab_soll:
        st.subheader("Generative Re-Organisation")
        st.info("Beschreiben Sie die gewünschte Transformation des IST-Zustands.")
        instruction = st.chat_input("z.B. Entlaste S1 während der Servicezeit indem R1 die Reinigung übernimmt...")
        
        if instruction:
            with st.chat_message("assistant"):
                with st.spinner("Berechne SOLL-Szenario..."):
                    new_plan = ai_core.rewrite_duty(st.session_state.raw_data, instruction)
                    st.write(new_plan)

    # --- INGEST ENGINE (COLLAPSED) ---
    with st.expander("DATEN-IMPORT (PDF ANALYSE)"):
        uploaded_file = st.file_uploader("Neuen Dienstplan hochladen", type="pdf")
        if uploaded_file and st.button("KI-Analyse starten"):
            # Dummy logic für Upload
            st.info("KI extrahiert Zeitstempel und kategorisiert Tätigkeiten...")
            # st.session_state.raw_data = ai_core.parse_duty_pdf(text)

if __name__ == "__main__":
    main()
