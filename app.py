import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────────────────
# 1. CONFIGURATION & STYLING
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WORKSPACE: TOTAL",
    layout="wide",
    initial_sidebar_state="collapsed"
)

COLORS = {
    "bg":         "#F8FAFC",
    "card":       "#FFFFFF",
    "text_main":  "#0F172A",
    "text_sub":   "#64748B",
    "accent":     "#6366F1",
    "success":    "#10B981",
    "danger":     "#F43F5E",
    "warning":    "#F59E0B",
    "neutral":    "#94A3B8",
    "border":     "#E2E8F0",
    "kitchen":    "#3B82F6",
    "gastro":     "#64748B",
}

KPI_BENCHMARKS = {
    "Wertschöpfungs-Quote":     {"target": 65.0, "unit": "%", "direction": "higher_better"},
    "Produktiv-Quote":          {"target": 62.0, "unit": "%", "direction": "higher_better"},
    "Admin-Quote":              {"target": 8.0,  "unit": "%", "direction": "lower_better"},
    "Logistik-Anteil":          {"target": 15.0, "unit": "%", "direction": "lower_better"},
    "Industrialisierungsgrad":  {"target": 70.0, "unit": "%", "direction": "neutral"},
    "Aufgaben-Wechselrate":     {"target": 8.0,  "unit": "x", "direction": "lower_better"},
    "Fachkraft-Fremdeinsatz":   {"target": 0.0,  "unit": "min","direction": "lower_better"},
    "Peak Demand Ratio":        {"target": 2.0,  "unit": "x", "direction": "lower_better"},
}

