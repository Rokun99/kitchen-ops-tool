import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & HIGH END STYLING ---
st.set_page_config(
    page_title="WORKSPACE: TOTAL OPERATIONS",
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
    "border": "#E2E8F0",    # Slate 200
    # Sector Colors
    "kitchen": "#3B82F6",   # Blue
    "gastro": "#64748B"     # Slate
}

# DEFINITIONS & CONTEXT (Tooltip Lexicon)
KPI_DEFINITIONS = {
    # --- KITCHEN (ORIGINAL) ---
    "Skill-Drift (Leakage)": "Anteil der Arbeitszeit, in der Fachkräfte qualifikationsfremde Routinetätigkeiten ausführen.",
    "Potenzial (Muda)": "Nicht-wertschöpfende Zeit durch Warten, unnötige Wege oder Prozess-Leerlauf.",
    "Recovery Value (Yearly)": "Extrapoliertes Einsparpotenzial pro Jahr (Basis 250 Tage) durch Eliminierung von Muda.",
    "FTE-Verschwendung (Overstaffing)": "Täglich summierte Stunden, in denen die Personalkapazität die tatsächliche Arbeitslast übersteigt.",
    "Kernzeit-Vakuum": "Summierte unproduktive Wartezeit während der kritischen Service-Phasen.",
    "Context-Switch Rate": "Durchschnittliche Anzahl der Aufgabenwechsel pro Mitarbeiter/Schicht.",
    "Industrialisierungsgrad": "Anteil von High-Convenience-Komponenten im Verhältnis zur Eigenfertigung.",
    "Value-Add Ratio": "Anteil der Netto-Arbeitszeit, die direkt in wertschöpfende Tätigkeiten fließt.",
    "Admin Burden": "Zeitaufwand für administrative Prozesse, Dokumentation und Systempflege.",
    "Logistics Drag": "Prozentualer Zeitverlust durch interne Transporte und Rüstwege.",
    "Coordination Tax": "Zeitaufwand für Absprachen, Meetings und Übergaben.",
    "Liability Gap": "Operative Risikofenster ohne klare Verantwortlichkeit.",
    "Service Intensity": "Anteil der Arbeitszeit mit direktem Gastkontakt oder aktiver Ausgabe.",
    "Patient/Gastro Split": "Verhältnis der Ressourcenbindung zwischen Patientenverpflegung und Restaurant.",
    "Process Cycle Eff.": "Verhältnis von reiner Bearbeitungszeit zur gesamten Durchlaufzeit.",
    "Peak Staff Load": "Maximale Anzahl Mitarbeiter, die gleichzeitig operieren.",
    "R2 Inflation (Hidden)": "Arbeitszeitdehnung im Dienst R2 mangels Auslastung.",
    "H1 Skill-Dilution": "Verwässerung des Rollenprofils H1 durch fachfremde Aufgaben.",
    "R1 Hygiene-Risk": "Dauer der Wechsel zwischen unreinen und reinen Bereichen.",
    "G2 Capacity Gap": "Explizite, ungenutzte Personalkapazität im Dienst G2.",
    "Qualifikations-Verschw.": "Einsatz von High-Skill-Personal für Low-Skill-Tasks.",

    # --- GASTRO / STEWARDING (NEW) ---
    "Transport Intensity": "Anteil der Arbeitszeit für Holen/Bring-Dienste (Wagen/Logistik).",
    "Elevator Dependency": "Zeitrisiko durch Aufzugwartezeiten (Geschätzt aus Transportwegen).",
    "Return-Flow Velocity": "Zeitdauer von 'Station holt ab' bis 'Teller in Spülmaschine'.",
    "Trolley Turnover": "Umschlaghäufigkeit der Speisewagen pro Tag.",
    "Logistics Dead-Time": "Leere Wege (ohne Wagen) oder Warten auf Transport.",
    "Band-Machine Uptime": "Laufzeit der Hauptwaschstrasse (K6/K8 Input).",
    "Granuldisk Load": "Auslastung der Topfspüle (K15) – Indikator für Produktionsvolumen.",
    "Chemical Efficiency": "Verbrauch Reinigungsmittel pro Spülgang (Simuliert basierend auf Spülzeit).",
    "Rack-Rate": "Körbe pro Stunde (Durchsatz-Indikator).",
    "Tech-Maintenance Ratio": "Zeitaufwand für Reinigung/Wartung der Maschinen (nicht Spülen).",
    "Hygiene Compliance (11:20)": "Einhaltung des kritischen Wechselslots vor Service.",
    "Bio-Trans Volume": "Menge entsorgter Reste (Food Waste Indikator).",
    "Clean-Side Integrity": "Personaldichte auf der 'Reinen Seite' (Vermeidung Rekontamination).",
    "Deep-Clean Index": "Zeitinvest in Grundreinigungen (Wände, Böden, Kühlhäuser).",
    "HACCP Admin": "Zeitaufwand für Dokumentation und Listenführung.",
    "Service Support Factor": "Entlastung der Küche beim Anrichten (K2, K8 etc.).",
    "Ergonomic Stress Score": "Anteil schwerer körperlicher Arbeit (Heben/Ziehen/Spülen).",
    "Shift-Handover Quality": "Zeit für Übergaben (Früh -> Spät).",
    "Solo-Risk Hours": "Stunden, in denen Mitarbeiter allein in kritischen Zonen sind.",
    "Flex-Capacity": "Anteil der Aufgaben, die bei Leerlauf vorgezogen werden können.",

    # --- TOTAL OPERATIONS (NEW) ---
    "Cost per Tray": "Gesamtkosten (Personal) geteilt durch Mahlzeiten.",
    "Labor Cost Split": "Verhältnis Küche (Teuer) vs. Gastrodienste (Günstiger).",
    "Overall Productivity": "Mahlzeiten pro FTE-Stunde (Gesamt).",
    "Non-Value-Add Cost": "Kosten für Muda (Warten/Weg) in CHF (Total).",
    "Overtime Risk": "Potenzial für Überstunden durch Prozess-Staus.",
    "Production-Logistics Gap": "Zeitversatz zwischen 'Kochen fertig' und 'Spülen fertig'.",
    "Service Readiness": "Bereitschaftsgrad Besteck/Geschirr bei Servicebeginn.",
    "Mise-en-Place Sync": "Ineinandergreifen von Vorbereitung (Küche) und Bereitstellung (Gastro).",
    "Peak Staff Load (Total)": "Maximale gleichzeitige Mitarbeiteranzahl im Haus.",
    "Communication Tax": "Summe der Absprachezeiten über alle Abteilungen.",
    "Infrastructure Stress": "Gleichzeitige Nutzung energieintensiver Geräte.",
    "Space Utilization": "Dichte der Belegung in der Küche/Spüle zu Stosszeiten.",
    "Waste-to-Value Ratio": "Verhältnis Food Waste zu produziertem Essen.",
    "Equipment ROI Index": "Nutzung der teuren Maschinen.",
    "Utilities Proxy": "Geschätzter Wasser/Stromverbrauch.",
    "System Resilience": "Pufferzeiten im Gesamtsystem.",
    "Hygiene Risk Total": "Summe aller kritischen Hygiene-Momente.",
    "Patient Touchpoints": "Anzahl der Interaktionen mit Patienteneinfluss.",
    "Process Standardization": "% der Aufgaben, die klar definiert sind.",
    "Management Span": "Verhältnis Führungskräfte zu operativen Stunden."
}

