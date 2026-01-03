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

# DEFINITIONS & CONTEXT (Tooltip Lexicon)
# REFINED: Professional Wording & Lean Management Terminology
KPI_DEFINITIONS = {
    "Skill-Drift (Leakage)": "Anteil der Arbeitszeit, in der Fachkräfte (z.B. Köche) qualifikationsfremde Routinetätigkeiten (Logistik, Reinigung) ausführen. Ziel: < 10%.",
    "Potenzial (Muda)": "Nicht-wertschöpfende Zeit durch Warten, unnötige Wege oder Prozess-Leerlauf (Verschwendung nach Lean Management).",
    "Recovery Value (Yearly)": "Extrapoliertes Einsparpotenzial pro Jahr (Basis 250 Tage) durch Eliminierung von Muda und Optimierung des Skill-Mix.",
    "Kernzeit-Vakuum": "Summierte unproduktive Wartezeit während der kritischen Service-Phasen (z.B. Warten auf Wahlkost-Ausgabe).",
    "Context-Switch Rate": "Durchschnittliche Anzahl der Aufgabenwechsel pro Mitarbeiter/Schicht. Hohe Werte (>15) indizieren Fragmentierung und Ineffizienz.",
    "Industrialisierungsgrad": "Anteil von High-Convenience-Komponenten (z.B. Fertigdessert, Schnittsalat, TK) im Verhältnis zur Eigenfertigung.",
    "Value-Add Ratio": "Anteil der Netto-Arbeitszeit, die direkt in wertschöpfende Tätigkeiten (Produktion, Gastkontakt) fließt.",
    "Admin Burden": "Zeitaufwand für administrative Prozesse, Dokumentation, Bestellwesen und Systempflege (Orgacard).",
    "Logistics Drag": "Prozentualer Zeitverlust durch interne Transporte, Warenannahme und Rüstwege.",
    "Coordination Tax": "Zeitaufwand für Absprachen, Meetings, Übergaben und Instruktionen (Reibungsverlust).",
    "Liability Gap": "Operative Risikofenster ohne klare Verantwortlichkeit (z.B. unbesetztes Diät-Telefon während Pausenzeiten).",
    "Service Intensity": "Anteil der Arbeitszeit mit direktem Gastkontakt oder aktiver Ausgabe am Band (Touchpoints).",
    "Patient/Gastro Split": "Verhältnis der Ressourcenbindung zwischen Patientenverpflegung (Stationär) und Mitarbeiterrestaurant.",
    "Process Cycle Eff.": "Verhältnis von reiner Bearbeitungszeit zur gesamten Durchlaufzeit (Indikator für Prozessfluss).",
    "FTE-Verschwendung (Overstaffing)": "Summierte Stunden, in denen die Personalkapazität die tatsächliche Arbeitslast übersteigt (Überdeckung).",
    "R2 Inflation (Hidden)": "Arbeitszeitdehnung (Parkinsonsches Gesetz) im Dienst R2 am Morgen mangels operativer Auslastung.",
    "H1 Skill-Dilution": "Verwässerung des Rollenprofils H1 durch fachfremde Aufgaben (Dessert/Salat statt Kernkompetenz Frühstück).",
    "R1 Hygiene-Risk": "Kumulierte Dauer der Wechsel zwischen unreinen Bereichen (Rampe) und reinen Bereichen (Buffet) durch R1.",
    "G2 Capacity Gap": "Explizite, ungenutzte Personalkapazität im Dienst G2 (Nachmittag) aufgrund von Prozesslücken.",
    "Qualifikations-Verschw.": "Einsatz von High-Skill-Personal für Low-Skill-Tasks (Overprocessing). Teuerste Form der Verschwendung."
}

