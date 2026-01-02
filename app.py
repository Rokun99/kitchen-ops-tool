import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import google.generativeai as genai
from datetime import datetime, timedelta

# --- CONFIGURATION & AI SETUP ---
st.set_page_config(page_title="Kitchen Palantir | Workforce Analytics", layout="wide", page_icon="🎯")

class GeminiHandler:
    def __init__(self):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            st.error(f"AI Initialization Error: {e}")

    def parse_schedule(self, text_content):
        prompt = f"""
        Analyze the following kitchen duty schedule text. 
        Extract every task into a structured JSON array of objects.
        
        Fields per object:
        - start_time (HH:mm)
        - end_time (HH:mm)
        - posten (e.g., R1, S1, D1)
        - task_description (text)
        - strategic_category: Assign one based on context:
            * 'Value Add' (Direct cooking, plating, service)
            * 'Coordination' (Handovers, meetings, briefings)
            * 'Logistics' (Cleaning, stocking, transport)
            * 'Waste' (Waiting, double-work, unnecessary travel)
        - cognitive_load: (0.1 to 1.0) based on stress level.
        - handover_to: (Posten name) if the task involves preparing work for another posten.

        Schedule Text:
        {text_content}
        
        Return ONLY valid JSON.
        """
        response = self.model.generate_content(prompt)
        try:
            # Cleaning potential markdown code blocks
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except:
            return None

    def check_compliance(self, schedule_data, policy_text):
        prompt = f"""
        Act as a Kitchen Compliance Officer. Compare the schedule data against the Nutrition/Org Policy.
        
        Schedule Data: {json.dumps(schedule_data)}
        Policy: {policy_text}
        
        Identify:
        1. Critical violations (Red)
        2. Efficiency warnings (Yellow)
        3. Compliance successes (Green)
        
        Return as a bulleted list with Color prefixes (RED:, YELLOW:, GREEN:).
        """
        return self.model.generate_content(prompt).text

    def get_chat_response(self, history, query, current_data):
        context = f"Current Schedule Data: {json.dumps(current_data)}"
        full_query = f"{context}\n\nUser Request: {query}\n\nInstruction: Rewrite or explain the schedule based on this request."
        chat = self.model.start_chat(history=history)
        return chat.send_message(full_query).text

# --- DATA & VISUALIZATION ENGINE ---
class Visualizer:
    @staticmethod
    def plot_sankey(df):
        # Filter rows that have handovers
        handover_df = df[df['handover_to'].notna() & (df['handover_to'] != "")]
        if handover_df.empty:
            return None
        
        all_nodes = list(set(df['posten'].tolist() + handover_df['handover_to'].tolist()))
        node_map = {name: i for i, name in enumerate(all_nodes)}
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=all_nodes, color="royalblue"),
            link=dict(
                source=[node_map[src] for src in handover_df['posten']],
                target=[node_map[tgt] for tgt in handover_df['handover_to']],
                value=[1] * len(handover_df),
                label=handover_df['task_description']
            )
        )])
        fig.update_layout(title_text="Handover Flow (Staffelstab-Effekt)", font_size=10, template="plotly_dark")
        return fig

    @staticmethod
    def plot_cognitive_heatmap(df):
        # Create a time grid
        hours = [f"{h:02d}:00" for h in range(5, 23)]
        postens = df['posten'].unique()
        
        z_data = []
        for p in postens:
            row = []
            p_df = df[df['posten'] == p]
            for h in range(5, 23):
                # Simple overlap check
                load = p_df[p_df['start_time'].str.startswith(f"{h:02d}")]['cognitive_load'].max()
                row.append(load if not pd.isna(load) else 0)
            z_data.append(row)
            
        fig = px.imshow(z_data, x=hours, y=postens, color_continuous_scale='Reds', aspect="auto",
                        labels=dict(x="Uhrzeit", y="Posten", color="Kognitive Last"))
        fig.update_layout(title="Stress-Heatmap (Red Zones)", template="plotly_dark")
        return fig

    @staticmethod
    def plot_sunburst(df):
        fig = px.sunburst(df, path=['posten', 'strategic_category', 'task_description'], 
                          values='cognitive_load', color='strategic_category',
                          color_discrete_map={'Value Add':'#00CC96', 'Coordination':'#636EFA', 'Logistics':'#AB63FA', 'Waste':'#EF553B'})
        fig.update_layout(title="Hierarchische Aufgaben-Verteilung", template="plotly_dark")
        return fig