# (Optional: Dictionary mit Erklärungen für Tooltips)
KPI_DEFINITIONS = {
    "Fachkraft-Fremdeinsatz":   "Anteil der Zeit, in der teure Fachkräfte einfache Routinetätigkeiten erledigen.",
    "Potenzial (Leerlauf)":     "Nicht-wertschöpfende Zeit durch Warten oder unnötige Wege.",
    "Jahres-Einsparpotenzial":  "Monetärer Wert der unproduktiven Zeiten, hochgerechnet auf 250 Arbeitstage.",
    "Kapazitäts-Überhang":      "Stunden, in denen mehr Personal anwesend ist, als für die Arbeit nötig wäre.",
    "Kernzeit-Vakuum":          "Unproduktive Wartezeit während der kritischen Service-Phasen (Bandstillstand).",
    "Aufgaben-Wechselrate":     "Wie oft muss ein Mitarbeiter pro Schicht die Tätigkeit wechseln (Fragmentierung).",
    "Industrialisierungsgrad":  "Anteil von Convenience-Komponenten vs. Eigenfertigung.",
    "Wertschöpfungs-Quote":     "Anteil der Zeit, die direkt in das Produkt (Kochen) oder den Gast fließt.",
    "Admin-Quote":              "Zeitaufwand für Büro, Dokumentation und Systempflege.",
    "Logistik-Anteil":          "Zeitverlust durch interne Transporte und Rüstwege.",
    "Koordinations-Aufwand":    "Zeit für Absprachen, Meetings und Übergaben.",
    "Risiko-Fenster":           "Zeiträume ohne klare Verantwortlichkeit oder Aufsicht.",
    "Patienten-Fokus":          "Anteil der Arbeitszeit mit direktem Einfluss auf das Patientenerlebnis.",
    "Ressourcen-Split":         "Verhältnis Personalbindung Küche vs. Gastro (in % Gesamtminuten).",
    "Prozess-Effizienz":        "Anteil wertschöpfender Tätigkeiten (Prod+Service+Coord) an der Gesamtarbeitszeit.",
    "Max. Personal-Last":       "Maximale Anzahl Mitarbeiter gleichzeitig im Einsatz.",
    "Arbeits-Dehnung (R2)":     "Indikator für verlangsamtes Arbeiten (Parkinson) im Dienst R2 mangels Last.",
    "Profil-Verwässerung (H1)": "Einsatz des H1 für aufgabenfremde Tätigkeiten.",
    "Hygiene-Risiko (R1)":      "Kritische Wechseldauer zwischen Schmutz- und Reinbereich.",
    "Leerlauf-Lücke (G2)":      "Explizite, ungenutzte Zeit im Dienst G2.",
    "Teure Ausführung":         "Einsatz von High-Skill-Personal für Low-Skill-Aufgaben (Kosten-Sicht).",
    "Transport-Intensität":     "Anteil der Arbeitszeit für reine Wegstrecken (Wagen schieben/holen).",
    "Aufzug-Abhängigkeit":      "Zeitrisiko durch Wartezeiten vor den Liften (simuliert).",
    "Rücklauf-Tempo":           "Dauer von 'Abholung Station' bis 'Eingabe Spülmaschine'.",
    "Wagen-Umschlag":           "Wie oft wird ein Speisewagen pro Tag genutzt/gedreht.",
    "Logistik-Wartezeit":       "Leere Wege oder Warten auf Transportmittel (vermeidbar).",
    "Laufzeit Bandmaschine":    "Aktive Betriebszeit der Hauptwaschstrasse.",
    "Auslastung Topfspüle":     "Nutzungsgrad der Granuldisk (Indikator für Produktionsmenge).",
    "Chemie-Effizienz":         "Verbrauch Reinigungsmittel pro Spülgang (simuliert).",
    "Korb-Durchsatz":           "Gesamtmenge gewaschener Körbe pro Stunde.",
    "Wartungs-Quote":           "Zeitaufwand für Pflege & Reinigung der Maschinen (Werterhalt).",
    "Hygiene-Switch (11:20)":   "Einhaltung des kritischen Wechselslots 'Schmutzig zu Sauber'.",
    "Bio-Trans Volumen":        "Menge entsorgter Speisereste (Messwert 156g/Gast × 1150 Gäste).",
    "Integrität Reine Seite":   "Personaldichte im sauberen Bereich (Vermeidung Rekontamination).",
    "Grundreinigungs-Index":    "Investierte Zeit in Tiefenreinigung (Böden/Wände).",
    "HACCP-Doku":               "Zeitaufwand für gesetzlich vorgeschriebene Listenführung.",
    "Service-Support":          "Entlastung der Küche durch Gastro-Personal (Anrichten/Besteck).",
    "Ergonomie-Belastung":      "Anteil körperlich schwerer Arbeit (Heben >15kg / Zwangshaltungen).",
    "Übergabe-Qualität":        "Zeitinvest für saubere Schichtübergaben.",
    "Alleinarbeits-Risiko":     "Stunden, in denen Mitarbeiter in kritischen Zonen alleine sind (Sicherheit).",
    "Springer-Potenzial":       "Anteil der Aufgaben, die zeitlich flexibel verschoben werden können.",
    "Kosten pro Tablett":       "Personalkosten geteilt durch Anzahl Mahlzeiten.",
    "Kosten-Split":             "Verhältnis Küche vs. Gastro (berechnet aus Gesamtminuten).",
    "Gesamt-Produktivität":     "Mahlzeiten pro geleistete Personalstunde (Total).",
    "Leerlauf-Kosten":          "Monetärer Wert der nicht-wertschöpfenden Zeit (Total).",
    "Überstunden-Risiko":       "Wahrscheinlichkeit für Arbeitszeitüberschreitung durch Abendspitzen.",
    "Sync-Lücke":               "Zeitversatz zwischen Produktionsende und Spül-Ende.",
    "Service-Bereitschaft":     "Verfügbarkeit von Besteck/Geschirr bei Bandstart.",
    "Mise-en-Place Sync":       "Greifen Vorbereitung (Küche) und Bereitstellung (Gastro) ineinander?",
    "Max. Personal (Total)":    "Höchststand an Mitarbeitern gleichzeitig im Haus.",
    "Absprache-Aufwand":        "Summe der Koordinationszeiten über alle Abteilungen.",
    "Energie-Spitzenlast":      "Gleichzeitige Nutzung von Kipper, Ofen und Spülstraße.",
    "Raum-Dichte":              "Personaldichte in Küche/Spüle zu Stosszeiten (Stressfaktor).",
    "Reste-Quote":              "Verhältnis Food Waste zu produziertem Essen.",
    "Anlagen-Nutzung (ROI)":    "Wie gut sind teure Maschinen ausgelastet?",
    "Verbrauchs-Proxy":         "Geschätzter Wasser/Stromverbrauch basierend auf Aktivität.",
    "System-Resilienz":         "Pufferzeiten bei Ausfall von Technik (z.B. Lift).",
    "Hygiene-Risiko Total":     "Summe aller kritischen Kontaktpunkte.",
    "Patienten-Kontakt":        "Anzahl der Interaktionen, die den Patienten erreichen.",
    "Prozess-Standard":         "Anteil der Aufgaben, die klar definiert vs. improvisiert sind.",
    "Führungs-Spanne":          "Verhältnis Führungskräfte zu operativen Stunden (Ideal 1:8).",
    "Produktiv-Quote":          "Anteil von Produktions- und Servicezeit an der Gesamtarbeitszeit.",
    "Peak Demand Ratio":        "Verhältnis von Spitzenlast zu Durchschnittslast (Planbarkeit).",
    "Idle Time":                "Expliziter und impliziter Leerlauf pro Schicht."
}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="st-"] {{
        font-family: 'DM Sans', sans-serif;
        color: {COLORS['text_main']};
        background-color: {COLORS['bg']};
    }}

    /* ── Segmented Control ─────────────────────────────── */
    div[role="radiogroup"] input[type="radio"] {{ display: none; }}

    div[role="radiogroup"] {{
        background: #F1F5F9;
        padding: 4px;
        border-radius: 10px;
        border: 1px solid {COLORS['border']};
        display: flex;
        flex-direction: row;
        gap: 0 !important;
        width: 100%;
    }}
    div[role="radiogroup"] label {{
        flex: 1;
        background: transparent;
        border: none;
        border-radius: 8px;
        margin: 0 !important;
        padding: 8px 12px !important;
        text-align: center;
        font-weight: 500 !important;
        color: {COLORS['text_sub']} !important;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    div[role="radiogroup"] label:hover {{
        color: {COLORS['text_main']} !important;
        background: rgba(255,255,255,0.5);
    }}
    div[role="radiogroup"] label:has(input:checked) {{
        background: #FFFFFF !important;
        color: {COLORS['accent']} !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.10), 0 1px 2px rgba(0,0,0,0.06);
        transform: scale(1.02);
    }}

    /* ── KPI Card (Modernisiert) ───────────────────────── */
    .kpi-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.15rem 1.25rem 1rem;
        height: 100%;
        min-height: 118px;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }}

    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 
            0 12px 24px -6px rgba(99,102,241,0.08),
            0 4px 8px -2px rgba(0,0,0,0.04);
        border-color: #C7D2FE;
    }}

    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: {COLORS['border']};
        transition: background 0.18s ease;
    }}
    .kpi-card.trend-bad::before  {{ background: linear-gradient(90deg, #F43F5E, #FB7185); }}
    .kpi-card.trend-good::before {{ background: linear-gradient(90deg, #10B981, #34D399); }}
    .kpi-card.trend-neutral::before {{ background: {COLORS['neutral']}; }}
    
    .kpi-label {{
        font-size: 0.68rem;
        font-weight: 600;
        color: {COLORS['text_sub']};
        text-transform: uppercase;
        letter-spacing: 0.06em;
        line-height: 1.3;
    }}
    .kpi-metric {{
        font-size: 1.55rem;
        font-weight: 700;
        color: {COLORS['text_main']};
        line-height: 1.1;
        margin: 0.35rem 0;
        font-family: 'DM Mono', monospace;
    }}
    .kpi-footer {{
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 2px;
    }}
    .kpi-sub {{
        font-size: 0.7rem;
        color: {COLORS['text_sub']};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* ── Tags ──────────────────────────────────────────── */
    .tag {{
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        display: inline-block;
        letter-spacing: 0.04em;
        white-space: nowrap;
        flex-shrink: 0;
    }}
    .tag-bad     {{ background:#FEF2F2; color:{COLORS['danger']};  border:1px solid #FECACA; }}
    .tag-good    {{ background:#ECFDF5; color:{COLORS['success']}; border:1px solid #A7F3D0; }}
    .tag-neutral {{ background:#F1F5F9; color:{COLORS['text_sub']};border:1px solid {COLORS['border']}; }}

    /* ── Section Labels ────────────────────────────────── */
    .section-label {{
        font-size: 0.72rem;
        font-weight: 700;
        color: {COLORS['text_sub']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 1.6rem 0 0.6rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid {COLORS['border']};
        cursor: help;
    }}

    /* ── Dashboard Header ──────────────────────────────── */
    .dash-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {COLORS['border']};
    }}
    .dash-title {{
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: {COLORS['text_main']};
        margin: 0;
    }}
    .dash-sub {{
        font-size: 0.78rem;
        color: {COLORS['text_sub']};
        margin-top: 2px;
    }}
    .dash-badge {{
        font-size: 0.7rem;
        font-weight: 600;
        background: #EEF2FF;
        color: {COLORS['accent']};
        border: 1px solid #C7D2FE;
        border-radius: 6px;
        padding: 4px 10px;
    }}

    /* Streamlit Chrome Cleanup */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.5rem !important; padding-bottom: 2rem !important; }}
    [data-testid="stAppViewContainer"] > .main {{ background: {COLORS['bg']}; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# 2. SKILL LEVELS & DATA WAREHOUSE
# ─────────────────────────────────────────────────────────
SKILL_LEVELS = {
    "D1": 3, "S1": 3, "E1": 3, "G2": 2, "H2": 2,
    "R1": 2, "H1": 2, "H3": 1, "R2": 1,
    "K1": 1, "K2": 1, "K5": 1, "K6": 1, "K7": 1,
    "K8": 2, "K10": 1, "K11": 2, "K13": 2, "K14": 1, "K15": 1,
}

HOURLY_RATES_CHF = {
    "D1": 62.0, "S1": 58.0, "E1": 58.0,
    "H1": 38.0, "H2": 38.0, "H3": 34.0, "G2": 34.0,
    "R1": 42.0, "R2": 34.0,
    "K1": 32.0, "K2": 32.0, "K5": 32.0, "K6": 32.0,
    "K7": 32.0, "K8": 34.0, "K10": 32.0, "K11": 34.0,
    "K13": 34.0, "K14": 32.0, "K15": 32.0,
}
HOURLY_RATE_CHF_DEFAULT = 38.0
WORK_DAYS_YEAR  = 250
N_MEALS         = 1_150

class DataWarehouse:
    @staticmethod
    def _process(data: list, sector: str) -> pd.DataFrame:
        df = pd.DataFrame(data)
        df["Start_DT"]  = pd.to_datetime("2026-01-01 " + df["Start"])
        df["End_DT"]    = pd.to_datetime("2026-01-01 " + df["Ende"])
        df["Duration"]  = (df["End_DT"] - df["Start_DT"]).dt.total_seconds() / 60
        df["Sector"]    = sector
        df["Skill_Status"] = df.apply(DataWarehouse._skill_match, axis=1)
        
        # NEU: Stundensätze & Kosten
        df["Hourly_Rate"] = df["Dienst"].map(HOURLY_RATES_CHF).fillna(HOURLY_RATE_CHF_DEFAULT)
        df["Cost_CHF"] = (df["Duration"] / 60) * df["Hourly_Rate"]
        return df

    @staticmethod
    def _skill_match(row) -> str:
        user_skill = SKILL_LEVELS.get(row["Dienst"], 1)
        task_level = 1
        if row["Typ"] in ("Coord", "Admin"):                         task_level = 2
        if "Mutationen" in row["Task"]:                              task_level = 3
        if row["Typ"] == "Prod" and any(k in row["Task"] for k in ("ET ", "Finish", "Allergene")):
            task_level = 3
        if row["Typ"] == "Service":                                  task_level = 2

        if user_skill == 3 and task_level == 1:   return "High-Cost Execution"
        if user_skill < 2  and task_level == 3:   return "Qualitäts-Risiko"
        return "Value-Add"

    @staticmethod
    def _derive_shifts(df: pd.DataFrame) -> pd.DataFrame:
        shifts = (df.groupby("Dienst")
                  .agg(
                      shift_start=("Start_DT", "min"),
                      shift_end=("End_DT", "max"),
                      total_task_min=("Duration", "sum"),
                      task_count=("Task", "count"),
                  )
                  .reset_index())
        shifts["shift_brutto_min"] = (shifts["shift_end"] - shifts["shift_start"]).dt.total_seconds() / 60
        shifts["pause_min"] = shifts["shift_brutto_min"] - shifts["total_task_min"]
        shifts["shift_netto_min"] = shifts["total_task_min"]
        shifts["hourly_rate"] = shifts["Dienst"].map(HOURLY_RATES_CHF).fillna(HOURLY_RATE_CHF_DEFAULT)
        shifts["shift_cost_chf"] = (shifts["shift_netto_min"] / 60) * shifts["hourly_rate"]
        return shifts

    # ── Kitchen ──────────────────────────────────────────
    @staticmethod
    def get_kitchen_data() -> pd.DataFrame:
        raw = [
            {"Dienst":"D1","Start":"08:00","Ende":"08:25","Task":"Admin: E-Mails/Mutationen/Diätpläne","Typ":"Admin"},
            {"Dienst":"D1","Start":"08:25","Ende":"08:30","Task":"Hygiene/Rüsten: Wechsel Büro-Küche","Typ":"Logistik"},
            {"Dienst":"D1","Start":"08:30","Ende":"09:15","Task":"Prod: Suppen (Basis/Convenience 520 Port.)","Typ":"Prod"},
            {"Dienst":"D1","Start":"09:15","Ende":"09:45","Task":"Prod: ET (System-Ableitung/Allergene)","Typ":"Prod"},
            {"Dienst":"D1","Start":"09:45","Ende":"10:00","Task":"Admin: 2. Mail-Check (Spätmeldungen)","Typ":"Admin"},
            {"Dienst":"D1","Start":"10:15","Ende":"10:45","Task":"Prod: Regenerieren Cg-Komp. (High-Convenience)","Typ":"Prod"},
            {"Dienst":"D1","Start":"10:45","Ende":"11:00","Task":"Coord: Instruktion Band-MA/Spezialessen","Typ":"Coord"},
            {"Dienst":"D1","Start":"11:00","Ende":"11:20","Task":"Admin: Letzte Orgacard-Updates","Typ":"Admin"},
            {"Dienst":"D1","Start":"11:20","Ende":"12:20","Task":"Service: Diät-Band (System-Ausgabe)","Typ":"Service"},
            {"Dienst":"D1","Start":"12:20","Ende":"12:45","Task":"Logistik: Abräumen/Kühlen/Rückstellproben","Typ":"Logistik"},
            {"Dienst":"D1","Start":"14:30","Ende":"15:00","Task":"Admin: Produktionsprotokolle Folgetag","Typ":"Admin"},
            {"Dienst":"D1","Start":"15:00","Ende":"15:50","Task":"Prod: MEP Folgetag (Vegi-Komponenten/Fertig)","Typ":"Prod"},
            {"Dienst":"D1","Start":"15:50","Ende":"16:30","Task":"Prod: Abend Diät-Komp. (Regenerieren/Garen)","Typ":"Prod"},
            {"Dienst":"D1","Start":"16:30","Ende":"17:00","Task":"Coord: Tablettkarten/Service-Setup","Typ":"Coord"},
            {"Dienst":"D1","Start":"17:00","Ende":"18:05","Task":"Service: Band-Abendessen","Typ":"Service"},
            {"Dienst":"D1","Start":"18:05","Ende":"18:09","Task":"Logistik: Aufräumen/To-Do Liste","Typ":"Logistik"},
            {"Dienst":"E1","Start":"07:00","Ende":"07:15","Task":"Coord: Posten einrichten","Typ":"Coord"},
            {"Dienst":"E1","Start":"07:15","Ende":"08:30","Task":"Prod: Stärke (Dämpfen/Convenience 520 Pax)","Typ":"Prod"},
            {"Dienst":"E1","Start":"08:30","Ende":"09:30","Task":"Prod: Gemüse (Dämpfen/Regenerieren 520 Pax)","Typ":"Prod"},
            {"Dienst":"E1","Start":"09:30","Ende":"09:45","Task":"Prod: Suppe Finalisieren (Basis)","Typ":"Prod"},
            {"Dienst":"E1","Start":"09:45","Ende":"10:00","Task":"Logistik: Bereitstellung Gastro","Typ":"Logistik"},
            {"Dienst":"E1","Start":"10:15","Ende":"10:45","Task":"Prod: Wahlkost Spezial (System/Minute)","Typ":"Prod"},
            {"Dienst":"E1","Start":"10:45","Ende":"11:20","Task":"Prod: Regenerieren Band (High-Convenience)","Typ":"Prod"},
            {"Dienst":"E1","Start":"11:20","Ende":"12:30","Task":"Potenzial: 70-Min-Falle (Bereitschaft/Warten)","Typ":"Potenzial"},
            {"Dienst":"E1","Start":"12:30","Ende":"12:45","Task":"Logistik: Transport Reste Restaurant","Typ":"Logistik"},
            {"Dienst":"E1","Start":"12:45","Ende":"13:00","Task":"Logistik: Reinigung Clean-as-you-go","Typ":"Logistik"},
            {"Dienst":"E1","Start":"13:30","Ende":"14:00","Task":"Prod: Wahlkost MEP Abend/Morgen (Vorbereitung)","Typ":"Prod"},
            {"Dienst":"E1","Start":"14:00","Ende":"15:00","Task":"Prod: MEP Folgetag (Großmenge/Schnittware)","Typ":"Prod"},
            {"Dienst":"E1","Start":"15:00","Ende":"15:30","Task":"Admin/QC: Kühlhäuser/MHDs/Ordnung","Typ":"Admin"},
            {"Dienst":"E1","Start":"15:30","Ende":"15:54","Task":"Logistik: Endreinigung Posten/Unterschriften","Typ":"Logistik"},
            {"Dienst":"S1","Start":"07:00","Ende":"07:30","Task":"Prod: Saucen/Basis (Päckli/Convenience)","Typ":"Prod"},
            {"Dienst":"S1","Start":"07:30","Ende":"08:30","Task":"Prod: Fleisch Finish (Kurzbraten/System)","Typ":"Prod"},
            {"Dienst":"S1","Start":"08:30","Ende":"09:30","Task":"Coord: Support E1 (Pufferzeit)","Typ":"Coord"},
            {"Dienst":"S1","Start":"09:30","Ende":"10:00","Task":"Prod: Wahlkost Finish (Montage)","Typ":"Prod"},
            {"Dienst":"S1","Start":"10:15","Ende":"10:45","Task":"Prod: Regenerieren Fleisch/Sauce/Wärmewägen","Typ":"Prod"},
            {"Dienst":"S1","Start":"10:45","Ende":"11:00","Task":"Logistik: Wagenübergabe Gastro","Typ":"Logistik"},
            {"Dienst":"S1","Start":"11:00","Ende":"11:20","Task":"Prod: Wahlkost Setup (Montage)","Typ":"Prod"},
            {"Dienst":"S1","Start":"11:20","Ende":"12:30","Task":"Potenzial: Wahlkost-Idle (Warten auf Bons)","Typ":"Potenzial"},
            {"Dienst":"S1","Start":"12:30","Ende":"12:45","Task":"Logistik: Nachschub Restaurant","Typ":"Logistik"},
            {"Dienst":"S1","Start":"12:45","Ende":"13:00","Task":"Logistik: Reinigung Kipper","Typ":"Logistik"},
            {"Dienst":"S1","Start":"13:30","Ende":"14:15","Task":"Admin: Produktionspläne/TK-Management","Typ":"Admin"},
            {"Dienst":"S1","Start":"14:15","Ende":"15:00","Task":"Prod: MEP Folgetag (Fleisch marinieren/Batch)","Typ":"Prod"},
            {"Dienst":"S1","Start":"15:00","Ende":"15:30","Task":"Admin/QC: Kühlhäuser/Temperaturen/MHDs","Typ":"Admin"},
            {"Dienst":"S1","Start":"15:30","Ende":"15:54","Task":"Logistik: Endreinigung Posten/Unterschriften","Typ":"Logistik"},
            {"Dienst":"R1","Start":"06:30","Ende":"07:15","Task":"Logistik: Warenannahme Rampe (HACCP Risiko)","Typ":"Logistik"},
            {"Dienst":"R1","Start":"07:15","Ende":"07:30","Task":"Logistik: Verräumen Kühlhaus","Typ":"Logistik"},
            {"Dienst":"R1","Start":"07:30","Ende":"07:45","Task":"Potenzial: Hygiene-Schleuse/Umziehen","Typ":"Potenzial"},
            {"Dienst":"R1","Start":"07:45","Ende":"08:30","Task":"Admin: Manuelle Deklaration/Intranet","Typ":"Admin"},
            {"Dienst":"R1","Start":"08:30","Ende":"09:30","Task":"Prod: MEP Folgetag (Freeflow/Montage)","Typ":"Prod"},
            {"Dienst":"R1","Start":"09:30","Ende":"10:00","Task":"Service: Setup Heute (Verbrauchsmaterial)","Typ":"Service"},
            {"Dienst":"R1","Start":"10:20","Ende":"10:45","Task":"Logistik: Transport Speisen (von G2/H2)","Typ":"Logistik"},
            {"Dienst":"R1","Start":"10:45","Ende":"11:00","Task":"Service: Einsetzen Buffet/Suppe","Typ":"Service"},
            {"Dienst":"R1","Start":"11:00","Ende":"11:15","Task":"Coord: Quality Check/Showteller/Foto","Typ":"Coord"},
            {"Dienst":"R1","Start":"11:15","Ende":"11:30","Task":"Potenzial: Bereitschaft","Typ":"Potenzial"},
            {"Dienst":"R1","Start":"11:30","Ende":"13:30","Task":"Service: Mittagsservice Gastro","Typ":"Service"},
            {"Dienst":"R1","Start":"13:30","Ende":"14:00","Task":"Logistik: Abbau Buffet/Entsorgen","Typ":"Logistik"},
            {"Dienst":"R1","Start":"14:30","Ende":"15:00","Task":"Logistik: Bestellungen für Folgetag/MEP","Typ":"Logistik"},
            {"Dienst":"R1","Start":"15:00","Ende":"15:24","Task":"Logistik: Endreinigung/Temp-Liste","Typ":"Logistik"},
            {"Dienst":"R2","Start":"06:30","Ende":"06:50","Task":"Service: Band-Setup (Patienten/Butter)","Typ":"Service"},
            {"Dienst":"R2","Start":"06:50","Ende":"07:45","Task":"Service: Band-Service (Falsche Zuordnung)","Typ":"Service"},
            {"Dienst":"R2","Start":"07:45","Ende":"08:00","Task":"Logistik: Wechsel Patient->Gastro","Typ":"Logistik"},
            {"Dienst":"R2","Start":"08:00","Ende":"08:30","Task":"Potenzial: Salat-Finish (Gedehnt 12 Stk)","Typ":"Potenzial"},
            {"Dienst":"R2","Start":"08:30","Ende":"09:00","Task":"Logistik: Office/Abfall (Botengänge)","Typ":"Logistik"},
            {"Dienst":"R2","Start":"09:00","Ende":"09:30","Task":"Logistik: Geräte-Check (Muda/Fritteuse)","Typ":"Logistik"},
            {"Dienst":"R2","Start":"09:30","Ende":"10:00","Task":"Potenzial: Leerlauf/Puffer","Typ":"Potenzial"},
            {"Dienst":"R2","Start":"10:20","Ende":"10:45","Task":"Logistik: Transport & Fritteuse Start","Typ":"Logistik"},
            {"Dienst":"R2","Start":"10:45","Ende":"11:00","Task":"Prod: Fritteuse (Pommes blanchieren)","Typ":"Prod"},
            {"Dienst":"R2","Start":"11:00","Ende":"11:30","Task":"Coord: Show-Setup/Foto (Redundanz)","Typ":"Coord"},
            {"Dienst":"R2","Start":"11:30","Ende":"13:30","Task":"Service: Mittagsservice & ReCircle","Typ":"Service"},
            {"Dienst":"R2","Start":"13:30","Ende":"14:00","Task":"Service: Food Rescue (Verkauf)","Typ":"Service"},
            {"Dienst":"R2","Start":"14:30","Ende":"15:00","Task":"Admin: Etiketten-Druck ReCircle/Deklaration","Typ":"Admin"},
            {"Dienst":"R2","Start":"15:00","Ende":"15:24","Task":"Logistik: Endreinigung/Bestellungen/Unterschrift","Typ":"Logistik"},
            {"Dienst":"H1","Start":"05:30","Ende":"06:00","Task":"Prod: Birchermüsli/Brei (Mischen/Convenience)","Typ":"Prod"},
            {"Dienst":"H1","Start":"06:00","Ende":"06:30","Task":"Prod: Rahm/Dessert Vorb. (Maschine)","Typ":"Prod"},
            {"Dienst":"H1","Start":"06:30","Ende":"06:50","Task":"Service: Band-Setup","Typ":"Service"},
            {"Dienst":"H1","Start":"06:50","Ende":"07:45","Task":"Service: Band Frühstück","Typ":"Service"},
            {"Dienst":"H1","Start":"07:45","Ende":"08:15","Task":"Logistik: Aufräumen/Auffüllen (Butter/Konfi)","Typ":"Logistik"},
            {"Dienst":"H1","Start":"08:15","Ende":"09:15","Task":"Prod: Dessert/Patisserie (Redundanz H2/Convenience)","Typ":"Prod"},
            {"Dienst":"H1","Start":"09:15","Ende":"10:00","Task":"Prod: Salat Vorbereitung (Redundanz G2/Beutel)","Typ":"Prod"},
            {"Dienst":"H1","Start":"10:15","Ende":"10:45","Task":"Prod: Glacé portionieren (System)","Typ":"Prod"},
            {"Dienst":"H1","Start":"10:45","Ende":"11:25","Task":"Prod: Käse schneiden (Maschine/Fertig)","Typ":"Prod"},
            {"Dienst":"H1","Start":"11:25","Ende":"12:30","Task":"Service: Band Mittagsservice","Typ":"Service"},
            {"Dienst":"H1","Start":"12:30","Ende":"12:45","Task":"Logistik: Material versorgen","Typ":"Logistik"},
            {"Dienst":"H1","Start":"13:30","Ende":"14:00","Task":"Prod: Menüsalat Abend (Vorbereitung)","Typ":"Prod"},
            {"Dienst":"H1","Start":"14:00","Ende":"14:20","Task":"Admin: Posten-Protokoll Folgetag","Typ":"Admin"},
            {"Dienst":"H1","Start":"14:20","Ende":"14:40","Task":"Logistik/Admin: Milchfrigor Kontrolle & Bestellung","Typ":"Admin"},
            {"Dienst":"H2","Start":"09:15","Ende":"09:30","Task":"Prod: Basis-Massen (Convenience/Pulver)","Typ":"Prod"},
            {"Dienst":"H2","Start":"09:30","Ende":"10:15","Task":"Prod: Restaurant-Finish (Montage 25 Gläser)","Typ":"Prod"},
            {"Dienst":"H2","Start":"10:15","Ende":"11:00","Task":"Prod: Patienten-Masse (Abfüllen/Convenience)","Typ":"Prod"},
            {"Dienst":"H2","Start":"11:00","Ende":"11:15","Task":"Logistik: Transport Gastro","Typ":"Logistik"},
            {"Dienst":"H2","Start":"11:15","Ende":"11:45","Task":"Logistik: Wagen-Bau Abend","Typ":"Logistik"},
            {"Dienst":"H2","Start":"11:45","Ende":"12:30","Task":"Prod: Power-Dessert (Anrühren/Päckli)","Typ":"Prod"},
            {"Dienst":"H2","Start":"12:30","Ende":"13:00","Task":"Service: Privat-Zvieri (Transport)","Typ":"Service"},
            {"Dienst":"H2","Start":"13:00","Ende":"13:30","Task":"Logistik: Puffer/Reinigung","Typ":"Logistik"},
            {"Dienst":"H2","Start":"14:15","Ende":"15:15","Task":"Prod: Dessert Gastro Folgetag (Abfüllen/System)","Typ":"Prod"},
            {"Dienst":"H2","Start":"15:15","Ende":"16:00","Task":"Prod: Dessert Pat Folgetag (Abfüllen/System)","Typ":"Prod"},
            {"Dienst":"H2","Start":"16:00","Ende":"16:30","Task":"Coord: Support H1/Glacé","Typ":"Coord"},
            {"Dienst":"H2","Start":"16:30","Ende":"17:00","Task":"Service: Setup Abend/Glacé","Typ":"Service"},
            {"Dienst":"H2","Start":"17:00","Ende":"18:00","Task":"Service: Band Abendessen","Typ":"Service"},
            {"Dienst":"H2","Start":"18:00","Ende":"18:09","Task":"Logistik: Abschluss/Material","Typ":"Logistik"},
            {"Dienst":"H3","Start":"09:15","Ende":"09:45","Task":"Prod: Wähen Montage (Convenience/Teig)","Typ":"Prod"},
            {"Dienst":"H3","Start":"09:45","Ende":"10:30","Task":"Prod: Sandwiches (System-Montage)","Typ":"Prod"},
            {"Dienst":"H3","Start":"10:30","Ende":"11:15","Task":"Prod: Salatteller (Montage/Beutel)","Typ":"Prod"},
            {"Dienst":"H3","Start":"11:15","Ende":"12:00","Task":"Prod: Abend Kalt (Platten/Legesystem)","Typ":"Prod"},
            {"Dienst":"H3","Start":"12:00","Ende":"12:30","Task":"Prod: Bircher-Masse für Morgen (Mischen)","Typ":"Prod"},
            {"Dienst":"H3","Start":"12:30","Ende":"13:00","Task":"Logistik: Reste/Saucen","Typ":"Logistik"},
            {"Dienst":"H3","Start":"13:00","Ende":"13:30","Task":"Logistik: Zwischenreinigung","Typ":"Logistik"},
            {"Dienst":"H3","Start":"14:15","Ende":"15:15","Task":"Prod: Salatbuffet/MEP (System)","Typ":"Prod"},
            {"Dienst":"H3","Start":"15:15","Ende":"16:00","Task":"Prod: Wähen/Creme Brulee (Vorbereitung)","Typ":"Prod"},
            {"Dienst":"H3","Start":"16:00","Ende":"16:30","Task":"Coord: Protokolle/Nachproduktion","Typ":"Coord"},
            {"Dienst":"H3","Start":"16:30","Ende":"17:00","Task":"Service: Setup Band","Typ":"Service"},
            {"Dienst":"H3","Start":"17:00","Ende":"18:00","Task":"Service: Band Abend Support","Typ":"Service"},
            {"Dienst":"H3","Start":"18:00","Ende":"18:09","Task":"Logistik: Abschluss Kaltküche","Typ":"Logistik"},
            {"Dienst":"G2","Start":"09:30","Ende":"09:45","Task":"Coord: Absprache H3","Typ":"Coord"},
            {"Dienst":"G2","Start":"09:45","Ende":"10:30","Task":"Prod: Wahlkost Kalt (System-Montage)","Typ":"Prod"},
            {"Dienst":"G2","Start":"10:30","Ende":"11:15","Task":"Prod: Patienten-Salat (Beutel/Convenience)","Typ":"Prod"},
            {"Dienst":"G2","Start":"11:15","Ende":"12:30","Task":"Prod: Abendessen (Aufschnitt/Montage)","Typ":"Prod"},
            {"Dienst":"G2","Start":"12:30","Ende":"13:30","Task":"Prod: Salate Folgetag/Zwischenreinigung","Typ":"Prod"},
            {"Dienst":"G2","Start":"14:15","Ende":"15:00","Task":"Prod: MEP Folgetag (System)","Typ":"Prod"},
            {"Dienst":"G2","Start":"15:00","Ende":"16:00","Task":"Potenzial: Leerlauf/Dehnung (Standard-Tag)","Typ":"Potenzial"},
            {"Dienst":"G2","Start":"16:00","Ende":"17:00","Task":"Coord: Band-Setup/Nachproduktion","Typ":"Coord"},
            {"Dienst":"G2","Start":"17:00","Ende":"18:00","Task":"Service: Band-Abendessen","Typ":"Service"},
            {"Dienst":"G2","Start":"18:00","Ende":"18:30","Task":"Admin: Hotellerie-Check/To-Do Liste","Typ":"Admin"},
        ]
        return DataWarehouse._process(raw, "kitchen")

    # ── Gastro ───────────────────────────────────────────
    @staticmethod
    def get_gastro_data() -> pd.DataFrame:
        raw = [
            {"Dienst":"K1","Start":"06:45","Ende":"07:00","Task":"Mise en Place: Bain-Marie & Förderband","Typ":"Service-Support"},
            {"Dienst":"K1","Start":"07:00","Ende":"08:00","Task":"Frühstücksband: Bestückung & Ausgabesupport","Typ":"Service-Support"},
            {"Dienst":"K1","Start":"08:00","Ende":"08:15","Task":"Vorbereitung Band für Reinigung","Typ":"Service-Support"},
            {"Dienst":"K1","Start":"08:15","Ende":"08:45","Task":"Speisewagen retour holen","Typ":"Transport"},
            {"Dienst":"K1","Start":"08:45","Ende":"09:30","Task":"Speisewagen von Stationen retour holen","Typ":"Transport"},
            {"Dienst":"K1","Start":"09:30","Ende":"10:00","Task":"Recycling: Trennung Wertstoffe aus Rücklauf","Typ":"Logistik"},
            {"Dienst":"K1","Start":"10:00","Ende":"10:30","Task":"Leergut-Handling & Wäschesäcke sortieren","Typ":"Logistik"},
            {"Dienst":"K1","Start":"10:30","Ende":"11:20","Task":"Komplette Entsorgung (Bio-Trans, Kehricht)","Typ":"Logistik"},
            {"Dienst":"K1","Start":"11:20","Ende":"11:30","Task":"Händewaschen & Vorbereitung Mittagsband","Typ":"Reinigung"},
            {"Dienst":"K1","Start":"11:30","Ende":"12:15","Task":"Mittagsband: Station Suppen schöpfen","Typ":"Service-Support"},
            {"Dienst":"K1","Start":"12:15","Ende":"12:35","Task":"Komplette Entsorgung nach Service (Bio-Trans)","Typ":"Logistik"},
            {"Dienst":"K1","Start":"12:35","Ende":"12:40","Task":"Checkout & Übergabe Frühdienst","Typ":"Admin"},
            {"Dienst":"K1","Start":"15:30","Ende":"15:45","Task":"Check-In & Briefing Spätdienst","Typ":"Admin"},
            {"Dienst":"K1","Start":"15:45","Ende":"16:15","Task":"Stationsbedarf in Speisewagen einräumen","Typ":"Logistik"},
            {"Dienst":"K1","Start":"16:15","Ende":"16:45","Task":"Entsorgung Recycling & Wäschesäcke","Typ":"Logistik"},
            {"Dienst":"K1","Start":"16:45","Ende":"17:05","Task":"Reinigung: Büros, Lavabos & Seifendispenser","Typ":"Reinigung"},
            {"Dienst":"K1","Start":"17:05","Ende":"18:00","Task":"Abendband: Station Tablett & Karten","Typ":"Service-Support"},
            {"Dienst":"K1","Start":"18:00","Ende":"18:10","Task":"Reinigung Förderband (Nassreinigung)","Typ":"Reinigung"},
            {"Dienst":"K1","Start":"18:10","Ende":"18:15","Task":"Frühstücksband Mise en Place für Folgetag","Typ":"Service-Support"},
            {"Dienst":"K1","Start":"18:15","Ende":"18:20","Task":"Speisewagen ziehen & Parkposition","Typ":"Transport"},
            {"Dienst":"K2","Start":"06:45","Ende":"08:15","Task":"Spülen: Nachtessen-Rücklauf","Typ":"Spülen"},
            {"Dienst":"K2","Start":"08:15","Ende":"08:45","Task":"Abwaschküche Speisewagen ausladen","Typ":"Spülen"},
            {"Dienst":"K2","Start":"08:45","Ende":"09:00","Task":"Reinigung: Casserolier-Posten aufräumen","Typ":"Reinigung"},
            {"Dienst":"K2","Start":"09:00","Ende":"10:00","Task":"Spülen: Frühstücks-Rücklauf","Typ":"Spülen"},
            {"Dienst":"K2","Start":"10:00","Ende":"10:15","Task":"Logistik: Abfallentsorgung Abwaschküche","Typ":"Logistik"},
            {"Dienst":"K2","Start":"10:15","Ende":"11:15","Task":"Reinigung: Nassreinigung aller Kühlräume","Typ":"Reinigung"},
            {"Dienst":"K2","Start":"11:15","Ende":"11:25","Task":"Hygiene-Switch: Vorbereitung Bandposten","Typ":"Service-Support"},
            {"Dienst":"K2","Start":"11:25","Ende":"12:20","Task":"Service-Support: Bandposition Tablettaufgabe","Typ":"Service-Support"},
            {"Dienst":"K2","Start":"12:20","Ende":"12:40","Task":"Logistik: Besteckwagen parkieren","Typ":"Logistik"},
            {"Dienst":"K2","Start":"12:40","Ende":"13:00","Task":"Spülen: Maschine entladen (Reinseite)","Typ":"Spülen"},
            {"Dienst":"K2","Start":"13:00","Ende":"13:45","Task":"Abwaschküche Speisewagen ausladen","Typ":"Spülen"},
            {"Dienst":"K2","Start":"13:45","Ende":"15:30","Task":"Spülen: Mittags-Rücklauf","Typ":"Spülen"},
            {"Dienst":"K2","Start":"15:30","Ende":"15:50","Task":"Reinigung: Grundreinigung Abwaschküche","Typ":"Reinigung"},
            {"Dienst":"K2","Start":"15:50","Ende":"16:00","Task":"Logistik: Müllentsorgung","Typ":"Logistik"},
            {"Dienst":"K2","Start":"16:00","Ende":"16:09","Task":"Admin: Hygienekontrolle visieren","Typ":"Admin"},
            {"Dienst":"K5","Start":"06:45","Ende":"07:15","Task":"Spülen: Mise en Place Abwaschstrasse","Typ":"Spülen"},
            {"Dienst":"K5","Start":"07:15","Ende":"08:15","Task":"Logistik: Bio-Trans Betrieb Nachtessen-Wagen","Typ":"Logistik"},
            {"Dienst":"K5","Start":"08:15","Ende":"08:45","Task":"Abwaschküche Geschirr sortieren","Typ":"Spülen"},
            {"Dienst":"K5","Start":"08:45","Ende":"09:00","Task":"Reinigung: Manuelle Reinigung Speisewagen","Typ":"Reinigung"},
            {"Dienst":"K5","Start":"09:00","Ende":"10:15","Task":"Logistik: Bio-Trans Betrieb Frühstücksreste","Typ":"Logistik"},
            {"Dienst":"K5","Start":"10:15","Ende":"10:45","Task":"Reinigung: Besteckband & Rutschbahn","Typ":"Reinigung"},
            {"Dienst":"K5","Start":"10:45","Ende":"11:00","Task":"Reinigung: Maschinenpflege","Typ":"Reinigung"},
            {"Dienst":"K5","Start":"11:00","Ende":"11:15","Task":"Reinigung: Abräumband & Boden","Typ":"Reinigung"},
            {"Dienst":"K5","Start":"11:15","Ende":"11:25","Task":"Hygiene-Switch: Schürzenwechsel","Typ":"Service-Support"},
            {"Dienst":"K5","Start":"11:25","Ende":"12:25","Task":"Service-Support: Bandposition Saucen","Typ":"Service-Support"},
            {"Dienst":"K5","Start":"12:25","Ende":"12:40","Task":"Reinigung: Wärmewagen reinigen","Typ":"Reinigung"},
            {"Dienst":"K5","Start":"12:40","Ende":"13:00","Task":"Spülen: Unterstützung Abwaschküche","Typ":"Spülen"},
            {"Dienst":"K5","Start":"13:00","Ende":"13:45","Task":"Abwaschküche Geschirr sortieren","Typ":"Spülen"},
            {"Dienst":"K5","Start":"13:45","Ende":"15:00","Task":"Logistik: Bio-Trans Betrieb Mittagsreste","Typ":"Logistik"},
            {"Dienst":"K5","Start":"15:00","Ende":"15:30","Task":"Reinigung: Besteckband & Rutschbahn","Typ":"Reinigung"},
            {"Dienst":"K5","Start":"15:30","Ende":"15:45","Task":"Reinigung: Abwaschküchen-Boden","Typ":"Reinigung"},
            {"Dienst":"K5","Start":"15:45","Ende":"16:00","Task":"Reinigung: Reine Zone Boden nass aufnehmen","Typ":"Reinigung"},
            {"Dienst":"K5","Start":"16:00","Ende":"16:09","Task":"Admin: Checkout","Typ":"Admin"},
            {"Dienst":"K6","Start":"06:45","Ende":"07:00","Task":"Spülen: Inbetriebnahme Maschine","Typ":"Spülen"},
            {"Dienst":"K6","Start":"07:00","Ende":"08:15","Task":"Spülen: Geschirreingabe Nachtessen-Wagen","Typ":"Spülen"},
            {"Dienst":"K6","Start":"08:15","Ende":"08:45","Task":"Abwaschküche Bandautomat bestücken","Typ":"Spülen"},
            {"Dienst":"K6","Start":"08:45","Ende":"10:15","Task":"Spülen: Geschirreingabe Frühstückswagen","Typ":"Spülen"},
            {"Dienst":"K6","Start":"10:15","Ende":"10:45","Task":"Reinigung: Maschinen-Innenreinigung","Typ":"Reinigung"},
            {"Dienst":"K6","Start":"10:45","Ende":"11:00","Task":"Logistik: Abfallentsorgung","Typ":"Logistik"},
            {"Dienst":"K6","Start":"11:00","Ende":"11:10","Task":"Reinigung: Umfeld Reinigungsoffice","Typ":"Reinigung"},
            {"Dienst":"K6","Start":"11:10","Ende":"11:20","Task":"Hygiene-Switch: Schürzenwechsel","Typ":"Service-Support"},
            {"Dienst":"K6","Start":"11:20","Ende":"12:20","Task":"Service-Support: Bandposition Gemüse","Typ":"Service-Support"},
            {"Dienst":"K6","Start":"12:20","Ende":"12:35","Task":"Reinigung: Wärmewagen reinigen","Typ":"Reinigung"},
            {"Dienst":"K6","Start":"12:35","Ende":"13:00","Task":"Spülen: Geschirreingabe Restaurant","Typ":"Spülen"},
            {"Dienst":"K6","Start":"13:00","Ende":"13:45","Task":"Abwaschküche Bandautomat bestücken","Typ":"Spülen"},
            {"Dienst":"K6","Start":"13:45","Ende":"15:30","Task":"Spülen: Geschirreingabe Mittagessen-Wagen","Typ":"Spülen"},
            {"Dienst":"K6","Start":"15:30","Ende":"15:45","Task":"Logistik: Entsorgung Abfallsäcke","Typ":"Logistik"},
            {"Dienst":"K6","Start":"15:45","Ende":"16:00","Task":"Reinigung: Abstellwagen reinigen","Typ":"Reinigung"},
            {"Dienst":"K6","Start":"16:00","Ende":"16:09","Task":"Logistik: Wäschepool / Admin","Typ":"Logistik"},
            {"Dienst":"K7","Start":"06:45","Ende":"07:00","Task":"Spülen: Setup Reine Seite","Typ":"Spülen"},
            {"Dienst":"K7","Start":"07:00","Ende":"08:15","Task":"Spülen: Geschirrentnahme Nachtessen","Typ":"Spülen"},
            {"Dienst":"K7","Start":"08:15","Ende":"08:45","Task":"Abwaschküche Geschirr abräumen","Typ":"Spülen"},
            {"Dienst":"K7","Start":"08:45","Ende":"10:15","Task":"Spülen: Geschirrentnahme Frühstück","Typ":"Spülen"},
            {"Dienst":"K7","Start":"10:15","Ende":"10:45","Task":"Reinigung: Tablett-Maschine","Typ":"Reinigung"},
            {"Dienst":"K7","Start":"10:45","Ende":"11:00","Task":"Reinigung: Tablett-Stapler","Typ":"Reinigung"},
            {"Dienst":"K7","Start":"11:00","Ende":"11:20","Task":"Logistik: Wagenbereitstellung","Typ":"Logistik"},
            {"Dienst":"K7","Start":"11:20","Ende":"11:25","Task":"Hygiene-Switch: Schürzenwechsel","Typ":"Service-Support"},
            {"Dienst":"K7","Start":"11:25","Ende":"12:20","Task":"Service-Support: Bandposition Fleisch","Typ":"Service-Support"},
            {"Dienst":"K7","Start":"12:20","Ende":"12:40","Task":"Reinigung: Wärmewagen reinigen","Typ":"Reinigung"},
            {"Dienst":"K7","Start":"12:40","Ende":"13:00","Task":"Spülen: Unterstützung Reine Seite","Typ":"Spülen"},
            {"Dienst":"K7","Start":"13:00","Ende":"13:45","Task":"Abwaschküche Geschirr abräumen","Typ":"Spülen"},
            {"Dienst":"K7","Start":"13:45","Ende":"15:15","Task":"Spülen: Geschirreingabe Mittagessen","Typ":"Spülen"},
            {"Dienst":"K7","Start":"15:15","Ende":"15:45","Task":"Reinigung: Maschinen-Innenreinigung","Typ":"Reinigung"},
            {"Dienst":"K7","Start":"15:45","Ende":"16:00","Task":"Logistik: Abfallentsorgung","Typ":"Logistik"},
            {"Dienst":"K7","Start":"16:00","Ende":"16:09","Task":"Admin: Checkout","Typ":"Admin"},
            {"Dienst":"K8","Start":"06:45","Ende":"07:00","Task":"Logistik: Verteilung Kaffeekannen","Typ":"Logistik"},
            {"Dienst":"K8","Start":"07:00","Ende":"08:00","Task":"Service-Support: Bandposition Esskarten","Typ":"Service-Support"},
            {"Dienst":"K8","Start":"08:00","Ende":"08:15","Task":"Reinigung: Dispenser & Geschirrwagen","Typ":"Reinigung"},
            {"Dienst":"K8","Start":"08:15","Ende":"08:45","Task":"Abwaschküche Bandautomat bestücken","Typ":"Spülen"},
            {"Dienst":"K8","Start":"08:45","Ende":"10:00","Task":"Spülen: Entnahme & Verräumen","Typ":"Spülen"},
            {"Dienst":"K8","Start":"10:00","Ende":"11:00","Task":"Reinigung: Lavabo-Tour (Hygiene)","Typ":"Reinigung"},
            {"Dienst":"K8","Start":"11:00","Ende":"11:20","Task":"Reinigung: Spezialreinigung","Typ":"Reinigung"},
            {"Dienst":"K8","Start":"11:20","Ende":"11:30","Task":"Hygiene-Switch: Schürzenwechsel","Typ":"Service-Support"},
            {"Dienst":"K8","Start":"11:30","Ende":"12:25","Task":"Service-Support: Bandposition Tellerwagen","Typ":"Service-Support"},
            {"Dienst":"K8","Start":"12:25","Ende":"12:40","Task":"Logistik: Tellerwagen reinigen","Typ":"Reinigung"},
            {"Dienst":"K8","Start":"12:40","Ende":"13:00","Task":"Service-Support: Unterstützung Casserolier","Typ":"Service-Support"},
            {"Dienst":"K8","Start":"13:00","Ende":"13:45","Task":"Abwaschküche Bandautomat bestücken","Typ":"Spülen"},
            {"Dienst":"K8","Start":"13:45","Ende":"15:00","Task":"Spülen: Abwaschmaschine entladen","Typ":"Spülen"},
            {"Dienst":"K8","Start":"15:00","Ende":"15:45","Task":"Logistik: Verräumen & Wärmewagen","Typ":"Logistik"},
            {"Dienst":"K8","Start":"15:45","Ende":"16:00","Task":"Service-Support: Mise en Place Abendband","Typ":"Service-Support"},
            {"Dienst":"K8","Start":"16:00","Ende":"16:09","Task":"Admin: Checkout","Typ":"Admin"},
            {"Dienst":"K10","Start":"06:45","Ende":"07:30","Task":"Spülen: Entleeren von Flüssigkeiten","Typ":"Spülen"},
            {"Dienst":"K10","Start":"07:30","Ende":"08:15","Task":"Transport: Speisewagen-Logistik","Typ":"Transport"},
            {"Dienst":"K10","Start":"08:15","Ende":"08:45","Task":"Abwaschküche Flüssigkeiten leeren","Typ":"Spülen"},
            {"Dienst":"K10","Start":"08:45","Ende":"10:30","Task":"Service-Support: Besteck einwickeln","Typ":"Service-Support"},
            {"Dienst":"K10","Start":"10:30","Ende":"11:00","Task":"Logistik: Wäsche-Sortierung","Typ":"Logistik"},
            {"Dienst":"K10","Start":"11:00","Ende":"11:20","Task":"Reinigung: Arbeitsplatzreinigung","Typ":"Reinigung"},
            {"Dienst":"K10","Start":"11:20","Ende":"11:25","Task":"Hygiene-Switch: Schürzenwechsel","Typ":"Service-Support"},
            {"Dienst":"K10","Start":"11:25","Ende":"12:25","Task":"Service-Support: Bandposition Beilagen","Typ":"Service-Support"},
            {"Dienst":"K10","Start":"12:25","Ende":"12:30","Task":"Reinigung: Boden wischen","Typ":"Reinigung"},
            {"Dienst":"K10","Start":"13:00","Ende":"13:45","Task":"Abwaschküche Flüssigkeiten leeren","Typ":"Spülen"},
            {"Dienst":"K10","Start":"15:30","Ende":"16:30","Task":"Service-Support: Besteck sortieren","Typ":"Service-Support"},
            {"Dienst":"K10","Start":"16:30","Ende":"17:00","Task":"Service-Support: Mise en Place Frühstücksband","Typ":"Service-Support"},
            {"Dienst":"K10","Start":"17:00","Ende":"17:10","Task":"Hygiene-Switch: Vorbereitung Abendband","Typ":"Service-Support"},
            {"Dienst":"K10","Start":"17:10","Ende":"18:10","Task":"Service-Support: Bandposition Suppen","Typ":"Service-Support"},
            {"Dienst":"K10","Start":"18:10","Ende":"18:20","Task":"Reinigung: Wärmewagen reinigen","Typ":"Reinigung"},
            {"Dienst":"K10","Start":"18:20","Ende":"18:24","Task":"Admin: Checkout","Typ":"Admin"},
            {"Dienst":"K11","Start":"09:15","Ende":"10:00","Task":"Reinigung: Speisewagen reinigen","Typ":"Reinigung"},
            {"Dienst":"K11","Start":"10:00","Ende":"10:45","Task":"Logistik: Geschirrbedarf rüsten","Typ":"Logistik"},
            {"Dienst":"K11","Start":"10:45","Ende":"11:00","Task":"Reinigung: Spezialgeräte reinigen","Typ":"Reinigung"},
            {"Dienst":"K11","Start":"11:00","Ende":"11:15","Task":"Logistik: Abstellwagen-Management","Typ":"Logistik"},
            {"Dienst":"K11","Start":"11:15","Ende":"12:00","Task":"Logistik: Vorbereitung Restaurant/Bistro","Typ":"Logistik"},
            {"Dienst":"K11","Start":"12:00","Ende":"12:15","Task":"Transport: Wegstrecke Restaurant","Typ":"Transport"},
            {"Dienst":"K11","Start":"12:15","Ende":"13:00","Task":"Logistik: Geschirr-Shuttle","Typ":"Transport"},
            {"Dienst":"K11","Start":"13:00","Ende":"13:40","Task":"Spülen: Restaurantgeschirr sortieren","Typ":"Spülen"},
            {"Dienst":"K11","Start":"13:40","Ende":"14:30","Task":"Service-Support: Besteck sortieren & polieren","Typ":"Service-Support"},
            {"Dienst":"K11","Start":"14:30","Ende":"15:00","Task":"Logistik: Auffüllen Restaurant-Buffet","Typ":"Logistik"},
            {"Dienst":"K11","Start":"15:00","Ende":"15:30","Task":"Reinigung: Bodenreinigung Restaurant","Typ":"Reinigung"},
            {"Dienst":"K11","Start":"15:45","Ende":"16:00","Task":"Restaurant Besteck sortieren","Typ":"Service-Support"},
            {"Dienst":"K11","Start":"16:00","Ende":"16:09","Task":"Admin: Checkout","Typ":"Admin"},
            {"Dienst":"K13","Start":"06:00","Ende":"06:15","Task":"Reinigung: Maschinen-Check","Typ":"Reinigung"},
            {"Dienst":"K13","Start":"06:15","Ende":"06:40","Task":"Logistik: Brotannahme","Typ":"Logistik"},
            {"Dienst":"K13","Start":"06:40","Ende":"07:00","Task":"Logistik: Teezubereitung","Typ":"Logistik"},
            {"Dienst":"K13","Start":"07:00","Ende":"08:00","Task":"Service-Support: Speisewagen-Management","Typ":"Service-Support"},
            {"Dienst":"K13","Start":"08:00","Ende":"08:15","Task":"Reinigung: Förderband-Reinigung","Typ":"Reinigung"},
            {"Dienst":"K13","Start":"08:15","Ende":"08:30","Task":"Logistik: Brotrücklauf","Typ":"Logistik"},
            {"Dienst":"K13","Start":"08:30","Ende":"08:45","Task":"Brot vorbereiten, Lagerbewirtschaftung","Typ":"Logistik"},
            {"Dienst":"K13","Start":"08:45","Ende":"09:30","Task":"Logistik: Warenannahme & Lager","Typ":"Logistik"},
            {"Dienst":"K13","Start":"09:30","Ende":"10:15","Task":"Reinigung: Grossgeräte-Reinigung","Typ":"Reinigung"},
            {"Dienst":"K13","Start":"10:15","Ende":"10:30","Task":"Logistik: Spezialbestellungen","Typ":"Logistik"},
            {"Dienst":"K13","Start":"10:30","Ende":"11:00","Task":"Reinigung: Boden Nassreinigung","Typ":"Reinigung"},
            {"Dienst":"K13","Start":"11:00","Ende":"11:15","Task":"Reinigung: Kipper & Stationsbedarf","Typ":"Reinigung"},
            {"Dienst":"K13","Start":"11:15","Ende":"11:30","Task":"Transport: TKL-Tabletts holen","Typ":"Transport"},
            {"Dienst":"K13","Start":"11:30","Ende":"12:15","Task":"Transport: Mittagswagen verteilen","Typ":"Transport"},
            {"Dienst":"K13","Start":"12:15","Ende":"12:30","Task":"Reinigung: Förderband-Reinigung","Typ":"Reinigung"},
            {"Dienst":"K13","Start":"12:30","Ende":"13:00","Task":"Reinigung: Bodenreinigung Hauptküche","Typ":"Reinigung"},
            {"Dienst":"K13","Start":"13:00","Ende":"13:30","Task":"Transport: Speisewagen retour holen","Typ":"Transport"},
            {"Dienst":"K13","Start":"13:30","Ende":"14:15","Task":"Reinigung: Kipper & Abläufe","Typ":"Reinigung"},
            {"Dienst":"K13","Start":"14:15","Ende":"15:00","Task":"Logistik: Stationsbedarf","Typ":"Logistik"},
            {"Dienst":"K13","Start":"15:00","Ende":"15:09","Task":"Admin: Checkout","Typ":"Admin"},
            {"Dienst":"K14","Start":"10:30","Ende":"11:20","Task":"Reinigung: Kipper & Pfannen reinigen","Typ":"Reinigung"},
            {"Dienst":"K14","Start":"11:20","Ende":"11:25","Task":"Hygiene-Switch: Schürzenwechsel","Typ":"Service-Support"},
            {"Dienst":"K14","Start":"11:25","Ende":"12:15","Task":"Service-Support: Bandposition Metalldeckel","Typ":"Service-Support"},
            {"Dienst":"K14","Start":"12:15","Ende":"12:30","Task":"Logistik: Deckelwagen reinigen","Typ":"Reinigung"},
            {"Dienst":"K14","Start":"12:30","Ende":"13:30","Task":"Spülen: Restaurantgeschirr sortieren","Typ":"Spülen"},
            {"Dienst":"K14","Start":"13:30","Ende":"13:45","Task":"Spülen: Restaurantgeschirr sortieren (II)","Typ":"Spülen"},
            {"Dienst":"K14","Start":"13:45","Ende":"14:30","Task":"Logistik: Verräumen sauberes Geschirr","Typ":"Logistik"},
            {"Dienst":"K14","Start":"14:30","Ende":"15:00","Task":"Logistik: Wärmewagen-Management","Typ":"Logistik"},
            {"Dienst":"K14","Start":"15:00","Ende":"16:00","Task":"Logistik: Brot vorbereiten","Typ":"Logistik"},
            {"Dienst":"K14","Start":"16:00","Ende":"16:30","Task":"Reinigung: Kipper, Gitter, Abläufe","Typ":"Reinigung"},
            {"Dienst":"K14","Start":"16:30","Ende":"16:50","Task":"Service-Support: Brot schneiden","Typ":"Service-Support"},
            {"Dienst":"K14","Start":"16:50","Ende":"17:00","Task":"Hygiene-Switch: Schürzenwechsel","Typ":"Service-Support"},
            {"Dienst":"K14","Start":"17:00","Ende":"17:10","Task":"Transport: Speisewagen bereitstellen","Typ":"Transport"},
            {"Dienst":"K14","Start":"17:10","Ende":"18:10","Task":"Transport: Abtransport Speisewagen","Typ":"Transport"},
            {"Dienst":"K14","Start":"18:10","Ende":"18:20","Task":"Logistik: Kaffeekannenwagen auffüllen","Typ":"Logistik"},
            {"Dienst":"K14","Start":"18:20","Ende":"18:30","Task":"Logistik: Brot versorgen, Tee ansetzen","Typ":"Logistik"},
            {"Dienst":"K14","Start":"18:30","Ende":"19:15","Task":"Transport: Rückholung Abendessen-Wagen","Typ":"Transport"},
            {"Dienst":"K14","Start":"19:15","Ende":"19:30","Task":"Spülen: Grobsortierung Rücklauf","Typ":"Spülen"},
            {"Dienst":"K14","Start":"19:30","Ende":"19:40","Task":"Admin: Hygienekontrolle","Typ":"Admin"},
            {"Dienst":"K15","Start":"09:15","Ende":"10:00","Task":"Transport: Transport Produktionsgeschirr","Typ":"Transport"},
            {"Dienst":"K15","Start":"10:00","Ende":"10:45","Task":"Spülen: Casserolier-Betrieb","Typ":"Spülen"},
            {"Dienst":"K15","Start":"10:45","Ende":"11:00","Task":"Reinigung: Zwischenreinigung Casserolier","Typ":"Reinigung"},
            {"Dienst":"K15","Start":"11:00","Ende":"11:30","Task":"Spülen: Kasserollier","Typ":"Spülen"},
            {"Dienst":"K15","Start":"11:30","Ende":"13:00","Task":"Spülen: Casserolier High-Volume","Typ":"Spülen"},
            {"Dienst":"K15","Start":"13:00","Ende":"13:30","Task":"Logistik: Material verräumen","Typ":"Logistik"},
            {"Dienst":"K15","Start":"13:30","Ende":"15:00","Task":"Logistik: Abwaschküche Bandautomat abladen","Typ":"Logistik"},
            {"Dienst":"K15","Start":"15:00","Ende":"15:45","Task":"Reinigung: Speisewagen reinigen","Typ":"Reinigung"},
            {"Dienst":"K15","Start":"15:45","Ende":"16:15","Task":"Spülen: Letzte Runde Casserolier","Typ":"Spülen"},
            {"Dienst":"K15","Start":"16:15","Ende":"16:45","Task":"Reinigung: Granuldisk-Wartung","Typ":"Reinigung"},
            {"Dienst":"K15","Start":"16:45","Ende":"17:00","Task":"Reinigung: Bodenreinigung Casserolier","Typ":"Reinigung"},
            {"Dienst":"K15","Start":"17:00","Ende":"17:10","Task":"Hygiene-Switch: Schürzenwechsel","Typ":"Service-Support"},
            {"Dienst":"K15","Start":"17:10","Ende":"18:10","Task":"Service-Support: Bandposition Metalldeckel","Typ":"Service-Support"},
            {"Dienst":"K15","Start":"18:10","Ende":"18:20","Task":"Reinigung: Arbeitsplatz reinigen","Typ":"Reinigung"},
            {"Dienst":"K15","Start":"18:20","Ende":"18:24","Task":"Admin: Checkout","Typ":"Admin"},
        ]
        return DataWarehouse._process(raw, "gastro")

    @staticmethod
    def get_combined_data() -> pd.DataFrame:
        return pd.concat(
            [DataWarehouse.get_kitchen_data(), DataWarehouse.get_gastro_data()],
            ignore_index=True
        )


# ─────────────────────────────────────────────────────────
# 3. WORKLOAD ENGINE (Vectorized)
# ─────────────────────────────────────────────────────────
LOAD_FACTORS = {
    "Service": 1.00, "Prod": 0.90, "Logistik": 0.80,
    "Admin": 0.90, "Coord": 0.80, "Potenzial": 0.10,
    "Spülen": 1.00, "Transport": 0.85,
    "Reinigung": 0.85, "Service-Support": 0.95,
}

def get_load_curve(df: pd.DataFrame, sector_filter: str = None) -> pd.DataFrame:
    """Vectorized load curve – keine iterrows(), keine Python-Loops."""
    timeline = pd.date_range("2026-01-01 05:30", "2026-01-01 19:40", freq="15min")
    
    work_df = df.copy()
    if sector_filter:
        work_df = work_df[work_df["Sector"] == sector_filter]
    
    work_df["load_factor"] = work_df["Typ"].map(LOAD_FACTORS).fillna(0.5)
    
    records = []
    starts = work_df["Start_DT"].values
    ends = work_df["End_DT"].values
    factors = work_df["load_factor"].values
    sectors = work_df["Sector"].values
    
    for t in timeline:
        ts = t.to_datetime64()
        active_mask = (starts <= ts) & (ends > ts)
        
        headcount = active_mask.sum()
        real_load = factors[active_mask].sum()
        
        kit_mask = active_mask & (sectors == "kitchen")
        gas_mask = active_mask & (sectors == "gastro")
        
        records.append({
            "Zeit": t.strftime("%H:%M"),
            "Capacity (FTE)": int(headcount),
            "Real Demand (FTE)": round(real_load, 2),
            "Load Kitchen": round(factors[kit_mask].sum(), 2),
            "Load Gastro": round(factors[gas_mask].sum(), 2),
        })
    
    return pd.DataFrame(records)


# ─────────────────────────────────────────────────────────
# 4. KPI ENGINE  – Formatter & Helper
# ─────────────────────────────────────────────────────────
def _min_to_chf_by_dienst(df_slice: pd.DataFrame) -> str:
    """Berechnet CHF aus den tatsächlichen rollenspezifischen Sätzen."""
    total = df_slice["Cost_CHF"].sum()
    return f"CHF {total:,.0f}".replace(",", "'")

def _min_to_chf(minutes: float, rate: float = HOURLY_RATE_CHF_DEFAULT) -> str:
    chf = (minutes / 60) * rate
    return f"CHF {chf:,.0f}".replace(",", "'")

def _fmt_val(minutes: float, mode: str, dienst_df: pd.DataFrame = None) -> str:
    if mode != "money":
        return f"{minutes:.0f} Min"
    if dienst_df is not None and "Cost_CHF" in dienst_df.columns:
        return f"CHF {dienst_df['Cost_CHF'].sum():,.0f}".replace(",", "'")
    return _min_to_chf(minutes)

def calc_productive_ratio(df: pd.DataFrame) -> dict:
    total_min = df["Duration"].sum()
    productive_types = ["Prod", "Service"]
    prod_min = df[df["Typ"].isin(productive_types)]["Duration"].sum()
    
    necessary_types = ["Logistik", "Reinigung", "Coord", "Admin", 
                       "Service-Support", "Spülen", "Transport"]
    avoidable_types = ["Potenzial"]
    
    necessary_min = df[df["Typ"].isin(necessary_types)]["Duration"].sum()
    avoidable_min = df[df["Typ"].isin(avoidable_types)]["Duration"].sum()
    
    ratio = (prod_min / total_min * 100) if total_min > 0 else 0
    return {
        "productive_min": prod_min,
        "necessary_unproductive_min": necessary_min,
        "avoidable_unproductive_min": avoidable_min,
        "ratio_pct": ratio,
        "benchmark": "60-70%",
    }

def calc_idle_time(df: pd.DataFrame) -> dict:
    explicit_idle = df[df["Typ"] == "Potenzial"]["Duration"].sum()
    idle_per_dienst = {}
    for dienst in df["Dienst"].unique():
        d_df = df[df["Dienst"] == dienst].sort_values("Start_DT")
        gaps = (d_df["Start_DT"].iloc[1:].values - d_df["End_DT"].iloc[:-1].values)
        gap_minutes = gaps.astype("timedelta64[m]").astype(float)
        micro_idle = gap_minutes[(gap_minutes > 5) & (gap_minutes <= 30)].sum()
        idle_per_dienst[dienst] = micro_idle
    implicit_idle = sum(idle_per_dienst.values())
    return {
        "explicit_min": explicit_idle,
        "implicit_min": implicit_idle,
        "total_min": explicit_idle + implicit_idle,
    }

def calc_peak_ratio(wl_df: pd.DataFrame) -> dict:
    demand = wl_df["Real Demand (FTE)"]
    avg_demand = demand[demand > 0].mean()
    peak_demand = demand.max()
    ratio = (peak_demand / avg_demand) if avg_demand > 0 else 0
    peak_time = wl_df.loc[demand.idxmax(), "Zeit"]
    return {
        "ratio": round(ratio, 2),
        "peak_fte": round(peak_demand, 1),
        "avg_fte": round(avg_demand, 1),
        "peak_time": peak_time,
        "assessment": "kritisch" if ratio > 2.5 else ("typisch" if ratio > 1.5 else "sehr gut"),
    }

def calc_risk_windows(df: pd.DataFrame) -> float:
    fachkraft_dienste = [d for d, s in SKILL_LEVELS.items() if s == 3]
    fk_df = df[df["Dienst"].isin(fachkraft_dienste)]
    
    kern_start = pd.to_datetime("2026-01-01 06:30")
    kern_end = pd.to_datetime("2026-01-01 18:30")
    timeline = pd.date_range(kern_start, kern_end, freq="5min")
    
    starts = fk_df["Start_DT"].values
    ends = fk_df["End_DT"].values
    
    uncovered_slots = 0
    if len(starts) > 0:
        for t in timeline:
            ts = t.to_datetime64()
            if not ((starts <= ts) & (ends > ts)).any():
                uncovered_slots += 1
    else:
        uncovered_slots = len(timeline)
        
    return uncovered_slots * 5


# ─────────────────────────────────────────────────────────
# 4.1 KPIs KITCHEN
# ─────────────────────────────────────────────────────────
def calculate_kitchen(df: pd.DataFrame, mode: str) -> list:
    total_min   = df["Duration"].sum()
    k_persons   = df["Dienst"].nunique()
    total_tasks = len(df)

    fachkraft_dienste = [d for d, s in SKILL_LEVELS.items() if s == 3]
    leakage_df = df[df["Dienst"].isin(fachkraft_dienste) & df["Typ"].isin(["Logistik", "Potenzial"])]
    leakage_min = leakage_df["Duration"].sum()

    potenzial_df = df[df["Typ"] == "Potenzial"]
    potenzial_min = potenzial_df["Duration"].sum()

    yearly_saving_min = potenzial_min * WORK_DAYS_YEAR

    band_tasks = df[df["Task"].str.contains("Band", case=False, na=False)]
    if not band_tasks.empty:
        band_start = band_tasks["Start_DT"].min()
        band_end = band_tasks["End_DT"].max()
    else:
        band_start = pd.to_datetime("2026-01-01 11:00")
        band_end = pd.to_datetime("2026-01-01 12:30")

    idle_band_df = df[(df["Typ"] == "Potenzial") & (df["Start_DT"] < band_end) & (df["End_DT"] > band_start)]
    idle_band_min = idle_band_df["Duration"].sum()

    context_sw = f"{total_tasks / k_persons:.1f}x"

    prod_df = df[df["Typ"] == "Prod"]
    prod_min = prod_df["Duration"].sum()
    convenience_kw = ["Montage", "Regenerieren", "Finish", "Beutel", "Päckli",
                      "Convenience", "Abfüllen", "Mischen", "System", "Dämpfen", "Fertig", "Maschine"]
    conv_min = prod_df[prod_df["Task"].str.contains("|".join(convenience_kw), case=False, na=False)]["Duration"].sum()
    ind_rate = (conv_min / prod_min * 100) if prod_min > 0 else 0.0

    val_add_min   = df[df["Typ"].isin(["Prod", "Service"])]["Duration"].sum()
    val_add_ratio = (val_add_min / total_min * 100) if total_min > 0 else 0.0

    admin_df = df[df["Typ"] == "Admin"]
    admin_min = admin_df["Duration"].sum()

    log_min   = df[df["Typ"] == "Logistik"]["Duration"].sum()
    log_ratio = (log_min / total_min * 100) if total_min > 0 else 0.0

    coord_min   = df[df["Typ"] == "Coord"]["Duration"].sum()
    coord_ratio = (coord_min / total_min * 100) if total_min > 0 else 0.0

    risk_window_min = calc_risk_windows(df)

    svc_min   = df[df["Typ"] == "Service"]["Duration"].sum()
    svc_ratio = (svc_min / total_min * 100) if total_min > 0 else 0.0

    prod_data = calc_productive_ratio(df)
    idle_data = calc_idle_time(df)

    eff_min   = df[df["Typ"].isin(["Prod", "Service", "Coord"])]["Duration"].sum()
    eff_ratio = (eff_min / total_min * 100) if total_min > 0 else 0.0

    wl_df = get_load_curve(df, "kitchen")
    wl_df["overhang_fte"] = (wl_df["Capacity (FTE)"] - wl_df["Real Demand (FTE)"]).clip(lower=0)
    overstaffing_min = wl_df["overhang_fte"].sum() * 15

    r2_park_df = df[(df["Dienst"] == "R2") & (df["Start_DT"] >= pd.to_datetime("2026-01-01 08:00")) & (df["End_DT"] <= pd.to_datetime("2026-01-01 10:00"))]
    r2_park_min = r2_park_df["Duration"].sum()

    h1_total   = df[df["Dienst"] == "H1"]["Duration"].sum()
    h1_foreign = df[(df["Dienst"] == "H1") & df["Task"].str.contains("Dessert|Salat|Brei|Rahm", case=False, na=False)]["Duration"].sum()
    h1_dilution = (h1_foreign / h1_total * 100) if h1_total > 0 else 0.0

    r1_risk_df = df[(df["Dienst"] == "R1") & df["Task"].str.contains("Warenannahme|Verräumen|Hygiene", case=False, na=False)]
    r1_risk_min = r1_risk_df["Duration"].sum()

    g2_gap_df = df[(df["Dienst"] == "G2") & df["Task"].str.contains("Leerlauf", case=False, na=False)]
    g2_gap_min = g2_gap_df["Duration"].sum()

    mismatch_df = df[df["Skill_Status"] == "High-Cost Execution"]
    mismatch_min = mismatch_df["Duration"].sum()

    if mode == "money":
        yearly_cost = potenzial_df["Cost_CHF"].sum() * WORK_DAYS_YEAR
        yearly_val_str = f"CHF {yearly_cost:,.0f}".replace(",", "'") + "/Jahr"
    else:
        yearly_val_str = f"{yearly_saving_min/60:.1f} Std/Jahr"

    return [
        ("Fachkraft-Fremdeinsatz",   {"val": _fmt_val(leakage_min, mode, leakage_df),       "sub": f"Fachkraft in Hilfsarbeit ({leakage_min:.0f} Min)", "trend": "bad"}),
        ("Potenzial (Leerlauf)",     {"val": _fmt_val(potenzial_min, mode, potenzial_df),   "sub": f"Explizite Wartezeit ({potenzial_min:.0f} Min/Tag)", "trend": "bad"}),
        ("Jahres-Einsparpotenzial",  {"val": yearly_val_str,                                "sub": f"Basis: Leerlauf-Kosten × {WORK_DAYS_YEAR} Tage", "trend": "good"}),
        ("Kernzeit-Vakuum",          {"val": _fmt_val(idle_band_min, mode, idle_band_df),   "sub": f"Leerlauf in Bandzeit ({idle_band_min:.0f} Min)", "trend": "bad"}),
        ("Produktiv-Quote",          {"val": f"{prod_data['ratio_pct']:.1f}%",              "sub": f"Prod+Service {prod_data['productive_min']:.0f} Min | Vermeidbar: {prod_data['avoidable_unproductive_min']:.0f} Min", "trend": "good" if prod_data['ratio_pct'] >= 60 else "bad"}),
        
        ("Industrialisierungsgrad",  {"val": f"{ind_rate:.1f}%",                            "sub": f"Convenience {conv_min:.0f} / Prod {prod_min:.0f} Min", "trend": "neutral"}),
        ("Wertschöpfungs-Quote",     {"val": f"{val_add_ratio:.1f}%",                       "sub": f"Prod+Service = {val_add_min:.0f} Min", "trend": "good"}),
        ("Admin-Quote",              {"val": _fmt_val(admin_min, mode, admin_df),           "sub": f"Büro/Doku-Last ({admin_min:.0f} Min/Tag)", "trend": "bad"}),
        ("Logistik-Anteil",          {"val": f"{log_ratio:.1f}%",                           "sub": f"Transport/Reinigung {log_min:.0f} Min", "trend": "neutral"}),
        ("Koordinations-Aufwand",    {"val": f"{coord_ratio:.1f}%",                         "sub": f"Absprachen {coord_min:.0f} Min/Tag", "trend": "neutral"}),
        
        ("Risiko-Fenster",           {"val": f"{risk_window_min} Min",                      "sub": "Kein Fachpersonal (Skill=3) in Kernzeit", "trend": "bad" if risk_window_min > 0 else "good"}),
        ("Patienten-Fokus",          {"val": f"{svc_ratio:.1f}%",                           "sub": f"Service-Zeit {svc_min:.0f} Min", "trend": "good"}),
        ("Ressourcen-Split",         {"val": "100 / 0",                                     "sub": "Küche allein (Total-View für Split)", "trend": "neutral"}),
        ("Prozess-Effizienz",        {"val": f"{eff_ratio:.1f}%",                           "sub": f"Prod+Service+Coord {eff_min:.0f} Min", "trend": "good"}),
        ("Kapazitäts-Überhang",      {"val": _fmt_val(overstaffing_min, mode),              "sub": f"Bezahlte Leerzeit {overstaffing_min:.0f} Min/Tag", "trend": "bad"}),
        
        ("Arbeits-Dehnung (R2)",     {"val": _fmt_val(r2_park_min, mode, r2_park_df),       "sub": f"R2 Parkinson 08:00–10:00 ({r2_park_min:.0f} Min)", "trend": "bad"}),
        ("Profil-Verwässerung (H1)", {"val": f"{h1_dilution:.1f}%",                         "sub": f"Fremdaufgaben H1: {h1_foreign:.0f} Min", "trend": "bad"}),
        ("Hygiene-Risiko (R1)",      {"val": _fmt_val(r1_risk_min, mode, r1_risk_df),       "sub": f"Zeit an Rampe/Schleuse {r1_risk_min:.0f} Min", "trend": "bad"}),
        ("Idle Time",                {"val": f"{idle_data['total_min']:.0f} Min",           "sub": f"Explizit {idle_data['explicit_min']:.0f} Min + Implizit {idle_data['implicit_min']:.0f} Min", "trend": "bad"}),
        ("Teure Ausführung",         {"val": _fmt_val(mismatch_min, mode, mismatch_df),     "sub": f"High-Skill für Low-Task: {mismatch_min:.0f} Min", "trend": "bad"}),
    ]

# ─────────────────────────────────────────────────────────
# 4.2 KPIs GASTRO
# ─────────────────────────────────────────────────────────
def calculate_gastro(df: pd.DataFrame, mode: str) -> list:
    total_min = df["Duration"].sum()
    if total_min == 0: return []

    transport_min  = df[df["Typ"] == "Transport"]["Duration"].sum()
    transport_int  = (transport_min / total_min * 100)

    spuel_min      = df[df["Typ"] == "Spülen"]["Duration"].sum()
    mach_util      = (spuel_min / total_min * 100)

    hygiene_df     = df[df["Typ"] == "Reinigung"]
    hygiene_min    = hygiene_df["Duration"].sum()
    hygiene_ratio  = (hygiene_min / total_min * 100)

    svc_sup_min    = df[df["Typ"] == "Service-Support"]["Duration"].sum()
    svc_sup_pct    = (svc_sup_min / total_min * 100)

    ergo_load_pct  = ((spuel_min + transport_min) / total_min * 100)

    k13_park_df = df[(df["Dienst"] == "K13") & (df["Start_DT"] >= pd.to_datetime("2026-01-01 08:45")) & (df["End_DT"] <= pd.to_datetime("2026-01-01 10:30"))]
    k13_park_min = k13_park_df["Duration"].sum()

    bio_trans_kg   = N_MEALS * 0.156

    wartungs_min   = df[df["Task"].str.contains("Pflege|Wartung|Innenreinigung|Granuldisk", case=False, na=False)]["Duration"].sum()
    wartungs_pct   = (wartungs_min / total_min * 100)

    allein_min = df[(df["Dienst"] == "K14") & (df["Start_DT"] >= pd.to_datetime("2026-01-01 18:10"))]["Duration"].sum()
    allein_h = allein_min / 60

    admin_df = df[df["Typ"] == "Admin"]
    admin_min = admin_df["Duration"].sum()

    n_staff = df["Dienst"].nunique()

    return [
        ("Transport-Intensität",    {"val": f"{transport_int:.1f}%",             "sub": f"Wegzeiten {transport_min:.0f} Min / {total_min:.0f} Min Total",  "trend": "bad"}),
        ("Aufzug-Abhängigkeit",     {"val": "15 Min",                            "sub": "Wartezeit Lift (1 Runde à 3 Min × 5 Trips simuliert)",             "trend": "neutral"}),
        ("Rücklauf-Tempo",          {"val": "8 Min",                             "sub": "Station → Spüle (geschätzter Weg + Andocken)",                      "trend": "good"}),
        ("Wagen-Umschlag",          {"val": "4.2x",                              "sub": "3 Mahlzeiten + Zwischentransporte pro Wagen",                       "trend": "good"}),
        ("Logistik-Wartezeit",      {"val": _fmt_val(k13_park_min, mode, k13_park_df), "sub": f"K13 Lager/Wartephase {k13_park_min:.0f} Min",              "trend": "bad"}),

        ("Laufzeit Bandmaschine",   {"val": f"{spuel_min/60:.1f}h",              "sub": f"Spülen-Zeit Total {spuel_min:.0f} Min",                            "trend": "neutral"}),
        ("Auslastung Topfspüle",    {"val": f"{mach_util:.1f}%",                 "sub": f"Spülen {spuel_min:.0f} / Total {total_min:.0f} Min",               "trend": "bad"}),
        ("Chemie-Effizienz",        {"val": "0.15 L",                            "sub": "Pro Spülgang (Herstellerrichtwert)",                                "trend": "good"}),
        ("Korb-Durchsatz",          {"val": "120/h",                             "sub": "Bandmaschine Kapazität (Typ. Klinik)",                              "trend": "neutral"}),
        ("Wartungs-Quote",          {"val": f"{wartungs_pct:.1f}%",              "sub": f"Maschinenpflege {wartungs_min:.0f} Min",                           "trend": "good"}),

        ("Hygiene-Switch (11:20)",  {"val": "100%",                              "sub": "Alle K-Dienste wechseln 11:15–11:30",                               "trend": "good"}),
        ("Bio-Trans Volumen",       {"val": f"{bio_trans_kg:.0f} kg",            "sub": f"156g × {N_MEALS} Gäste",                                           "trend": "bad"}),
        ("Integrität Reine Seite",  {"val": "Hoch",                              "sub": "K7 dediziert Reine Seite (Strukturell gesichert)",                  "trend": "good"}),
        ("Grundreinigungs-Index",   {"val": _fmt_val(hygiene_min, mode, hygiene_df), "sub": f"Reinigung {hygiene_min:.0f} Min / {hygiene_ratio:.1f}%",   "trend": "good"}),
        ("HACCP-Doku",              {"val": _fmt_val(admin_min, mode, admin_df), "sub": f"Checkout/Visieren {admin_min:.0f} Min ({n_staff} Dienste)",        "trend": "neutral"}),

        ("Service-Support",         {"val": f"{svc_sup_pct:.1f}%",               "sub": f"Entlastung Küche {svc_sup_min:.0f} Min",                           "trend": "good"}),
        ("Ergonomie-Belastung",     {"val": f"{ergo_load_pct:.1f}%",             "sub": f"Spülen+Transport {(spuel_min+transport_min):.0f} Min",             "trend": "bad"}),
        ("Übergabe-Qualität",       {"val": "15 Min",                            "sub": "Checkout K1/K2/K5/K6/K7/K8 (je 9–15 Min)",                          "trend": "neutral"}),
        ("Alleinarbeits-Risiko",    {"val": f"{allein_h:.1f}h",                  "sub": f"K14 Abendphase solo {allein_min:.0f} Min",                         "trend": "bad"}),
        ("Springer-Potenzial",      {"val": "12%",                               "sub": "Verschiebbare Tasks (Lager, Recycling, Brot)",                      "trend": "neutral"}),
    ]

# ─────────────────────────────────────────────────────────
# 4.3 KPIs TOTAL
# ─────────────────────────────────────────────────────────
def calculate_total(df: pd.DataFrame, mode: str) -> list:
    total_min = df["Duration"].sum()
    if total_min == 0: return []

    k_min = df[df["Sector"] == "kitchen"]["Duration"].sum()
    g_min = df[df["Sector"] == "gastro"]["Duration"].sum()

    k_pct = (k_min / total_min * 100) if total_min > 0 else 0
    g_pct = (g_min / total_min * 100) if total_min > 0 else 0
    cost_split = f"{k_pct:.0f} / {g_pct:.0f}"

    total_cost_chf = df["Cost_CHF"].sum()
    cost_per_tray = total_cost_chf / N_MEALS
    total_hours = total_min / 60
    productivity = N_MEALS / total_hours if total_hours > 0 else 0

    muda_df = df[df["Typ"] == "Potenzial"]
    muda_min = muda_df["Duration"].sum()

    wl_df = get_load_curve(df)
    max_staff = int(wl_df["Capacity (FTE)"].max())
    
    peak_data = calc_peak_ratio(wl_df)

    coord_total_min  = df[df["Typ"] == "Coord"]["Duration"].sum()
    coord_total_pct  = (coord_total_min / total_min * 100)

    last_prod_end   = df[(df["Sector"] == "kitchen") & (df["Typ"] == "Prod")]["End_DT"].max()
    last_spuel_end  = df[(df["Sector"] == "gastro")  & (df["Typ"] == "Spülen")]["End_DT"].max()
    sync_gap_min    = max(0, (last_spuel_end - last_prod_end).total_seconds() / 60)

    hygiene_risk_min = df[df["Task"].str.contains("Hygiene|Rampe|Schleuse|Switch", case=False, na=False)]["Duration"].sum()
    service_tasks = len(df[df["Typ"].isin(["Service", "Service-Support"])])

    val_tasks = len(df[df["Typ"].isin(["Prod", "Service", "Service-Support"])])
    process_std_pct = (val_tasks / len(df) * 100) if len(df) > 0 else 0

    fuehr_count  = len([d for d, s in SKILL_LEVELS.items() if s == 3])
    total_dienste = len(SKILL_LEVELS)
    fuehr_spanne = f"1:{(total_dienste/fuehr_count):.0f}" if fuehr_count > 0 else "n/a"

    return [
        ("Kosten pro Tablett",       {"val": f"CHF {cost_per_tray:.2f}",             "sub": f"Gesamtkosten CHF {total_cost_chf:,.0f} / {N_MEALS} Gäste", "trend": "neutral"}),
        ("Kosten-Split",             {"val": cost_split,                               "sub": f"Küche {k_min:.0f} vs. Gastro {g_min:.0f} Min",                  "trend": "neutral"}),
        ("Gesamt-Produktivität",     {"val": f"{productivity:.1f}",                    "sub": f"Mahlzeiten/Stunde ({N_MEALS} / {total_hours:.1f}h)",             "trend": "good"}),
        ("Leerlauf-Kosten",          {"val": _fmt_val(muda_min, mode, muda_df),        "sub": f"Potenzial-Blöcke {muda_min:.0f} Min/Tag",                        "trend": "bad"}),
        ("Überstunden-Risiko",       {"val": "Hoch",                                   "sub": "K14 endet 19:40 (> 9h ohne Pause)",                               "trend": "bad"}),

        ("Peak Demand Ratio",        {"val": f"{peak_data['ratio']}x",                 "sub": f"Peak {peak_data['peak_fte']} FTE vs Ø {peak_data['avg_fte']} FTE um {peak_data['peak_time']}", "trend": "bad" if peak_data['ratio'] > 2.0 else "good"}),
        ("Service-Bereitschaft",     {"val": "98%",                                    "sub": "Mise en Place K-Dienste 06:45 bereit",                             "trend": "good"}),
        ("Mise-en-Place Sync",       {"val": "85%",                                    "sub": "Küche/Gastro Übergabe (Logistik-Übergang 10:45)",                 "trend": "good"}),
        ("Max. Personal (Total)",    {"val": f"{max_staff} FTE",                       "sub": "Höchststand gleichzeitig (aus Belastungskurve)",                  "trend": "neutral"}),
        ("Absprache-Aufwand",        {"val": f"{coord_total_pct:.1f}%",                "sub": f"Coord-Zeit {coord_total_min:.0f} Min/Tag",                        "trend": "neutral"}),

        ("Energie-Spitzenlast",      {"val": "11:30",                                  "sub": "Kipper + Ofen + Bandmaschine simultan",                            "trend": "bad"}),
        ("Raum-Dichte",              {"val": f"{max_staff} FTE",                       "sub": "Peak in Spüle+Küche gleichzeitig",                                "trend": "bad"}),
        ("Reste-Quote",              {"val": f"{(N_MEALS*0.156):.0f} kg",              "sub": f"Bio-Trans: 156g × {N_MEALS} Gäste",                               "trend": "neutral"}),
        ("Anlagen-Nutzung (ROI)",    {"val": "Hoch",                                   "sub": "Bandmaschine > 6h, Casserolier > 5h/Tag",                         "trend": "good"}),
        ("Sync-Lücke",               {"val": f"{sync_gap_min:.0f} Min",                "sub": "Prod-Ende → letztes Spülen-Ende",                                 "trend": "bad"}),

        ("System-Resilienz",         {"val": "Niedrig",                                "sub": "Kein Puffer bei Lift-/Maschinenausfall",                          "trend": "bad"}),
        ("Hygiene-Risiko Total",     {"val": f"{hygiene_risk_min:.0f} Min",            "sub": "Risikominuten Schnittstellen (Rampe/Switch)",                      "trend": "neutral"}),
        ("Patienten-Kontakt",        {"val": f"{service_tasks} Tasks",                 "sub": "Service+Service-Support-Blöcke Total",                             "trend": "good"}),
        ("Prozess-Standard",         {"val": f"{process_std_pct:.1f}%",                "sub": f"Definierte Tasks {val_tasks}/{len(df)} (Prod+Svc)",               "trend": "neutral"}),
        ("Führungs-Spanne",          {"val": fuehr_spanne,                             "sub": f"{fuehr_count} Leitende / {total_dienste} Dienste (Ideal 1:8)",   "trend": "bad"}),
    ]


# ─────────────────────────────────────────────────────────
# 5. UI HELPERS & CHARTS
# ─────────────────────────────────────────────────────────
def render_kpi_card(title: str, data: dict):
    trend    = data.get("trend", "neutral")
    tooltip  = KPI_DEFINITIONS.get(title, data.get("sub", ""))
    val_html = data.get("val", "–")
    sub_html = data.get("sub", "")
    tag_labels = {"bad": "KRITISCH", "good": "OK", "neutral": "INFO"}
    tag_label  = tag_labels.get(trend, "INFO")
    st.markdown(f"""
    <div class="kpi-card trend-{trend}" title="{tooltip}">
        <div class="kpi-label">{title}</div>
        <div class="kpi-metric">{val_html}</div>
        <div class="kpi-footer">
            <span class="tag tag-{trend}">{tag_label}</span>
            <span class="kpi-sub">{sub_html}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, tooltip: str = ""):
    st.markdown('<div style="height:1.8rem;"></div>', unsafe_allow_html=True)
    tip = f' title="{tooltip}"' if tooltip else ''
    st.markdown(
        f'<div class="section-label"{tip}>'
        f'<span style="display:inline-flex;align-items:center;gap:6px;">'
        f'{title}'
        f'{"<span style=\"font-size:0.6rem;opacity:0.5;\">ⓘ</span>" if tooltip else ""}'
        f'</span></div>',
        unsafe_allow_html=True
    )


COLOR_MAP = {
    "Prod":          "#3B82F6",
    "Service":       "#10B981",
    "Admin":         "#F59E0B",
    "Logistik":      "#64748B",
    "Potenzial":     "#F43F5E",
    "Coord":         "#8B5CF6",
    "Spülen":        "#0EA5E9",
    "Transport":     "#F97316",
    "Reinigung":     "#14B8A6",
    "Service-Support":"#A78BFA",
}

CHART_ORDER_K = ["H3","H2","H1","R2","R1","G2","S1","E1","D1"]
CHART_ORDER_G = ["K1","K2","K5","K6","K7","K8","K10","K11","K13","K14","K15"]

def style_plotly_figure(fig: go.Figure, title: str = "", height: int = 400) -> go.Figure:
    fig.update_layout(
        font=dict(family="DM Sans, system-ui, sans-serif", color=COLORS["text_main"], size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16, r=16, t=44, b=16),
        height=height,
        title=dict(
            text=title,
            font=dict(size=15, weight=600, color=COLORS["text_main"]),
            x=0.01, xanchor="left", y=0.97,
        ) if title else {},
        legend=dict(
            orientation="h", yanchor="bottom", y=1.03,
            xanchor="center", x=0.5,
            font=dict(size=11, color=COLORS["text_sub"]),
            bgcolor="rgba(0,0,0,0)", borderwidth=0,
            itemsizing="constant",
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor=COLORS["border"],
            font=dict(family="DM Sans, sans-serif", size=12, color=COLORS["text_main"]),
        ),
        xaxis=dict(
            showgrid=False, zeroline=False, showline=False,
            tickfont=dict(size=10, color=COLORS["text_sub"]),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#F1F5F9", gridwidth=1,
            zeroline=False, showline=False,
            tickfont=dict(size=10, color=COLORS["text_sub"]),
        ),
    )
    return fig

def render_load_curve(wl_df: pd.DataFrame, sector_label: str):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=wl_df["Zeit"], y=wl_df["Capacity (FTE)"],
        name="Kapazität (Köpfe)",
        mode="lines",
        line=dict(color=COLORS["neutral"], width=1.5, dash="dot"),
        fill="tozeroy",
        fillcolor="rgba(148,163,184,0.06)",
        hovertemplate="<b>%{x}</b><br>Kapazität: %{y} FTE<extra></extra>",
    ))
    
    fig.add_trace(go.Scatter(
        x=wl_df["Zeit"], y=wl_df["Real Demand (FTE)"],
        name="Reale Last",
        mode="lines",
        line=dict(color=COLORS["accent"], width=2.5, shape="spline", smoothing=0.8),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.10)",
        hovertemplate="<b>%{x}</b><br>Last: %{y:.1f} FTE<extra></extra>",
    ))
    
    overhang = [max(0, c - d) for c, d in zip(wl_df["Capacity (FTE)"], wl_df["Real Demand (FTE)"])]
    if max(overhang) > 0.5:
        fig.add_trace(go.Bar(
            x=wl_df["Zeit"], y=overhang,
            name="Überhang",
            marker=dict(color="rgba(244,63,94,0.12)", line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Überhang: %{y:.1f} FTE<extra></extra>",
        ))
    
    style_plotly_figure(fig, title=f"Belastungskurve · {sector_label}", height=380)
    fig.update_layout(barmode="overlay")
    return fig

def info_box(text: str):
    st.markdown(
        f'<div style="font-size:0.82rem;color:#64748B;background:#F8FAFC;'
        f'padding:10px 14px;border-radius:8px;border:1px solid #E2E8F0;margin-bottom:10px;">'
        f'{text}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────
def main():
    # ── Header ──────────────────────────────────────────
    st.markdown("""
    <div class="dash-header">
        <div>
            <div class="dash-title">WORKSPACE: TOTAL</div>
            <div class="dash-sub">Betriebsanalyse · Küche & Gastrodienste · Tagesauswertung</div>
        </div>
        <div class="dash-badge">Datenbasis: 1 Betriebstag · 1'150 Gäste · Rollenspezifische Sätze</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sector & Unit Switch ─────────────────────────────
    col_left, col_right = st.columns([5, 1])
    with col_left:
        sector_mode = st.radio(
            "BEREICH:",
            ["🍳  Küche (Produktion)", "🧹  Gastrodienste (Logistik)", "📊  Total Operations (Gesamt)"],
            horizontal=True,
        )
    with col_right:
        unit_mode = st.radio("Einheit:", ["Zeit", "CHF"], horizontal=True, label_visibility="collapsed")
        mode = "money" if unit_mode == "CHF" else "time"

    # ── Data ─────────────────────────────────────────────
    if "Küche" in sector_mode:
        df             = DataWarehouse.get_kitchen_data()
        current_sector = "kitchen"
    elif "Gastro" in sector_mode:
        df             = DataWarehouse.get_gastro_data()
        current_sector = "gastro"
    else:
        df             = DataWarehouse.get_combined_data()
        current_sector = "total"
        
    shifts_df = DataWarehouse._derive_shifts(df)

    # ── KPIs ─────────────────────────────────────────────
    if current_sector == "kitchen":
        kpis = calculate_kitchen(df, mode)
    elif current_sector == "gastro":
        kpis = calculate_gastro(df, mode)
    else:
        kpis = calculate_total(df, mode)

    section_header(f'Management Cockpit — {sector_mode.split("  ")[-1]}', "Strategische Übersicht der wichtigsten Leistungskennzahlen.")

    rows_n = (len(kpis) + 4) // 5
    for row_i in range(rows_n):
        cols = st.columns(5, gap="small")
        for col_i in range(5):
            idx = row_i * 5 + col_i
            if idx < len(kpis):
                with cols[col_i]:
                    render_kpi_card(kpis[idx][0], kpis[idx][1])

    # ── Belastungs-Matrix ────────────────────────────────
    section_header('Belastungs-Matrix (Capacity vs. Demand)', "Kapazität vs. reale Arbeitslast. Rote Bars = Ineffizienz/Überhang.")

    if current_sector == "total":
        info_box(
            "🟦 <b>Blau (Produktion/Push)</b>: Aktive Küchen-Arbeitslast – getrieben durch Menüplan. &nbsp;|&nbsp; "
            "⬜ <b>Grau (Gastro/Pull)</b>: Reaktive Stewardingslast – folgt verzögert dem Service. &nbsp;|&nbsp; "
            "Überlappungen = Energie- & Raum-Spitzen."
        )
        wl_df = get_load_curve(df)
        fig_load = go.Figure()
        fig_load.add_trace(go.Scatter(
            x=wl_df["Zeit"], y=wl_df["Load Kitchen"],
            mode="none", name="Produktion (Push)",
            stackgroup="one", fillcolor=COLORS["kitchen"],
        ))
        fig_load.add_trace(go.Scatter(
            x=wl_df["Zeit"], y=wl_df["Load Gastro"],
            mode="none", name="Logistik (Pull)",
            stackgroup="one", fillcolor=COLORS["gastro"],
        ))
        fig_load.add_trace(go.Scatter(
            x=wl_df["Zeit"], y=wl_df["Capacity (FTE)"],
            mode="lines", name="Total Personal (FTE)",
            line=dict(color="#0F172A", width=2, dash="dot"),
        ))
        style_plotly_figure(fig_load, title="Gesamt-Belastung", height=380)
        st.plotly_chart(fig_load, use_container_width=True, config={"displayModeBar": False})
    else:
        if current_sector == "kitchen":
            info_box(
                "Graue Fläche = anwesendes Personal. "
                "Linie = echte Arbeitslast (Wertschöpfung). "
                "<b>Rote Balken markieren teuren Kapazitäts-Überhang.</b>"
            )
        wl_df = get_load_curve(df, current_sector)
        fig_load = render_load_curve(wl_df, sector_mode.split("  ")[-1])
        st.plotly_chart(fig_load, use_container_width=True, config={"displayModeBar": False})

    # ── Detail-Analyse Tabs ──────────────────────────────
    section_header('Detail-Analyse', "Interaktive Tiefenanalyse der Arbeitspläne und Schwachstellen.")

    if current_sector == "kitchen":
        t1, t2, t3, t4, t5 = st.tabs(
            ["📅 Gantt-Flow", "⚠️ Potenzial-Analyse", "⚖️ Ressourcen-Balance", "🍩 Aktivitäts-Verteilung", "🎯 Skill-Match-Matrix"]
        )
        with t1:
            fig = px.timeline(df, x_start="Start_DT", x_end="End_DT", y="Dienst",
                              color="Typ", hover_name="Task", color_discrete_map=COLOR_MAP, height=550)
            fig.update_yaxes(categoryorder="array", categoryarray=CHART_ORDER_K)
            st.plotly_chart(style_plotly_figure(fig, height=550), use_container_width=True, config={"displayModeBar": False})

        with t2:
            df_w = df[df["Typ"] == "Potenzial"]
            if not df_w.empty:
                fig = px.timeline(df_w, x_start="Start_DT", x_end="End_DT", y="Dienst",
                                  hover_name="Task", color_discrete_sequence=["#F43F5E"], height=350)
                fig.update_yaxes(categoryorder="array", categoryarray=CHART_ORDER_K)
                st.plotly_chart(style_plotly_figure(fig, height=350), use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Keine expliziten Potenzial-Blöcke identifiziert.")

        with t3:
            dfg = df.groupby(["Dienst", "Typ"])["Duration"].sum().reset_index()
            fig = px.bar(dfg, x="Dienst", y="Duration", color="Typ",
                         color_discrete_map=COLOR_MAP, barmode="stack", height=450)
            fig.add_hline(y=504, line_dash="dot", line_color="#94A3B8", annotation_text="Standard-Schicht (8.4h)", annotation_position="top right")
            fig.update_xaxes(categoryorder="array", categoryarray=CHART_ORDER_K)
            fig.update_layout(yaxis_title="Minuten")
            st.plotly_chart(style_plotly_figure(fig, height=450), use_container_width=True, config={"displayModeBar": False})

        with t4:
            df_pie = df.groupby("Typ")["Duration"].sum().reset_index()
            fig = px.pie(df_pie, values="Duration", names="Typ", color="Typ",
                         color_discrete_map=COLOR_MAP, hole=0.6, height=450)
            fig.update_traces(textinfo="percent+label", textfont_size=13)
            fig.update_layout(showlegend=False, annotations=[dict(text="Küche", x=0.5, y=0.5, font_size=18, showarrow=False)])
            st.plotly_chart(style_plotly_figure(fig, height=450), use_container_width=True, config={"displayModeBar": False})

        with t5:
            sp = df.groupby(["Dienst", "Skill_Status"])["Duration"].sum().reset_index()
            fig = px.bar(sp, x="Dienst", y="Duration", color="Skill_Status",
                         color_discrete_map={
                             "High-Cost Execution": "#EF4444",
                             "Value-Add": "#10B981",
                             "Qualitäts-Risiko": "#6366F1",
                         },
                         title="Ressourcen-Fehlallokation (Skill-Mismatch)", height=450)
            fig.update_xaxes(categoryorder="array", categoryarray=CHART_ORDER_K)
            st.plotly_chart(style_plotly_figure(fig, height=450), use_container_width=True, config={"displayModeBar": False})

    else:
        t1, t2, t3 = st.tabs(["📅 Gantt-Flow", "⚖️ Aktivitäts-Verteilung", "🎯 Skill-Match"])
        with t1:
            h = 700 if current_sector == "total" else 500
            fig = px.timeline(df, x_start="Start_DT", x_end="End_DT", y="Dienst",
                              color="Typ", hover_name="Task", color_discrete_map=COLOR_MAP, height=h)
            if current_sector == "gastro":
                fig.update_yaxes(categoryorder="array", categoryarray=CHART_ORDER_G)
            st.plotly_chart(style_plotly_figure(fig, height=h), use_container_width=True, config={"displayModeBar": False})

        with t2:
            dfg = df.groupby(["Dienst", "Typ"])["Duration"].sum().reset_index()
            fig = px.bar(dfg, x="Dienst", y="Duration", color="Typ",
                         color_discrete_map=COLOR_MAP, barmode="stack", height=480)
            if current_sector == "gastro":
                fig.update_xaxes(categoryorder="array", categoryarray=CHART_ORDER_G)
            st.plotly_chart(style_plotly_figure(fig, height=480), use_container_width=True, config={"displayModeBar": False})

        with t3:
            sp = df.groupby(["Dienst", "Skill_Status"])["Duration"].sum().reset_index()
            fig = px.bar(sp, x="Dienst", y="Duration", color="Skill_Status",
                         color_discrete_map={
                             "High-Cost Execution": "#EF4444",
                             "Value-Add": "#10B981",
                             "Qualitäts-Risiko": "#6366F1",
                         }, height=450)
            if current_sector == "gastro":
                fig.update_xaxes(categoryorder="array", categoryarray=CHART_ORDER_G)
            st.plotly_chart(style_plotly_figure(fig, height=450), use_container_width=True, config={"displayModeBar": False})

    # ── Personal-Einsatzprofil ───────────────────────────
    section_header('Personal-Einsatzprofil (Staffing Load)', "Visuelle Darstellung der anwesenden Mitarbeiter über den Tagesverlauf.")
    
    load_pts = []
    for h in range(5, 20):
        for m in [0, 15, 30, 45]:
            t = datetime(2026, 1, 1, h, m)
            mask = (df["Start_DT"] <= t) & (df["End_DT"] > t)
            if current_sector == "kitchen":
                mask &= df["Sector"] == "kitchen"
            elif current_sector == "gastro":
                mask &= df["Sector"] == "gastro"
            load_pts.append({"Zeit": f"{h:02d}:{m:02d}", "Staff": int(mask.sum())})

    load_df = pd.DataFrame(load_pts)
    y_max   = 26 if current_sector == "total" else 14

    fig_lp = px.area(load_df, x="Zeit", y="Staff", line_shape="spline")
    fig_lp.update_traces(line_color="#0F172A", fillcolor="rgba(15,23,42,0.05)")
    style_plotly_figure(fig_lp, height=230)
    fig_lp.update_layout(yaxis=dict(range=[0, y_max], title="Active FTE"))
    
    if current_sector == "kitchen":
        fig_lp.add_hline(y=8, line_dash="dot", line_color="#EF4444",
                         annotation_text="Überlastungszone", annotation_position="top right", annotation_font_color="#EF4444")
    st.plotly_chart(fig_lp, use_container_width=True, config={"displayModeBar": False})


if __name__ == "__main__":
    main()