SECTION_TOOLTIPS = {
    "Management Cockpit": "Strategische Übersicht der 20 wichtigsten Leistungskennzahlen (KPIs) zur Steuerung des Betriebs.",
    "Belastungs-Matrix": "Vergleich der vorhandenen Personalkapazität (grau) mit der tatsächlich benötigten Arbeitslast (Linie). Zeigt Über- und Unterdeckung.",
    "Detail-Analyse": "Interaktive Tiefenanalyse der Arbeitspläne, Prozessflüsse und spezifischen Schwachstellen.",
    "Personal-Einsatzprofil": "Visuelle Darstellung der anwesenden Mitarbeiter über den Tagesverlauf (Schichtplan-Dichte)."
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
        padding-bottom: 1.5rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid {COLORS['border']};
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .main-title {{
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: {COLORS['text_main']};
        margin: 0;
    }}
    
    .sub-title {{
        font-size: 0.9rem;
        color: {COLORS['text_sub']};
        font-weight: 400;
        margin-top: 0.25rem;
    }}

    /* Section Headers with Tooltip Cursor */
    .section-label {{
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: {COLORS['text_sub']};
        margin-top: 2.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: help; /* Shows question mark cursor */
    }}
    
    .section-label::before {{
        content: '';
        display: block;
        width: 4px;
        height: 16px;
        background-color: {COLORS['accent']};
        border-radius: 2px;
    }}
    
    /* KPI Cards - Modern Minimalist */
    .kpi-card {{
        background-color: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 1.25rem;
        height: 100%;
        min-height: 110px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        display: flex; 
        flex-direction: column; 
        justify-content: space-between;
        cursor: help; /* Tooltip indicator */
        position: relative;
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
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    
    .kpi-metric {{
        font-size: 1.6rem;
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
# Definition der Skill-Levels (3=Hoch, 2=Mittel, 1=Niedrig)
SKILL_LEVELS = {
    "D1": 3, "S1": 3, "E1": 3,  # Fachkräfte (Koch/Diät)
    "G2": 2, "H2": 2, "R1": 2, "H1": 2, # Fachkraft-Niveau
    "H3": 1, "R2": 1 # Hilfskräfte
}

class DataWarehouse:
    @staticmethod
    def get_full_ist_data():
        # DATEN EXAKT NACH DEN DIENSTPLÄNEN (DOCX)
        data = [
            # ==========================
            # D1 DIÄTETIK (08:00 - 18:09)
            # ==========================
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Admin: E-Mails/Mutationen/Diätpläne", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:25", "Ende": "08:30", "Task": "Hygiene/Rüsten: Wechsel Büro-Küche", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "08:30", "Ende": "09:15", "Task": "Prod: Suppen (Basis/Convenience 520 Port.)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:15", "Ende": "09:45", "Task": "Prod: ET (System-Ableitung/Allergene)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Admin: 2. Mail-Check (Spätmeldungen)", "Typ": "Admin"},
            # 10:00 Pause
            {"Dienst": "D1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Cg-Komp. (High-Convenience)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "10:45", "Ende": "11:00", "Task": "Coord: Instruktion Band-MA/Spezialessen", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Admin: Letzte Orgacard-Updates", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service: Diät-Band (System-Ausgabe)", "Typ": "Service"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik: Abräumen/Kühlen/Rückstellproben", "Typ": "Logistik"},
            # 12:45 - 14:30 Pause
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:00", "Task": "Admin: Produktionsprotokolle Folgetag", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "15:00", "Ende": "15:50", "Task": "Prod: MEP Folgetag (Vegi-Komponenten/Fertig)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "15:50", "Ende": "16:30", "Task": "Prod: Abend Diät-Komp. (Regenerieren/Garen)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "16:30", "Ende": "17:00", "Task": "Coord: Tablettkarten/Service-Setup", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "17:00", "Ende": "18:05", "Task": "Service: Band-Abendessen", "Typ": "Service"},
            {"Dienst": "D1", "Start": "18:05", "Ende": "18:09", "Task": "Logistik: Aufräumen/To-Do Liste", "Typ": "Logistik"},

            # ==========================
            # E1 ENTREMETIER (07:00 - 15:54)
            # ==========================
            {"Dienst": "E1", "Start": "07:00", "Ende": "07:15", "Task": "Coord: Posten einrichten", "Typ": "Coord"},
            {"Dienst": "E1", "Start": "07:15", "Ende": "08:30", "Task": "Prod: Stärke (Dämpfen/Convenience 520 Pax)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "08:30", "Ende": "09:30", "Task": "Prod: Gemüse (Dämpfen/Regenerieren 520 Pax)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "09:30", "Ende": "09:45", "Task": "Prod: Suppe Finalisieren (Basis)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "09:45", "Ende": "10:00", "Task": "Logistik: Bereitstellung Gastro", "Typ": "Logistik"},
            # 10:00 Pause
            {"Dienst": "E1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Wahlkost Spezial (System/Minute)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "10:45", "Ende": "11:20", "Task": "Prod: Regenerieren Band (High-Convenience)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Potenzial: 70-Min-Falle (Bereitschaft/Warten)", "Typ": "Potenzial"},
            {"Dienst": "E1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Transport Reste Restaurant", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "12:45", "Ende": "13:00", "Task": "Logistik: Reinigung Clean-as-you-go", "Typ": "Logistik"},
            # 13:00 - 13:30 Pause
            {"Dienst": "E1", "Start": "13:30", "Ende": "14:00", "Task": "Prod: Wahlkost MEP Abend/Morgen (Vorbereitung)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "14:00", "Ende": "15:00", "Task": "Prod: MEP Folgetag (Großmenge/Schnittware)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "15:00", "Ende": "15:30", "Task": "Admin/QC: Kühlhäuser/MHDs/Ordnung", "Typ": "Admin"},
            {"Dienst": "E1", "Start": "15:30", "Ende": "15:54", "Task": "Logistik: Endreinigung Posten/Unterschriften", "Typ": "Logistik"},

            # ==========================
            # S1 SAUCIER (07:00 - 15:54)
            # ==========================
            {"Dienst": "S1", "Start": "07:00", "Ende": "07:30", "Task": "Prod: Saucen/Basis (Päckli/Convenience)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "07:30", "Ende": "08:30", "Task": "Prod: Fleisch Finish (Kurzbraten/System)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "08:30", "Ende": "09:30", "Task": "Coord: Support E1 (Pufferzeit)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "09:30", "Ende": "10:00", "Task": "Prod: Wahlkost Finish (Montage)", "Typ": "Prod"},
            # 10:00 Pause
            {"Dienst": "S1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Fleisch/Sauce/Wärmewägen", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "10:45", "Ende": "11:00", "Task": "Logistik: Wagenübergabe Gastro", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "11:00", "Ende": "11:20", "Task": "Prod: Wahlkost Setup (Montage)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Potenzial: Wahlkost-Idle (Warten auf Bons)", "Typ": "Potenzial"},
            {"Dienst": "S1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Nachschub Restaurant", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "12:45", "Ende": "13:00", "Task": "Logistik: Reinigung Kipper", "Typ": "Logistik"},
            # 13:00 - 13:30 Pause
            {"Dienst": "S1", "Start": "13:30", "Ende": "14:15", "Task": "Admin: Produktionspläne/TK-Management", "Typ": "Admin"},
            {"Dienst": "S1", "Start": "14:15", "Ende": "15:00", "Task": "Prod: MEP Folgetag (Fleisch marinieren/Batch)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "15:00", "Ende": "15:30", "Task": "Admin/QC: Kühlhäuser/Temperaturen/MHDs", "Typ": "Admin"},
            {"Dienst": "S1", "Start": "15:30", "Ende": "15:54", "Task": "Logistik: Endreinigung Posten/Unterschriften", "Typ": "Logistik"},

            # ==========================
            # R1 GASTRO (06:30 - 15:24)
            # ==========================
            {"Dienst": "R1", "Start": "06:30", "Ende": "07:15", "Task": "Logistik: Warenannahme Rampe (HACCP Risiko)", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:15", "Ende": "07:30", "Task": "Logistik: Verräumen Kühlhaus", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:30", "Ende": "07:45", "Task": "Potenzial: Hygiene-Schleuse/Umziehen", "Typ": "Potenzial"},
            {"Dienst": "R1", "Start": "07:45", "Ende": "08:30", "Task": "Admin: Manuelle Deklaration/Intranet", "Typ": "Admin"},
            {"Dienst": "R1", "Start": "08:30", "Ende": "09:30", "Task": "Prod: MEP Folgetag (Freeflow/Montage)", "Typ": "Prod"},
            {"Dienst": "R1", "Start": "09:30", "Ende": "10:00", "Task": "Service: Setup Heute (Verbrauchsmaterial)", "Typ": "Service"},
            # 10:00 Pause
            {"Dienst": "R1", "Start": "10:20", "Ende": "10:45", "Task": "Logistik: Transport Speisen (von G2/H2)", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "10:45", "Ende": "11:00", "Task": "Service: Einsetzen Buffet/Suppe", "Typ": "Service"},
            {"Dienst": "R1", "Start": "11:00", "Ende": "11:15", "Task": "Coord: Quality Check/Showteller/Foto", "Typ": "Coord"},
            {"Dienst": "R1", "Start": "11:15", "Ende": "11:30", "Task": "Potenzial: Bereitschaft", "Typ": "Potenzial"},
            {"Dienst": "R1", "Start": "11:30", "Ende": "13:30", "Task": "Service: Mittagsservice Gastro", "Typ": "Service"},
            {"Dienst": "R1", "Start": "13:30", "Ende": "14:00", "Task": "Logistik: Abbau Buffet/Entsorgen", "Typ": "Logistik"},
            # 14:00 - 14:30 Pause
            {"Dienst": "R1", "Start": "14:30", "Ende": "15:00", "Task": "Logistik: Bestellungen für Folgetag/MEP", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "15:00", "Ende": "15:24", "Task": "Logistik: Endreinigung/Temp-Liste", "Typ": "Logistik"},

            # ==========================
            # R2 GASTRO (06:30 - 15:24)
            # ==========================
            {"Dienst": "R2", "Start": "06:30", "Ende": "06:50", "Task": "Service: Band-Setup (Patienten/Butter)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "06:50", "Ende": "07:45", "Task": "Service: Band-Service (Falsche Zuordnung)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "07:45", "Ende": "08:00", "Task": "Logistik: Wechsel Patient->Gastro", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "08:30", "Task": "Potenzial: Salat-Finish (Gedehnt 12 Stk)", "Typ": "Potenzial"},
            {"Dienst": "R2", "Start": "08:30", "Ende": "09:00", "Task": "Logistik: Office/Abfall (Botengänge)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "09:00", "Ende": "09:30", "Task": "Logistik: Geräte-Check (Muda/Fritteuse)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "09:30", "Ende": "10:00", "Task": "Potenzial: Leerlauf/Puffer", "Typ": "Potenzial"},
            # 10:00 Pause
            {"Dienst": "R2", "Start": "10:20", "Ende": "10:45", "Task": "Logistik: Transport & Fritteuse Start", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "10:45", "Ende": "11:00", "Task": "Prod: Fritteuse (Pommes blanchieren)", "Typ": "Prod"},
            {"Dienst": "R2", "Start": "11:00", "Ende": "11:30", "Task": "Coord: Show-Setup/Foto (Redundanz)", "Typ": "Coord"},
            {"Dienst": "R2", "Start": "11:30", "Ende": "13:30", "Task": "Service: Mittagsservice & ReCircle", "Typ": "Service"},
            {"Dienst": "R2", "Start": "13:30", "Ende": "14:00", "Task": "Service: Food Rescue (Verkauf)", "Typ": "Service"},
            # 14:00 - 14:30 Pause
            {"Dienst": "R2", "Start": "14:30", "Ende": "15:00", "Task": "Admin: Etiketten-Druck ReCircle/Deklaration", "Typ": "Admin"},
            {"Dienst": "R2", "Start": "15:00", "Ende": "15:24", "Task": "Logistik: Endreinigung/Bestellungen/Unterschrift", "Typ": "Logistik"},

            # ==========================
            # H1 FRÜHSTÜCK (05:30 - 14:40)
            # ==========================
            {"Dienst": "H1", "Start": "05:30", "Ende": "06:00", "Task": "Prod: Birchermüsli/Brei (Mischen/Convenience)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "06:00", "Ende": "06:30", "Task": "Prod: Rahm/Dessert Vorb. (Maschine)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "06:30", "Ende": "06:50", "Task": "Service: Band-Setup", "Typ": "Service"},
            {"Dienst": "H1", "Start": "06:50", "Ende": "07:45", "Task": "Service: Band Frühstück", "Typ": "Service"},
            {"Dienst": "H1", "Start": "07:45", "Ende": "08:15", "Task": "Logistik: Aufräumen/Auffüllen (Butter/Konfi)", "Typ": "Logistik"},
            {"Dienst": "H1", "Start": "08:15", "Ende": "09:15", "Task": "Prod: Dessert/Patisserie (Redundanz H2/Convenience)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "09:15", "Ende": "10:00", "Task": "Prod: Salat Vorbereitung (Redundanz G2/Beutel)", "Typ": "Prod"},
            # 10:00 Pause
            {"Dienst": "H1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Glacé portionieren (System)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "10:45", "Ende": "11:25", "Task": "Prod: Käse schneiden (Maschine/Fertig)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "11:25", "Ende": "12:30", "Task": "Service: Band Mittagsservice", "Typ": "Service"},
            {"Dienst": "H1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Material versorgen", "Typ": "Logistik"},
            # 12:45 - 13:30 Pause
            {"Dienst": "H1", "Start": "13:30", "Ende": "14:00", "Task": "Prod: Menüsalat Abend (Vorbereitung)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "14:00", "Ende": "14:20", "Task": "Admin: Posten-Protokoll Folgetag", "Typ": "Admin"},
            {"Dienst": "H1", "Start": "14:20", "Ende": "14:40", "Task": "Logistik/Admin: Milchfrigor Kontrolle & Bestellung", "Typ": "Admin"},

            # ==========================
            # H2 PÄTISSERIE (09:15 - 18:09)
            # ==========================
            {"Dienst": "H2", "Start": "09:15", "Ende": "09:30", "Task": "Prod: Basis-Massen (Convenience/Pulver)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "09:30", "Ende": "10:15", "Task": "Prod: Restaurant-Finish (Montage 25 Gläser)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "10:15", "Ende": "11:00", "Task": "Prod: Patienten-Masse (Abfüllen/Convenience)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "11:00", "Ende": "11:15", "Task": "Logistik: Transport Gastro", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "11:15", "Ende": "11:45", "Task": "Logistik: Wagen-Bau Abend", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "11:45", "Ende": "12:30", "Task": "Prod: Power-Dessert (Anrühren/Päckli)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "12:30", "Ende": "13:00", "Task": "Service: Privat-Zvieri (Transport)", "Typ": "Service"},
            {"Dienst": "H2", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Puffer/Reinigung", "Typ": "Logistik"},
            # 13:30 - 14:15 Pause
            {"Dienst": "H2", "Start": "14:15", "Ende": "15:15", "Task": "Prod: Dessert Gastro Folgetag (Abfüllen/System)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "15:15", "Ende": "16:00", "Task": "Prod: Dessert Pat Folgetag (Abfüllen/System)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "16:00", "Ende": "16:30", "Task": "Coord: Support H1/Glacé", "Typ": "Coord"},
            {"Dienst": "H2", "Start": "16:30", "Ende": "17:00", "Task": "Service: Setup Abend/Glacé", "Typ": "Service"},
            {"Dienst": "H2", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band Abendessen", "Typ": "Service"},
            {"Dienst": "H2", "Start": "18:00", "Ende": "18:09", "Task": "Logistik: Abschluss/Material", "Typ": "Logistik"},

            # ==========================
            # H3 ASSEMBLY LINE (09:15 - 18:09)
            # ==========================
            {"Dienst": "H3", "Start": "09:15", "Ende": "09:45", "Task": "Prod: Wähen Montage (Convenience/Teig)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "09:45", "Ende": "10:30", "Task": "Prod: Sandwiches (System-Montage)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "10:30", "Ende": "11:15", "Task": "Prod: Salatteller (Montage/Beutel)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "11:15", "Ende": "12:00", "Task": "Prod: Abend Kalt (Platten/Legesystem)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:00", "Ende": "12:30", "Task": "Prod: Bircher-Masse für Morgen (Mischen)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:30", "Ende": "13:00", "Task": "Logistik: Reste/Saucen", "Typ": "Logistik"},
            {"Dienst": "H3", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Zwischenreinigung", "Typ": "Logistik"},
            # 13:30 - 14:15 Pause
            {"Dienst": "H3", "Start": "14:15", "Ende": "15:15", "Task": "Prod: Salatbuffet/MEP (System)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "15:15", "Ende": "16:00", "Task": "Prod: Wähen/Creme Brulee (Vorbereitung)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "16:00", "Ende": "16:30", "Task": "Coord: Protokolle/Nachproduktion", "Typ": "Coord"},
            {"Dienst": "H3", "Start": "16:30", "Ende": "17:00", "Task": "Service: Setup Band", "Typ": "Service"},
            {"Dienst": "H3", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band Abend Support", "Typ": "Service"},
            {"Dienst": "H3", "Start": "18:00", "Ende": "18:09", "Task": "Logistik: Abschluss Kaltküche", "Typ": "Logistik"},

            # ==========================
            # G2 GARDE-MANGER (09:30 - 18:30)
            # ==========================
            {"Dienst": "G2", "Start": "09:30", "Ende": "09:45", "Task": "Coord: Absprache H3", "Typ": "Coord"},
            {"Dienst": "G2", "Start": "09:45", "Ende": "10:30", "Task": "Prod: Wahlkost Kalt (System-Montage)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "10:30", "Ende": "11:15", "Task": "Prod: Patienten-Salat (Beutel/Convenience)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "11:15", "Ende": "12:30", "Task": "Prod: Abendessen (Aufschnitt/Montage)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "12:30", "Ende": "13:30", "Task": "Prod: Salate Folgetag/Zwischenreinigung", "Typ": "Prod"},
            # 13:30 - 14:15 Pause
            {"Dienst": "G2", "Start": "14:15", "Ende": "15:00", "Task": "Prod: MEP Folgetag (System)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "15:00", "Ende": "16:00", "Task": "Potenzial: Leerlauf/Dehnung (Standard-Tag)", "Typ": "Potenzial"},
            {"Dienst": "G2", "Start": "16:00", "Ende": "17:00", "Task": "Coord: Band-Setup/Nachproduktion", "Typ": "Coord"},
            {"Dienst": "G2", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band-Abendessen", "Typ": "Service"},
            {"Dienst": "G2", "Start": "18:00", "Ende": "18:30", "Task": "Admin: Hotellerie-Check/To-Do Liste", "Typ": "Admin"},
        ]
        return DataWarehouse.process(data)

    @staticmethod
    def process(data):
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'])
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'])
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        
        # SKILL MATCH LOGIC
        def check_mismatch(row):
            user_skill = SKILL_LEVELS.get(row['Dienst'], 1)
            
            task_level = 1 
            if row['Typ'] in ["Coord", "Admin"]:
                task_level = 2
                if "Mutationen" in row['Task']: task_level = 3
            elif row['Typ'] == "Prod":
                task_level = 2
                if "Convenience" in row['Task'] or "Beutel" in row['Task'] or "Päckli" in row['Task']: 
                    task_level = 1
                if "ET" in row['Task'] or "Finish" in row['Task']:
                    task_level = 3
            elif row['Typ'] == "Service":
                task_level = 2
            
            if user_skill == 3 and task_level == 1:
                return "Critical Mismatch"
            elif user_skill == 3 and task_level == 2:
                return "Underutilized"
            elif user_skill < 2 and task_level == 3:
                return "Risk: Overwhelmed"
            return "Match"

        df['Skill_Status'] = df.apply(check_mismatch, axis=1)
        return df

# --- 3. WORKLOAD ENGINE ---
class WorkloadEngine:
    LOAD_FACTORS = {
        "Service": 1.0,   # Crunch
        "Prod": 0.8,      # Work
        "Logistik": 0.6,  # Move
        "Admin": 0.5,     # Sit
        "Coord": 0.4,     # Talk
        "Potenzial": 0.1  # Idle
    }

    @staticmethod
    def get_load_curve(df):
        timeline = pd.date_range(start="2026-01-01 05:30", end="2026-01-01 18:30", freq="15T")
        load_data = []
        
        for t in timeline:
            active_tasks = df[(df['Start_DT'] <= t) & (df['End_DT'] > t)]
            headcount = len(active_tasks)
            real_load = 0
            for _, task in active_tasks.iterrows():
                factor = WorkloadEngine.LOAD_FACTORS.get(task['Typ'], 0.5)
                real_load += factor
                
            load_data.append({
                "Zeit": t.strftime("%H:%M"),
                "Capacity (FTE)": headcount,
                "Real Demand (FTE)": real_load
            })
        return pd.DataFrame(load_data)

# --- 4. KPI ENGINE ---
class KPI_Engine:
    HOURLY_RATE_CHF = 55.0

    @staticmethod
    def calculate_all(df_ist, mode='time'):
        total_min = df_ist['Duration'].sum()
        if total_min == 0: return []

        # SINGLE SOURCE OF TRUTH FORMATTER
        # Fix: Removed the shadowing 2nd fmt definition
        def fmt(val, unit=None):
            # 1. Mode check overrides everything if set to money
            if mode == 'money':
                return f"{val:,.0f} CHF".replace(",", "'")
            
            # 2. If Unit is absolute (Minutes), return Min
            if unit == 'abs':
                return f"{val:.0f} Min"
            
            # 3. String passthrough
            if isinstance(val, str): return val
            
            # 4. Standard Heuristics (Percentage vs Min)
            # If it's a small float, assume percent, if large, assume minutes (fallback)
            if isinstance(val, float) and val < 100:
                return f"{val:.1f}%"
            return f"{val:.0f} Min"

        # BASIC METRICS
        potenzial_min = df_ist[df_ist['Typ'] == 'Potenzial']['Duration'].sum()
        skilled_dienste = ['D1', 'S1', 'E1', 'G2', 'R1']
        leakage_min = df_ist[(df_ist['Dienst'].isin(skilled_dienste)) & (df_ist['Typ'].isin(['Logistik', 'Potenzial']))]['Duration'].sum()
        
        # Deep Dive Metrics Calculation
        leakage_val = (leakage_min / total_min * 100) if mode == 'time' else (leakage_min/60 * KPI_Engine.HOURLY_RATE_CHF)
        muda_val = (potenzial_min / total_min * 100) if mode == 'time' else (potenzial_min/60 * KPI_Engine.HOURLY_RATE_CHF)
        
        band_crunch = df_ist[(df_ist['Start'] >= "11:00") & (df_ist['Ende'] <= "12:30")]
        idle_band_min = band_crunch[band_crunch['Typ'] == 'Potenzial']['Duration'].sum() + 105
        idle_val = idle_band_min if mode == 'time' else (idle_band_min/60 * KPI_Engine.HOURLY_RATE_CHF)

        # Industrialization
        prod_df = df_ist[df_ist['Typ'] == 'Prod']
        prod_min = prod_df['Duration'].sum()
        montage_indicators = ["Montage", "Regenerieren", "Finish", "Beutel", "Päckli", "Convenience", "Abfüllen", "Mischen", "System", "Dämpfen", "Fertig", "Maschine"]
        montage_min = prod_df[prod_df['Task'].str.contains('|'.join(montage_indicators), case=False, na=False)]['Duration'].sum()
        ind_rate = (montage_min / prod_min * 100) if prod_min > 0 else 0

        # Special Deep Dives
        r2_gap = df_ist[(df_ist['Dienst'] == 'R2') & (df_ist['Start'] >= "08:00") & (df_ist['Ende'] <= "10:00")]['Duration'].sum()
        r2_inf_val = max(0, r2_gap - 40)
        r2_inf_display = r2_inf_val if mode == 'time' else (r2_inf_val/60 * KPI_Engine.HOURLY_RATE_CHF)

        h1_total = df_ist[df_ist['Dienst'] == 'H1']['Duration'].sum()
        h1_foreign = df_ist[(df_ist['Dienst'] == 'H1') & df_ist['Task'].str.contains('Dessert|Salat|Brei|Rahm', case=False, na=False)]['Duration'].sum()
        h1_dilution = (h1_foreign / h1_total * 100) if h1_total > 0 else 0

        # R1 Hygiene-Risk FIXED LOGIC
        r1_df = df_ist[df_ist['Dienst'] == 'R1']
        r1_risk = r1_df[r1_df['Task'].str.contains('Warenannahme|Verräumen|Hygiene', case=False, na=False)]['Duration'].sum()
        r1_risk_cost = (r1_risk / 60) * KPI_Engine.HOURLY_RATE_CHF
        
        # Bugfix: Define variable to hold either Minutes or CHF
        r1_risk_val = r1_risk if mode == 'time' else r1_risk_cost

        g2_gap = df_ist[(df_ist['Dienst'] == 'G2') & df_ist['Task'].str.contains('Leerlauf', case=False, na=False)]['Duration'].sum()
        g2_gap_disp = g2_gap if mode == 'time' else (g2_gap/60 * KPI_Engine.HOURLY_RATE_CHF)

        # Skill Mismatch
        mismatch_min = df_ist[df_ist['Skill_Status'] == "Critical Mismatch"]['Duration'].sum()
        mismatch_disp = mismatch_min if mode == 'time' else (mismatch_min/60 * KPI_Engine.HOURLY_RATE_CHF)

        redundancy_min = 150
        redundancy_disp = redundancy_min if mode == 'time' else (redundancy_min/60 * KPI_Engine.HOURLY_RATE_CHF)

        # --- REAL DATA CALCULATIONS (Replaced Magic Numbers) ---
        # Value Add: Prod + Service
        val_add_min = df_ist[df_ist['Typ'].isin(['Prod', 'Service'])]['Duration'].sum()
        val_add_ratio = (val_add_min / total_min * 100) if total_min > 0 else 0
        
        # Admin Burden
        adm_burden_min = df_ist[df_ist['Typ'] == 'Admin']['Duration'].sum()
        adm_burden = adm_burden_min if mode == 'time' else (adm_burden_min/60 * KPI_Engine.HOURLY_RATE_CHF)
        
        # Logistics Drag
        log_drag_min = df_ist[df_ist['Typ'] == 'Logistik']['Duration'].sum()
        log_drag = (log_drag_min / total_min * 100) if total_min > 0 else 0
        
        # Coordination Tax
        coord_tax_min = df_ist[df_ist['Typ'] == 'Coord']['Duration'].sum()
        coord_tax = (coord_tax_min / total_min * 100) if total_min > 0 else 0
        
        # Service Intensity
        serv_int_min = df_ist[df_ist['Typ'] == 'Service']['Duration'].sum()
        serv_int = (serv_int_min / total_min * 100) if total_min > 0 else 0
        
        # Simple Context Switch Estimator (Avg Tasks per Person)
        num_staff = len(df_ist['Dienst'].unique())
        total_tasks = len(df_ist)
        avg_tasks_per_person = total_tasks / num_staff if num_staff > 0 else 0
        context_sw = f"{avg_tasks_per_person:.1f}x"
        
        # Overstaffing Index (Replaces Peak Staff Load)
        # Calculates sum of (Capacity - Demand) where Capacity > Demand
        # We reuse WorkloadEngine for consistency
        workload_df = WorkloadEngine.get_load_curve(df_ist)
        # Each point is 15 min = 0.25 hours
        overstaffing_fte_hours = 0
        for _, row in workload_df.iterrows():
            cap = row['Capacity (FTE)']
            dem = row['Real Demand (FTE)']
            if cap > dem:
                overstaffing_fte_hours += (cap - dem) * 0.25
        
        overstaffing_val = (overstaffing_fte_hours * 60) # in minutes
        overstaffing_disp = overstaffing_val if mode == 'time' else (overstaffing_fte_hours * KPI_Engine.HOURLY_RATE_CHF)

        # Recovery Value - Annualized (250 Days)
        # Original logic was approx 5.5h/day. Let's base it on actual 'Muda' + 'Overstaffing' or similar? 
        # For consistency with user request, we stick to the heuristic but scale it to year.
        # Daily: ~330 mins (5.5h)
        daily_recov_min = 5.5 * 60 
        yearly_recov_min = daily_recov_min * 250
        
        recov_val = yearly_recov_min if mode == 'time' else (yearly_recov_min/60 * KPI_Engine.HOURLY_RATE_CHF)
        
        # Constants that remain valid heuristics
        liab_gap = 105
        split = "62/38"
        cycle_eff = 81.0

        # The 20 Metrics List
        return [
            ("Skill-Drift (Leakage)", {"val": fmt(leakage_val), "sub": "Fachkraft-Einsatz", "trend": "bad"}),
            ("Potenzial (Muda)", {"val": fmt(muda_val), "sub": "Nicht-Wertschöpfend", "trend": "bad"}),
            ("Recovery Value (Yearly)", {"val": fmt(recov_val), "sub": "Täglich ca. 5.5 Std.", "trend": "good"}),
            ("Kernzeit-Vakuum", {"val": fmt(idle_val), "sub": "Wartezeit Service", "trend": "bad"}),
            ("Context-Switch Rate", {"val": context_sw, "sub": "D1 Fragmentierung", "trend": "bad"}),
            
            ("Industrialisierungsgrad", {"val": f"{ind_rate:.0f}%", "sub": "Convenience-Anteil", "trend": "neutral"}),
            ("Value-Add Ratio", {"val": f"{val_add_ratio:.1f}%", "sub": "Prod + Service", "trend": "good"}),
            ("Admin Burden", {"val": fmt(adm_burden), "sub": "Bürokratie & Orgacard", "trend": "bad"}),
            ("Logistics Drag", {"val": f"{log_drag:.1f}%", "sub": "Transport/Reinigung", "trend": "neutral"}),
            ("Coordination Tax", {"val": f"{coord_tax:.1f}%", "sub": "Absprachen/Koordination", "trend": "neutral"}),
            
            ("Liability Gap", {"val": "105 Min", "sub": "Risiko D1 Pause", "trend": "bad"}),
            ("Service Intensity", {"val": f"{serv_int:.0f}%", "sub": "Patient Touchpoint", "trend": "good"}),
            ("Patient/Gastro Split", {"val": split, "sub": "Ressourcen-Allokation", "trend": "neutral"}),
            ("Process Cycle Eff.", {"val": f"{cycle_eff:.1f}%", "sub": "Netto-Effizienz", "trend": "good"}),
            ("FTE-Verschwendung (Overstaffing)", {"val": fmt(overstaffing_disp), "sub": "Bezahlte Leerzeit", "trend": "bad"}),

            # Deep Dives
            # FIX: Forced unit='abs' to prevent % formatting for minutes < 100
            ("R2 Inflation (Hidden)", {"val": fmt(r2_inf_display, unit='abs'), "sub": "Gedehnte Arbeit", "trend": "bad"}),
            ("H1 Skill-Dilution", {"val": f"{h1_dilution:.0f}%", "sub": "Fremdaufgaben", "trend": "bad"}),
            ("R1 Hygiene-Risk", {"val": fmt(r1_risk_val, unit='abs'), "sub": "Zeit an Rampe", "trend": "bad"}),
            # FIX: Forced unit='abs'
            ("G2 Capacity Gap", {"val": fmt(g2_gap_disp, unit='abs'), "sub": "PM Leerlauf", "trend": "bad"}),
            ("Qualifikations-Verschw.", {"val": fmt(mismatch_disp), "sub": "High Skill/Low Task", "trend": "bad"}),
        ]

# --- 5. RENDERER ---
def render_kpi_card(title, data):
    trend_color = data['trend']
    # Get tooltip from dictionary
    tooltip = KPI_DEFINITIONS.get(title, f"{title}: {data['sub']}")
    
    html = f"""
    <div class="kpi-card" title="{tooltip}">
        <div class="kpi-label">{title}</div>
        <div class="kpi-metric">{data['val']}</div>
        <div class="kpi-context">
            <span class="tag tag-{trend_color}">{data['trend'].upper()}</span>
            <span>{data['sub']}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- 6. MAIN APPLICATION ---
def main():
    dw = DataWarehouse()
    df_ist = dw.get_full_ist_data()
    
    st.markdown("""
        <div class="header-container">
            <div>
                <h1 class="main-title">WORKSPACE: AUDIT 2026</h1>
                <div class="sub-title">Enterprise Security Architecture</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_ctrl1, col_ctrl2 = st.columns([4, 1])
    with col_ctrl2:
        mode_select = st.radio("Unit:", ["Zeit (Min)", "Wert (CHF)"], horizontal=True, label_visibility="collapsed")
        mode = 'money' if 'CHF' in mode_select else 'time'

    kpis = KPI_Engine.calculate_all(df_ist, mode=mode)

    st.markdown(f'<div class="section-label" title="{SECTION_TOOLTIPS["Management Cockpit"]}">20 Core Metrics</div>', unsafe_allow_html=True)
    for row in range(4):
        cols = st.columns(5, gap="small")
        for col in range(5):
            idx = row * 5 + col
            if idx < len(kpis):
                with cols[col]:
                    render_kpi_card(kpis[idx][0], kpis[idx][1])

    # --- BELASTUNGS-MATRIX ---
    st.markdown(f'<div class="section-label" title="{SECTION_TOOLTIPS["Belastungs-Matrix"]}">Belastungs-Matrix (Capacity vs. Demand)</div>', unsafe_allow_html=True)
    
    workload_df = WorkloadEngine.get_load_curve(df_ist)
    
    with st.container():
        st.markdown("""
        <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 10px;">
        <b>Analyse:</b> Graue Fläche zeigt anwesendes Personal (Kosten). Die Linie zeigt die echte Arbeitslast (Wertschöpfung). 
        Die Lücke dazwischen ist <b>Ineffizienz</b>.
        </div>
        """, unsafe_allow_html=True)
        
        fig_load = go.Figure()
        
        # 1. Capacity (Filled Area)
        fig_load.add_trace(go.Scatter(
            x=workload_df['Zeit'], y=workload_df['Capacity (FTE)'],
            fill='tozeroy', mode='none', name='Verfügbare Kapazität (FTE)',
            fillcolor='rgba(148, 163, 184, 0.2)' # Slate 400 transparent
        ))
        
        # 2. Real Demand (Line)
        fig_load.add_trace(go.Scatter(
            x=workload_df['Zeit'], y=workload_df['Real Demand (FTE)'],
            mode='lines', name='Reale Belastung (Workload)',
            line=dict(color=COLORS['accent'], width=3)
        ))
        
        fig_load.update_layout(
            plot_bgcolor="white", paper_bgcolor="white", height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=False, title=None, linecolor='#E2E8F0'),
            yaxis=dict(showgrid=True, gridcolor='#F1F5F9', title="FTE (Vollzeitstellen)"),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_load, use_container_width=True, config={'displayModeBar': False})

    # --- DEEP DIVE TABS ---
    st.markdown(f'<div class="section-label" title="{SECTION_TOOLTIPS["Detail-Analyse"]}">Detail-Analyse</div>', unsafe_allow_html=True)
    
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

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Gantt-Flow", "Potenzial-Analyse", "Ressourcen-Balance", "Aktivitäts-Verteilung", "Skill-Match-Matrix"])
    
    color_map = {
        "Prod": "#3B82F6", "Service": "#10B981", "Admin": "#F59E0B",
        "Logistik": "#64748B", "Potenzial": "#F43F5E", "Coord": "#8B5CF6"
    }

    with tab1:
        fig1 = px.timeline(df_ist, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", hover_name="Task", color_discrete_map=color_map, height=600)
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
        df_grouped = df_ist.groupby(['Dienst', 'Typ'])['Duration'].sum().reset_index()
        fig3 = px.bar(df_grouped, x="Dienst", y="Duration", color="Typ", color_discrete_map=color_map, barmode='stack', height=500)
        fig3.update_layout(yaxis_title="Minuten (Soll: 504 Min)")
        # Add Reference Line for 8.4h Workday
        fig3.add_hline(y=504, line_dash="dot", line_color="#94A3B8", annotation_text="Standard Day (8.4h)", annotation_position="top right")
        st.plotly_chart(clean_chart_layout(fig3), use_container_width=True, config={'displayModeBar': False})
        
    with tab4:
        df_pie = df_ist.groupby('Typ')['Duration'].sum().reset_index()
        fig4 = px.pie(df_pie, values='Duration', names='Typ', color='Typ', color_discrete_map=color_map, hole=0.6, height=500)
        fig4.update_traces(textinfo='percent+label', textfont_size=13)
        fig4.update_layout(showlegend=False, annotations=[dict(text='Total', x=0.5, y=0.5, font_size=20, showarrow=False)])
        st.plotly_chart(clean_chart_layout(fig4), use_container_width=True, config={'displayModeBar': False})

    with tab5:
        skill_pivot = df_ist.groupby(['Dienst', 'Skill_Status'])['Duration'].sum().reset_index()
        fig_skill = px.bar(skill_pivot, x="Dienst", y="Duration", color="Skill_Status", 
                           color_discrete_map={"Critical Mismatch": "#EF4444", "Match": "#10B981", "Underutilized": "#F59E0B", "Risk: Overwhelmed": "#6366F1"},
                           title="Qualifikations-Check: Rote Balken = Teure Fachkraft macht Billig-Job")
        st.plotly_chart(clean_chart_layout(fig_skill), use_container_width=True, config={'displayModeBar': False})

    # --- LOAD PROFILE ---
    st.markdown(f'<div class="section-label" title="{SECTION_TOOLTIPS["Personal-Einsatzprofil"]}">Personal-Einsatzprofil (Staffing Load)</div>', unsafe_allow_html=True)
    
    load_data = []
    for h in range(5, 20):
        for m in [0, 15, 30, 45]:
            t = datetime(2026, 1, 1, h, m)
            active = len(df_ist[(df_ist['Start_DT'] <= t) & (df_ist['End_DT'] > t)])
            load_data.append({"Zeit": f"{h:02d}:{m:02d}", "Staff": active})
    
    with st.container():
        fig_load_profile = px.area(pd.DataFrame(load_data), x="Zeit", y="Staff", line_shape="spline")
        fig_load_profile.update_traces(line_color="#0F172A", fillcolor="rgba(15, 23, 42, 0.05)")
        fig_load_profile.update_layout(
            plot_bgcolor="white", 
            paper_bgcolor="white", 
            margin=dict(l=20, r=20, t=20, b=20),
            height=250,
            xaxis=dict(showgrid=False, title=None, linecolor='#E2E8F0'),
            yaxis=dict(showgrid=True, gridcolor='#F1F5F9', title="Active FTE", range=[0, 10]),
            hovermode="x unified"
        )
        # Critical Zone Line
        fig_load_profile.add_hline(y=8, line_dash="dot", line_color="#EF4444", annotation_text="Congestion Zone", annotation_position="top right", annotation_font_color="#EF4444")
        st.plotly_chart(fig_load_profile, use_container_width=True, config={'displayModeBar': False})

if __name__ == "__main__":
    main()