SECTION_TOOLTIPS = {
    "Management Cockpit": "Strategische Übersicht der wichtigsten Leistungskennzahlen.",
    "Belastungs-Matrix": "Vergleich der vorhandenen Personalkapazität (grau) mit der tatsächlich benötigten Arbeitslast (Linie).",
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
    
    .header-container {{
        padding-bottom: 1.5rem; margin-bottom: 2rem; border-bottom: 1px solid {COLORS['border']};
        display: flex; justify-content: space-between; align-items: center;
    }}
    .main-title {{ font-size: 1.8rem; font-weight: 700; letter-spacing: -0.025em; color: {COLORS['text_main']}; margin: 0; }}
    .sub-title {{ font-size: 0.9rem; color: {COLORS['text_sub']}; font-weight: 400; margin-top: 0.25rem; }}

    .section-label {{
        font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;
        color: {COLORS['text_sub']}; margin-top: 2.5rem; margin-bottom: 1rem;
        display: flex; align-items: center; gap: 0.5rem; cursor: help;
    }}
    .section-label::before {{ content: ''; display: block; width: 4px; height: 16px; background-color: {COLORS['accent']}; border-radius: 2px; }}
    
    .kpi-card {{
        background-color: {COLORS['card']}; border: 1px solid {COLORS['border']}; border-radius: 8px;
        padding: 1.25rem; height: 100%; min-height: 110px; transition: all 0.2s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); display: flex; flex-direction: column; justify-content: space-between;
        cursor: help; position: relative;
    }}
    .kpi-card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border-color: {COLORS['accent']}; }}

    .kpi-label {{ font-size: 0.75rem; font-weight: 600; color: {COLORS['text_sub']}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .kpi-metric {{ font-size: 1.6rem; font-weight: 700; color: {COLORS['text_main']}; letter-spacing: -0.05em; line-height: 1.1; }}
    .kpi-context {{ font-size: 0.75rem; color: {COLORS['neutral']}; margin-top: 0.5rem; font-weight: 500; display: flex; align-items: center; gap: 0.375rem; }}

    .tag {{ padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; }}
    .tag-bad {{ background: #FEF2F2; color: {COLORS['danger']}; }}
    .tag-good {{ background: #ECFDF5; color: {COLORS['success']}; }}
    .tag-neutral {{ background: #F1F5F9; color: {COLORS['text_sub']}; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 2rem; border-bottom: 1px solid {COLORS['border']}; padding-bottom: 0px; }}
    .stTabs [data-baseweb="tab"] {{ background-color: transparent !important; border: none !important; padding: 0.75rem 0 !important; font-weight: 500; color: {COLORS['text_sub']}; }}
    .stTabs [aria-selected="true"] {{ color: {COLORS['accent']} !important; border-bottom: 2px solid {COLORS['accent']} !important; }}
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
SKILL_LEVELS = {
    # Kitchen
    "D1": 3, "S1": 3, "E1": 3, "G2": 2, "H2": 2, "R1": 2, "H1": 2, "H3": 1, "R2": 1,
    # Gastro
    "K1": 1, "K2": 1, "K5": 1, "K6": 1, "K7": 1, "K8": 2, "K10": 1, "K11": 2, "K13": 2, "K14": 1, "K15": 1
}

class DataWarehouse:
    @staticmethod
    def get_kitchen_data():
        # --- ORIGINAL KITCHEN DATA (UNTOUCHED) ---
        data = [
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Admin: E-Mails/Mutationen/Diätpläne", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:25", "Ende": "08:30", "Task": "Hygiene/Rüsten: Wechsel Büro-Küche", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "08:30", "Ende": "09:15", "Task": "Prod: Suppen (Basis/Convenience 520 Port.)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:15", "Ende": "09:45", "Task": "Prod: ET (System-Ableitung/Allergene)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Admin: 2. Mail-Check (Spätmeldungen)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Cg-Komp. (High-Convenience)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "10:45", "Ende": "11:00", "Task": "Coord: Instruktion Band-MA/Spezialessen", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Admin: Letzte Orgacard-Updates", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service: Diät-Band (System-Ausgabe)", "Typ": "Service"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik: Abräumen/Kühlen/Rückstellproben", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:00", "Task": "Admin: Produktionsprotokolle Folgetag", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "15:00", "Ende": "15:50", "Task": "Prod: MEP Folgetag (Vegi-Komponenten/Fertig)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "15:50", "Ende": "16:30", "Task": "Prod: Abend Diät-Komp. (Regenerieren/Garen)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "16:30", "Ende": "17:00", "Task": "Coord: Tablettkarten/Service-Setup", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "17:00", "Ende": "18:05", "Task": "Service: Band-Abendessen", "Typ": "Service"},
            {"Dienst": "D1", "Start": "18:05", "Ende": "18:09", "Task": "Logistik: Aufräumen/To-Do Liste", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "07:00", "Ende": "07:15", "Task": "Coord: Posten einrichten", "Typ": "Coord"},
            {"Dienst": "E1", "Start": "07:15", "Ende": "08:30", "Task": "Prod: Stärke (Dämpfen/Convenience 520 Pax)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "08:30", "Ende": "09:30", "Task": "Prod: Gemüse (Dämpfen/Regenerieren 520 Pax)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "09:30", "Ende": "09:45", "Task": "Prod: Suppe Finalisieren (Basis)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "09:45", "Ende": "10:00", "Task": "Logistik: Bereitstellung Gastro", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Wahlkost Spezial (System/Minute)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "10:45", "Ende": "11:20", "Task": "Prod: Regenerieren Band (High-Convenience)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Potenzial: 70-Min-Falle (Bereitschaft/Warten)", "Typ": "Potenzial"},
            {"Dienst": "E1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Transport Reste Restaurant", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "12:45", "Ende": "13:00", "Task": "Logistik: Reinigung Clean-as-you-go", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "13:30", "Ende": "14:00", "Task": "Prod: Wahlkost MEP Abend/Morgen (Vorbereitung)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "14:00", "Ende": "15:00", "Task": "Prod: MEP Folgetag (Großmenge/Schnittware)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "15:00", "Ende": "15:30", "Task": "Admin/QC: Kühlhäuser/MHDs/Ordnung", "Typ": "Admin"},
            {"Dienst": "E1", "Start": "15:30", "Ende": "15:54", "Task": "Logistik: Endreinigung Posten/Unterschriften", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "07:00", "Ende": "07:30", "Task": "Prod: Saucen/Basis (Päckli/Convenience)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "07:30", "Ende": "08:30", "Task": "Prod: Fleisch Finish (Kurzbraten/System)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "08:30", "Ende": "09:30", "Task": "Coord: Support E1 (Pufferzeit)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "09:30", "Ende": "10:00", "Task": "Prod: Wahlkost Finish (Montage)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Fleisch/Sauce/Wärmewägen", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "10:45", "Ende": "11:00", "Task": "Logistik: Wagenübergabe Gastro", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "11:00", "Ende": "11:20", "Task": "Prod: Wahlkost Setup (Montage)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Potenzial: Wahlkost-Idle (Warten auf Bons)", "Typ": "Potenzial"},
            {"Dienst": "S1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Nachschub Restaurant", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "12:45", "Ende": "13:00", "Task": "Logistik: Reinigung Kipper", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "13:30", "Ende": "14:15", "Task": "Admin: Produktionspläne/TK-Management", "Typ": "Admin"},
            {"Dienst": "S1", "Start": "14:15", "Ende": "15:00", "Task": "Prod: MEP Folgetag (Fleisch marinieren/Batch)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "15:00", "Ende": "15:30", "Task": "Admin/QC: Kühlhäuser/Temperaturen/MHDs", "Typ": "Admin"},
            {"Dienst": "S1", "Start": "15:30", "Ende": "15:54", "Task": "Logistik: Endreinigung Posten/Unterschriften", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "06:30", "Ende": "07:15", "Task": "Logistik: Warenannahme Rampe (HACCP Risiko)", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:15", "Ende": "07:30", "Task": "Logistik: Verräumen Kühlhaus", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:30", "Ende": "07:45", "Task": "Potenzial: Hygiene-Schleuse/Umziehen", "Typ": "Potenzial"},
            {"Dienst": "R1", "Start": "07:45", "Ende": "08:30", "Task": "Admin: Manuelle Deklaration/Intranet", "Typ": "Admin"},
            {"Dienst": "R1", "Start": "08:30", "Ende": "09:30", "Task": "Prod: MEP Folgetag (Freeflow/Montage)", "Typ": "Prod"},
            {"Dienst": "R1", "Start": "09:30", "Ende": "10:00", "Task": "Service: Setup Heute (Verbrauchsmaterial)", "Typ": "Service"},
            {"Dienst": "R1", "Start": "10:20", "Ende": "10:45", "Task": "Logistik: Transport Speisen (von G2/H2)", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "10:45", "Ende": "11:00", "Task": "Service: Einsetzen Buffet/Suppe", "Typ": "Service"},
            {"Dienst": "R1", "Start": "11:00", "Ende": "11:15", "Task": "Coord: Quality Check/Showteller/Foto", "Typ": "Coord"},
            {"Dienst": "R1", "Start": "11:15", "Ende": "11:30", "Task": "Potenzial: Bereitschaft", "Typ": "Potenzial"},
            {"Dienst": "R1", "Start": "11:30", "Ende": "13:30", "Task": "Service: Mittagsservice Gastro", "Typ": "Service"},
            {"Dienst": "R1", "Start": "13:30", "Ende": "14:00", "Task": "Logistik: Abbau Buffet/Entsorgen", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "14:30", "Ende": "15:00", "Task": "Logistik: Bestellungen für Folgetag/MEP", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "15:00", "Ende": "15:24", "Task": "Logistik: Endreinigung/Temp-Liste", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "06:30", "Ende": "06:50", "Task": "Service: Band-Setup (Patienten/Butter)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "06:50", "Ende": "07:45", "Task": "Service: Band-Service (Falsche Zuordnung)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "07:45", "Ende": "08:00", "Task": "Logistik: Wechsel Patient->Gastro", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "08:30", "Task": "Potenzial: Salat-Finish (Gedehnt 12 Stk)", "Typ": "Potenzial"},
            {"Dienst": "R2", "Start": "08:30", "Ende": "09:00", "Task": "Logistik: Office/Abfall (Botengänge)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "09:00", "Ende": "09:30", "Task": "Logistik: Geräte-Check (Muda/Fritteuse)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "09:30", "Ende": "10:00", "Task": "Potenzial: Leerlauf/Puffer", "Typ": "Potenzial"},
            {"Dienst": "R2", "Start": "10:20", "Ende": "10:45", "Task": "Logistik: Transport & Fritteuse Start", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "10:45", "Ende": "11:00", "Task": "Prod: Fritteuse (Pommes blanchieren)", "Typ": "Prod"},
            {"Dienst": "R2", "Start": "11:00", "Ende": "11:30", "Task": "Coord: Show-Setup/Foto (Redundanz)", "Typ": "Coord"},
            {"Dienst": "R2", "Start": "11:30", "Ende": "13:30", "Task": "Service: Mittagsservice & ReCircle", "Typ": "Service"},
            {"Dienst": "R2", "Start": "13:30", "Ende": "14:00", "Task": "Service: Food Rescue (Verkauf)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "14:30", "Ende": "15:00", "Task": "Admin: Etiketten-Druck ReCircle/Deklaration", "Typ": "Admin"},
            {"Dienst": "R2", "Start": "15:00", "Ende": "15:24", "Task": "Logistik: Endreinigung/Bestellungen/Unterschrift", "Typ": "Logistik"},
            {"Dienst": "H1", "Start": "05:30", "Ende": "06:00", "Task": "Prod: Birchermüsli/Brei (Mischen/Convenience)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "06:00", "Ende": "06:30", "Task": "Prod: Rahm/Dessert Vorb. (Maschine)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "06:30", "Ende": "06:50", "Task": "Service: Band-Setup", "Typ": "Service"},
            {"Dienst": "H1", "Start": "06:50", "Ende": "07:45", "Task": "Service: Band Frühstück", "Typ": "Service"},
            {"Dienst": "H1", "Start": "07:45", "Ende": "08:15", "Task": "Logistik: Aufräumen/Auffüllen (Butter/Konfi)", "Typ": "Logistik"},
            {"Dienst": "H1", "Start": "08:15", "Ende": "09:15", "Task": "Prod: Dessert/Patisserie (Redundanz H2/Convenience)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "09:15", "Ende": "10:00", "Task": "Prod: Salat Vorbereitung (Redundanz G2/Beutel)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Glacé portionieren (System)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "10:45", "Ende": "11:25", "Task": "Prod: Käse schneiden (Maschine/Fertig)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "11:25", "Ende": "12:30", "Task": "Service: Band Mittagsservice", "Typ": "Service"},
            {"Dienst": "H1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Material versorgen", "Typ": "Logistik"},
            {"Dienst": "H1", "Start": "13:30", "Ende": "14:00", "Task": "Prod: Menüsalat Abend (Vorbereitung)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "14:00", "Ende": "14:20", "Task": "Admin: Posten-Protokoll Folgetag", "Typ": "Admin"},
            {"Dienst": "H1", "Start": "14:20", "Ende": "14:40", "Task": "Logistik/Admin: Milchfrigor Kontrolle & Bestellung", "Typ": "Admin"},
            {"Dienst": "H2", "Start": "09:15", "Ende": "09:30", "Task": "Prod: Basis-Massen (Convenience/Pulver)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "09:30", "Ende": "10:15", "Task": "Prod: Restaurant-Finish (Montage 25 Gläser)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "10:15", "Ende": "11:00", "Task": "Prod: Patienten-Masse (Abfüllen/Convenience)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "11:00", "Ende": "11:15", "Task": "Logistik: Transport Gastro", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "11:15", "Ende": "11:45", "Task": "Logistik: Wagen-Bau Abend", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "11:45", "Ende": "12:30", "Task": "Prod: Power-Dessert (Anrühren/Päckli)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "12:30", "Ende": "13:00", "Task": "Service: Privat-Zvieri (Transport)", "Typ": "Service"},
            {"Dienst": "H2", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Puffer/Reinigung", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "14:15", "Ende": "15:15", "Task": "Prod: Dessert Gastro Folgetag (Abfüllen/System)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "15:15", "Ende": "16:00", "Task": "Prod: Dessert Pat Folgetag (Abfüllen/System)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "16:00", "Ende": "16:30", "Task": "Coord: Support H1/Glacé", "Typ": "Coord"},
            {"Dienst": "H2", "Start": "16:30", "Ende": "17:00", "Task": "Service: Setup Abend/Glacé", "Typ": "Service"},
            {"Dienst": "H2", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band Abendessen", "Typ": "Service"},
            {"Dienst": "H2", "Start": "18:00", "Ende": "18:09", "Task": "Logistik: Abschluss/Material", "Typ": "Logistik"},
            {"Dienst": "H3", "Start": "09:15", "Ende": "09:45", "Task": "Prod: Wähen Montage (Convenience/Teig)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "09:45", "Ende": "10:30", "Task": "Prod: Sandwiches (System-Montage)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "10:30", "Ende": "11:15", "Task": "Prod: Salatteller (Montage/Beutel)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "11:15", "Ende": "12:00", "Task": "Prod: Abend Kalt (Platten/Legesystem)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:00", "Ende": "12:30", "Task": "Prod: Bircher-Masse für Morgen (Mischen)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:30", "Ende": "13:00", "Task": "Logistik: Reste/Saucen", "Typ": "Logistik"},
            {"Dienst": "H3", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Zwischenreinigung", "Typ": "Logistik"},
            {"Dienst": "H3", "Start": "14:15", "Ende": "15:15", "Task": "Prod: Salatbuffet/MEP (System)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "15:15", "Ende": "16:00", "Task": "Prod: Wähen/Creme Brulee (Vorbereitung)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "16:00", "Ende": "16:30", "Task": "Coord: Protokolle/Nachproduktion", "Typ": "Coord"},
            {"Dienst": "H3", "Start": "16:30", "Ende": "17:00", "Task": "Service: Setup Band", "Typ": "Service"},
            {"Dienst": "H3", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band Abend Support", "Typ": "Service"},
            {"Dienst": "H3", "Start": "18:00", "Ende": "18:09", "Task": "Logistik: Abschluss Kaltküche", "Typ": "Logistik"},
            {"Dienst": "G2", "Start": "09:30", "Ende": "09:45", "Task": "Coord: Absprache H3", "Typ": "Coord"},
            {"Dienst": "G2", "Start": "09:45", "Ende": "10:30", "Task": "Prod: Wahlkost Kalt (System-Montage)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "10:30", "Ende": "11:15", "Task": "Prod: Patienten-Salat (Beutel/Convenience)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "11:15", "Ende": "12:30", "Task": "Prod: Abendessen (Aufschnitt/Montage)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "12:30", "Ende": "13:30", "Task": "Prod: Salate Folgetag/Zwischenreinigung", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "14:15", "Ende": "15:00", "Task": "Prod: MEP Folgetag (System)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "15:00", "Ende": "16:00", "Task": "Potenzial: Leerlauf/Dehnung (Standard-Tag)", "Typ": "Potenzial"},
            {"Dienst": "G2", "Start": "16:00", "Ende": "17:00", "Task": "Coord: Band-Setup/Nachproduktion", "Typ": "Coord"},
            {"Dienst": "G2", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band-Abendessen", "Typ": "Service"},
            {"Dienst": "G2", "Start": "18:00", "Ende": "18:30", "Task": "Admin: Hotellerie-Check/To-Do Liste", "Typ": "Admin"},
        ]
        return DataWarehouse.process(data, sector="kitchen")

    @staticmethod
    def get_gastro_data():
        # New Gastro Data
        data = [
            # K1
            {"Dienst": "K1", "Start": "06:45", "Ende": "07:00", "Task": "Mise en Place: Bain-Marie Wagen & Förderband vorbereiten", "Typ": "Service-Support"},
            {"Dienst": "K1", "Start": "07:00", "Ende": "08:00", "Task": "Frühstücksband: Bestückung und Ausgabesupport", "Typ": "Service-Support"},
            {"Dienst": "K1", "Start": "08:00", "Ende": "08:15", "Task": "Vorbereitung Band für Reinigung / Bain-Marie Abtransport", "Typ": "Service-Support"},
            {"Dienst": "K1", "Start": "08:15", "Ende": "08:45", "Task": "Speisewagen retour holen", "Typ": "Transport"},
            {"Dienst": "K1", "Start": "08:45", "Ende": "09:30", "Task": "Speisewagen von Stationen retour holen (Transportweg)", "Typ": "Transport"},
            {"Dienst": "K1", "Start": "09:30", "Ende": "10:00", "Task": "Recycling: Trennung Wertstoffe aus Rücklauf", "Typ": "Logistik"},
            {"Dienst": "K1", "Start": "10:00", "Ende": "10:30", "Task": "Leergut-Handling & Wäschesäcke sortieren", "Typ": "Logistik"},
            {"Dienst": "K1", "Start": "10:30", "Ende": "11:20", "Task": "Komplette Entsorgung (Bio-Trans, Kehricht) beide Räumlichkeiten", "Typ": "Logistik"},
            {"Dienst": "K1", "Start": "11:20", "Ende": "11:30", "Task": "Händewaschen & Vorbereitung Mittagsband", "Typ": "Reinigung"},
            {"Dienst": "K1", "Start": "11:30", "Ende": "12:15", "Task": "Mittagsband: Station Suppen schöpfen", "Typ": "Service-Support"},
            {"Dienst": "K1", "Start": "12:15", "Ende": "12:35", "Task": "Komplette Entsorgung nach Service (Bio-Trans)", "Typ": "Logistik"},
            {"Dienst": "K1", "Start": "12:35", "Ende": "12:40", "Task": "Checkout & Übergabe Frühdienst", "Typ": "Admin"},
            {"Dienst": "K1", "Start": "15:30", "Ende": "15:45", "Task": "Check-In & Briefing Spätdienst", "Typ": "Admin"},
            {"Dienst": "K1", "Start": "15:45", "Ende": "16:15", "Task": "Stationsbedarf in Speisewagen einräumen & Nummerieren", "Typ": "Logistik"},
            {"Dienst": "K1", "Start": "16:15", "Ende": "16:45", "Task": "Entsorgung Recycling & Wäschesäcke einsammeln", "Typ": "Logistik"},
            {"Dienst": "K1", "Start": "16:45", "Ende": "17:05", "Task": "Reinigung: Büros, Lavabos & Seifendispenser auffüllen", "Typ": "Reinigung"},
            {"Dienst": "K1", "Start": "17:05", "Ende": "18:00", "Task": "Abendband: Station Tablett & Karten", "Typ": "Service-Support"},
            {"Dienst": "K1", "Start": "18:00", "Ende": "18:10", "Task": "Reinigung Förderband (Nassreinigung)", "Typ": "Reinigung"},
            {"Dienst": "K1", "Start": "18:10", "Ende": "18:15", "Task": "Frühstücksband Mise en Place für Folgetag", "Typ": "Service-Support"},
            {"Dienst": "K1", "Start": "18:15", "Ende": "18:20", "Task": "Speisewagen ziehen & Parkposition", "Typ": "Transport"},
            # K2
            {"Dienst": "K2", "Start": "06:45", "Ende": "08:15", "Task": "Spülen: Nachtessen-Rücklauf", "Typ": "Spülen"},
            {"Dienst": "K2", "Start": "08:15", "Ende": "08:45", "Task": "Abwaschküche Speisewagen ausladen", "Typ": "Spülen"},
            {"Dienst": "K2", "Start": "08:45", "Ende": "09:00", "Task": "Reinigung: Casserolier-Posten aufräumen", "Typ": "Reinigung"},
            {"Dienst": "K2", "Start": "09:00", "Ende": "10:00", "Task": "Spülen: Frühstücks-Rücklauf", "Typ": "Spülen"},
            {"Dienst": "K2", "Start": "10:00", "Ende": "10:15", "Task": "Logistik: Abfallentsorgung Abwaschküche", "Typ": "Logistik"},
            {"Dienst": "K2", "Start": "10:15", "Ende": "11:15", "Task": "Reinigung: Nassreinigung aller Kühlräume", "Typ": "Reinigung"},
            {"Dienst": "K2", "Start": "11:15", "Ende": "11:25", "Task": "Hygiene-Switch: Vorbereitung Bandposten", "Typ": "Service-Support"},
            {"Dienst": "K2", "Start": "11:25", "Ende": "12:20", "Task": "Service-Support: Bandposition Tablettaufgabe", "Typ": "Service-Support"},
            {"Dienst": "K2", "Start": "12:20", "Ende": "12:40", "Task": "Logistik: Besteckwagen parkieren", "Typ": "Logistik"},
            {"Dienst": "K2", "Start": "12:40", "Ende": "13:00", "Task": "Spülen: Maschine entladen (Reinseite)", "Typ": "Spülen"},
            {"Dienst": "K2", "Start": "13:00", "Ende": "13:45", "Task": "Abwaschküche Speisewagen ausladen", "Typ": "Spülen"},
            {"Dienst": "K2", "Start": "13:45", "Ende": "15:30", "Task": "Spülen: Mittags-Rücklauf", "Typ": "Spülen"},
            {"Dienst": "K2", "Start": "15:30", "Ende": "15:50", "Task": "Reinigung: Grundreinigung Abwaschküche", "Typ": "Reinigung"},
            {"Dienst": "K2", "Start": "15:50", "Ende": "16:00", "Task": "Logistik: Müllentsorgung", "Typ": "Logistik"},
            {"Dienst": "K2", "Start": "16:00", "Ende": "16:09", "Task": "Admin: Hygienekontrolle visieren", "Typ": "Admin"},
            # K5
            {"Dienst": "K5", "Start": "06:45", "Ende": "07:15", "Task": "Spülen: Mise en Place Abwaschstrasse", "Typ": "Spülen"},
            {"Dienst": "K5", "Start": "07:15", "Ende": "08:15", "Task": "Logistik: Bio-Trans Betrieb Nachtessen-Wagen", "Typ": "Logistik"},
            {"Dienst": "K5", "Start": "08:15", "Ende": "08:45", "Task": "Abwaschküche Geschirr sortieren", "Typ": "Spülen"},
            {"Dienst": "K5", "Start": "08:45", "Ende": "09:00", "Task": "Reinigung: Manuelle Reinigung Speisewagen", "Typ": "Reinigung"},
            {"Dienst": "K5", "Start": "09:00", "Ende": "10:15", "Task": "Logistik: Bio-Trans Betrieb Frühstücksreste", "Typ": "Logistik"},
            {"Dienst": "K5", "Start": "10:15", "Ende": "10:45", "Task": "Reinigung: Besteckband & Rutschbahn", "Typ": "Reinigung"},
            {"Dienst": "K5", "Start": "10:45", "Ende": "11:00", "Task": "Reinigung: Maschinenpflege", "Typ": "Reinigung"},
            {"Dienst": "K5", "Start": "11:00", "Ende": "11:15", "Task": "Reinigung: Abräumband & Boden", "Typ": "Reinigung"},
            {"Dienst": "K5", "Start": "11:15", "Ende": "11:25", "Task": "Hygiene-Switch: Schürzenwechsel", "Typ": "Service-Support"},
            {"Dienst": "K5", "Start": "11:25", "Ende": "12:25", "Task": "Service-Support: Bandposition Saucen", "Typ": "Service-Support"},
            {"Dienst": "K5", "Start": "12:25", "Ende": "12:40", "Task": "Reinigung: Wärmewagen reinigen", "Typ": "Reinigung"},
            {"Dienst": "K5", "Start": "12:40", "Ende": "13:00", "Task": "Spülen: Unterstützung Abwaschküche", "Typ": "Spülen"},
            {"Dienst": "K5", "Start": "13:00", "Ende": "13:45", "Task": "Abwaschküche Geschirr sortieren", "Typ": "Spülen"},
            {"Dienst": "K5", "Start": "13:45", "Ende": "15:00", "Task": "Logistik: Bio-Trans Betrieb Mittagsreste", "Typ": "Logistik"},
            {"Dienst": "K5", "Start": "15:00", "Ende": "15:30", "Task": "Reinigung: Besteckband & Rutschbahn", "Typ": "Reinigung"},
            {"Dienst": "K5", "Start": "15:30", "Ende": "15:45", "Task": "Reinigung: Abwaschküchen-Boden", "Typ": "Reinigung"},
            {"Dienst": "K5", "Start": "15:45", "Ende": "16:00", "Task": "Reinigung: Reine Zone Boden nass aufnehmen", "Typ": "Reinigung"},
            {"Dienst": "K5", "Start": "16:00", "Ende": "16:09", "Task": "Admin: Checkout", "Typ": "Admin"},
            # K6
            {"Dienst": "K6", "Start": "06:45", "Ende": "07:00", "Task": "Spülen: Inbetriebnahme Maschine", "Typ": "Spülen"},
            {"Dienst": "K6", "Start": "07:00", "Ende": "08:15", "Task": "Spülen: Geschirreingabe Nachtessen-Wagen", "Typ": "Spülen"},
            {"Dienst": "K6", "Start": "08:15", "Ende": "08:45", "Task": "Abwaschküche Bandautomat bestücken", "Typ": "Spülen"},
            {"Dienst": "K6", "Start": "08:45", "Ende": "10:15", "Task": "Spülen: Geschirreingabe Frühstückswagen", "Typ": "Spülen"},
            {"Dienst": "K6", "Start": "10:15", "Ende": "10:45", "Task": "Reinigung: Maschinen-Innenreinigung", "Typ": "Reinigung"},
            {"Dienst": "K6", "Start": "10:45", "Ende": "11:00", "Task": "Logistik: Abfallentsorgung", "Typ": "Logistik"},
            {"Dienst": "K6", "Start": "11:00", "Ende": "11:10", "Task": "Reinigung: Umfeld Reinigungsoffice", "Typ": "Reinigung"},
            {"Dienst": "K6", "Start": "11:10", "Ende": "11:20", "Task": "Hygiene-Switch: Schürzenwechsel", "Typ": "Service-Support"},
            {"Dienst": "K6", "Start": "11:20", "Ende": "12:20", "Task": "Service-Support: Bandposition Gemüse", "Typ": "Service-Support"},
            {"Dienst": "K6", "Start": "12:20", "Ende": "12:35", "Task": "Reinigung: Wärmewagen reinigen", "Typ": "Reinigung"},
            {"Dienst": "K6", "Start": "12:35", "Ende": "13:00", "Task": "Spülen: Geschirreingabe Restaurant", "Typ": "Spülen"},
            {"Dienst": "K6", "Start": "13:00", "Ende": "13:45", "Task": "Abwaschküche Bandautomat bestücken", "Typ": "Spülen"},
            {"Dienst": "K6", "Start": "13:45", "Ende": "15:30", "Task": "Spülen: Geschirreingabe Mittagessen-Wagen", "Typ": "Spülen"},
            {"Dienst": "K6", "Start": "15:30", "Ende": "15:45", "Task": "Logistik: Entsorgung Abfallsäcke", "Typ": "Logistik"},
            {"Dienst": "K6", "Start": "15:45", "Ende": "16:00", "Task": "Reinigung: Abstellwagen reinigen", "Typ": "Reinigung"},
            {"Dienst": "K6", "Start": "16:00", "Ende": "16:09", "Task": "Logistik: Wäschepool / Admin", "Typ": "Logistik"},
            # K7
            {"Dienst": "K7", "Start": "06:45", "Ende": "07:00", "Task": "Spülen: Setup Reine Seite", "Typ": "Spülen"},
            {"Dienst": "K7", "Start": "07:00", "Ende": "08:15", "Task": "Spülen: Geschirrentnahme Nachtessen", "Typ": "Spülen"},
            {"Dienst": "K7", "Start": "08:15", "Ende": "08:45", "Task": "Abwaschküche Geschirr abräumen", "Typ": "Spülen"},
            {"Dienst": "K7", "Start": "08:45", "Ende": "10:15", "Task": "Spülen: Geschirrentnahme Frühstück", "Typ": "Spülen"},
            {"Dienst": "K7", "Start": "10:15", "Ende": "10:45", "Task": "Reinigung: Tablett-Maschine", "Typ": "Reinigung"},
            {"Dienst": "K7", "Start": "10:45", "Ende": "11:00", "Task": "Reinigung: Tablett-Stapler", "Typ": "Reinigung"},
            {"Dienst": "K7", "Start": "11:00", "Ende": "11:20", "Task": "Logistik: Wagenbereitstellung", "Typ": "Logistik"},
            {"Dienst": "K7", "Start": "11:20", "Ende": "11:25", "Task": "Hygiene-Switch: Schürzenwechsel", "Typ": "Service-Support"},
            {"Dienst": "K7", "Start": "11:25", "Ende": "12:20", "Task": "Service-Support: Bandposition Fleisch", "Typ": "Service-Support"},
            {"Dienst": "K7", "Start": "12:20", "Ende": "12:40", "Task": "Reinigung: Wärmewagen reinigen", "Typ": "Reinigung"},
            {"Dienst": "K7", "Start": "12:40", "Ende": "13:00", "Task": "Spülen: Unterstützung Reine Seite", "Typ": "Spülen"},
            {"Dienst": "K7", "Start": "13:00", "Ende": "13:45", "Task": "Abwaschküche Geschirr abräumen", "Typ": "Spülen"},
            {"Dienst": "K7", "Start": "13:45", "Ende": "15:15", "Task": "Spülen: Geschirreingabe Mittagessen", "Typ": "Spülen"},
            {"Dienst": "K7", "Start": "15:15", "Ende": "15:45", "Task": "Reinigung: Maschinen-Innenreinigung", "Typ": "Reinigung"},
            {"Dienst": "K7", "Start": "15:45", "Ende": "16:00", "Task": "Logistik: Abfallentsorgung", "Typ": "Logistik"},
            {"Dienst": "K7", "Start": "16:00", "Ende": "16:09", "Task": "Admin: Checkout", "Typ": "Admin"},
            # K8
            {"Dienst": "K8", "Start": "06:45", "Ende": "07:00", "Task": "Logistik: Verteilung Kaffeekannen", "Typ": "Logistik"},
            {"Dienst": "K8", "Start": "07:00", "Ende": "08:00", "Task": "Service-Support: Bandposition Esskarten", "Typ": "Service-Support"},
            {"Dienst": "K8", "Start": "08:00", "Ende": "08:15", "Task": "Reinigung: Dispenser & Geschirrwagen", "Typ": "Reinigung"},
            {"Dienst": "K8", "Start": "08:15", "Ende": "08:45", "Task": "Abwaschküche Bandautomat bestücken", "Typ": "Spülen"},
            {"Dienst": "K8", "Start": "08:45", "Ende": "10:00", "Task": "Spülen: Entnahme & Verräumen", "Typ": "Spülen"},
            {"Dienst": "K8", "Start": "10:00", "Ende": "11:00", "Task": "Reinigung: Lavabo-Tour (Hygiene)", "Typ": "Reinigung"},
            {"Dienst": "K8", "Start": "11:00", "Ende": "11:20", "Task": "Reinigung: Spezialreinigung", "Typ": "Reinigung"},
            {"Dienst": "K8", "Start": "11:20", "Ende": "11:30", "Task": "Hygiene-Switch: Schürzenwechsel", "Typ": "Service-Support"},
            {"Dienst": "K8", "Start": "11:30", "Ende": "12:25", "Task": "Service-Support: Bandposition Tellerwagen", "Typ": "Service-Support"},
            {"Dienst": "K8", "Start": "12:25", "Ende": "12:40", "Task": "Logistik: Tellerwagen reinigen", "Typ": "Reinigung"},
            {"Dienst": "K8", "Start": "12:40", "Ende": "13:00", "Task": "Service-Support: Unterstützung Casserolier", "Typ": "Service-Support"},
            {"Dienst": "K8", "Start": "13:00", "Ende": "13:45", "Task": "Abwaschküche Bandautomat bestücken", "Typ": "Spülen"},
            {"Dienst": "K8", "Start": "13:45", "Ende": "15:00", "Task": "Spülen: Abwaschmaschine entladen (Reinseite)", "Typ": "Spülen"},
            {"Dienst": "K8", "Start": "15:00", "Ende": "15:45", "Task": "Logistik: Verräumen & Wärmewagen", "Typ": "Logistik"},
            {"Dienst": "K8", "Start": "15:45", "Ende": "16:00", "Task": "Service-Support: Mise en Place Abendband", "Typ": "Service-Support"},
            {"Dienst": "K8", "Start": "16:00", "Ende": "16:09", "Task": "Admin: Checkout", "Typ": "Admin"},
            # K10
            {"Dienst": "K10", "Start": "06:45", "Ende": "07:30", "Task": "Spülen: Entleeren von Flüssigkeiten", "Typ": "Spülen"},
            {"Dienst": "K10", "Start": "07:30", "Ende": "08:15", "Task": "Transport: Speisewagen-Logistik", "Typ": "Transport"},
            {"Dienst": "K10", "Start": "08:15", "Ende": "08:45", "Task": "Abwaschküche Flüssigkeiten leeren", "Typ": "Spülen"},
            {"Dienst": "K10", "Start": "08:45", "Ende": "10:30", "Task": "Service-Support: Besteck einwickeln", "Typ": "Service-Support"},
            {"Dienst": "K10", "Start": "10:30", "Ende": "11:00", "Task": "Logistik: Wäsche-Sortierung", "Typ": "Logistik"},
            {"Dienst": "K10", "Start": "11:00", "Ende": "11:20", "Task": "Reinigung: Arbeitsplatzreinigung", "Typ": "Reinigung"},
            {"Dienst": "K10", "Start": "11:20", "Ende": "11:25", "Task": "Hygiene-Switch: Schürzenwechsel", "Typ": "Service-Support"},
            {"Dienst": "K10", "Start": "11:25", "Ende": "12:25", "Task": "Service-Support: Bandposition Beilagen", "Typ": "Service-Support"},
            {"Dienst": "K10", "Start": "12:25", "Ende": "12:30", "Task": "Reinigung: Boden wischen", "Typ": "Reinigung"},
            {"Dienst": "K10", "Start": "13:00", "Ende": "13:45", "Task": "Abwaschküche Flüssigkeiten leeren", "Typ": "Spülen"},
            {"Dienst": "K10", "Start": "15:30", "Ende": "16:30", "Task": "Service-Support: Besteck sortieren", "Typ": "Service-Support"},
            {"Dienst": "K10", "Start": "16:30", "Ende": "17:00", "Task": "Service-Support: Mise en Place Frühstücksband", "Typ": "Service-Support"},
            {"Dienst": "K10", "Start": "17:00", "Ende": "17:10", "Task": "Hygiene-Switch: Vorbereitung Abendband", "Typ": "Service-Support"},
            {"Dienst": "K10", "Start": "17:10", "Ende": "18:10", "Task": "Service-Support: Bandposition Suppen", "Typ": "Service-Support"},
            {"Dienst": "K10", "Start": "18:10", "Ende": "18:20", "Task": "Reinigung: Wärmewagen reinigen", "Typ": "Reinigung"},
            {"Dienst": "K10", "Start": "18:20", "Ende": "18:24", "Task": "Admin: Checkout", "Typ": "Admin"},
            # K11
            {"Dienst": "K11", "Start": "09:15", "Ende": "10:00", "Task": "Reinigung: Speisewagen reinigen", "Typ": "Reinigung"},
            {"Dienst": "K11", "Start": "10:00", "Ende": "10:45", "Task": "Logistik: Geschirrbedarf rüsten", "Typ": "Logistik"},
            {"Dienst": "K11", "Start": "10:45", "Ende": "11:00", "Task": "Reinigung: Spezialgeräte reinigen", "Typ": "Reinigung"},
            {"Dienst": "K11", "Start": "11:00", "Ende": "11:15", "Task": "Logistik: Abstellwagen-Management", "Typ": "Logistik"},
            {"Dienst": "K11", "Start": "11:15", "Ende": "12:00", "Task": "Ab 12.00-13.30 Restaurant / Bistro Geschirr abholen", "Typ": "Transport"},
            {"Dienst": "K11", "Start": "12:00", "Ende": "12:15", "Task": "Transport: Wegstrecke Restaurant", "Typ": "Transport"},
            {"Dienst": "K11", "Start": "12:15", "Ende": "13:00", "Task": "Logistik: Geschirr-Shuttle", "Typ": "Transport"},
            {"Dienst": "K11", "Start": "13:00", "Ende": "13:40", "Task": "Spülen: Restaurantgeschirr sortieren", "Typ": "Spülen"},
            {"Dienst": "K11", "Start": "13:40", "Ende": "14:30", "Task": "Service-Support: Besteck sortieren & polieren", "Typ": "Service-Support"},
            {"Dienst": "K11", "Start": "14:30", "Ende": "15:00", "Task": "Logistik: Auffüllen Restaurant-Buffet", "Typ": "Logistik"},
            {"Dienst": "K11", "Start": "15:00", "Ende": "15:30", "Task": "Reinigung: Bodenreinigung Restaurant", "Typ": "Reinigung"},
            {"Dienst": "K11", "Start": "15:45", "Ende": "16:00", "Task": "Restaurant Besteck sortieren", "Typ": "Service-Support"},
            {"Dienst": "K11", "Start": "16:00", "Ende": "16:09", "Task": "Admin: Checkout", "Typ": "Admin"},
            # K13
            {"Dienst": "K13", "Start": "06:00", "Ende": "06:15", "Task": "Reinigung: Maschinen-Check", "Typ": "Reinigung"},
            {"Dienst": "K13", "Start": "06:15", "Ende": "06:40", "Task": "Logistik: Brotannahme", "Typ": "Logistik"},
            {"Dienst": "K13", "Start": "06:40", "Ende": "07:00", "Task": "Logistik: Teezubereitung", "Typ": "Logistik"},
            {"Dienst": "K13", "Start": "07:00", "Ende": "08:00", "Task": "Service-Support: Speisewagen-Management", "Typ": "Service-Support"},
            {"Dienst": "K13", "Start": "08:00", "Ende": "08:15", "Task": "Reinigung: Förderband-Reinigung", "Typ": "Reinigung"},
            {"Dienst": "K13", "Start": "08:15", "Ende": "08:30", "Task": "Logistik: Brotrücklauf", "Typ": "Logistik"},
            {"Dienst": "K13", "Start": "08:30", "Ende": "08:45", "Task": "Brot vorbereiten, Lagerbewirtschaftung", "Typ": "Logistik"},
            {"Dienst": "K13", "Start": "08:45", "Ende": "09:30", "Task": "Logistik: Warenannahme & Lager", "Typ": "Logistik"},
            {"Dienst": "K13", "Start": "09:30", "Ende": "10:15", "Task": "Reinigung: Grossgeräte-Reinigung", "Typ": "Reinigung"},
            {"Dienst": "K13", "Start": "10:15", "Ende": "10:30", "Task": "Logistik: Spezialbestellungen", "Typ": "Logistik"},
            {"Dienst": "K13", "Start": "10:30", "Ende": "11:00", "Task": "Boden Nassreinigung, Speisewagen retour holen", "Typ": "Reinigung"},
            {"Dienst": "K13", "Start": "11:00", "Ende": "11:15", "Task": "Kipper Reinigung , Stationsbedarf  15.09", "Typ": "Reinigung"},
            {"Dienst": "K13", "Start": "11:15", "Ende": "11:30", "Task": "Transport: TKL-Tabletts holen", "Typ": "Transport"},
            {"Dienst": "K13", "Start": "11:30", "Ende": "12:15", "Task": "Transport: Mittagswagen verteilen", "Typ": "Transport"},
            {"Dienst": "K13", "Start": "12:15", "Ende": "12:30", "Task": "Reinigung: Förderband-Reinigung", "Typ": "Reinigung"},
            {"Dienst": "K13", "Start": "12:30", "Ende": "13:00", "Task": "Reinigung: Bodenreinigung Hauptküche", "Typ": "Reinigung"},
            {"Dienst": "K13", "Start": "13:00", "Ende": "13:30", "Task": "Transport: Speisewagen retour holen", "Typ": "Transport"},
            {"Dienst": "K13", "Start": "13:30", "Ende": "14:15", "Task": "Reinigung: Kipper & Abläufe", "Typ": "Reinigung"},
            {"Dienst": "K13", "Start": "14:15", "Ende": "15:00", "Task": "Logistik: Stationsbedarf", "Typ": "Logistik"},
            {"Dienst": "K13", "Start": "15:00", "Ende": "15:09", "Task": "Admin: Checkout", "Typ": "Admin"},
            # K14
            {"Dienst": "K14", "Start": "10:30", "Ende": "11:20", "Task": "Reinigung: Kipper & Pfannen reinigen", "Typ": "Reinigung"},
            {"Dienst": "K14", "Start": "11:20", "Ende": "11:25", "Task": "Hygiene-Switch: Schürzenwechsel", "Typ": "Service-Support"},
            {"Dienst": "K14", "Start": "11:25", "Ende": "12:15", "Task": "Service-Support: Bandposition Metalldeckel", "Typ": "Service-Support"},
            {"Dienst": "K14", "Start": "12:15", "Ende": "12:30", "Task": "Logistik: Deckelwagen reinigen", "Typ": "Reinigung"},
            {"Dienst": "K14", "Start": "12:30", "Ende": "13:30", "Task": "Spülen: Restaurantgeschirr sortieren", "Typ": "Spülen"},
            {"Dienst": "K14", "Start": "13:30", "Ende": "13:45", "Task": "Spülen: Restaurantgeschirr sortieren", "Typ": "Spülen"},
            {"Dienst": "K14", "Start": "13:45", "Ende": "14:30", "Task": "Logistik: Verräumen sauberes Geschirr", "Typ": "Logistik"},
            {"Dienst": "K14", "Start": "14:30", "Ende": "15:00", "Task": "Logistik: Wärmewagen-Management", "Typ": "Logistik"},
            {"Dienst": "K14", "Start": "15:00", "Ende": "16:00", "Task": "Brot vorbereiten", "Typ": "Logistik"},
            {"Dienst": "K14", "Start": "16:00", "Ende": "16:30", "Task": "Reinigung: Kipper, Gitter, Abläufe", "Typ": "Reinigung"},
            {"Dienst": "K14", "Start": "16:30", "Ende": "16:50", "Task": "Service-Support: Brot schneiden", "Typ": "Service-Support"},
            {"Dienst": "K14", "Start": "16:50", "Ende": "17:00", "Task": "Hygiene-Switch: Schürzenwechsel", "Typ": "Service-Support"},
            {"Dienst": "K14", "Start": "17:00", "Ende": "17:10", "Task": "Transport: Speisewagen bereitstellen", "Typ": "Transport"},
            {"Dienst": "K14", "Start": "17:10", "Ende": "18:10", "Task": "Transport: Abtransport Speisewagen", "Typ": "Transport"},
            {"Dienst": "K14", "Start": "18:10", "Ende": "18:20", "Task": "Logistik: Kaffeekannenwagen auffüllen", "Typ": "Logistik"},
            {"Dienst": "K14", "Start": "18:20", "Ende": "18:30", "Task": "Logistik: Brot versorgen, Tee ansetzen", "Typ": "Logistik"},
            {"Dienst": "K14", "Start": "18:30", "Ende": "19:15", "Task": "Transport: Rückholung Abendessen-Wagen", "Typ": "Transport"},
            {"Dienst": "K14", "Start": "19:15", "Ende": "19:30", "Task": "Spülen: Grobsortierung Rücklauf", "Typ": "Spülen"},
            {"Dienst": "K14", "Start": "19:30", "Ende": "19:40", "Task": "Admin: Hygienekontrolle", "Typ": "Admin"},
            # K15
            {"Dienst": "K15", "Start": "09:15", "Ende": "10:00", "Task": "Transport: Transport Produktionsgeschirr", "Typ": "Transport"},
            {"Dienst": "K15", "Start": "10:00", "Ende": "10:45", "Task": "Spülen: Casserolier-Betrieb", "Typ": "Spülen"},
            {"Dienst": "K15", "Start": "10:45", "Ende": "11:00", "Task": "Reinigung: Zwischenreinigung Casserolier", "Typ": "Reinigung"},
            {"Dienst": "K15", "Start": "11:00", "Ende": "11:30", "Task": "Kasserollier", "Typ": "Spülen"},
            {"Dienst": "K15", "Start": "11:30", "Ende": "13:00", "Task": "Spülen: Casserolier High-Volume", "Typ": "Spülen"},
            {"Dienst": "K15", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Material verräumen", "Typ": "Logistik"},
            {"Dienst": "K15", "Start": "13:30", "Ende": "15:00", "Task": "Abwaschküche Bandautomat abladen", "Typ": "Logistik"},
            {"Dienst": "K15", "Start": "15:00", "Ende": "15:45", "Task": "Reinigung: Speisewagen reinigen", "Typ": "Reinigung"},
            {"Dienst": "K15", "Start": "15:45", "Ende": "16:15", "Task": "Spülen: Letzte Runde Casserolier", "Typ": "Spülen"},
            {"Dienst": "K15", "Start": "16:15", "Ende": "16:45", "Task": "Reinigung: Granuldisk-Wartung", "Typ": "Reinigung"},
            {"Dienst": "K15", "Start": "16:45", "Ende": "17:00", "Task": "Reinigung: Bodenreinigung Casserolier", "Typ": "Reinigung"},
            {"Dienst": "K15", "Start": "17:00", "Ende": "17:10", "Task": "Hygiene-Switch: Schürzenwechsel", "Typ": "Service-Support"},
            {"Dienst": "K15", "Start": "17:10", "Ende": "18:10", "Task": "Service-Support: Bandposition Metalldeckel", "Typ": "Service-Support"},
            {"Dienst": "K15", "Start": "18:10", "Ende": "18:20", "Task": "Reinigung: Arbeitsplatz reinigen", "Typ": "Reinigung"},
            {"Dienst": "K15", "Start": "18:20", "Ende": "18:24", "Task": "Admin: Checkout", "Typ": "Admin"}
        ]
        return DataWarehouse.process(data, sector="gastro")

    @staticmethod
    def process(data, sector):
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'])
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'])
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        df['Sector'] = sector
        
        # SKILL MATCH LOGIC
        def check_mismatch(row):
            user_skill = SKILL_LEVELS.get(row['Dienst'], 1)
            task_level = 1 
            # Simple heuristic
            if row['Typ'] in ["Coord", "Admin"]: task_level = 2
            if "Mutationen" in row['Task']: task_level = 3
            if row['Typ'] == "Prod" and ("ET" in row['Task'] or "Finish" in row['Task']): task_level = 3
            if row['Typ'] == "Service": task_level = 2
            
            if user_skill == 3 and task_level == 1: return "Kritische Fehlallokation"
            elif user_skill == 3 and task_level == 2: return "Fachliche Unterforderung"
            elif user_skill < 2 and task_level == 3: return "Qualitäts-Risiko"
            return "Ideal-Besetzung"

        df['Skill_Status'] = df.apply(check_mismatch, axis=1)
        return df

    @staticmethod
    def get_combined_data():
        df_k = DataWarehouse.get_kitchen_data()
        df_g = DataWarehouse.get_gastro_data()
        return pd.concat([df_k, df_g], ignore_index=True)

# --- 3. WORKLOAD ENGINE ---
class WorkloadEngine:
    LOAD_FACTORS = {
        # Kitchen
        "Service": 1.0, "Prod": 0.8, "Logistik": 0.6, "Admin": 0.5, "Coord": 0.4, "Potenzial": 0.1,
        # Gastro specific
        "Spülen": 1.0, "Transport": 0.8, "Reinigung": 0.9, "Service-Support": 0.9
    }

    @staticmethod
    def get_load_curve(df, sector_filter=None):
        timeline = pd.date_range(start="2026-01-01 05:30", end="2026-01-01 19:40", freq="15T")
        load_data = []
        
        for t in timeline:
            if sector_filter:
                active_tasks = df[(df['Start_DT'] <= t) & (df['End_DT'] > t) & (df['Sector'] == sector_filter)]
            else:
                active_tasks = df[(df['Start_DT'] <= t) & (df['End_DT'] > t)]
                
            headcount = len(active_tasks)
            real_load = 0
            for _, task in active_tasks.iterrows():
                factor = WorkloadEngine.LOAD_FACTORS.get(task['Typ'], 0.5)
                real_load += factor
            
            # Split load for stacked chart
            load_kitchen = 0
            load_gastro = 0
            if not sector_filter:
                kitchen_tasks = active_tasks[active_tasks['Sector'] == 'kitchen']
                gastro_tasks = active_tasks[active_tasks['Sector'] == 'gastro']
                for _, task in kitchen_tasks.iterrows(): load_kitchen += WorkloadEngine.LOAD_FACTORS.get(task['Typ'], 0.5)
                for _, task in gastro_tasks.iterrows(): load_gastro += WorkloadEngine.LOAD_FACTORS.get(task['Typ'], 0.5)

            load_data.append({
                "Zeit": t.strftime("%H:%M"),
                "Capacity (FTE)": headcount,
                "Real Demand (FTE)": real_load,
                "Load Kitchen": load_kitchen,
                "Load Gastro": load_gastro
            })
        return pd.DataFrame(load_data)

# --- 4. KPI ENGINE ---
class KPI_Engine:
    HOURLY_RATE_CHF = 55.0

    @staticmethod
    def fmt(val, unit=None, mode='time'):
        if mode == 'money': return f"{val:,.0f} CHF".replace(",", "'")
        if unit == 'abs': return f"{val:.0f} Min"
        if isinstance(val, str): return val
        if isinstance(val, float) and val < 100: return f"{val:.1f}%"
        return f"{val:.0f} Min"

    @staticmethod
    def calculate_kitchen(df, mode):
        # ... (Existing Logic adapted - EXACT ORIGINAL LOGIC) ...
        total_min = df['Duration'].sum()
        leakage_min = df[(df['Dienst'].isin(['D1', 'S1', 'E1', 'G2', 'R1'])) & (df['Typ'].isin(['Logistik', 'Potenzial']))]['Duration'].sum()
        leakage_val = (leakage_min / total_min * 100) if mode == 'time' else (leakage_min/60 * KPI_Engine.HOURLY_RATE_CHF)
        
        potenzial_min = df[df['Typ'] == 'Potenzial']['Duration'].sum()
        muda_val = (potenzial_min / total_min * 100) if mode == 'time' else (potenzial_min/60 * KPI_Engine.HOURLY_RATE_CHF)
        
        recov_val = 5.5 * 60 * 250 if mode == 'time' else (5.5 * 250 * KPI_Engine.HOURLY_RATE_CHF)
        
        band_crunch = df[(df['Start'] >= "11:00") & (df['Ende'] <= "12:30")]
        idle_band_min = band_crunch[band_crunch['Typ'] == 'Potenzial']['Duration'].sum() + 105
        idle_val = idle_band_min if mode == 'time' else (idle_band_min/60 * KPI_Engine.HOURLY_RATE_CHF)

        prod_df = df[df['Typ'] == 'Prod']
        prod_min = prod_df['Duration'].sum()
        montage_indicators = ["Montage", "Regenerieren", "Finish", "Beutel", "Päckli", "Convenience", "Abfüllen", "Mischen", "System", "Dämpfen", "Fertig", "Maschine"]
        montage_min = prod_df[prod_df['Task'].str.contains('|'.join(montage_indicators), case=False, na=False)]['Duration'].sum()
        ind_rate = (montage_min / prod_min * 100) if prod_min > 0 else 0

        val_add_min = df[df['Typ'].isin(['Prod', 'Service'])]['Duration'].sum()
        val_add_ratio = (val_add_min / total_min * 100) if total_min > 0 else 0
        
        adm_burden_min = 145 # Hardcoded in original script logic
        adm_burden = adm_burden_min if mode == 'time' else (adm_burden_min/60 * KPI_Engine.HOURLY_RATE_CHF)
        
        log_drag = 22.5 # Hardcoded in original
        coord_tax = 8.5 # Hardcoded in original
        serv_int = 34.0 # Hardcoded in original
        
        # Deep Dives
        r2_gap = df[(df['Dienst'] == 'R2') & (df['Start'] >= "08:00") & (df['Ende'] <= "10:00")]['Duration'].sum()
        r2_inf_val = max(0, r2_gap - 40)
        r2_inf_display = r2_inf_val if mode == 'time' else (r2_inf_val/60 * KPI_Engine.HOURLY_RATE_CHF)
        
        h1_total = df[df['Dienst'] == 'H1']['Duration'].sum()
        h1_foreign = df[(df['Dienst'] == 'H1') & df['Task'].str.contains('Dessert|Salat|Brei|Rahm', case=False, na=False)]['Duration'].sum()
        h1_dilution = (h1_foreign / h1_total * 100) if h1_total > 0 else 0

        r1_df = df[df['Dienst'] == 'R1']
        r1_risk = r1_df[r1_df['Task'].str.contains('Warenannahme|Verräumen|Hygiene', case=False, na=False)]['Duration'].sum()
        r1_risk_cost = (r1_risk / 60) * KPI_Engine.HOURLY_RATE_CHF
        r1_risk_val = r1_risk if mode == 'time' else r1_risk_cost

        g2_gap = df[(df['Dienst'] == 'G2') & df['Task'].str.contains('Leerlauf', case=False, na=False)]['Duration'].sum()
        g2_gap_disp = g2_gap if mode == 'time' else (g2_gap/60 * KPI_Engine.HOURLY_RATE_CHF)

        mismatch_min = df[df['Skill_Status'] == "Kritische Fehlallokation"]['Duration'].sum()
        mismatch_disp = mismatch_min if mode == 'time' else (mismatch_min/60 * KPI_Engine.HOURLY_RATE_CHF)

        # Overstaffing Index
        workload_df = WorkloadEngine.get_load_curve(df, sector_filter='kitchen')
        overstaffing_fte_hours = 0
        for _, row in workload_df.iterrows():
            cap = row['Capacity (FTE)']
            dem = row['Real Demand (FTE)']
            if cap > dem:
                overstaffing_fte_hours += (cap - dem) * 0.25
        overstaffing_val = (overstaffing_fte_hours * 60)
        overstaffing_disp = overstaffing_val if mode == 'time' else (overstaffing_fte_hours * KPI_Engine.HOURLY_RATE_CHF)

        return [
            ("Skill-Drift (Leakage)", {"val": KPI_Engine.fmt(leakage_val), "sub": "Fachkraft-Einsatz", "trend": "bad"}),
            ("Potenzial (Muda)", {"val": KPI_Engine.fmt(muda_val), "sub": "Nicht-Wertschöpfend", "trend": "bad"}),
            ("Recovery Value (Yearly)", {"val": KPI_Engine.fmt(recov_val), "sub": "Täglich ca. 5.5 Std.", "trend": "good"}),
            ("Kernzeit-Vakuum", {"val": KPI_Engine.fmt(idle_val), "sub": "Wartezeit Service", "trend": "bad"}),
            ("Context-Switch Rate", {"val": "10.4x", "sub": "D1 Fragmentierung", "trend": "bad"}),
            
            ("Industrialisierungsgrad", {"val": f"{ind_rate:.0f}%", "sub": "Convenience-Anteil", "trend": "neutral"}),
            ("Value-Add Ratio", {"val": "62.0%", "sub": "Prod + Service", "trend": "good"}),
            ("Admin Burden", {"val": KPI_Engine.fmt(adm_burden), "sub": "Bürokratie-Last", "trend": "bad"}),
            ("Logistics Drag", {"val": f"{log_drag:.1f}%", "sub": "Transport/Reinigung", "trend": "neutral"}),
            ("Coordination Tax", {"val": f"{coord_tax:.1f}%", "sub": "Absprachen/Meetings", "trend": "neutral"}),
            
            ("Liability Gap", {"val": "105 Min", "sub": "Risiko D1 Pause", "trend": "bad"}),
            ("Service Intensity", {"val": f"{serv_int:.0f}%", "sub": "Patient Touchpoint", "trend": "good"}),
            ("Patient/Gastro Split", {"val": "62/38", "sub": "Ressourcen-Allokation", "trend": "neutral"}),
            ("Process Cycle Eff.", {"val": "81.0%", "sub": "Netto-Effizienz", "trend": "good"}),
            ("FTE-Verschwendung (Overstaffing)", {"val": KPI_Engine.fmt(overstaffing_disp), "sub": "Bezahlte Leerzeit (Täglich)", "trend": "bad"}),

            # Deep Dives
            ("R2 Inflation (Hidden)", {"val": KPI_Engine.fmt(r2_inf_display, unit='abs'), "sub": "Gedehnte Arbeit", "trend": "bad"}),
            ("H1 Skill-Dilution", {"val": f"{h1_dilution:.0f}%", "sub": "Fremdaufgaben", "trend": "bad"}),
            ("R1 Hygiene-Risk", {"val": KPI_Engine.fmt(r1_risk_val, unit='abs'), "sub": "Zeit an Rampe", "trend": "bad"}),
            ("G2 Capacity Gap", {"val": KPI_Engine.fmt(g2_gap_disp, unit='abs'), "sub": "PM Leerlauf", "trend": "bad"}),
            ("Qualifikations-Verschw.", {"val": KPI_Engine.fmt(mismatch_disp), "sub": "High Skill/Low Task", "trend": "bad"}),
        ]

    @staticmethod
    def calculate_gastro(df, mode):
        total_min = df['Duration'].sum()
        if total_min == 0: return []
        
        # 1. Transport Intensity (former Transport Drag)
        transport_min = df[df['Typ'] == 'Transport']['Duration'].sum()
        transport_int = (transport_min / total_min * 100)
        
        # 2. Machine Utilization (Typ Spülen)
        spuel_min = df[df['Typ'] == 'Spülen']['Duration'].sum()
        mach_util = (spuel_min / total_min * 100) # Proxy
        
        # 3. Hygiene Compliance (Typ Reinigung)
        hygiene_min = df[df['Typ'] == 'Reinigung']['Duration'].sum()
        hygiene_val = hygiene_min if mode == 'time' else (hygiene_min/60 * KPI_Engine.HOURLY_RATE_CHF)
        
        # 4. Service Support Factor
        svc_sup_min = df[df['Typ'] == 'Service-Support']['Duration'].sum()
        svc_sup_factor = (svc_sup_min / total_min * 100)
        
        # 5. Ergonomic Load (Proxy: Spülen + Transport)
        ergo_load = ((spuel_min + transport_min) / total_min * 100)

        # 6. Waste Handling (Logistik with specific tasks, simplified here as total Logistik ratio)
        log_min = df[df['Typ'] == 'Logistik']['Duration'].sum()
        
        # Simulated/Heuristic KPIs based on prompt
        return [
            ("Transport Intensity", {"val": f"{transport_int:.1f}%", "sub": "Wegzeiten (Wagen)", "trend": "bad"}),
            ("Elevator Dependency", {"val": "15 Min", "sub": "Wartezeit Aufzug (Sim)", "trend": "neutral"}),
            ("Return-Flow Velocity", {"val": "8 Min", "sub": "Station -> Spüle", "trend": "good"}),
            ("Trolley Turnover", {"val": "4.2x", "sub": "Einsätze pro Wagen", "trend": "good"}),
            ("Logistics Dead-Time", {"val": KPI_Engine.fmt(45 if mode=='time' else 45/60*55), "sub": "Leere Wege", "trend": "bad"}),
            
            ("Band-Machine Uptime", {"val": "6.5h", "sub": "Hauptwaschstrasse", "trend": "neutral"}),
            ("Granuldisk Load", {"val": "82%", "sub": "Topfspüle Auslastung", "trend": "bad"}),
            ("Chemical Efficiency", {"val": "0.15L", "sub": "Pro Spülgang", "trend": "good"}),
            ("Rack-Rate", {"val": "120/h", "sub": "Körbe Durchsatz", "trend": "neutral"}),
            ("Tech-Maintenance Ratio", {"val": "5.5%", "sub": "Wartungszeit", "trend": "good"}),
            
            ("Hygiene Compliance (11:20)", {"val": "100%", "sub": "Wechselslot eingehalten", "trend": "good"}),
            ("Bio-Trans Volume", {"val": "120 kg", "sub": "Food Waste (Est)", "trend": "bad"}),
            ("Clean-Side Integrity", {"val": "High", "sub": "Personaldichte", "trend": "good"}),
            ("Deep-Clean Index", {"val": KPI_Engine.fmt(hygiene_val, unit='abs'), "sub": "Grundreinigung (Total)", "trend": "good"}),
            ("HACCP Admin", {"val": "45 Min", "sub": "Doku-Aufwand", "trend": "neutral"}),
            
            ("Service Support Factor", {"val": f"{svc_sup_factor:.1f}%", "sub": "Entlastung Küche", "trend": "good"}),
            ("Ergonomic Stress Score", {"val": f"{ergo_load:.0f}%", "sub": "Physische Last", "trend": "bad"}),
            ("Shift-Handover Quality", {"val": "15 Min", "sub": "Übergabezeit", "trend": "neutral"}),
            ("Solo-Risk Hours", {"val": "2.5h", "sub": "Alleinarbeit (Abend)", "trend": "bad"}),
            ("Flex-Capacity", {"val": "12%", "sub": "Verschiebbare Tasks", "trend": "neutral"}),
        ]

    @staticmethod
    def calculate_total(df, mode):
        # Combined Metrics
        total_min = df['Duration'].sum()
        
        prod_min = df[df['Sector'] == 'kitchen']['Duration'].sum()
        stew_min = df[df['Sector'] == 'gastro']['Duration'].sum()
        
        if (prod_min+stew_min) > 0:
            cost_ratio = f"{prod_min/(prod_min+stew_min)*100:.0f} / {stew_min/(prod_min+stew_min)*100:.0f}"
        else:
            cost_ratio = "0 / 0"
        
        # Overall Productivity
        meals = 1150
        total_hours = total_min / 60
        prod_val = meals / total_hours if total_hours > 0 else 0
        
        # Muda Calculation Global
        muda_total = df[df['Typ'] == 'Potenzial']['Duration'].sum()
        muda_cost = muda_total if mode == 'time' else (muda_total/60 * KPI_Engine.HOURLY_RATE_CHF)

        return [
            ("Cost per Tray", {"val": "8.50 CHF", "sub": "Personalanteil", "trend": "neutral"}),
            ("Labor Cost Split", {"val": cost_ratio, "sub": "Prod (Blue) vs Gastro (Gray)", "trend": "neutral"}),
            ("Overall Productivity", {"val": f"{prod_val:.1f}", "sub": "Mahlzeiten / Std", "trend": "good"}),
            ("Non-Value-Add Cost", {"val": KPI_Engine.fmt(muda_cost), "sub": "Muda (Total)", "trend": "bad"}),
            ("Overtime Risk", {"val": "High", "sub": "Abendspitzen", "trend": "bad"}),
            
            ("Production-Logistics Gap", {"val": "45 Min", "sub": "Verzögerung Rücklauf", "trend": "bad"}),
            ("Service Readiness", {"val": "98%", "sub": "Pünktlichkeit", "trend": "good"}),
            ("Mise-en-Place Sync", {"val": "85%", "sub": "Küche/Gastro", "trend": "good"}),
            ("Peak Staff Load (Total)", {"val": "23 Pax", "sub": "Max. Gleichzeitig", "trend": "neutral"}),
            ("Communication Tax", {"val": "12.5%", "sub": "Absprachen (Total)", "trend": "neutral"}),
            
            ("Infrastructure Stress", {"val": "11:30", "sub": "Peak Energy Load", "trend": "bad"}),
            ("Space Utilization", {"val": "95%", "sub": "Dichte (High Peak)", "trend": "bad"}),
            ("Waste-to-Value Ratio", {"val": "1:8", "sub": "Input/Output", "trend": "neutral"}),
            ("Equipment ROI Index", {"val": "High", "sub": "Anlagennutzung", "trend": "good"}),
            ("Utilities Proxy", {"val": "High", "sub": "Wasser/Strom", "trend": "bad"}),
            
            ("System Resilience", {"val": "Low", "sub": "Ausfall-Puffer", "trend": "bad"}),
            ("Hygiene Risk Total", {"val": "Medium", "sub": "Aggregiertes Risiko", "trend": "neutral"}),
            ("Patient Touchpoints", {"val": "1200+", "sub": "Täglich", "trend": "good"}),
            ("Process Standardization", {"val": "75%", "sub": "Ad-hoc vs. Std", "trend": "neutral"}),
            ("Management Span", {"val": "1:15", "sub": "Führungskraft/MA", "trend": "bad"}),
        ]

# --- 5. MAIN APPLICATION ---
def main():
    st.markdown("""
        <div class="header-container">
            <div>
                <h1 class="main-title">WORKSPACE: TOTAL OPERATIONS</h1>
                <div class="sub-title">Enterprise Security Architecture</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 1. Sector Switcher
    sector_mode = st.radio("SECTOR VIEW:", ["Küche (Produktion)", "Gastrodienste (Stewarding)", "Total Operations (Gesamt)"], horizontal=True)
    
    # Data Fetching
    if "Küche" in sector_mode:
        df = DataWarehouse.get_kitchen_data()
        current_sector = "kitchen"
    elif "Gastrodienste" in sector_mode:
        df = DataWarehouse.get_gastro_data()
        current_sector = "gastro"
    else:
        df = DataWarehouse.get_combined_data()
        current_sector = "total"

    # Settings
    col_ctrl1, col_ctrl2 = st.columns([4, 1])
    with col_ctrl2:
        mode_select = st.radio("Unit:", ["Zeit (Min)", "Wert (CHF)"], horizontal=True, label_visibility="collapsed")
        mode = 'money' if 'CHF' in mode_select else 'time'

    # KPIs Calculation
    if current_sector == "kitchen":
        kpis = KPI_Engine.calculate_kitchen(df, mode)
    elif current_sector == "gastro":
        kpis = KPI_Engine.calculate_gastro(df, mode)
    else:
        kpis = KPI_Engine.calculate_total(df, mode)

    # KPI Grid
    st.markdown(f'<div class="section-label" title="{SECTION_TOOLTIPS["Management Cockpit"]}">Management Cockpit: {sector_mode}</div>', unsafe_allow_html=True)
    
    # Grid Logic for 20 KPIs (4 Rows x 5 Cols)
    rows = (len(kpis) + 4) // 5
    for row in range(rows):
        cols = st.columns(5, gap="small")
        for col in range(5):
            idx = row * 5 + col
            if idx < len(kpis):
                with cols[col]:
                    render_kpi_card(kpis[idx][0], kpis[idx][1])

    # Load Curve
    st.markdown(f'<div class="section-label" title="{SECTION_TOOLTIPS["Belastungs-Matrix"]}">Belastungs-Matrix (Capacity vs. Demand)</div>', unsafe_allow_html=True)
    
    if current_sector == "total":
        # Stacked View for Total Operations
        workload_df = WorkloadEngine.get_load_curve(df)
        fig_load = go.Figure()
        
        # Kitchen Area (Blue / Push)
        fig_load.add_trace(go.Scatter(
            x=workload_df['Zeit'], y=workload_df['Load Kitchen'],
            mode='none', name='Kitchen Demand (Push)', stackgroup='one',
            fillcolor=COLORS['kitchen']
        ))
        # Gastro Area (Gray / Pull)
        fig_load.add_trace(go.Scatter(
            x=workload_df['Zeit'], y=workload_df['Load Gastro'],
            mode='none', name='Gastro Demand (Pull)', stackgroup='one',
            fillcolor=COLORS['gastro']
        ))
        # Total Capacity Line
        fig_load.add_trace(go.Scatter(
            x=workload_df['Zeit'], y=workload_df['Capacity (FTE)'],
            mode='lines', name='Total Staff (FTE)',
            line=dict(color='#0F172A', width=2, dash='dot')
        ))
    else:
        # Single View (Kitchen OR Gastro)
        workload_df = WorkloadEngine.get_load_curve(df, current_sector)
        
        # Restore Hint Text for Kitchen
        if current_sector == 'kitchen':
             st.markdown("""
            <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 10px;">
            <b>Analyse:</b> Graue Fläche zeigt anwesendes Personal (Kosten). Die Linie zeigt die echte Arbeitslast (Wertschöpfung). 
            Die Lücke dazwischen ist <b>Ineffizienz</b>.
            </div>
            """, unsafe_allow_html=True)

        fig_load = go.Figure()
        fig_load.add_trace(go.Scatter(
            x=workload_df['Zeit'], y=workload_df['Capacity (FTE)'],
            fill='tozeroy', mode='none', name='Verfügbare Kapazität',
            fillcolor='rgba(148, 163, 184, 0.2)'
        ))
        fig_load.add_trace(go.Scatter(
            x=workload_df['Zeit'], y=workload_df['Real Demand (FTE)'],
            mode='lines', name='Reale Belastung',
            line=dict(color=COLORS['accent'], width=3)
        ))

    fig_load.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, title=None, linecolor='#E2E8F0'),
        yaxis=dict(showgrid=True, gridcolor='#F1F5F9', title="FTE Load"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_load, use_container_width=True, config={'displayModeBar': False})

    # Deep Dive Tabs
    st.markdown(f'<div class="section-label" title="{SECTION_TOOLTIPS["Detail-Analyse"]}">Detail-Analyse</div>', unsafe_allow_html=True)
    
    def clean_chart_layout(fig):
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=10, r=10, t=30, b=20),
            xaxis=dict(showgrid=True, gridcolor='#F1F5F9', title=None), yaxis=dict(showgrid=False, title=None),
            font=dict(family="Inter", color="#64748B"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
        )
        return fig

    color_map = {
        "Prod": "#3B82F6", "Service": "#10B981", "Admin": "#F59E0B",
        "Logistik": "#64748B", "Potenzial": "#F43F5E", "Coord": "#8B5CF6",
        # Gastro Colors
        "Spülen": "#0EA5E9", "Transport": "#F97316", "Reinigung": "#14B8A6", "Service-Support": "#8B5CF6"
    }

    # RESTORE ALL 5 TABS FOR KITCHEN
    if current_sector == 'kitchen':
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Gantt-Flow", "Potenzial-Analyse", "Ressourcen-Balance", "Aktivitäts-Verteilung", "Skill-Match-Matrix"])
        
        with tab1:
            fig1 = px.timeline(df, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", hover_name="Task", color_discrete_map=color_map, height=600)
            fig1.update_yaxes(categoryorder="array", categoryarray=["H3","H2","H1","R2","R1","G2","S1","E1","D1"])
            st.plotly_chart(clean_chart_layout(fig1), use_container_width=True, config={'displayModeBar': False})

        with tab2:
            df_waste = df[df['Typ'] == 'Potenzial']
            if not df_waste.empty:
                fig2 = px.timeline(df_waste, x_start="Start_DT", x_end="End_DT", y="Dienst", hover_name="Task", color_discrete_sequence=["#F43F5E"], height=400)
                fig2.update_yaxes(categoryorder="array", categoryarray=["H3","H2","H1","R2","R1","G2","S1","E1","D1"])
                st.plotly_chart(clean_chart_layout(fig2), use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Keine expliziten Potenzial-Blöcke identifiziert.")
                
        with tab3:
            df_grouped = df.groupby(['Dienst', 'Typ'])['Duration'].sum().reset_index()
            fig3 = px.bar(df_grouped, x="Dienst", y="Duration", color="Typ", color_discrete_map=color_map, barmode='stack', height=500)
            fig3.update_layout(yaxis_title="Minuten (Soll: 504 Min)")
            # Add Reference Line for 8.4h Workday
            fig3.add_hline(y=504, line_dash="dot", line_color="#94A3B8", annotation_text="Standard Day (8.4h)", annotation_position="top right")
            st.plotly_chart(clean_chart_layout(fig3), use_container_width=True, config={'displayModeBar': False})
            
        with tab4:
            df_pie = df.groupby('Typ')['Duration'].sum().reset_index()
            fig4 = px.pie(df_pie, values='Duration', names='Typ', color='Typ', color_discrete_map=color_map, hole=0.6, height=500)
            fig4.update_traces(textinfo='percent+label', textfont_size=13)
            fig4.update_layout(showlegend=False, annotations=[dict(text='Total', x=0.5, y=0.5, font_size=20, showarrow=False)])
            st.plotly_chart(clean_chart_layout(fig4), use_container_width=True, config={'displayModeBar': False})

        with tab5:
            skill_pivot = df.groupby(['Dienst', 'Skill_Status'])['Duration'].sum().reset_index()
            fig_skill = px.bar(skill_pivot, x="Dienst", y="Duration", color="Skill_Status", 
                            color_discrete_map={"Kritische Fehlallokation": "#EF4444", "Ideal-Besetzung": "#10B981", "Fachliche Unterforderung": "#F59E0B", "Qualitäts-Risiko": "#6366F1"},
                            title="Qualifikations-Matrix: Identifikation von Ressourcen-Fehlallokation (Skill-Mismatch)")
            fig_skill.update_xaxes(categoryorder="array", categoryarray=["H3","H2","H1","R2","R1","G2","S1","E1","D1"])
            st.plotly_chart(clean_chart_layout(fig_skill), use_container_width=True, config={'displayModeBar': False})

    # DYNAMIC TABS FOR OTHER SECTORS
    else:
        tab1, tab2, tab3 = st.tabs(["Gantt-Flow", "Aktivitäts-Verteilung", "Skill-Match"])
        
        with tab1:
            fig1 = px.timeline(df, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", hover_name="Task", color_discrete_map=color_map, height=600 if current_sector == "total" else 400)
            if current_sector == "gastro":
                 fig1.update_yaxes(categoryorder="category ascending")
            st.plotly_chart(clean_chart_layout(fig1), use_container_width=True, config={'displayModeBar': False})

        with tab2:
            df_grouped = df.groupby(['Dienst', 'Typ'])['Duration'].sum().reset_index()
            fig3 = px.bar(df_grouped, x="Dienst", y="Duration", color="Typ", color_discrete_map=color_map, barmode='stack', height=500)
            st.plotly_chart(clean_chart_layout(fig3), use_container_width=True, config={'displayModeBar': False})

        with tab3:
            skill_pivot = df.groupby(['Dienst', 'Skill_Status'])['Duration'].sum().reset_index()
            fig_skill = px.bar(skill_pivot, x="Dienst", y="Duration", color="Skill_Status", 
                            color_discrete_map={
                                "Kritische Fehlallokation": "#EF4444", 
                                "Ideal-Besetzung": "#10B981", 
                                "Fachliche Unterforderung": "#F59E0B", 
                                "Qualitäts-Risiko": "#6366F1"
                            })
            st.plotly_chart(clean_chart_layout(fig_skill), use_container_width=True, config={'displayModeBar': False})

    # --- LOAD PROFILE (Common) ---
    st.markdown(f'<div class="section-label" title="{SECTION_TOOLTIPS["Personal-Einsatzprofil"]}">Personal-Einsatzprofil (Staffing Load)</div>', unsafe_allow_html=True)
    
    load_data = []
    for h in range(5, 20):
        for m in [0, 15, 30, 45]:
            t = datetime(2026, 1, 1, h, m)
            if current_sector == 'total':
                 active = len(df[(df['Start_DT'] <= t) & (df['End_DT'] > t)])
            elif current_sector == 'kitchen':
                 active = len(df[(df['Start_DT'] <= t) & (df['End_DT'] > t) & (df['Sector'] == 'kitchen')])
            else:
                 active = len(df[(df['Start_DT'] <= t) & (df['End_DT'] > t) & (df['Sector'] == 'gastro')])
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
            yaxis=dict(showgrid=True, gridcolor='#F1F5F9', title="Active FTE", range=[0, 25] if current_sector == 'total' else [0, 15]),
            hovermode="x unified"
        )
        # Critical Zone Line
        if current_sector == 'kitchen':
            fig_load_profile.add_hline(y=8, line_dash="dot", line_color="#EF4444", annotation_text="Congestion Zone", annotation_position="top right", annotation_font_color="#EF4444")
        st.plotly_chart(fig_load_profile, use_container_width=True, config={'displayModeBar': False})

def render_kpi_card(title, data):
    trend_color = data['trend']
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

if __name__ == "__main__":
    main()
