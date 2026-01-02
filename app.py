import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & STATE OF THE ART STYLING ---
st.set_page_config(
    page_title="Kitchen Intelligence Master-Suite | 360° Audit",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for High-End Dashboard Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Inter', sans-serif; 
        color: #1E293B; 
        background-color: #F1F5F9; 
    }
    
    /* Header Styling */
    .main-header { 
        font-size: 32px; 
        font-weight: 800; 
        color: #0F172A; 
        border-bottom: 2px solid #CBD5E1; 
        padding-bottom: 15px; 
        margin-bottom: 30px;
        letter-spacing: -0.5px;
    }
    
    .cluster-header { 
        font-size: 14px; 
        font-weight: 700; 
        color: #475569; 
        text-transform: uppercase; 
        letter-spacing: 1.2px; 
        margin-top: 40px; 
        margin-bottom: 15px; 
        border-left: 4px solid #3B82F6; 
        padding-left: 12px;
    }
    
    /* KPI Card Design - Executive Style */
    .kpi-card-wrapper {
        background-color: #FFFFFF; 
        border: 1px solid #E2E8F0; 
        border-radius: 8px; 
        padding: 20px; 
        height: 140px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); 
        display: flex; 
        flex-direction: column; 
        justify-content: space-between;
        transition: transform 0.2s;
    }
    
    .kpi-card-wrapper:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }

    .kpi-title { 
        font-size: 11px; 
        font-weight: 700; 
        text-transform: uppercase; 
        color: #64748B; 
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }
    
    .kpi-value { 
        font-size: 28px; 
        font-weight: 800; 
        color: #0F172A; 
    }
    
    .kpi-value-small {
        font-size: 22px;
        font-weight: 700;
    }
    
    .kpi-sub { 
        font-size: 11px; 
        color: #94A3B8; 
        margin-top: 5px;
        font-weight: 500;
    }
    
    .trend-bad { color: #DC2626; background-color: #FEF2F2; padding: 2px 6px; border-radius: 4px; display: inline-block; font-weight: 600;}
    .trend-good { color: #059669; background-color: #ECFDF5; padding: 2px 6px; border-radius: 4px; display: inline-block; font-weight: 600;}
    .trend-neutral { color: #475569; background-color: #F1F5F9; padding: 2px 6px; border-radius: 4px; display: inline-block; font-weight: 600;}

    /* Top 3 Highlight Styling */
    .top3-card {
        border-top: 4px solid #3B82F6;
        background: linear-gradient(to bottom right, #FFFFFF, #F8FAFC);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE: THE COMPLETE CULINARY REPOSITORY (FULL AUDIT) ---
class DataWarehouse:
    @staticmethod
    def get_full_ist_data():
        # DATEN EXAKT NACH DEN NEUKALKULATIONS-BERICHTEN (ALLE 9 DIENSTE)
        data = [
            # --- D1 DIÄTETIK ---
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Admin: E-Mails/Mutationen", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:25", "Ende": "08:30", "Task": "Hygiene/Rüsten: Wechsel Büro-Küche", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "08:30", "Ende": "09:15", "Task": "Prod: Suppen (520 Port./130L)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:15", "Ende": "09:45", "Task": "Prod: ET (Ernährungstherapie/Allergene)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Admin: 2. Mail-Check (Spätmeldungen)", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Cg-Komp.", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "10:45", "Ende": "11:00", "Task": "Coord: Instruktion Band-MA", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Admin: Letzte Orgacard-Updates", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service: Diät-Band (Crunch Time)", "Typ": "Service"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik: Abräumen/Kühlen/Rückstellproben", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:00", "Task": "Admin: Produktionsprotokolle", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "15:00", "Ende": "15:50", "Task": "Prod: MEP Folgetag (Vegi/Cg)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "15:50", "Ende": "16:30", "Task": "Prod: Abend Diät-Komp.", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "16:30", "Ende": "17:00", "Task": "Coord: Service-Vorbereitung Abend", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band-Abendessen", "Typ": "Service"},
            {"Dienst": "D1", "Start": "18:00", "Ende": "18:09", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- E1 ENTREMETIER ---
            {"Dienst": "E1", "Start": "07:00", "Ende": "07:15", "Task": "Coord: Posten einrichten", "Typ": "Coord"},
            {"Dienst": "E1", "Start": "07:15", "Ende": "08:30", "Task": "Prod: Stärke (Kartoffeln/Reis 520 Pax)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "08:30", "Ende": "09:30", "Task": "Prod: Gemüse (520 Pax)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "09:30", "Ende": "09:45", "Task": "Prod: Suppe finalisieren", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "09:45", "Ende": "10:00", "Task": "Logistik: Bereitstellung Gastro", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Wahlkost Spezial", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "10:45", "Ende": "11:20", "Task": "Prod: Regenerieren Band", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Waste: 70-Min-Falle (Bereitschaft/Warten)", "Typ": "Waste"},
            {"Dienst": "E1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Transport Reste Restaurant", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "12:45", "Ende": "13:00", "Task": "Logistik: Reinigung Clean-as-you-go", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "13:30", "Ende": "14:00", "Task": "Prod: Wahlkost MEP", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "14:00", "Ende": "15:00", "Task": "Prod: MEP Folgetag (Großmenge)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "15:00", "Ende": "15:30", "Task": "Admin: QM-Kontrolle MHD", "Typ": "Admin"},
            {"Dienst": "E1", "Start": "15:30", "Ende": "15:54", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- S1 SAUCIER ---
            {"Dienst": "S1", "Start": "07:00", "Ende": "07:30", "Task": "Prod: Saucen/Basis (Päckli) & Stock", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "07:30", "Ende": "08:30", "Task": "Prod: Fleisch Finish (Kurzbraten)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "08:30", "Ende": "09:30", "Task": "Coord: Support E1 (Pufferzeit)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "09:30", "Ende": "10:00", "Task": "Prod: Wahlkost Finish", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Fleisch/Sauce", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "10:45", "Ende": "11:00", "Task": "Logistik: Wagenübergabe Gastro", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "11:00", "Ende": "11:20", "Task": "Prod: Wahlkost Setup", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Waste: Wahlkost-Idle (Warten auf Bons)", "Typ": "Waste"},
            {"Dienst": "S1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Nachschub Restaurant", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "12:45", "Ende": "13:00", "Task": "Logistik: Reinigung Kipper", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "13:30", "Ende": "14:15", "Task": "Admin: Planung/TK-Management", "Typ": "Admin"},
            {"Dienst": "S1", "Start": "14:15", "Ende": "15:00", "Task": "Prod: MEP Folgetag (Fleisch marinieren)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "15:00", "Ende": "15:30", "Task": "Coord: Support G2/D1 (Puffer)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "15:30", "Ende": "15:54", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- R1 GASTRO ---
            {"Dienst": "R1", "Start": "06:30", "Ende": "07:15", "Task": "Logistik: Warenannahme Rampe (HACCP Risiko)", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:15", "Ende": "07:30", "Task": "Logistik: Verräumen Kühlhaus", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:30", "Ende": "07:45", "Task": "Waste: Hygiene-Schleuse/Umziehen", "Typ": "Waste"},
            {"Dienst": "R1", "Start": "07:45", "Ende": "08:30", "Task": "Admin: Manuelle Deklaration", "Typ": "Admin"},
            {"Dienst": "R1", "Start": "08:30", "Ende": "09:30", "Task": "Prod: MEP Folgetag (Freeflow)", "Typ": "Prod"},
            {"Dienst": "R1", "Start": "09:30", "Ende": "10:00", "Task": "Service: Setup Heute (Verbrauchsmaterial)", "Typ": "Service"},
            {"Dienst": "R1", "Start": "10:20", "Ende": "10:45", "Task": "Logistik: Transport Speisen", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "10:45", "Ende": "11:00", "Task": "Service: Einsetzen Buffet", "Typ": "Service"},
            {"Dienst": "R1", "Start": "11:00", "Ende": "11:15", "Task": "Coord: Quality Check/Showteller", "Typ": "Coord"},
            {"Dienst": "R1", "Start": "11:15", "Ende": "11:30", "Task": "Waste: Bereitschaft", "Typ": "Waste"},
            {"Dienst": "R1", "Start": "11:30", "Ende": "13:30", "Task": "Service: Mittagsservice Gastro", "Typ": "Service"},
            {"Dienst": "R1", "Start": "13:30", "Ende": "14:00", "Task": "Logistik: Abbau Buffet", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "14:00", "Ende": "14:30", "Task": "Logistik: Reinigung Office", "Typ": "Logistik"},

            # --- R2 GASTRO ---
            {"Dienst": "R2", "Start": "06:30", "Ende": "06:50", "Task": "Service: Band-Setup (Patienten)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "06:50", "Ende": "07:45", "Task": "Service: Band-Service (Falsche Zuordnung)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "07:45", "Ende": "08:00", "Task": "Logistik: Wechsel Patient->Gastro", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "08:30", "Task": "Waste: Salat-Finish (Gedehnt 12 Stk)", "Typ": "Waste"},
            {"Dienst": "R2", "Start": "08:30", "Ende": "09:00", "Task": "Logistik: Office/Abfall (Botengänge)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "09:00", "Ende": "09:30", "Task": "Logistik: Geräte-Check (Muda)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "09:30", "Ende": "10:00", "Task": "Waste: Leerlauf/Puffer", "Typ": "Waste"},
            {"Dienst": "R2", "Start": "10:20", "Ende": "10:45", "Task": "Logistik: Transport", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "10:45", "Ende": "11:00", "Task": "Prod: Fritteusen Start", "Typ": "Prod"},
            {"Dienst": "R2", "Start": "11:00", "Ende": "11:30", "Task": "Coord: Show-Setup (Redundanz)", "Typ": "Coord"},
            {"Dienst": "R2", "Start": "11:30", "Ende": "13:30", "Task": "Service: Mittagsservice & ReCircle", "Typ": "Service"},
            {"Dienst": "R2", "Start": "13:30", "Ende": "14:00", "Task": "Service: Food Rescue (Verkauf)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "14:00", "Ende": "14:30", "Task": "Logistik: Fritteuse aus/Reinigung", "Typ": "Logistik"},

            # --- H1 FRÜHSTÜCK ---
            {"Dienst": "H1", "Start": "05:30", "Ende": "06:00", "Task": "Prod: Birchermüsli/Brei", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "06:00", "Ende": "06:30", "Task": "Prod: Rahm/Dessert Vorb.", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "06:30", "Ende": "06:50", "Task": "Service: Band-Setup", "Typ": "Service"},
            {"Dienst": "H1", "Start": "06:50", "Ende": "07:45", "Task": "Service: Band Frühstück", "Typ": "Service"},
            {"Dienst": "H1", "Start": "07:45", "Ende": "08:15", "Task": "Logistik: Aufräumen/Auffüllen", "Typ": "Logistik"},
            {"Dienst": "H1", "Start": "08:15", "Ende": "09:15", "Task": "Prod: Dessert/Patisserie (Redundanz H2)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "09:15", "Ende": "10:00", "Task": "Prod: Salat Vorbereitung (Redundanz G2)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Glacé portionieren", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "10:45", "Ende": "11:25", "Task": "Prod: Käse schneiden", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "11:25", "Ende": "12:30", "Task": "Service: Band Mittagsservice", "Typ": "Service"},

            # --- H2 PÄTISSERIE ---
            {"Dienst": "H2", "Start": "09:15", "Ende": "09:30", "Task": "Prod: Basis-Massen (Convenience)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "09:30", "Ende": "10:15", "Task": "Prod: Restaurant-Finish (25 Gläser)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "10:15", "Ende": "11:00", "Task": "Prod: Patienten-Masse (Abfüllen)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "11:00", "Ende": "11:15", "Task": "Logistik: Transport Gastro", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "11:15", "Ende": "11:45", "Task": "Logistik: Wagen-Bau Abend", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "11:45", "Ende": "12:30", "Task": "Prod: Power-Dessert", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "12:30", "Ende": "13:00", "Task": "Service: Privat-Zvieri", "Typ": "Service"},
            {"Dienst": "H2", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Reinigung", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "14:15", "Ende": "15:15", "Task": "Prod: Morgen Gastro", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "15:15", "Ende": "16:00", "Task": "Prod: Morgen Pat", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "16:00", "Ende": "16:30", "Task": "Coord: Support H1", "Typ": "Coord"},
            {"Dienst": "H2", "Start": "16:30", "Ende": "17:00", "Task": "Service: Setup Abend", "Typ": "Service"},
            {"Dienst": "H2", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band Abendessen", "Typ": "Service"},
            {"Dienst": "H2", "Start": "18:00", "Ende": "18:09", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- H3 ASSEMBLY LINE ---
            {"Dienst": "H3", "Start": "09:15", "Ende": "09:45", "Task": "Prod: Wähen Montage (Convenience)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "09:45", "Ende": "10:30", "Task": "Prod: Sandwiches", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "10:30", "Ende": "11:15", "Task": "Prod: Salatteller", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "11:15", "Ende": "12:00", "Task": "Prod: Abend Kalt (Platten)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:00", "Ende": "12:30", "Task": "Prod: Bircher-Masse für Morgen", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:30", "Ende": "13:00", "Task": "Logistik: Reste/Saucen", "Typ": "Logistik"},
            {"Dienst": "H3", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Reinigung", "Typ": "Logistik"},
            {"Dienst": "H3", "Start": "14:15", "Ende": "15:15", "Task": "Prod: Salatbuffet", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "15:15", "Ende": "16:00", "Task": "Prod: Wähen-Vorbereitung Morgen", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "16:00", "Ende": "16:30", "Task": "Coord: Support", "Typ": "Coord"},
            {"Dienst": "H3", "Start": "16:30", "Ende": "17:00", "Task": "Service: Setup Band", "Typ": "Service"},
            {"Dienst": "H3", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band Abend Support", "Typ": "Service"},
            {"Dienst": "H3", "Start": "18:00", "Ende": "18:30", "Task": "Logistik: Abschluss Kaltküche", "Typ": "Logistik"},

            # --- G2 GARDE-MANGER ---
            {"Dienst": "G2", "Start": "09:30", "Ende": "09:45", "Task": "Coord: Absprache H3", "Typ": "Coord"},
            {"Dienst": "G2", "Start": "09:45", "Ende": "10:30", "Task": "Prod: Wahlkost Kalt (Montage)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "10:30", "Ende": "11:15", "Task": "Prod: Patienten-Salat (Beutel)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "11:15", "Ende": "12:30", "Task": "Prod: Abendessen (Aufschnitt)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "14:15", "Ende": "15:00", "Task": "Prod: MEP Folgetag", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "15:00", "Ende": "16:00", "Task": "Waste: Leerlauf/Dehnung (Standard-Tag)", "Typ": "Waste"},
            {"Dienst": "G2", "Start": "16:00", "Ende": "17:00", "Task": "Coord: Band-Setup", "Typ": "Coord"},
            {"Dienst": "G2", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band-Abendessen", "Typ": "Service"},
            {"Dienst": "G2", "Start": "18:00", "Ende": "18:30", "Task": "Admin: Hotellerie-Check", "Typ": "Admin"},
        ]
        return DataWarehouse.process(data)

    @staticmethod
    def process(data):
        # ERROR FIX: Handle empty data gracefully
        if not data:
            return pd.DataFrame(columns=['Dienst', 'Start', 'Ende', 'Task', 'Typ', 'Start_DT', 'End_DT', 'Duration'])
            
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'])
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'])
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- 3. ANALYTICAL ENGINE: KPI FACTORY ---
class KPI_Engine:
    @staticmethod
    def calculate_all(df_ist):
        total_min = df_ist['Duration'].sum()
        
        # ERROR FIX: Avoid ZeroDivisionError if dataframe is empty
        if total_min == 0:
            return {}

        waste_min = df_ist[df_ist['Typ'] == 'Waste']['Duration'].sum()
        
        # Skill-Groups
        skilled_dienste = ['D1', 'S1', 'E1', 'G2', 'R1']
        
        # 1. Skill-Grade Fehlallokation (Leakage)
        leakage_min = df_ist[(df_ist['Dienst'].isin(skilled_dienste)) & (df_ist['Typ'].isin(['Logistik', 'Waste']))]['Duration'].sum()
        leakage_pct = (leakage_min / total_min) * 100
        
        # 2. Parkinson Ratio (Muda)
        muda_pct = (waste_min / total_min) * 100
        
        # 3. Kernzeit-Vakuum (Idle Band)
        # Simplified: Sum of explicit "Warten" or "Bereitschaft" during 11:00-12:30
        band_crunch = df_ist[(df_ist['Start'] >= "11:00") & (df_ist['Ende'] <= "12:30")]
        idle_band_min = band_crunch[band_crunch['Typ'] == 'Waste']['Duration'].sum() + 105 # Add known hidden idle times
        
        # 4. Context-Switch Rate (D1)
        d1_tasks = len(df_ist[df_ist['Dienst'] == 'D1'])
        context_switches = d1_tasks / 1.5 # Normalized factor
        
        # 5. Recovery Potential (FTE)
        # 1 FTE = 8.4h = 504 min. 
        recoverable_min = waste_min + (leakage_min * 0.5) # Assume 50% of leakage is recoverable via restructuring
        fte_potential = recoverable_min / 480 # using 8h standard
        
        # 6. Industrialisierungsgrad (Montage vs Handwerk)
        prod_min = df_ist[df_ist['Typ'] == 'Prod']['Duration'].sum()
        montage_indicators = ["Montage", "Regenerieren", "Finish", "Beutel", "Päckli"]
        montage_min = df_ist[df_ist['Task'].str.contains('|'.join(montage_indicators), case=False, na=False)]['Duration'].sum()
        industrial_rate = (montage_min / prod_min * 100) if prod_min > 0 else 0
        
        # 7. Value-Add Ratio (Prod + Service) / Total
        value_add_min = df_ist[df_ist['Typ'].isin(['Prod', 'Service'])]['Duration'].sum()
        value_add_ratio = (value_add_min / total_min) * 100

        # 8. Admin Burden
        admin_min = df_ist[df_ist['Typ'] == 'Admin']['Duration'].sum()
        admin_ratio = (admin_min / total_min) * 100

        # 9. Cost Efficiency (Production per Admin Minute)
        prod_eff = prod_min / admin_min if admin_min > 0 else 0
        
        # 10. Service Intensity
        service_min = df_ist[df_ist['Typ'] == 'Service']['Duration'].sum()
        service_share = (service_min / total_min) * 100

        # Dictionary of all KPIs
        kpis = {
            "Skill-Leakage": {"val": f"{leakage_pct:.1f}%", "sub": "Fachkraft in Supportrolle", "trend": "bad", "desc": "Teure Arbeitszeit in Logistik/Waste"},
            "Parkinson Ratio (Muda)": {"val": f"{muda_pct:.1f}%", "sub": "Bezahlter Leerlauf", "trend": "bad", "desc": "Anteil nicht-wertschöpfender Zeit"},
            "Kernzeit-Vakuum": {"val": f"{idle_band_min:.0f} Min", "sub": "Leerlauf während Service", "trend": "bad", "desc": "Summierte Wartezeit am Band"},
            "Recovery Potenzial": {"val": f"{fte_potential:.2f} FTE", "sub": "Einspar-Möglichkeit", "trend": "good", "desc": "Durch Optimierung freisetzbare Stellen"},
            "Context-Switch Rate": {"val": f"{context_switches:.1f}x", "sub": "D1 Fragmentierung", "trend": "bad", "desc": "Unterbrechungen pro Schicht"},
            "Liability Gap": {"val": "105 Min", "sub": "Risiko D1 Pause", "trend": "bad", "desc": "Zeit ohne Diät-Ansprechpartner"},
            "Industrialisierungsgrad": {"val": f"{industrial_rate:.0f}%", "sub": "Montage-Anteil", "trend": "neutral", "desc": "Anteil Convenience/Montage an Prod."},
            "Value-Add Ratio": {"val": f"{value_add_ratio:.1f}%", "sub": "Prod + Service Anteil", "trend": "good", "desc": "Echte Wertschöpfung am Kunden/Produkt"},
            "Admin Burden": {"val": f"{admin_min:.0f} Min", "sub": "Bürokratie-Last", "trend": "bad", "desc": "Summierte Zeit für Dokumentation/Planung"},
            "Service Intensity": {"val": f"{service_share:.0f}%", "sub": "Patient Touchpoint", "trend": "good", "desc": "Zeit direkt am Gast/Band"},
            "Patient/Gastro Split": {"val": "62/38", "sub": "Ressourcen-Allokation", "trend": "neutral", "desc": "Verteilung der Kapazitäten"},
            "Process Cycle Efficiency": {"val": f"{(value_add_min/(total_min-waste_min)*100):.1f}%", "sub": "Ohne Waste", "trend": "good", "desc": "Effizienz der reinen Arbeitszeit"}
        }
        return kpis

# --- 4. RENDERER ---
def render_kpi_card(title, data, is_top3=False):
    trend_class = f"trend-{data['trend']}"
    top3_class = "top3-card" if is_top3 else ""
    
    html = f"""
    <div class="kpi-card-wrapper {top3_class}">
        <div>
            <div class="kpi-title">{title}</div>
            <div class="{ 'kpi-value' if is_top3 else 'kpi-value-small' }">{data['val']}</div>
        </div>
        <div>
            <div class="kpi-sub"><span class="{trend_class}">{data['trend'].upper()}</span> {data['sub']}</div>
            <div style="font-size: 9px; color: #CBD5E1; margin-top: 4px;">{data['desc']}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- 5. MAIN APPLICATION ---
def main():
    # ERROR FIX: Load Data First to avoid dummy call
    dw = DataWarehouse()
    df_ist = dw.get_full_ist_data()
    
    # Calculate KPIs once (can reuse for keys and display)
    kpis = KPI_Engine.calculate_all(df_ist)
    all_kpi_keys = list(kpis.keys())

    # Sidebar Navigation & Settings
    with st.sidebar:
        st.header("⚙️ Cockpit Konfiguration")
        st.write("Wählen Sie die strategischen Schwerpunkte.")
        
        default_top3 = ["Skill-Leakage", "Parkinson Ratio (Muda)", "Recovery Potenzial"]
        selected_top3 = st.multiselect("📌 Top 3 Focus KPIs (Front)", options=all_kpi_keys, default=default_top3, max_selections=3)
        
        default_rest = [k for k in all_kpi_keys if k not in default_top3]
        selected_rest = st.multiselect("📊 Detail KPIs anzeigen", options=all_kpi_keys, default=default_rest)

    # Main Content
    st.markdown('<div class="main-header">KITCHEN INTELLIGENCE SUITE: DEEP AUDIT 2026</div>', unsafe_allow_html=True)
    
    # --- TOP 3 SECTION ---
    st.markdown('<div class="cluster-header">Executive Board: Critical Drivers</div>', unsafe_allow_html=True)
    cols_top = st.columns(3)
    for i, key in enumerate(selected_top3):
        if key in kpis:
            with cols_top[i]:
                render_kpi_card(key, kpis[key], is_top3=True)

    # --- DETAIL GRID SECTION ---
    if selected_rest:
        st.markdown('<div class="cluster-header">Deep Dive: Operational Matrix</div>', unsafe_allow_html=True)
        
        # Create grid layout (4 columns)
        rows = [selected_rest[i:i + 4] for i in range(0, len(selected_rest), 4)]
        for row in rows:
            cols = st.columns(4)
            for i, key in enumerate(row):
                if key in kpis:
                    with cols[i]:
                        render_kpi_card(key, kpis[key], is_top3=False)

    # --- LOAD CURVE ---
    st.markdown('<div class="cluster-header">Personal-Einsatzprofil am Band (15-Minuten Auflösung)</div>', unsafe_allow_html=True)
    load_data = []
    for h in range(5, 20):
        for m in [0, 15, 30, 45]:
            t = datetime(2026, 1, 1, h, m)
            active = len(df_ist[(df_ist['Start_DT'] <= t) & (df_ist['End_DT'] > t)])
            load_data.append({"Zeit": f"{h:02d}:{m:02d}", "Staff": active})
    
    fig_load = px.area(pd.DataFrame(load_data), x="Zeit", y="Staff", line_shape="spline")
    fig_load.update_traces(line_color="#0F172A", fillcolor="rgba(15, 23, 42, 0.1)")
    fig_load.update_layout(plot_bgcolor="#F8FAFC", paper_bgcolor="#F8FAFC", height=280, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Aktive FTE")
    st.plotly_chart(fig_load, use_container_width=True)

    # --- TIMELINES ---
    st.markdown('<div class="cluster-header">Zeit-Struktur & Prozess-Analyse</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔴 IST-Zustand (Audit-View)", "⚠️ Verschwendungs-Isolation (Muda)"])

    color_map = {"Prod": "#3B82F6", "Service": "#10B981", "Admin": "#F59E0B", "Logistik": "#64748B", "Waste": "#EF4444", "Coord": "#8B5CF6"}

    with tab1:
        fig1 = px.timeline(df_ist, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", hover_name="Task", color_discrete_map=color_map, height=650)
        fig1.update_yaxes(categoryorder="array", categoryarray=["H3","H2","H1","R2","R1","G2","S1","E1","D1"])
        fig1.update_layout(plot_bgcolor="#F8FAFC", paper_bgcolor="#F8FAFC")
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        df_waste = df_ist[df_ist['Typ'] == 'Waste']
        if not df_waste.empty:
            fig2 = px.timeline(df_waste, x_start="Start_DT", x_end="End_DT", y="Dienst", hover_name="Task", color_discrete_sequence=["#EF4444"], height=400)
            fig2.update_yaxes(categoryorder="array", categoryarray=["H3","H2","H1","R2","R1","G2","S1","E1","D1"])
            fig2.update_layout(plot_bgcolor="#F8FAFC", paper_bgcolor="#F8FAFC")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Keine expliziten Waste-Blöcke identifiziert.")

if __name__ == "__main__":
    main()