# --- STREAMLIT UI ---
def main():
    ai = GeminiHandler()
    vis = Visualizer()
    
    # Initialize State
    if 'schedule_data' not in st.session_state:
        st.session_state.schedule_data = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # --- SIDEBAR & INGEST ---
    with st.sidebar:
        st.header("1. The AI Ingest Engine")
        uploaded_file = st.file_uploader("Dienstplan Upload (Text/PDF)", type=["txt", "pdf"])
        
        if st.button("🚀 Analyze & Structure") or not st.session_state.schedule_data:
            if uploaded_file:
                # In a real app, use PyPDF2 here
                text = uploaded_file.read().decode("utf-8")
                with st.spinner("AI is parsing context..."):
                    st.session_state.schedule_data = ai.parse_schedule(text)
            else:
                # DEMO MODE DUMMY DATA
                st.session_state.schedule_data = [
                    {"start_time": "07:00", "end_time": "10:00", "posten": "S1", "task_description": "Saucen Produktion", "strategic_category": "Value Add", "cognitive_load": 0.6, "handover_to": "G2"},
                    {"start_time": "09:00", "end_time": "11:00", "posten": "G2", "task_description": "Salat MEP", "strategic_category": "Value Add", "cognitive_load": 0.4, "handover_to": ""},
                    {"start_time": "11:30", "end_time": "13:30", "posten": "S1", "task_description": "Mittagsservice", "strategic_category": "Value Add", "cognitive_load": 1.0, "handover_to": ""},
                    {"start_time": "06:30", "end_time": "09:00", "posten": "R1", "task_description": "Warenannahme", "strategic_category": "Logistics", "cognitive_load": 0.3, "handover_to": "S1"},
                    {"start_time": "14:00", "end_time": "15:00", "posten": "D1", "task_description": "Protokolle schreiben", "strategic_category": "Coordination", "cognitive_load": 0.5, "handover_to": ""}
                ]
                st.success("Demo Mode Active: Dummy Data Loaded")

    # --- MAIN DASHBOARD ---
    st.title("🎯 Kitchen Ops Intelligence Suite")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics 2.0", "🚦 Compliance", "💬 Generative Re-Org", "📋 Raw Data"])

    if st.session_state.schedule_data:
        df = pd.DataFrame(st.session_state.schedule_data)

        with tab1:
            st.subheader("High-End Workforce Analytics")
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(vis.plot_cognitive_heatmap(df), use_container_width=True)
            with c2:
                st.plotly_chart(vis.plot_sunburst(df), use_container_width=True)
            
            sankey = vis.plot_sankey(df)
            if sankey:
                st.plotly_chart(sankey, use_container_width=True)

        with tab2:
            st.subheader("The Constraint Solver")
            policy = st.text_area("Ernährungskonzept / Organigramm Regeln eingeben:", 
                                  "R1 darf nur Logistik machen. S1 ist für alle Saucen verantwortlich. D1 muss alle Diät-Checks machen.")
            if st.button("Check Compliance"):
                with st.spinner("AI auditing schedule..."):
                    report = ai.check_compliance(st.session_state.schedule_data, policy)
                    for line in report.split("\n"):
                        if "RED:" in line: st.error(line)
                        elif "YELLOW:" in line: st.warning(line)
                        elif "GREEN:" in line: st.success(line)

        with tab3:
            st.subheader("Generative Re-Org Bot")
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if prompt := st.chat_input("z.B.: Schreibe R1 um, sodass er Logistik abgibt..."):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    response = ai.get_chat_response([], prompt, st.session_state.schedule_data)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

        with tab4:
            st.dataframe(df, use_container_width=True)

    else:
        st.warning("Bitte laden Sie Daten hoch oder nutzen Sie den Demo-Modus.")

if __name__ == "__main__":
    main()
