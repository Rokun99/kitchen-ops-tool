import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & CLINICAL STYLING ---
st.set_page_config(
    page_title="Kitchen Intelligence Master-Suite | 360° Audit",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; color: #0F172A; background-color: #F8FAFC; }
    
    .main-header { font-size: 26px; font-weight: 700; color: #1E293B; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 20px;}
    .cluster-header { font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 25px; margin-bottom: 12px; border-left: 3px solid #3B82F6; padding-left: 10px;}
    
    .kpi-card { background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 2px; padding: 14px; height: 105px; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03); display: flex; flex-direction: column; justify-content: space-between; }
    .kpi-title { font-size: 9px; font-weight: 700; text-transform: uppercase; color: #64748B; line-height: 1.2;}
    .kpi-value { font-size: 20px; font-weight: 700; color: #0F172A; }
    .kpi-sub { font-size: 10px; color: #94A3B8; }
    .trend-bad { color: #EF4444; font-weight: 600; }
    .trend-good { color: #10B981; font-weight: 600; }
    .ai-box { background: #F0F9FF; border-left: 4px solid #0EA5E9; padding: 20px; border-radius: 2px; font-size: 13px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE: THE COMPLETE CULINARY REPOSITORY (FULL AUDIT) ---
class DataWarehouse:
    @staticmethod
    def get_full_ist_data():
        # DATEN EXAKT NACH DEN NEUKALKULATIONS-BERICHTEN (ALLE 9 DIENSTE)
        # Basierend auf dem Dokument "Learnings Arbeitsbeschreibungen.docx"
        data = [
            # --- D1 DIÄTETIK (Der Admin-Spagat) ---
            {"Dienst": "D1", "Start": "08:00", "Ende": "08:25", "Task": "Admin: E-Mails/Mutationen", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "08:25", "Ende": "08:30", "Task": "Hygiene/Rüsten: Wechsel Büro-Küche", "Typ": "Logistik"},
            {"Dienst": "D1", "Start": "08:30", "Ende": "09:15", "Task": "Prod: Suppen (520 Port./130L)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:15", "Ende": "09:45", "Task": "Prod: ET (Ernährungstherapie/Allergene)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "09:45", "Ende": "10:00", "Task": "Admin: 2. Mail-Check (Spätmeldungen)", "Typ": "Admin"},
            # 10:00-10:15 Pause
            {"Dienst": "D1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Cg-Komp.", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "10:45", "Ende": "11:00", "Task": "Coord: Instruktion Band-MA", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "11:00", "Ende": "11:20", "Task": "Admin: Letzte Orgacard-Updates", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "11:20", "Ende": "12:20", "Task": "Service: Diät-Band (Crunch Time)", "Typ": "Service"},
            {"Dienst": "D1", "Start": "12:20", "Ende": "12:45", "Task": "Logistik: Abräumen/Kühlen/Rückstellproben", "Typ": "Logistik"},
            # 12:45-14:30 Pause & Lücke (Sicherheitsrisiko im Dok erwähnt)
            {"Dienst": "D1", "Start": "14:30", "Ende": "15:00", "Task": "Admin: Produktionsprotokolle", "Typ": "Admin"},
            {"Dienst": "D1", "Start": "15:00", "Ende": "15:50", "Task": "Prod: MEP Folgetag (Vegi/Cg)", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "15:50", "Ende": "16:30", "Task": "Prod: Abend Diät-Komp.", "Typ": "Prod"},
            {"Dienst": "D1", "Start": "16:30", "Ende": "17:00", "Task": "Coord: Service-Vorbereitung Abend", "Typ": "Coord"},
            {"Dienst": "D1", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band-Abendessen", "Typ": "Service"},
            {"Dienst": "D1", "Start": "18:00", "Ende": "18:09", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- E1 ENTREMETIER (Das Wahlkost-Dilemma) ---
            {"Dienst": "E1", "Start": "07:00", "Ende": "07:15", "Task": "Coord: Posten einrichten", "Typ": "Coord"},
            {"Dienst": "E1", "Start": "07:15", "Ende": "08:30", "Task": "Prod: Stärke (Kartoffeln/Reis 520 Pax)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "08:30", "Ende": "09:30", "Task": "Prod: Gemüse (520 Pax)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "09:30", "Ende": "09:45", "Task": "Prod: Suppe finalisieren", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "09:45", "Ende": "10:00", "Task": "Logistik: Bereitstellung Gastro", "Typ": "Logistik"},
            # 10:00-10:15 Pause
            {"Dienst": "E1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Wahlkost Spezial", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "10:45", "Ende": "11:20", "Task": "Prod: Regenerieren Band", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "11:20", "Ende": "12:30", "Task": "Waste: 70-Min-Falle (Bereitschaft/Warten)", "Typ": "Waste"},
            {"Dienst": "E1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Transport Reste Restaurant", "Typ": "Logistik"},
            {"Dienst": "E1", "Start": "12:45", "Ende": "13:00", "Task": "Logistik: Reinigung Clean-as-you-go", "Typ": "Logistik"},
            # 13:00-13:30 Pause
            {"Dienst": "E1", "Start": "13:30", "Ende": "14:00", "Task": "Prod: Wahlkost MEP", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "14:00", "Ende": "15:00", "Task": "Prod: MEP Folgetag (Großmenge)", "Typ": "Prod"},
            {"Dienst": "E1", "Start": "15:00", "Ende": "15:30", "Task": "Admin: QM-Kontrolle MHD", "Typ": "Admin"},
            {"Dienst": "E1", "Start": "15:30", "Ende": "15:54", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- S1 SAUCIER (Convenience Joker) ---
            {"Dienst": "S1", "Start": "07:00", "Ende": "07:30", "Task": "Prod: Saucen/Basis (Päckli) & Stock", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "07:30", "Ende": "08:30", "Task": "Prod: Fleisch Finish (Kurzbraten)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "08:30", "Ende": "09:30", "Task": "Coord: Support E1 (Pufferzeit)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "09:30", "Ende": "10:00", "Task": "Prod: Wahlkost Finish", "Typ": "Prod"},
            # 10:00-10:15 Pause
            {"Dienst": "S1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Regenerieren Fleisch/Sauce", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "10:45", "Ende": "11:00", "Task": "Logistik: Wagenübergabe Gastro", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "11:00", "Ende": "11:20", "Task": "Prod: Wahlkost Setup", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "11:20", "Ende": "12:30", "Task": "Waste: Wahlkost-Idle (Warten auf Bons)", "Typ": "Waste"},
            {"Dienst": "S1", "Start": "12:30", "Ende": "12:45", "Task": "Logistik: Nachschub Restaurant", "Typ": "Logistik"},
            {"Dienst": "S1", "Start": "12:45", "Ende": "13:00", "Task": "Logistik: Reinigung Kipper", "Typ": "Logistik"},
            # 13:00-13:30 Pause
            {"Dienst": "S1", "Start": "13:30", "Ende": "14:15", "Task": "Admin: Planung/TK-Management", "Typ": "Admin"},
            {"Dienst": "S1", "Start": "14:15", "Ende": "15:00", "Task": "Prod: MEP Folgetag (Fleisch marinieren)", "Typ": "Prod"},
            {"Dienst": "S1", "Start": "15:00", "Ende": "15:30", "Task": "Coord: Support G2/D1 (Puffer)", "Typ": "Coord"},
            {"Dienst": "S1", "Start": "15:30", "Ende": "15:54", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- R1 GASTRO (Der Schmutzig-zu-Sauber Konflikt) ---
            {"Dienst": "R1", "Start": "06:30", "Ende": "07:15", "Task": "Logistik: Warenannahme Rampe (HACCP Risiko)", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:15", "Ende": "07:30", "Task": "Logistik: Verräumen Kühlhaus", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "07:30", "Ende": "07:45", "Task": "Waste: Hygiene-Schleuse/Umziehen", "Typ": "Waste"},
            {"Dienst": "R1", "Start": "07:45", "Ende": "08:30", "Task": "Admin: Manuelle Deklaration", "Typ": "Admin"},
            {"Dienst": "R1", "Start": "08:30", "Ende": "09:30", "Task": "Prod: MEP Folgetag (Freeflow)", "Typ": "Prod"},
            {"Dienst": "R1", "Start": "09:30", "Ende": "10:00", "Task": "Service: Setup Heute (Verbrauchsmaterial)", "Typ": "Service"},
            # 10:00-10:20 Pause
            {"Dienst": "R1", "Start": "10:20", "Ende": "10:45", "Task": "Logistik: Transport Speisen", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "10:45", "Ende": "11:00", "Task": "Service: Einsetzen Buffet", "Typ": "Service"},
            {"Dienst": "R1", "Start": "11:00", "Ende": "11:15", "Task": "Coord: Quality Check/Showteller", "Typ": "Coord"},
            {"Dienst": "R1", "Start": "11:15", "Ende": "11:30", "Task": "Waste: Bereitschaft", "Typ": "Waste"},
            {"Dienst": "R1", "Start": "11:30", "Ende": "13:30", "Task": "Service: Mittagsservice Gastro", "Typ": "Service"},
            {"Dienst": "R1", "Start": "13:30", "Ende": "14:00", "Task": "Logistik: Abbau Buffet", "Typ": "Logistik"},
            {"Dienst": "R1", "Start": "14:00", "Ende": "14:30", "Task": "Logistik: Reinigung Office", "Typ": "Logistik"},

            # --- R2 GASTRO (Der Leerlauf-König) ---
            {"Dienst": "R2", "Start": "06:30", "Ende": "06:50", "Task": "Service: Band-Setup (Patienten)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "06:50", "Ende": "07:45", "Task": "Service: Band-Service (Falsche Zuordnung)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "07:45", "Ende": "08:00", "Task": "Logistik: Wechsel Patient->Gastro", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "08:00", "Ende": "08:30", "Task": "Waste: Salat-Finish (Gedehnt 12 Stk)", "Typ": "Waste"},
            {"Dienst": "R2", "Start": "08:30", "Ende": "09:00", "Task": "Logistik: Office/Abfall (Botengänge)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "09:00", "Ende": "09:30", "Task": "Logistik: Geräte-Check (Muda)", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "09:30", "Ende": "10:00", "Task": "Waste: Leerlauf/Puffer", "Typ": "Waste"},
            # 10:00-10:20 Pause
            {"Dienst": "R2", "Start": "10:20", "Ende": "10:45", "Task": "Logistik: Transport", "Typ": "Logistik"},
            {"Dienst": "R2", "Start": "10:45", "Ende": "11:00", "Task": "Prod: Fritteusen Start", "Typ": "Prod"},
            {"Dienst": "R2", "Start": "11:00", "Ende": "11:30", "Task": "Coord: Show-Setup (Redundanz)", "Typ": "Coord"},
            {"Dienst": "R2", "Start": "11:30", "Ende": "13:30", "Task": "Service: Mittagsservice & ReCircle", "Typ": "Service"},
            {"Dienst": "R2", "Start": "13:30", "Ende": "14:00", "Task": "Service: Food Rescue (Verkauf)", "Typ": "Service"},
            {"Dienst": "R2", "Start": "14:00", "Ende": "14:30", "Task": "Logistik: Fritteuse aus/Reinigung", "Typ": "Logistik"},

            # --- H1 FRÜHSTÜCK (Der Zwitter) ---
            {"Dienst": "H1", "Start": "05:30", "Ende": "06:00", "Task": "Prod: Birchermüsli/Brei", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "06:00", "Ende": "06:30", "Task": "Prod: Rahm/Dessert Vorb.", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "06:30", "Ende": "06:50", "Task": "Service: Band-Setup", "Typ": "Service"},
            {"Dienst": "H1", "Start": "06:50", "Ende": "07:45", "Task": "Service: Band Frühstück", "Typ": "Service"},
            {"Dienst": "H1", "Start": "07:45", "Ende": "08:15", "Task": "Logistik: Aufräumen/Auffüllen", "Typ": "Logistik"},
            {"Dienst": "H1", "Start": "08:15", "Ende": "09:15", "Task": "Prod: Dessert/Patisserie (Redundanz H2)", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "09:15", "Ende": "10:00", "Task": "Prod: Salat Vorbereitung (Redundanz G2)", "Typ": "Prod"},
            # 10:00-10:15 Pause
            {"Dienst": "H1", "Start": "10:15", "Ende": "10:45", "Task": "Prod: Glacé portionieren", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "10:45", "Ende": "11:25", "Task": "Prod: Käse schneiden", "Typ": "Prod"},
            {"Dienst": "H1", "Start": "11:25", "Ende": "12:30", "Task": "Service: Band Mittagsservice", "Typ": "Service"},

            # --- H2 PÄTISSERIE (Handlanger-Rolle) ---
            {"Dienst": "H2", "Start": "09:15", "Ende": "09:30", "Task": "Prod: Basis-Massen (Convenience)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "09:30", "Ende": "10:15", "Task": "Prod: Restaurant-Finish (25 Gläser)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "10:15", "Ende": "11:00", "Task": "Prod: Patienten-Masse (Abfüllen)", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "11:00", "Ende": "11:15", "Task": "Logistik: Transport Gastro", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "11:15", "Ende": "11:45", "Task": "Logistik: Wagen-Bau Abend", "Typ": "Logistik"},
            {"Dienst": "H2", "Start": "11:45", "Ende": "12:30", "Task": "Prod: Power-Dessert", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "12:30", "Ende": "13:00", "Task": "Service: Privat-Zvieri", "Typ": "Service"},
            {"Dienst": "H2", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Reinigung", "Typ": "Logistik"},
            # 13:30-14:15 Pause
            {"Dienst": "H2", "Start": "14:15", "Ende": "15:15", "Task": "Prod: Morgen Gastro", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "15:15", "Ende": "16:00", "Task": "Prod: Morgen Pat", "Typ": "Prod"},
            {"Dienst": "H2", "Start": "16:00", "Ende": "16:30", "Task": "Coord: Support H1", "Typ": "Coord"},
            {"Dienst": "H2", "Start": "16:30", "Ende": "17:00", "Task": "Service: Setup Abend", "Typ": "Service"},
            {"Dienst": "H2", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band Abendessen", "Typ": "Service"},
            {"Dienst": "H2", "Start": "18:00", "Ende": "18:09", "Task": "Logistik: Abschluss", "Typ": "Logistik"},

            # --- H3 ASSEMBLY LINE (Der Worker) ---
            {"Dienst": "H3", "Start": "09:15", "Ende": "09:45", "Task": "Prod: Wähen Montage (Convenience)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "09:45", "Ende": "10:30", "Task": "Prod: Sandwiches", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "10:30", "Ende": "11:15", "Task": "Prod: Salatteller", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "11:15", "Ende": "12:00", "Task": "Prod: Abend Kalt (Platten)", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:00", "Ende": "12:30", "Task": "Prod: Bircher-Masse für Morgen", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "12:30", "Ende": "13:00", "Task": "Logistik: Reste/Saucen", "Typ": "Logistik"},
            {"Dienst": "H3", "Start": "13:00", "Ende": "13:30", "Task": "Logistik: Reinigung", "Typ": "Logistik"},
            # 13:30-14:15 Pause
            {"Dienst": "H3", "Start": "14:15", "Ende": "15:15", "Task": "Prod: Salatbuffet", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "15:15", "Ende": "16:00", "Task": "Prod: Wähen-Vorbereitung Morgen", "Typ": "Prod"},
            {"Dienst": "H3", "Start": "16:00", "Ende": "16:30", "Task": "Coord: Support", "Typ": "Coord"},
            {"Dienst": "H3", "Start": "16:30", "Ende": "17:00", "Task": "Service: Setup Band", "Typ": "Service"},
            {"Dienst": "H3", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band Abend Support", "Typ": "Service"},
            {"Dienst": "H3", "Start": "18:00", "Ende": "18:30", "Task": "Logistik: Abschluss Kaltküche", "Typ": "Logistik"},

            # --- G2 GARDE-MANGER (Der Teilzeit-Produzent) ---
            {"Dienst": "G2", "Start": "09:30", "Ende": "09:45", "Task": "Coord: Absprache H3", "Typ": "Coord"},
            {"Dienst": "G2", "Start": "09:45", "Ende": "10:30", "Task": "Prod: Wahlkost Kalt (Montage)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "10:30", "Ende": "11:15", "Task": "Prod: Patienten-Salat (Beutel)", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "11:15", "Ende": "12:30", "Task": "Prod: Abendessen (Aufschnitt)", "Typ": "Prod"},
            # 12:30-14:15 Pause (Standard-Split)
            {"Dienst": "G2", "Start": "14:15", "Ende": "15:00", "Task": "Prod: MEP Folgetag", "Typ": "Prod"},
            {"Dienst": "G2", "Start": "15:00", "Ende": "16:00", "Task": "Waste: Leerlauf/Dehnung (Standard-Tag)", "Typ": "Waste"},
            {"Dienst": "G2", "Start": "16:00", "Ende": "17:00", "Task": "Coord: Band-Setup", "Typ": "Coord"},
            {"Dienst": "G2", "Start": "17:00", "Ende": "18:00", "Task": "Service: Band-Abendessen", "Typ": "Service"},
            {"Dienst": "G2", "Start": "18:00", "Ende": "18:30", "Task": "Admin: Hotellerie-Check", "Typ": "Admin"},
        ]
        return DataWarehouse.process(data)

    @staticmethod
    def process(data):
        df = pd.DataFrame(data)
        df['Start_DT'] = pd.to_datetime('2026-01-01 ' + df['Start'])
        df['End_DT'] = pd.to_datetime('2026-01-01 ' + df['Ende'])
        df['Duration'] = (df['End_DT'] - df['Start_DT']).dt.total_seconds() / 60
        return df

# --- 3. ANALYTICAL SCORECARD (16 KPIs) ---
def render_master_scorecard(df_ist):
    st.markdown('<div class="cluster-header">Strategische Performance-Indikatoren (Management Summary)</div>', unsafe_allow_html=True)
    
    total_min = df_ist['Duration'].sum()
    waste_min = df_ist[df_ist['Typ'] == 'Waste']['Duration'].sum()
    
    # Fachkräfte (Skilled)
    skilled_dienste = ['D1', 'S1', 'E1', 'G2', 'R1']
    
    # Leakage: Wenn Fachkräfte Logistik oder Waste machen
    leakage_min = df_ist[(df_ist['Dienst'].isin(skilled_dienste)) & (df_ist['Typ'].isin(['Logistik', 'Waste']))]['Duration'].sum()
    leakage = (leakage_min / total_min) * 100
    
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Skill-Grade Fehlallokation</div><div class="kpi-value">{leakage:.1f}%</div><div class="kpi-sub trend-bad">Teure Fachkraftzeit in Supportrollen</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Parkinson Ratio (Muda)</div><div class="kpi-value">{(waste_min/total_min*100):.1f}%</div><div class="kpi-sub trend-bad">Bezahlter Leerlauf / Tag</div></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Kernzeit-Vakuum</div><div class="kpi-value">125 Min</div><div class="kpi-sub trend-bad">Summierter Leerlauf am Band</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Context-Switch Rate</div><div class="kpi-value">5.0x</div><div class="kpi-sub trend-bad">Büro-Küche Wechsel D1</div></div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Liability Gap</div><div class="kpi-value">105 Min</div><div class="kpi-sub trend-bad">Unbesetzte Diätetik (Pause D1)</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Recovery Potenzial</div><div class="kpi-value">1.35 FTE</div><div class="kpi-sub trend-good">Freisetzbare Kapazität</div></div>', unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Industrialisierungsgrad</div><div class="kpi-value">72%</div><div class="kpi-sub">Anteil Montage vs. Kochen</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Patient/Gastro Split</div><div class="kpi-value">62/38</div><div class="kpi-sub">Ressourcen-Allokation</div></div>', unsafe_allow_html=True)

# --- 4. MAIN APPLICATION ---
def main():
    st.markdown('<div class="main-header">KITCHEN INTELLIGENCE SUITE: DEEP AUDIT 2026</div>', unsafe_allow_html=True)
    
    dw = DataWarehouse()
    df_ist = dw.get_full_ist_data()
    render_master_scorecard(df_ist)

    # --- LOAD CURVE ---
    st.markdown('<div class="cluster-header">Personal-Einsatzprofil am Band (15-Minuten Auflösung)</div>', unsafe_allow_html=True)
    load_data = []
    # 05:00 bis 20:00 Uhr
    for h in range(5, 20):
        for m in [0, 15, 30, 45]:
            t = datetime(2026, 1, 1, h, m)
            # Zähle aktive Dienste in diesem Timeslot
            active = len(df_ist[(df_ist['Start_DT'] <= t) & (df_ist['End_DT'] > t)])
            load_data.append({"Zeit": f"{h:02d}:{m:02d}", "Staff": active})
    
    fig_load = px.area(pd.DataFrame(load_data), x="Zeit", y="Staff", line_shape="spline")
    fig_load.update_traces(line_color="#0F172A", fillcolor="rgba(15, 23, 42, 0.05)")
    fig_load.update_layout(plot_bgcolor="white", height=250, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Personen")
    st.plotly_chart(fig_load, use_container_width=True)

    # --- TIMELINES ---
    st.markdown('<div class="cluster-header">Zeit-Struktur & Transformations-Szenarien</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔴 IST-ZUSTAND (AUDIT-DETAIL)", "⚠️ VERSCHWENDUNGS-ISO (MUDA)"])

    color_map = {"Prod": "#3B82F6", "Service": "#10B981", "Admin": "#F59E0B", "Logistik": "#64748B", "Waste": "#EF4444", "Coord": "#8B5CF6"}

    with tab1:
        fig1 = px.timeline(df_ist, x_start="Start_DT", x_end="End_DT", y="Dienst", color="Typ", hover_name="Task", color_discrete_map=color_map, height=650)
        # Sortierung der Achse nach Hierarchie/Funktion
        fig1.update_yaxes(categoryorder="array", categoryarray=["H3","H2","H1","R2","R1","G2","S1","E1","D1"])
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        df_waste = df_ist[df_ist['Typ'] == 'Waste']
        if not df_waste.empty:
            fig2 = px.timeline(df_waste, x_start="Start_DT", x_end="End_DT", y="Dienst", hover_name="Task", color_discrete_sequence=["#EF4444"], height=400)
            fig2.update_yaxes(categoryorder="array", categoryarray=["H3","H2","H1","R2","R1","G2","S1","E1","D1"])
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Keine expliziten Waste-Blöcke identifiziert.")

    # --- AI SECTION ---
    st.markdown('<div class="cluster-header">KI-Befund & Begründung (Professor Flash)</div>', unsafe_allow_html=True)
    if st.button("Deep-Audit Analyse durch KI anfordern"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Prompt angepasst an die neuen Daten
            prompt = f"""
            Analysiere diesen detaillierten IST-Zustand (9 Dienste).
            Gehe spezifisch auf folgende Ineffizienzen ein, die in den Daten sichtbar sind:
            1. D1: Die 'Admin-Zerstückelung' (4x Büro-Wechsel).
            2. E1 & S1: Die '70-Minuten-Falle' (Warten auf Wahlkost).
            3. R1: Der 'Hygienische Sündenfall' am Morgen (Rampe -> Küche).
            4. H1/H2: Die Kompetenz-Überschneidung bei Desserts.
            
            Gib eine kurze, scharfe Management-Summary mit Einsparpotenzial.
            Daten-Auszug: {df_ist[['Dienst', 'Task', 'Duration', 'Typ']].to_dict()}
            """
            with st.spinner("KI analysiert Prozessdaten..."):
                response = model.generate_content(prompt)
                st.markdown(f'<div class="ai-box">{response.text}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"KI-Service nicht erreichbar. (Error: {str(e)}) Bitte API-Key prüfen.")

if __name__ == "__main__":
    main()
