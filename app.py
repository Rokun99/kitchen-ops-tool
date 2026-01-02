import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & HIGH END STYLING ---
st.set_page_config(
    page_title="WORKSPACE: AUDIT 2026",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# COLOR PALETTE (Strategic/Profi)
COLORS = {
    "bg": "#F8FAFC",        # Slate 50
    "card": "#FFFFFF",      # White
    "text_main": "#0F172A", # Slate 900
    "text_sub": "#64748B",  # Slate 500
    "accent": "#6366F1",    # Indigo 500
    "success": "#10B981",   # Emerald 500
    "danger": "#F43F5E",    # Rose 500
    "warning": "#F59E0B",   # Amber 500
    "neutral": "#94A3B8",   # Slate 400
    "border": "#E2E8F0"     # Slate 200
}

# Custom CSS for Minimalist/Profi Look
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {{ 
        font-family: 'Inter', sans-serif; 
        color: {COLORS['text_main']}; 
        background-color: {COLORS['bg']}; 
    }}
    
    /* Clean Header */
    .header-container {{
        padding-bottom: 2rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid {COLORS['border']};
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .main-title {{
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: {COLORS['text_main']};
        margin: 0;
    }}
    
    .sub-title {{
        font-size: 0.875rem;
        color: {COLORS['text_sub']};
        font-weight: 400;
        margin-top: 0.25rem;
    }}

    /* Section Headers */
    .section-label {{
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: {COLORS['text_sub']};
        margin-top: 3rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    .section-label::before {{
        content: '';
        display: block;
        width: 12px;
        height: 2px;
        background-color: {COLORS['accent']};
        border-radius: 2px;
    }}
    
    /* KPI Cards - Modern Minimalist */
    .kpi-card {{
        background-color: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 1.25rem;
        height: 100%;
        min-height: 110px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
        border-color: {COLORS['accent']};
    }}

    .kpi-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {COLORS['text_sub']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }}
    
    .kpi-metric {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {COLORS['text_main']};
        letter-spacing: -0.05em;
        line-height: 1.1;
    }}
    
    .kpi-context {{
        font-size: 0.75rem;
        color: {COLORS['neutral']};
        margin-top: 0.5rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.375rem;
    }}

    /* Tags for Trends */
    .tag {{
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
    }}
    .tag-bad {{ background: #FEF2F2; color: {COLORS['danger']}; }}
    .tag-good {{ background: #ECFDF5; color: {COLORS['success']}; }}
    .tag-neutral {{ background: #F1F5F9; color: {COLORS['text_sub']}; }}

    /* Tabs Override - Cleaner */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
        border-bottom: 1px solid {COLORS['border']};
        padding-bottom: 0px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent !important;
        border: none !important;
        padding: 0.75rem 0 !important;
        font-weight: 500;
        color: {COLORS['text_sub']};
    }}
    .stTabs [aria-selected="true"] {{
        color: {COLORS['accent']} !important;
        border-bottom: 2px solid {COLORS['accent']} !important;
    }}

    /* Input Widgets Polish */
    div[data-baseweb="select"] > div {{
        background-color: {COLORS['card']};
        border-color: {COLORS['border']};
        border-radius: 8px;
    }}
    
    /* Plotly Charts Container */
    .chart-container {{
        background-color: {COLORS['card']};
        border-radius: 12px;
        border: 1px solid {COLORS['border']};
        padding: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }}
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
class DataWarehouse:
    @staticmethod
    def get_full_ist_data():
        # DATEN EXAKT NACH DEN NEUKALKULATIONS-BERICHTEN
        data = [
            # --- D1 DIÄTETIK ---
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Admin: E-Mails/Mutationen", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:25", "Ende": "08:30", "Task": "Hygiene/Rüsten: Wechsel Büro-Küche", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "08:30", "Ende": "09:15", "Task": "Prod: Suppen (Basis/Convenience 520 Port.)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:15", "Ende": "09:45", "Task": "Prod: ET (System-Ableitung/Allergene)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Admin: 2. Mail-Check (Spätmeldungen)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Cg-Komp. (High-Convenience)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "10:45", "Ende": "11:00", "Task": "Coord: Instruktion Band-MA", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Admin: Letzte Orgacard-Updates", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service: Diät-Band (System-Ausgabe)", "Typ": "Service"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik: Abräumen/Kühlen/Rückstellproben", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:00", "Task": "Admin: Produktionsprotokolle", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "15:00", "Ende": "15:50", "Task": "Prod: MEP Folgetag (Vegi-Komponenten/Fertig)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "15:50", "Ende": "16:30", "Task": "Prod: Abend Diät-Komp. (Regenerieren)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "16:30", "Ende": "17:00", "Task": "Coord: Service-Vorbereitung Abend", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band-Abendessen", "Typ": "Service"},
            {"Dienst": "D1", "Start": "18:00", "Ende": "18:09", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- E1 ENTREMETIER ---
            {"Dienst": "E1", "Start": "07:00", "Ende": "07:15", "Task": "Coord: Posten einrichten", "Typ": "Coord"},
            {"Dienst": "E1", "Start": "07:15", "Ende": "08:30", "Task": "Prod: Stärke (Dämpfen/Convenience 520 Pax)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "08:30", "Ende": "09:30", "Task": "Prod: Gemüse (Dämpfen/Regenerieren 520 Pax)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "09:30", "Ende": "09:45", "Task": "Prod: Suppe Finalisieren (Basis)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "09:45", "Ende": "10:00", "Task": "Logistik: Bereitstellung Gastro", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Wahlkost Spezial (System)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "10:45", "Ende": "11:20", "Task": "Prod: Regenerieren Band (High-Convenience)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Potenzial: 70-Min-Falle (Bereitschaft/Warten)", "Typ": "Potenzial"},
            {"Dienst": "E1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Transport Reste Restaurant", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "12:45", "Ende": "13:00", "Task": "Logistik: Reinigung Clean-as-you-go", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "13:30", "Ende": "14:00", "Task": "Prod: Wahlkost MEP (Vorbereitung)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "14:00", "Ende": "15:00", "Task": "Prod: MEP Folgetag (Großmenge/Schnittware)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "15:00", "Ende": "15:30", "Task": "Admin: QM-Kontrolle MHD", "Typ": "Admin"},
            {"Dienst": "E1", "Start": "15:30", "Ende": "15:54", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- S1 SAUCIER ---
            {"Dienst": "S1", "Start": "07:00", "Ende": "07:30", "Task": "Prod: Saucen/Basis (Päckli/Convenience)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "07:30", "Ende": "08:30", "Task": "Prod: Fleisch Finish (Kurzbraten/System)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "08:30", "Ende": "09:30", "Task": "Coord: Support E1 (Pufferzeit)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "09:30", "Ende": "10:00", "Task": "Prod: Wahlkost Finish (Montage)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Fleisch/Sauce", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "10:45", "Ende": "11:00", "Task": "Logistik: Wagenübergabe Gastro", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "11:00", "Ende": "11:20", "Task": "Prod: Wahlkost Setup (Montage)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Potenzial: Wahlkost-Idle (Warten auf Bons)", "Typ": "Potenzial"},
            {"Dienst": "S1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Nachschub Restaurant", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "12:45", "Ende": "13:00", "Task": "Logistik: Reinigung Kipper", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "13:30", "Ende": "14:15", "Task": "Admin: Planung/TK-Management", "Typ": "Admin"},
            {"Dienst": "S1", "Start": "14:15", "Ende": "15:00", "Task": "Prod: MEP Folgetag (Fleisch marinieren/Batch)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "15:00", "Ende": "15:30", "Task": "Coord: Support G2/D1 (Puffer)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "15:30", "Ende": "15:54", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- R1 GASTRO ---
            {"Dienst": "R1", "Start": "06:30", "Ende": "07:15", "Task": "Logistik: Warenannahme Rampe (HACCP Risiko)", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:15", "Ende": "07:30", "Task": "Logistik: Verräumen Kühlhaus", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:30", "Ende": "07:45", "Task": "Potenzial: Hygiene-Schleuse/Umziehen", "Typ": "Potenzial"},
            {"Dienst": "R1", "Start": "07:45", "Ende": "08:30", "Task": "Admin: Manuelle Deklaration", "Typ": "Admin"},
            {"Dienst": "R1", "Start": "08:30", "Ende": "09:30", "Task": "Prod: MEP Folgetag (Freeflow/Montage)", "Typ": "Prod"},
            {"Dienst": "R1", "Start": "09:30", "Ende": "10:00", "Task": "Service: Setup Heute (Verbrauchsmaterial)", "Typ": "Service"},
            {"Dienst": "R1", "Start": "10:20", "Ende": "10:45", "Task": "Logistik: Transport Speisen", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "10:45", "Ende": "11:00", "Task": "Service: Einsetzen Buffet", "Typ": "Service"},
            {"Dienst": "R1", "Start": "11:00", "Ende": "11:15", "Task": "Coord: Quality Check/Showteller", "Typ": "Coord"},
            {"Dienst": "R1", "Start": "11:15", "Ende": "11:30", "Task": "Potenzial: Bereitschaft", "Typ": "Potenzial"},
            {"Dienst": "R1", "Start": "11:30", "Ende": "13:30", "Task": "Service: Mittagsservice Gastro", "Typ": "Service"},
            {"Dienst": "R1", "Start": "13:30", "Ende": "14:00", "Task": "Logistik: Abbau Buffet", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "14:00", "Ende": "14:30", "Task": "Logistik: Reinigung Office", "Typ": "Logistik"},

            # --- R2 GASTRO ---
            {"Dienst": "R2", "Start": "06:30", "Ende": "06:50", "Task": "Service: Band-Setup (Patienten)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "06:50", "Ende": "07:45", "Task": "Service: Band-Service (Falsche Zuordnung)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "07:45", "Ende": "08:00", "Task": "Logistik: Wechsel Patient->Gastro", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "08:30", "Task": "Potenzial: Salat-Finish (Gedehnt 12 Stk)", "Typ": "Potenzial"},
            {"Dienst": "R2", "Start": "08:30", "Ende": "09:00", "Task": "Logistik: Office/Abfall (Botengänge)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "09:00", "Ende": "09:30", "Task": "Logistik: Geräte-Check (Muda)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "09:30", "Ende": "10:00", "Task": "Potenzial: Leerlauf/Puffer", "Typ": "Potenzial"},
            {"Dienst": "R2", "Start": "10:20", "Ende": "10:45", "Task": "Logistik: Transport", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "10:45", "Ende": "11:00", "Task": "Prod: Fritteusen Start (System)", "Typ": "Prod"},
            {"Dienst": "R2", "Start": "11:00", "Ende": "11:30", "Task": "Coord: Show-Setup (Redundanz)", "Typ": "Coord"},
            {"Dienst": "R2", "Start": "11:30", "Ende": "13:30", "Task": "Service: Mittagsservice & ReCircle", "Typ": "Service"},
            {"Dienst": "R2", "Start": "13:30", "Ende": "14:00", "Task": "Service: Food Rescue (Verkauf)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "14:00", "Ende": "14:30", "Task": "Logistik: Fritteuse aus/Reinigung", "Typ": "Logistik"},

            # --- H1 FRÜHSTÜCK ---
            {"Dienst": "H1", "Start": "05:30", "Ende": "06:00", "Task": "Prod: Birchermüsli/Brei (Mischen/Convenience)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "06:00", "Ende": "06:30", "Task": "Prod: Rahm/Dessert Vorb. (Maschine)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "06:30", "Ende": "06:50", "Task": "Service: Band-Setup", "Typ": "Service"},
            {"Dienst": "H1", "Start": "06:50", "Ende": "07:45", "Task": "Service: Band Frühstück", "Typ": "Service"},
            {"Dienst": "H1", "Start": "07:45", "Ende": "08:15", "Task": "Logistik: Aufräumen/Auffüllen", "Typ": "Logistik"},
            {"Dienst": "H1", "Start": "08:15", "Ende": "09:15", "Task": "Prod: Dessert/Patisserie (Redundanz H2/Convenience)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "09:15", "Ende": "10:00", "Task": "Prod: Salat Vorbereitung (Redundanz G2/Beutel)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Glacé portionieren (System)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "10:45", "Ende": "11:25", "Task": "Prod: Käse schneiden (Maschine/Fertig)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "11:25", "Ende": "12:30", "Task": "Service: Band Mittagsservice", "Typ": "Service"},

            # --- H2 PÄTISSERIE ---
            {"Dienst": "H2", "Start": "09:15", "Ende": "09:30", "Task": "Prod: Basis-Massen (Convenience/Pulver)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "09:30", "Ende": "10:15", "Task": "Prod: Restaurant-Finish (Montage 25 Gläser)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "10:15", "Ende": "11:00", "Task": "Prod: Patienten-Masse (Abfüllen/Convenience)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "11:00", "Ende": "11:15", "Task": "Logistik: Transport Gastro", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "11:15", "Ende": "11:45", "Task": "Logistik: Wagen-Bau Abend", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "11:45", "Ende": "12:30", "Task": "Prod: Power-Dessert (Anrühren/Päckli)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "12:30", "Ende": "13:00", "Task": "Service: Privat-Zvieri", "Typ": "Service"},
            {"Dienst": "H2", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Reinigung", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "14:15", "Ende": "15:15", "Task": "Prod: Morgen Gastro (Abfüllen/System)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "15:15", "Ende": "16:00", "Task": "Prod: Morgen Pat (Abfüllen/System)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "16:00", "Ende": "16:30", "Task": "Coord: Support H1", "Typ": "Coord"},
            {"Dienst": "H2", "Start": "16:30", "Ende": "17:00", "Task": "Service: Setup Abend", "Typ": "Service"},
            {"Dienst": "H2", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band Abendessen", "Typ": "Service"},
            {"Dienst": "H2", "Start": "18:00", "Ende": "18:09", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- H3 ASSEMBLY LINE ---
            {"Dienst": "H3", "Start": "09:15", "Ende": "09:45", "Task": "Prod: Wähen Montage (Convenience/Teig)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "09:45", "Ende": "10:30", "Task": "Prod: Sandwiches (System-Montage)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "10:30", "Ende": "11:15", "Task": "Prod: Salatteller (Montage/Beutel)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "11:15", "Ende": "12:00", "Task": "Prod: Abend Kalt (Platten/Legesystem)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:00", "Ende": "12:30", "Task": "Prod: Bircher-Masse für Morgen (Mischen)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:30", "Ende": "13:00", "Task": "Logistik: Reste/Saucen", "Typ": "Logistik"},
            {"Dienst": "H3", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Reinigung", "Typ": "Logistik"},
            {"Dienst": "H3", "Start": "14:15", "Ende": "15:15", "Task": "Prod: Salatbuffet (Montage/System)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "15:15", "Ende": "16:00", "Task": "Prod: Wähen-Vorbereitung Morgen (Teig)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "16:00", "Ende": "16:30", "Task": "Coord: Support", "Typ": "Coord"},
            {"Dienst": "H3", "Start": "16:30", "Ende": "17:00", "Task": "Service: Setup Band", "Typ": "Service"},
            {"Dienst": "H3", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band Abend Support", "Typ": "Service"},
            {"Dienst": "H3", "Start": "18:00", "Ende": "18:30", "Task": "Logistik: Abschluss Kaltküche", "Typ": "Logistik"},

            # --- G2 GARDE-MANGER ---
            {"Dienst": "G2", "Start": "09:30", "Ende": "09:45", "Task": "Coord: Absprache H3", "Typ": "Coord"},
            {"Dienst": "G2", "Start": "09:45", "Ende": "10:30", "Task": "Prod: Wahlkost Kalt (System-Montage)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "10:30", "Ende": "11:15", "Task": "Prod: Patienten-Salat (Beutel/Convenience)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "11:15", "Ende": "12:30", "Task": "Prod: Abendessen (Aufschnitt/Montage)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "14:15", "Ende": "15:00", "Task": "Prod: MEP Folgetag (System)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "15:00", "Ende": "16:00", "Task": "Potenzial: Leerlauf/Dehnung (Standard-Tag)", "Typ": "Potenzial"},
            {"Dienst": "G2", "Start": "16:00", "Ende": "17:00", "Task": "Coord: Band-Setup", "Typ": "Coord"},
            {"Dienst": "G2", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band-Abendessen", "Typ": "Service"},
            {"Dienst": "G2", "Start": "18:00", "Ende": "18:30", "Task": "Admin: Hotellerie-Check", "Typ": "Admin"},
        ]
        return DataWarehouse.process(data)

    @staticmethod
    def process(data):
        if not data:
            return pd.DataFrame(columns=['Dienst', 'Start', 'Ende', 'Task', 'Typ', 'Start_DT', 'End_DT', 'Duration'])
            
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'])
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'])
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- 3. ANALYTICAL ENGINE: KPI FACTORY ---
class KPI_Engine:
    HOURLY_RATE_CHF = 55.0 

    @staticmethod
    def calculate_all(df_ist, mode='time'):
        total_min = df_ist['Duration'].sum()
        if total_min == 0: return {}

        potenzial_min = df_ist[df_ist['Typ'] == 'Potenzial']['Duration'].sum()
        skilled_dienste = ['D1', 'S1', 'E1', 'G2', 'R1']
        
        # 1. Skill-Drift
        leakage_min = df_ist[(df_ist['Dienst'].isin(skilled_dienste)) & (df_ist['Typ'].isin(['Logistik', 'Potenzial']))]['Duration'].sum()
        leakage_pct = (leakage_min / total_min) * 100
        leakage_cost = (leakage_min / 60) * KPI_Engine.HOURLY_RATE_CHF
        
        # 2. Potenzial Ratio
        muda_pct = (potenzial_min / total_min) * 100
        muda_cost = (potenzial_min / 60) * KPI_Engine.HOURLY_RATE_CHF
        
        # 3. Kernzeit-Vakuum
        band_crunch = df_ist[(df_ist['Start'] >= "11:00") & (df_ist['Ende'] <= "12:30")]
        idle_band_min = band_crunch[band_crunch['Typ'] == 'Potenzial']['Duration'].sum() + 105
        idle_band_cost = (idle_band_min / 60) * KPI_Engine.HOURLY_RATE_CHF
        
        # 4. Context-Switch Rate
        d1_tasks = len(df_ist[df_ist['Dienst'] == 'D1'])
        context_switches = d1_tasks / 1.5
        
        # 5. Recovery Potential
        recoverable_min = potenzial_min + (leakage_min * 0.5)
        fte_potential = recoverable_min / 480
        recoverable_cost = (recoverable_min / 60) * KPI_Engine.HOURLY_RATE_CHF
        
        # 6. Industrialisierungsgrad
        prod_df = df_ist[df_ist['Typ'] == 'Prod']
        prod_min = prod_df['Duration'].sum()
        
        montage_indicators = [
            "Montage", "Regenerieren", "Finish", "Beutel", "Päckli", 
            "Convenience", "Abfüllen", "Mischen", "Anrühren", "Portionieren", 
            "Basis", "System", "Dämpfen", "Fertig", "Vorbereitung", "Maschine"
        ]
        
        # Only count duration if it is a production task
        montage_min = prod_df[prod_df['Task'].str.contains('|'.join(montage_indicators), case=False, na=False)]['Duration'].sum()
        industrial_rate = (montage_min / prod_min * 100) if prod_min > 0 else 0
        
        # 7. Value-Add Ratio
        value_add_min = df_ist[df_ist['Typ'].isin(['Prod', 'Service'])]['Duration'].sum()
        value_add_ratio = (value_add_min / total_min) * 100

        # 8. Admin Burden
        admin_min = df_ist[df_ist['Typ'] == 'Admin']['Duration'].sum()
        admin_cost = (admin_min / 60) * KPI_Engine.HOURLY_RATE_CHF
        
        # 10. Service Intensity
        service_min = df_ist[df_ist['Typ'] == 'Service']['Duration'].sum()
        service_share = (service_min / total_min) * 100

        # NEW 11-13
        logistics_min = df_ist[df_ist['Typ'] == 'Logistik']['Duration'].sum()
        logistics_share = (logistics_min / total_min) * 100
        
        coord_min = df_ist[df_ist['Typ'] == 'Coord']['Duration'].sum()
        coord_share = (coord_min / total_min) * 100
        
        peak_staff = 9 

        # FORMATTING LOGIC
        def fmt(val, type='pct'):
            if mode == 'money' and type == 'abs':
                return f"{val:,.0f} CHF".replace(",", "'")
            elif type == 'abs_min':
                return f"{val:,.0f} CHF".replace(",", "'") if mode == 'money' else f"{val:.0f} Min"
            else: 
                return f"{val:.1f}%"

        kpis_list = [
            ("Skill-Drift (Leakage)", {"val": fmt(leakage_cost if mode=='money' else leakage_pct, 'abs' if mode=='money' else 'pct'), "sub": "Fachkraft-Einsatz", "trend": "bad"}),
            ("Potenzial (Muda)", {"val": fmt(muda_cost if mode=='money' else muda_pct, 'abs' if mode=='money' else 'pct'), "sub": "Nicht-Wertschöpfend", "trend": "bad"}),
            ("Recovery Value", {"val": fmt(recoverable_cost, 'abs') if mode=='money' else f"{fte_potential:.2f} FTE", "sub": "Einspar-Möglichkeit", "trend": "good"}),
            ("Kernzeit-Vakuum", {"val": fmt(idle_band_cost if mode=='money' else idle_band_min, 'abs_min'), "sub": "Wartezeit Service", "trend": "bad"}),
            ("Context-Switch Rate", {"val": f"{context_switches:.1f}x", "sub": "D1 Fragmentierung", "trend": "bad"}),
            
            ("Industrialisierungsgrad", {"val": f"{industrial_rate:.0f}%", "sub": "Convenience-Anteil", "trend": "neutral"}),
            ("Value-Add Ratio", {"val": f"{value_add_ratio:.1f}%", "sub": "Prod + Service", "trend": "good"}),
            ("Admin Burden", {"val": fmt(admin_cost if mode=='money' else admin_min, 'abs_min'), "sub": "Bürokratie-Last", "trend": "bad"}),
            ("Logistics Drag", {"val": f"{logistics_share:.1f}%", "sub": "Transport/Reinigung", "trend": "neutral"}),
            ("Coordination Tax", {"val": f"{coord_share:.1f}%", "sub": "Absprachen/Meetings", "trend": "neutral"}),
            
            ("Liability Gap", {"val": "105 Min", "sub": "Risiko D1 Pause", "trend": "bad"}),
            ("Service Intensity", {"val": f"{service_share:.0f}%", "sub": "Patient Touchpoint", "trend": "good"}),
            ("Patient/Gastro Split", {"val": "62/38", "sub": "Ressourcen-Allokation", "trend": "neutral"}),
            ("Process Cycle Eff.", {"val": f"{(value_add_min/(total_min-potenzial_min)*100):.1f}%", "sub": "Netto-Effizienz", "trend": "good"}),
            ("Peak Staff Load", {"val": "9 Pax", "sub": "Max. Gleichzeitig", "trend": "neutral"}),
        ]
        return kpis_list

# --- 4. RENDERER ---
def render_kpi_card(title, data):
    trend_color = data['trend']
    html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{title}</div>
        <div class="kpi-metric">{data['val']}</div>
        <div class="kpi-context">
            <span class="tag tag-{trend_color}">{data['trend'].upper()}</span>
            <span>{data['sub']}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- 5. MAIN APPLICATION ---
def main():
    dw = DataWarehouse()
    df_ist = dw.get_full_ist_data()
    
    # --- HEADER ---
    st.markdown("""
        <div class="header-container">
            <div>
                <h1 class="main-title">WORKSPACE: AUDIT 2026</h1>
                <div class="sub-title">Kitchen Intelligence Master-Suite v2.4 (High-End)</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Controls (integrated, not sidebar)
    col_ctrl1, col_ctrl2 = st.columns([4, 1])
    with col_ctrl2:
        mode_select = st.radio("Unit:", ["Zeit (Min)", "Wert (CHF)"], horizontal=True, label_visibility="collapsed")
        mode = 'money' if 'CHF' in mode_select else 'time'

    kpis_list = KPI_Engine.calculate_all(df_ist, mode=mode)

    # --- MANAGEMENT COCKPIT ---
    st.markdown('<div class="section-label">Management Cockpit: 15 Core Metrics</div>', unsafe_allow_html=True)
    
    for row_idx in range(3):
        cols = st.columns(5, gap="medium")
        for col_idx in range(5):
            index = row_idx * 5 + col_idx
            if index < len(kpis_list):
                kpi_name, kpi_data = kpis_list[index]
                with cols[col_idx]:
                    render_kpi_card(kpi_name, kpi_data)

    # --- LOAD PROFILE ---
    st.markdown('<div class="section-label">Personal-Einsatzprofil (Staffing Load)</div>', unsafe_allow_html=True)
    
    load_data = []
    for h in range(5, 20):
        for m in [0, 15, 30, 45]:
            t = datetime(2026, 1, 1, h, m)
            active = len(df_ist[(df_ist['Start_DT'] <= t) & (df_ist['End_DT'] > t)])
            load_data.append({"Zeit": f"{h:02d}:{m:02d}", "Staff": active})
    
    with st.container():
        # Clean Plotly Chart
        fig_load = px.area(pd.DataFrame(load_data), x="Zeit", y="Staff", line_shape="spline")
        fig_load.update_traces(line_color="#0F172A", fillcolor="rgba(15, 23, 42, 0.05)")
        fig_load.update_layout(
            plot_bgcolor="white", 
            paper_bgcolor="white", 
            margin=dict(l=20, r=20, t=20, b=20),
            height=250,
            xaxis=dict(showgrid=False, title=None, linecolor='#E2E8F0'),
            yaxis=dict(showgrid=True, gridcolor='#F1F5F9', title="Active FTE", range=[0, 10]),
            hovermode="x unified"
        )
        # Critical Zone Line
        fig_load.add_hline(y=8, line_dash="dot", line_color="#EF4444", annotation_text="Congestion Zone", annotation_position="top right", annotation_font_color="#EF4444")
        st.plotly_chart(fig_load, use_container_width=True, config={'displayModeBar': False})

    # --- DEEP DIVE ANALYTICS ---
    st.markdown('<div class="section-label">Prozess-Analyse</div>', unsafe_allow_html=True)
    
    # Filter
    filter_col, _ = st.columns([2, 3])
    with filter_col:
        all_types = list(df_ist['Typ'].unique())
        selected_types = st.multiselect("Fokus-Filter (Typen)", all_types, default=all_types, label_visibility="collapsed", placeholder="Filter Tasks...")
    
    df_filtered = df_ist[df_ist['Typ'].isin(selected_types)]

    # Clean Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Gantt-Flow", 
        "Potenzial-Analyse", 
        "Ressourcen-Balance", 
        "Aktivitäts-Verteilung"
    ])

    # Modern Palette for Charts
    color_map = {
        "Prod": "#3B82F6",      # Blue
        "Service": "#10B981",   # Emerald
        "Admin": "#F59E0B",     # Amber
        "Logistik": "#64748B",  # Slate
        "Potenzial": "#F43F5E", # Rose
        "Coord": "#8B5CF6"      # Violet
    }

    def clean_chart_layout(fig):
        fig.update_layout(
            plot_bgcolor="white", 
            paper_bgcolor="white", 
            margin=dict(l=10, r=10, t=30, b=20),
            xaxis=dict(showgrid=True, gridcolor='#F1F5F9', title=None),
            yaxis=dict(showgrid=False, title=None),
            font=dict(family="Inter", color="#64748B"),
            hoverlabel=dict(bgcolor="white", font_size=12, font_family="Inter"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
        )
        return fig

    with tab1:
        fig1 = px.timeline(df_filtered, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", hover_name="Task", color_discrete_map=color_map, height=600)
        fig1.update_yaxes(categoryorder="array", categoryarray=["H3","H2","H1","R2","R1","G2","S1","E1","D1"])
        st.plotly_chart(clean_chart_layout(fig1), use_container_width=True, config={'displayModeBar': False})

    with tab2:
        df_waste = df_ist[df_ist['Typ'] == 'Potenzial']
        if not df_waste.empty:
            fig2 = px.timeline(df_waste, x_start="Start_DT", x_end="End_DT", y="Dienst", hover_name="Task", color_discrete_sequence=["#F43F5E"], height=400)
            fig2.update_yaxes(categoryorder="array", categoryarray=["H3","H2","H1","R2","R1","G2","S1","E1","D1"])
            st.plotly_chart(clean_chart_layout(fig2), use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Keine expliziten Potenzial-Blöcke identifiziert.")
            
    with tab3:
        df_grouped = df_filtered.groupby(['Dienst', 'Typ'])['Duration'].sum().reset_index()
        fig3 = px.bar(df_grouped, x="Dienst", y="Duration", color="Typ", color_discrete_map=color_map, barmode='stack', height=500)
        fig3.update_layout(yaxis_title="Minuten")
        st.plotly_chart(clean_chart_layout(fig3), use_container_width=True, config={'displayModeBar': False})
        
    with tab4:
        df_pie = df_filtered.groupby('Typ')['Duration'].sum().reset_index()
        fig4 = px.pie(df_pie, values='Duration', names='Typ', color='Typ', color_discrete_map=color_map, hole=0.6, height=500)
        fig4.update_traces(textinfo='percent+label', textfont_size=13)
        fig4.update_layout(showlegend=False, annotations=[dict(text='Total', x=0.5, y=0.5, font_size=20, showarrow=False)])
        st.plotly_chart(clean_chart_layout(fig4), use_container_width=True, config={'displayModeBar': False})

if __name__ == "__main__":
    main()
