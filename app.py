import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import google.generativeai as genai
from datetime import datetime, timedelta

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Workforce Analytics Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Injection
st.markdown("""
<style>
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }

    /* Header Styling */
    h1, h2, h3 {
        font-weight: 600;
        color: #0f172a;
        letter-spacing: -0.025em;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }

    /* Button Styling - Minimalist */
    .stButton > button {
        background-color: #0f172a;
        color: white;
        border: 1px solid #0f172a;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #1e293b;
        border-color: #1e293b;
    }
    .stButton > button:active {
        background-color: #334155;
    }

    /* Input Fields */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        color: #1e293b;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: #64748b;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #0f172a;
        border-bottom: 2px solid #0f172a;
    }
    
    /* Remove default Streamlit decorations */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- AI LOGIC CLASS ---
class GeminiHandler:
    def __init__(self):
        try:
            # Check for API key in secrets
            if "GEMINI_API_KEY" in st.secrets:
                 genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                 self.model = genai.GenerativeModel('gemini-1.5-pro')
            else:
                 # Silent fail for UI cleanliness, handled in main logic
                 self.model = None
        except Exception:
            self.model = None

    def parse_schedule(self, text_content):
        if not self.model: return []
        
        prompt = f"""
        Analyze the submitted schedule text. 
        Extract tasks into a valid JSON array.
        
        Schema per object:
        - start_time (HH:mm)
        - end_time (HH:mm)
        - posten (string identifier)
        - task_description (string)
        - strategic_category: Choose one: 'Value Creation', 'Coordination', 'Logistics', 'Inefficiency'
        - cognitive_load: (0.1 to 1.0) float
        - handover_to: (string) Target posten identifier or empty string.

        Input Text:
        {text_content}
        
        Output only raw JSON.
        """
        try:
            response = self.model.generate_content(prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception:
            return []

    def check_compliance(self, schedule_data, policy_text):
        if not self.model: return "Service unavailable."
        
        prompt = f"""
        Audit the schedule data against the policy text.
        
        Data: {json.dumps(schedule_data)}
        Policy: {policy_text}
        
        Output format: Plain text list. Start lines with 'CRITICAL:', 'WARNING:', or 'PASS:'.
        """
        return self.model.generate_content(prompt).text

    def get_chat_response(self, history, query, current_data):
        if not self.model: return "Service unavailable."
        
        # Optimized context for token efficiency
        context = f"Dataset Summary: {json.dumps(current_data[:15])}..."
        full_query = f"{context}\n\nQuery: {query}\n\nTask: Provide a professional operational recommendation."
        
        gemini_history = []
        for msg in history:
             role = "user" if msg["role"] == "user" else "model"
             gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat = self.model.start_chat(history=gemini_history)
        return chat.send_message(full_query).text

# --- VISUALIZATION CLASS ---
class Visualizer:
    @staticmethod
    def get_color_map():
        # Professional Corporate Palette
        return {
            'Value Creation': '#0f172a',  # Dark Slate
            'Coordination': '#3b82f6',    # Blue
            'Logistics': '#94a3b8',       # Grey
            'Inefficiency': '#ef4444'     # Red (muted)
        }

    @staticmethod
    def plot_sankey(df):
        if df.empty or 'handover_to' not in df.columns: return None
        
        handover_df = df[df['handover_to'].notna() & (df['handover_to'] != "")]
        if handover_df.empty: return None
        
        all_nodes = list(set(df['posten'].tolist() + handover_df['handover_to'].tolist()))
        node_map = {name: i for i, name in enumerate(all_nodes)}
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15, 
                thickness=15, 
                line=dict(color="white", width=0.5), 
                label=all_nodes, 
                color="#cbd5e1" # Light grey nodes
            ),
            link=dict(
                source=[node_map[src] for src in handover_df['posten']],
                target=[node_map[tgt] for tgt in handover_df['handover_to']],
                value=[1] * len(handover_df),
                color="#e2e8f0" # Very light flow lines
            )
        )])
        fig.update_layout(
            title_text="Workflow Handovers", 
            font_family="Inter",
            font_size=12, 
            height=400,
            template="plotly_white",
            margin=dict(l=0, r=0, t=40, b=10)
        )
        return fig

    @staticmethod
    def plot_cognitive_heatmap(df):
        if df.empty: return None
        
        hours = [f"{h:02d}" for h in range(5, 23)]
        postens = sorted(df['posten'].unique())
        
        z_data = []
        for p in postens:
            row = []
            p_df = df[df['posten'] == p]
            for h in range(5, 23):
                hour_str = f"{h:02d}"
                tasks_in_hour = p_df[p_df['start_time'].astype(str).str.startswith(hour_str)]
                load = tasks_in_hour['cognitive_load'].max() if not tasks_in_hour.empty else 0
                row.append(load if not pd.isna(load) else 0)
            z_data.append(row)
            
        fig = px.imshow(
            z_data, 
            x=[f"{h}:00" for h in hours], 
            y=postens, 
            color_continuous_scale='Greys', # Professional Monochromatic
            aspect="auto"
        )
        fig.update_layout(
            title="Resource Load Intensity", 
            template="plotly_white",
            font_family="Inter",
            margin=dict(l=0, r=0, t=40, b=10)
        )
        return fig

    @staticmethod
    def plot_sunburst(df):
        if df.empty: return None
        
        fig = px.sunburst(
            df, 
            path=['strategic_category', 'posten', 'task_description'], 
            values='cognitive_load', 
            color='strategic_category',
            color_discrete_map=Visualizer.get_color_map()
        )
        fig.update_layout(
            title="Strategic Task Distribution", 
            template="plotly_white",
            font_family="Inter",
            margin=dict(l=0, r=0, t=40, b=10)
        )
        return fig

# --- MAIN APPLICATION ---
def main():
    ai = GeminiHandler()
    vis = Visualizer()
    
    # Session State Init
    if 'schedule_data' not in st.session_state:
        st.session_state.schedule_data = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # --- SIDEBAR ---
    with st.sidebar:
        st.subheader("Data Import")
        uploaded_file = st.file_uploader("Upload Schedule (PDF/TXT)", type=["txt", "pdf"])
        
        st.write("") # Spacer
        
        if st.button("Process Data", use_container_width=True):
            if uploaded_file and ai.model:
                try:
                    text = uploaded_file.read().decode("utf-8")
                    with st.spinner("Processing..."):
                        data = ai.parse_schedule(text)
                        if data:
                            st.session_state.schedule_data = data
                            st.success("Import successful")
                        else:
                            st.error("Parsing failed")
                except Exception:
                    st.error("File error")
            elif not ai.model:
                st.error("API Key missing")
        
        st.write("") # Spacer
        if st.button("Load Demo Dataset", use_container_width=True):
            # Professional Dummy Data
            st.session_state.schedule_data = [
                {"start_time": "07:00", "end_time": "10:00", "posten": "S1", "task_description": "Sauce Production", "strategic_category": "Value Creation", "cognitive_load": 0.6, "handover_to": "G2"},
                {"start_time": "09:00", "end_time": "11:00", "posten": "G2", "task_description": "Mise en Place", "strategic_category": "Value Creation", "cognitive_load": 0.4, "handover_to": ""},
                {"start_time": "11:30", "end_time": "13:30", "posten": "S1", "task_description": "Lunch Service", "strategic_category": "Value Creation", "cognitive_load": 1.0, "handover_to": ""},
                {"start_time": "06:30", "end_time": "09:00", "posten": "R1", "task_description": "Goods Receipt", "strategic_category": "Logistics", "cognitive_load": 0.3, "handover_to": "S1"},
                {"start_time": "14:00", "end_time": "15:00", "posten": "D1", "task_description": "Documentation", "strategic_category": "Coordination", "cognitive_load": 0.5, "handover_to": ""},
                {"start_time": "10:00", "end_time": "10:15", "posten": "All", "task_description": "Break", "strategic_category": "Inefficiency", "cognitive_load": 0.1, "handover_to": ""}
            ]
            st.success("Demo data loaded")

    # --- MAIN CONTENT ---
    st.title("Operations Intelligence")
    st.markdown("Strategic workforce planning and process optimization.")
    st.write("") # Margin

    # Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Analytics", "Compliance Audit", "Optimization Consultant", "Source Data"])

    if st.session_state.schedule_data:
        df = pd.DataFrame(st.session_state.schedule_data)

        # TAB 1: ANALYTICS
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(vis.plot_cognitive_heatmap(df), use_container_width=True)
            with col2:
                st.plotly_chart(vis.plot_sunburst(df), use_container_width=True)
            
            st.write("")
            sankey = vis.plot_sankey(df)
            if sankey:
                st.plotly_chart(sankey, use_container_width=True)

        # TAB 2: COMPLIANCE
        with tab2:
            st.subheader("Policy Validation")
            policy = st.text_area(
                "Defined Ruleset", 
                value="R1 handles logistics only. S1 manages production. Mandatory break times apply.",
                height=120
            )
            
            if st.button("Run Audit"):
                if ai.model:
                    with st.spinner("Auditing..."):
                        report = ai.check_compliance(st.session_state.schedule_data, policy)
                        
                        # Professional Formatting
                        for line in report.split("\n"):
                            line = line.strip()
                            if "CRITICAL:" in line:
                                st.error(line.replace("CRITICAL:", "").strip())
                            elif "WARNING:" in line:
                                st.warning(line.replace("WARNING:", "").strip())
                            elif "PASS:" in line:
                                st.success(line.replace("PASS:", "").strip())
                            elif line:
                                st.markdown(f"**{line}**")
                else:
                    st.error("System configuration error")

        # TAB 3: CONSULTANT
        with tab3:
            st.subheader("Scenario Simulation")
            
            # Chat Container
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.chat_history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            # Input Area
            if prompt := st.chat_input("Enter simulation parameters..."):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"): 
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Calculating..."):
                        response = ai.get_chat_response(
                            st.session_state.chat_history[:-1],
                            prompt, 
                            st.session_state.schedule_data
                        )
                        st.markdown(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})

        # TAB 4: DATA
        with tab4:
            st.subheader("Structured Dataset")
            st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        # Empty State
        st.info("No data available. Please import a schedule or load demo data.")

if __name__ == "__main__":
    main()
